#!/usr/bin/env python3
"""Inspect and preview Hermes OmniVoice registry entries."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


ROOT_DIR = Path(__file__).resolve().parents[1]
WRAPPER_PATH = ROOT_DIR / "scripts" / "hermes-omnivoice-tts.py"
SPEC = importlib.util.spec_from_file_location("hermes_omnivoice_tts", WRAPPER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load wrapper module: {WRAPPER_PATH}")
omnivoice = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(omnivoice)


def _profile_summary(voices_dir: Path, voice_id: str) -> dict:
    try:
        profile, voice_dir = omnivoice.load_voice_profile(voices_dir, voice_id)
        validated = omnivoice.validate_voice_profile(profile, voice_dir)
        consent = validated.get("consent") if isinstance(validated.get("consent"), dict) else {}
        return {
            "id": voice_id,
            "name": validated.get("name") or voice_id,
            "mode": validated.get("mode"),
            "language": validated.get("language") or "Auto",
            "speed": validated.get("speed", 1.0),
            "consent_status": consent.get("status", "missing"),
            "source": consent.get("source", ""),
            "studio_profile_id": validated.get("studio_profile_id", ""),
            "status": "ready",
        }
    except Exception as exc:
        return {
            "id": voice_id,
            "name": voice_id,
            "status": "invalid",
            "error": str(exc),
        }


def list_profiles(voices_dir: Path) -> list[dict]:
    root = voices_dir.expanduser()
    if not root.exists():
        return []
    if root.is_symlink():
        raise RuntimeError(f"voices root cannot be a symlink: {root}")
    profiles = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or not (child / "voice.yaml").exists():
            continue
        profiles.append(_profile_summary(root, child.name))
    return profiles


def print_profiles(profiles: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps({"voices": profiles}, indent=2, sort_keys=True))
        return
    if not profiles:
        print("No OmniVoice profiles found.")
        return
    for profile in profiles:
        if profile["status"] == "ready":
            print(
                f"{profile['id']}\t{profile['name']}\t{profile['mode']}\t"
                f"{profile['language']}\tconsent={profile['consent_status']}"
            )
        else:
            print(f"{profile['id']}\tINVALID\t{profile['error']}")


def command_list(args: argparse.Namespace) -> int:
    print_profiles(list_profiles(args.voices_dir), args.json)
    return 0


def command_info(args: argparse.Namespace) -> int:
    summary = _profile_summary(args.voices_dir, args.voice)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif summary["status"] == "ready":
        print(f"Voice: {summary['id']}")
        print(f"Name: {summary['name']}")
        print(f"Mode: {summary['mode']}")
        print(f"Language: {summary['language']}")
        print(f"Speed: {summary['speed']}")
        print(f"Consent: {summary['consent_status']}")
        if summary.get("studio_profile_id"):
            print(f"Studio profile: {summary['studio_profile_id']}")
    else:
        print(f"Voice {args.voice} is invalid: {summary['error']}", file=sys.stderr)
        return 1
    return 0 if summary["status"] == "ready" else 1


def command_preview(args: argparse.Namespace) -> int:
    timeout = _positive_int(args.timeout, "timeout")
    summary = _profile_summary(args.voices_dir, args.voice)
    if summary["status"] != "ready":
        print(f"Voice {args.voice} is invalid: {summary['error']}", file=sys.stderr)
        return 1
    speed = omnivoice.normalize_speed(args.speed if args.speed is not None else summary["speed"])
    out_path = omnivoice.resolve_output_path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(args.text)
        text_path = Path(handle.name)
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(WRAPPER_PATH),
                "--voices-dir",
                str(args.voices_dir.expanduser()),
                "--text-file",
                str(text_path),
                "--out",
                str(out_path),
                "--voice",
                args.voice,
                "--speed",
                speed,
                "--timeout",
                str(timeout),
            ],
            check=False,
            text=True,
        )
    finally:
        text_path.unlink(missing_ok=True)
    if completed.returncode == 0:
        print(f"Preview written: {out_path}")
    return completed.returncode


def _selection_payload(voices_dir: Path, voice: str, summary: dict) -> dict:
    return {
        "provider": "omnivoice",
        "voice": voice,
        "voices_dir": str(voices_dir.expanduser()),
        "speed": summary["speed"],
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def write_selection_file(path: Path, payload: dict) -> None:
    selection_path = path.expanduser()
    selection_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            dir=str(selection_path.parent),
            encoding="utf-8",
            prefix=f".{selection_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        temp_path.chmod(0o600)
        temp_path.replace(selection_path)
        selection_path.chmod(0o600)
    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise


def command_set(args: argparse.Namespace) -> int:
    summary = _profile_summary(args.voices_dir, args.voice)
    if summary["status"] != "ready":
        print(f"Voice {args.voice} is invalid: {summary['error']}", file=sys.stderr)
        return 1
    selection_path = args.selection_file.expanduser()
    payload = _selection_payload(args.voices_dir, args.voice, summary)
    write_selection_file(selection_path, payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Selected OmniVoice voice {args.voice} in {selection_path}")
    return 0


def command_current(args: argparse.Namespace) -> int:
    selection_path = args.selection_file.expanduser()
    if selection_path.is_symlink():
        print(f"Selection file cannot be a symlink: {selection_path}", file=sys.stderr)
        return 1
    if not selection_path.is_file():
        print(f"No OmniVoice selection found: {selection_path}", file=sys.stderr)
        return 1
    try:
        payload = json.loads(selection_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Selection is not readable JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(payload, dict):
        print("Selection JSON must be an object", file=sys.stderr)
        return 1
    if payload.get("provider") != "omnivoice":
        print("Selection provider is not omnivoice", file=sys.stderr)
        return 1
    voice = payload.get("voice", "")
    if not isinstance(voice, str) or not voice:
        print("Selection is missing voice id", file=sys.stderr)
        return 1
    if "voices_dir" in payload and payload.get("voices_dir") is not None:
        voices_dir_value = payload.get("voices_dir")
    else:
        voices_dir_value = str(args.voices_dir)
    if not isinstance(voices_dir_value, str) or not voices_dir_value:
        print("Selection has invalid voices_dir", file=sys.stderr)
        return 1
    voices_dir = Path(voices_dir_value).expanduser()
    summary = _profile_summary(voices_dir, voice)
    if summary["status"] != "ready":
        print(f"Selected OmniVoice voice {voice} is invalid: {summary['error']}", file=sys.stderr)
        return 1
    current_payload = dict(payload)
    current_payload.update(
        {
            "provider": "omnivoice",
            "voice": voice,
            "voices_dir": str(voices_dir),
            "speed": summary["speed"],
            "status": "ready",
        }
    )
    if args.json:
        print(json.dumps(current_payload, indent=2, sort_keys=True))
        return 0
    print(f"Voice: {current_payload['voice']}")
    print(f"Provider: {current_payload['provider']}")
    print(f"Voices dir: {current_payload['voices_dir']}")
    print(f"Speed: {current_payload['speed']}")
    print("Status: ready")
    return 0


def _positive_int(value: int, name: str) -> int:
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than 0")
    return value


def command_config(args: argparse.Namespace) -> int:
    timeout = _positive_int(args.timeout, "timeout")
    max_text_length = _positive_int(args.max_text_length, "max text length")
    summary = _profile_summary(args.voices_dir, args.voice)
    if summary["status"] != "ready":
        print(f"Voice {args.voice} is invalid: {summary['error']}", file=sys.stderr)
        return 1
    script_path = args.script_path or WRAPPER_PATH
    voices_dir = args.voices_dir.expanduser()
    command = (
        f"{shlex.quote(sys.executable)} {shlex.quote(str(script_path))} "
        f"--voices-dir {shlex.quote(str(voices_dir))} --voice {{voice}} --speed {{speed}} "
        f"--max-chars {max_text_length} --text-file {{input_path}} --out {{output_path}}"
    )
    print(
        "\n".join(
            [
                "tts:",
                "  provider: omnivoice",
                "  providers:",
                "    omnivoice:",
                "      type: command",
                f"      command: {json.dumps(command)}",
                f"      voice: {args.voice}",
                f"      speed: {summary['speed']}",
                "      output_format: wav",
                f"      timeout: {timeout}",
                "      voice_compatible: true",
                f"      max_text_length: {max_text_length}",
            ]
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Hermes OmniVoice profiles")
    parser.add_argument(
        "--voices-dir",
        default=Path("~/.hermes/voices/omnivoice"),
        type=Path,
        help="Directory containing <voice_id>/voice.yaml registries",
    )
    parser.add_argument(
        "--selection-file",
        default=Path("~/.hermes/omnivoice-selection.json"),
        type=Path,
        help="User-level selected OmniVoice profile file",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List local OmniVoice profiles")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=command_list)

    info_parser = subparsers.add_parser("info", help="Show one profile")
    info_parser.add_argument("voice")
    info_parser.add_argument("--json", action="store_true")
    info_parser.set_defaults(func=command_info)

    preview_parser = subparsers.add_parser("preview", help="Generate a short preview")
    preview_parser.add_argument("voice")
    preview_parser.add_argument("--text", default="Hermes custom voice synthesis test.")
    preview_parser.add_argument("--out", required=True, type=Path)
    preview_parser.add_argument("--speed", default=None)
    preview_parser.add_argument("--timeout", default=180, type=int)
    preview_parser.set_defaults(func=command_preview)

    set_parser = subparsers.add_parser("set", help="Set the selected local OmniVoice profile")
    set_parser.add_argument("voice")
    set_parser.add_argument("--json", action="store_true")
    set_parser.set_defaults(func=command_set)

    current_parser = subparsers.add_parser("current", help="Show the selected OmniVoice profile")
    current_parser.add_argument("--json", action="store_true")
    current_parser.set_defaults(func=command_current)

    config_parser = subparsers.add_parser("config", help="Print sample Hermes TTS config")
    config_parser.add_argument("voice")
    config_parser.add_argument("--script-path", default=None)
    config_parser.add_argument("--timeout", default=180, type=int)
    config_parser.add_argument("--max-text-length", default=2000, type=int)
    config_parser.set_defaults(func=command_config)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"hermes-omnivoice-voices: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run())
