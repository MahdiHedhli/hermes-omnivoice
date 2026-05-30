#!/usr/bin/env python3
"""Hermes command-provider bridge for OmniVoice-compatible local TTS."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave


VOICE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


class OmniVoiceConfigError(RuntimeError):
    """Raised when a voice profile or backend command is not usable."""


def _strip_inline_comment(value: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(value):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return value[:index].rstrip()
    return value.rstrip()


def _parse_scalar(value: str):
    value = _strip_inline_comment(value.strip())
    if value == "":
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_yaml_subset(text: str) -> dict:
    """Parse the small YAML subset used by Hermes voice registry files.

    PyYAML is intentionally optional so the wrapper remains usable in a minimal
    Hermes install. This fallback supports nested mappings and scalar lists.
    """

    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(-1, root)]

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        text_line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise OmniVoiceConfigError(f"invalid indentation at line {line_number}")

        parent = stack[-1][1]
        if text_line.startswith("- "):
            if not isinstance(parent, list):
                raise OmniVoiceConfigError(f"unexpected list item at line {line_number}")
            parent.append(_parse_scalar(text_line[2:]))
            continue

        if ":" not in text_line:
            raise OmniVoiceConfigError(f"expected key/value at line {line_number}")
        key, raw_value = text_line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if not isinstance(parent, dict):
            raise OmniVoiceConfigError(f"cannot add key under list at line {line_number}")
        if not key:
            raise OmniVoiceConfigError(f"empty key at line {line_number}")

        if raw_value == "":
            child: dict | list = [] if key == "allowed_uses" else {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(raw_value)

    return root


def load_voice_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return _parse_yaml_subset(path.read_text(encoding="utf-8"))

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise OmniVoiceConfigError(f"{path} must contain a YAML mapping")
    return loaded


def resolve_voice_dir(voices_dir: Path, voice_id: str) -> Path:
    if not VOICE_ID_RE.fullmatch(voice_id) or voice_id in {".", ".."}:
        raise OmniVoiceConfigError(
            "voice id may contain only letters, numbers, dot, underscore, and dash, "
            "and cannot be . or .."
        )
    resolved_root = voices_dir.expanduser().resolve()
    resolved_child = (resolved_root / voice_id).resolve()
    try:
        resolved_child.relative_to(resolved_root)
    except ValueError as exc:
        raise OmniVoiceConfigError("voice directory escapes the voices root") from exc
    return resolved_child


def _safe_child_path(parent: Path, child: str) -> Path:
    resolved_parent = parent.resolve()
    resolved_child = (resolved_parent / child).resolve()
    try:
        resolved_child.relative_to(resolved_parent)
    except ValueError as exc:
        raise OmniVoiceConfigError("voice profile path escapes the voice directory") from exc
    return resolved_child


def load_voice_profile(voices_dir: Path, voice_id: str) -> tuple[dict, Path]:
    voice_dir = resolve_voice_dir(voices_dir, voice_id)
    profile_path = voice_dir / "voice.yaml"
    if not profile_path.exists():
        raise OmniVoiceConfigError(f"voice profile not found: {profile_path}")

    profile = load_voice_yaml(profile_path)
    if profile.get("id") and str(profile["id"]) != voice_id:
        raise OmniVoiceConfigError(
            f"voice profile id {profile['id']!r} does not match requested voice {voice_id!r}"
        )
    return profile, voice_dir


def validate_voice_profile(profile: dict, voice_dir: Path) -> dict:
    engine = str(profile.get("engine", "")).strip()
    mode = str(profile.get("mode", "")).strip()
    consent = profile.get("consent")

    if engine != "omnivoice":
        raise OmniVoiceConfigError("voice profile engine must be 'omnivoice'")
    if mode not in {"clone", "design"}:
        raise OmniVoiceConfigError("voice profile mode must be 'clone' or 'design'")
    if not isinstance(consent, dict) or consent.get("status") != "confirmed":
        raise OmniVoiceConfigError("voice profile requires consent.status: confirmed")

    resolved = dict(profile)
    if mode == "clone":
        ref_audio = str(profile.get("ref_audio", "")).strip()
        ref_text = str(profile.get("ref_text", "")).strip()
        if not ref_audio:
            raise OmniVoiceConfigError("clone voice requires ref_audio")
        if not ref_text:
            raise OmniVoiceConfigError("clone voice requires ref_text")
        ref_audio_path = _safe_child_path(voice_dir, ref_audio)
        if not ref_audio_path.is_file():
            raise OmniVoiceConfigError(f"clone voice ref_audio is missing: {ref_audio_path}")
        resolved["ref_audio_path"] = str(ref_audio_path)
    elif not str(profile.get("instruct", "")).strip():
        raise OmniVoiceConfigError("design voice requires instruct")

    return resolved


def build_backend_command(
    *,
    env: dict[str, str],
    profile: dict,
    voice_id: str,
    voice_dir: Path,
    text_file: Path,
    output_path: Path,
    speed: str,
) -> list[str]:
    mapping = {
        "text_file": str(text_file),
        "input_path": str(text_file),
        "out": str(output_path),
        "output_path": str(output_path),
        "voice": voice_id,
        "voice_id": voice_id,
        "voice_dir": str(voice_dir),
        "speed": speed,
        "language": str(profile.get("language", "")),
        "ref_audio": str(profile.get("ref_audio_path", "")),
        "ref_text": str(profile.get("ref_text", "")),
        "instruct": str(profile.get("instruct", "")),
    }

    json_template = env.get("HERMES_OMNIVOICE_COMMAND_JSON")
    if json_template:
        try:
            argv = json.loads(json_template)
        except json.JSONDecodeError as exc:
            raise OmniVoiceConfigError("HERMES_OMNIVOICE_COMMAND_JSON is not valid JSON") from exc
        if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
            raise OmniVoiceConfigError("HERMES_OMNIVOICE_COMMAND_JSON must be a JSON string array")
        return [item.format_map(mapping) for item in argv]

    string_template = env.get("HERMES_OMNIVOICE_COMMAND")
    if string_template:
        quoted = {key: shlex.quote(value) for key, value in mapping.items()}
        return shlex.split(string_template.format_map(quoted))

    omnivoice_bin = shutil.which("omnivoice")
    if omnivoice_bin and env.get("HERMES_OMNIVOICE_AUTO_CLI") == "1":
        return [
            omnivoice_bin,
            "tts",
            "--text-file",
            str(text_file),
            "--out",
            str(output_path),
            "--voice",
            voice_id,
            "--speed",
            speed,
        ]

    raise OmniVoiceConfigError(
        "no OmniVoice backend configured; set HERMES_OMNIVOICE_COMMAND_JSON "
        "or HERMES_OMNIVOICE_COMMAND"
    )


def validate_audio_file(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise OmniVoiceConfigError(f"backend did not create audio output: {path}")
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as wav:
                wav.getparams()
        except wave.Error as exc:
            raise OmniVoiceConfigError(f"output is not a valid WAV file: {path}") from exc


def validate_studio_url(url: str, env: dict[str, str]) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise OmniVoiceConfigError("Studio URL must be an absolute http(s) URL")
    host = parsed.hostname or ""
    allow_remote = env.get("HERMES_OMNIVOICE_ALLOW_REMOTE_STUDIO") == "1"
    if host not in LOOPBACK_HOSTS and not host.endswith(".localhost") and not allow_remote:
        raise OmniVoiceConfigError(
            "refusing non-loopback OmniVoice-Studio URL; set "
            "HERMES_OMNIVOICE_ALLOW_REMOTE_STUDIO=1 only after adding auth"
        )
    return url.rstrip("/")


def _multipart_form(
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
) -> tuple[bytes, str]:
    boundary = f"----hermes-omnivoice-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode("ascii"))
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii")
        )
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    for name, (filename, content, content_type) in files.items():
        safe_name = os.path.basename(filename) or "audio.wav"
        chunks.append(f"--{boundary}\r\n".encode("ascii"))
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{safe_name}"\r\n'
            ).encode("ascii")
        )
        chunks.append(f"Content-Type: {content_type}\r\n\r\n".encode("ascii"))
        chunks.append(content)
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def synthesize_with_studio_api(
    *,
    studio_url: str,
    profile: dict,
    voice_dir: Path,
    text_file: Path,
    output_path: Path,
    speed: str,
    env: dict[str, str],
    timeout: int,
) -> None:
    base_url = validate_studio_url(studio_url, env)
    endpoint = f"{base_url}/generate"
    text = text_file.read_text(encoding="utf-8")
    fields = {
        "text": text,
        "speed": speed,
        "language": str(profile.get("language", "Auto") or "Auto"),
    }
    files: dict[str, tuple[str, bytes, str]] = {}

    studio_profile_id = str(profile.get("studio_profile_id", "")).strip()
    if studio_profile_id:
        fields["profile_id"] = studio_profile_id
    elif profile.get("mode") == "clone":
        ref_audio = Path(str(profile["ref_audio_path"]))
        fields["ref_text"] = str(profile.get("ref_text", ""))
        if profile.get("instruct"):
            fields["instruct"] = str(profile["instruct"])
        files["ref_audio"] = (ref_audio.name, ref_audio.read_bytes(), "audio/wav")
    else:
        fields["instruct"] = str(profile.get("instruct", ""))

    body, content_type = _multipart_form(fields, files)
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": content_type,
            "Accept": "audio/wav",
            "User-Agent": "hermes-omnivoice-tts/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise OmniVoiceConfigError(
            f"OmniVoice-Studio API failed with HTTP {exc.code}: {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise OmniVoiceConfigError(f"OmniVoice-Studio API is unreachable: {exc}") from exc

    output_path.write_bytes(payload)
    validate_audio_file(output_path)


def run(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize Hermes TTS with OmniVoice")
    parser.add_argument("--text-file", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--speed", default=None)
    parser.add_argument(
        "--voices-dir",
        default="~/.hermes/voices/omnivoice",
        type=Path,
        help="Directory containing <voice_id>/voice.yaml registries",
    )
    parser.add_argument("--timeout", default=180, type=int)
    args = parser.parse_args(argv)

    runtime_env = dict(os.environ if env is None else env)

    try:
        text_file = args.text_file.expanduser().resolve()
        output_path = args.out.expanduser().resolve()
        if not text_file.is_file():
            raise OmniVoiceConfigError(f"text file not found: {text_file}")

        profile, voice_dir = load_voice_profile(args.voices_dir, args.voice)
        profile = validate_voice_profile(profile, voice_dir)
        speed = str(args.speed if args.speed is not None else profile.get("speed", "1.0"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        studio_url = str(
            profile.get("studio_url") or runtime_env.get("HERMES_OMNIVOICE_STUDIO_URL") or ""
        ).strip()
        has_explicit_command = bool(
            runtime_env.get("HERMES_OMNIVOICE_COMMAND_JSON")
            or runtime_env.get("HERMES_OMNIVOICE_COMMAND")
        )
        if studio_url and not has_explicit_command:
            synthesize_with_studio_api(
                studio_url=studio_url,
                profile=profile,
                voice_dir=voice_dir,
                text_file=text_file,
                output_path=output_path,
                speed=speed,
                env=runtime_env,
                timeout=args.timeout,
            )
        else:
            command = build_backend_command(
                env=runtime_env,
                profile=profile,
                voice_id=args.voice,
                voice_dir=voice_dir,
                text_file=text_file,
                output_path=output_path,
                speed=speed,
            )
            completed = subprocess.run(
                command,
                check=False,
                text=True,
                capture_output=True,
                timeout=args.timeout,
            )
            if completed.returncode != 0:
                if completed.stderr:
                    print(completed.stderr.strip(), file=sys.stderr)
                raise OmniVoiceConfigError(
                    f"OmniVoice backend failed with exit code {completed.returncode}"
                )
            validate_audio_file(output_path)
    except (OSError, subprocess.SubprocessError, OmniVoiceConfigError) as exc:
        print(f"hermes-omnivoice-tts: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run())
