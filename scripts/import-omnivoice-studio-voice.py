#!/usr/bin/env python3
"""Import an OmniVoice-Studio profile into the Hermes local voice registry."""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import wave


VOICE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


class ImportErrorWithContext(RuntimeError):
    pass


def validate_voice_id(voice_id: str) -> None:
    if not VOICE_ID_RE.fullmatch(voice_id) or voice_id in {".", ".."}:
        raise ImportErrorWithContext("voice id contains unsupported characters")


def resolve_voice_dir(voices_dir: Path, voice_id: str) -> Path:
    validate_voice_id(voice_id)
    resolved_root = voices_dir.expanduser().resolve()
    resolved_child = (resolved_root / voice_id).resolve()
    try:
        resolved_child.relative_to(resolved_root)
    except ValueError as exc:
        raise ImportErrorWithContext("voice directory escapes the voices root") from exc
    return resolved_child


def prepare_voice_dir(voices_dir: Path, voice_id: str, force: bool) -> Path:
    voice_dir = resolve_voice_dir(voices_dir, voice_id)
    if voice_dir.exists() and any(voice_dir.iterdir()) and not force:
        raise ImportErrorWithContext(f"voice directory already contains files: {voice_dir}")
    voice_dir.mkdir(parents=True, exist_ok=True)
    voice_dir.chmod(PRIVATE_DIR_MODE)
    return voice_dir


def replace_private_file(path: Path, mode: str, data: str | bytes) -> None:
    fd = -1
    tmp_path: Path | None = None
    try:
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        tmp_path = Path(tmp_name)
        os.chmod(tmp_path, PRIVATE_FILE_MODE)
        if "b" in mode:
            with os.fdopen(fd, mode) as handle:
                fd = -1
                handle.write(data)
        else:
            with os.fdopen(fd, mode, encoding="utf-8") as handle:
                fd = -1
                handle.write(data)
        os.replace(tmp_path, path)
    except Exception:
        if fd != -1:
            os.close(fd)
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise


def validate_studio_url(url: str, allow_remote: bool = False) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ImportErrorWithContext("Studio URL must be an absolute http(s) URL")
    host = parsed.hostname or ""
    if host not in LOOPBACK_HOSTS and not host.endswith(".localhost") and not allow_remote:
        raise ImportErrorWithContext(
            "refusing non-loopback Studio URL; expose OmniVoice-Studio only behind auth"
        )
    return url.rstrip("/")


def request_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "hermes-omnivoice-import/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_bytes(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"Accept": "audio/wav", "User-Agent": "hermes-omnivoice-import/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def validate_wav_bytes(audio_bytes: bytes) -> None:
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav:
            wav.getparams()
    except wave.Error as exc:
        raise ImportErrorWithContext("downloaded Studio reference audio is not a valid WAV") from exc


def yaml_scalar(value: object) -> str:
    return json.dumps("" if value is None else str(value))


def write_voice_yaml(path: Path, profile: dict, voice_id: str, mode: str, allowed_uses: list[str]) -> None:
    lines = [
        f"id: {voice_id}",
        f"name: {yaml_scalar(profile.get('name') or voice_id)}",
        "engine: omnivoice",
        f"mode: {mode}",
    ]
    if mode == "clone":
        lines.extend(
            [
                "ref_audio: ref.wav",
                f"ref_text: {yaml_scalar(profile.get('ref_text') or '')}",
            ]
        )
        if profile.get("instruct"):
            lines.append(f"instruct: {yaml_scalar(profile.get('instruct'))}")
    else:
        lines.append(f"instruct: {yaml_scalar(profile.get('instruct') or '')}")
    lines.extend(
        [
            f"language: {yaml_scalar(profile.get('language') or 'Auto')}",
            "speed: 1.0",
            f"studio_profile_id: {yaml_scalar(profile.get('id') or '')}",
            "consent:",
            "  status: confirmed",
            "  source: user_confirmed_studio_import",
            "  allowed_uses:",
        ]
    )
    for use in allowed_uses:
        lines.append(f"    - {use}")
    replace_private_file(path, "w", "\n".join(lines) + "\n")


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import an OmniVoice-Studio voice profile")
    parser.add_argument("--studio-url", default="http://127.0.0.1:3900")
    parser.add_argument("--profile-id", required=True)
    parser.add_argument("--voice-id", default=None)
    parser.add_argument("--voices-dir", type=Path, default=Path("~/.hermes/voices/omnivoice"))
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument(
        "--allowed-use",
        action="append",
        default=None,
        help="Consent allowed use to write; may be repeated",
    )
    parser.add_argument(
        "--confirm-consent",
        action="store_true",
        help="Confirm that you may use this voice for local Hermes generation",
    )
    parser.add_argument(
        "--allow-remote-studio",
        action="store_true",
        help="Allow a non-loopback Studio URL only when it is protected by auth",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing local voice directory",
    )
    args = parser.parse_args(argv)

    try:
        if not args.confirm_consent:
            raise ImportErrorWithContext("refusing import without --confirm-consent")
        voice_id = args.voice_id or args.profile_id
        validate_voice_id(voice_id)
        voice_dir = prepare_voice_dir(args.voices_dir, voice_id, args.force)

        base_url = validate_studio_url(args.studio_url, args.allow_remote_studio)
        profile = request_json(f"{base_url}/profiles/{urllib.parse.quote(args.profile_id)}", args.timeout)

        audio_bytes = b""
        try:
            audio_bytes = request_bytes(
                f"{base_url}/profiles/{urllib.parse.quote(args.profile_id)}/audio",
                args.timeout,
            )
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise

        has_instruct = bool(str(profile.get("instruct") or "").strip())
        mode = "clone" if audio_bytes else "design"
        if mode == "clone":
            validate_wav_bytes(audio_bytes)
            replace_private_file(voice_dir / "ref.wav", "wb", audio_bytes)
        elif not has_instruct:
            raise ImportErrorWithContext(
                "Studio profile has no downloadable audio and no design instruction"
            )

        write_voice_yaml(
            voice_dir / "voice.yaml",
            profile,
            voice_id,
            mode,
            args.allowed_use or ["personal_assistant", "local_generation"],
        )
        print(f"Imported Studio profile {args.profile_id} as {voice_id} in {voice_dir}")
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ImportErrorWithContext) as exc:
        print(f"import-omnivoice-studio-voice: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
