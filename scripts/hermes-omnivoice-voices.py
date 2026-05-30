#!/usr/bin/env python3
"""Inspect and preview Hermes OmniVoice registry entries."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
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
    summary = _profile_summary(args.voices_dir, args.voice)
    if summary["status"] != "ready":
        print(f"Voice {args.voice} is invalid: {summary['error']}", file=sys.stderr)
        return 1
    out_path = args.out.expanduser().resolve()
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
                str(args.speed if args.speed is not None else summary["speed"]),
                "--timeout",
                str(args.timeout),
            ],
            check=False,
            text=True,
        )
    finally:
        text_path.unlink(missing_ok=True)
    if completed.returncode == 0:
        print(f"Preview written: {out_path}")
    return completed.returncode


def command_config(args: argparse.Namespace) -> int:
    script_path = args.script_path or WRAPPER_PATH
    command = (
        f"{sys.executable} {script_path} --voice {{voice}} --speed {{speed}} "
        "--text-file {input_path} --out {output_path}"
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
                "      output_format: wav",
                f"      timeout: {args.timeout}",
                "      voice_compatible: true",
                f"      max_text_length: {args.max_text_length}",
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
    return args.func(args)


if __name__ == "__main__":
    sys.exit(run())
