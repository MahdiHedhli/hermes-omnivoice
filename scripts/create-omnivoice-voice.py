#!/usr/bin/env python3
"""Create local Hermes OmniVoice registry profiles with consent metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import wave


VOICE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
DEFAULT_ALLOWED_USES = ["personal_assistant", "local_generation"]


class CreateVoiceError(RuntimeError):
    pass


def yaml_scalar(value: object) -> str:
    return json.dumps("" if value is None else str(value))


def validate_voice_id(voice_id: str) -> None:
    if not VOICE_ID_RE.fullmatch(voice_id) or voice_id in {".", ".."}:
        raise CreateVoiceError(
            "voice id may contain only letters, numbers, dot, underscore, and dash, "
            "and cannot be . or .."
        )


def validate_speed(speed: float) -> str:
    if speed <= 0:
        raise CreateVoiceError("speed must be greater than 0")
    return f"{speed:g}"


def validate_allowed_uses(values: list[str] | None) -> list[str]:
    allowed_uses = values or DEFAULT_ALLOWED_USES
    clean: list[str] = []
    for value in allowed_uses:
        item = value.strip()
        if not item:
            raise CreateVoiceError("allowed uses cannot be empty")
        clean.append(item)
    return clean


def prepare_voice_dir(voices_dir: Path, voice_id: str, force: bool) -> Path:
    validate_voice_id(voice_id)
    voices_root = voices_dir.expanduser().resolve()
    voice_dir = (voices_root / voice_id).resolve()
    try:
        voice_dir.relative_to(voices_root)
    except ValueError as exc:
        raise CreateVoiceError("voice directory escapes the voices root") from exc
    if voice_dir.exists() and any(voice_dir.iterdir()) and not force:
        raise CreateVoiceError(f"voice directory already contains files: {voice_dir}")
    voice_dir.mkdir(parents=True, exist_ok=True)
    return voice_dir


def validate_wav_file(path: Path) -> None:
    try:
        with wave.open(str(path), "rb") as wav:
            wav.getparams()
    except wave.Error as exc:
        raise CreateVoiceError(f"reference audio is not a valid WAV file: {path}") from exc


def write_voice_yaml(
    *,
    path: Path,
    voice_id: str,
    name: str,
    mode: str,
    language: str,
    speed: str,
    consent_source: str,
    allowed_uses: list[str],
    ref_text: str = "",
    instruct: str = "",
) -> None:
    lines = [
        f"id: {voice_id}",
        f"name: {yaml_scalar(name or voice_id)}",
        "engine: omnivoice",
        f"mode: {mode}",
    ]
    if mode == "clone":
        lines.extend(
            [
                "ref_audio: ref.wav",
                f"ref_text: {yaml_scalar(ref_text)}",
            ]
        )
        if instruct:
            lines.append(f"instruct: {yaml_scalar(instruct)}")
    else:
        lines.append(f"instruct: {yaml_scalar(instruct)}")
    lines.extend(
        [
            f"language: {yaml_scalar(language)}",
            f"speed: {speed}",
            "consent:",
            "  status: confirmed",
            f"  source: {yaml_scalar(consent_source)}",
            "  allowed_uses:",
        ]
    )
    for allowed_use in allowed_uses:
        lines.append(f"    - {yaml_scalar(allowed_use)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def require_consent(args: argparse.Namespace) -> None:
    if not args.confirm_consent:
        raise CreateVoiceError("refusing to create voice without --confirm-consent")


def command_design(args: argparse.Namespace) -> int:
    require_consent(args)
    instruct = args.instruct.strip()
    if not instruct:
        raise CreateVoiceError("design voice requires --instruct")
    voice_dir = prepare_voice_dir(args.voices_dir, args.voice_id, args.force)
    write_voice_yaml(
        path=voice_dir / "voice.yaml",
        voice_id=args.voice_id,
        name=args.name or args.voice_id,
        mode="design",
        language=args.language,
        speed=validate_speed(args.speed),
        consent_source=args.consent_source,
        allowed_uses=validate_allowed_uses(args.allowed_use),
        instruct=instruct,
    )
    print(f"Created design voice {args.voice_id} in {voice_dir}")
    return 0


def command_clone(args: argparse.Namespace) -> int:
    require_consent(args)
    ref_audio = args.ref_audio.expanduser().resolve()
    if ref_audio.suffix.lower() != ".wav":
        raise CreateVoiceError("clone reference audio must be a WAV file")
    if not ref_audio.is_file():
        raise CreateVoiceError(f"reference audio not found: {ref_audio}")
    validate_wav_file(ref_audio)
    ref_text = args.ref_text.strip()
    if not ref_text:
        raise CreateVoiceError("clone voice requires --ref-text")

    voice_dir = prepare_voice_dir(args.voices_dir, args.voice_id, args.force)
    ref_dest = voice_dir / "ref.wav"
    if ref_dest.exists() and not args.force:
        raise CreateVoiceError(f"reference audio already exists: {ref_dest}")
    shutil.copyfile(ref_audio, ref_dest)
    write_voice_yaml(
        path=voice_dir / "voice.yaml",
        voice_id=args.voice_id,
        name=args.name or args.voice_id,
        mode="clone",
        language=args.language,
        speed=validate_speed(args.speed),
        consent_source=args.consent_source,
        allowed_uses=validate_allowed_uses(args.allowed_use),
        ref_text=ref_text,
        instruct=args.instruct.strip(),
    )
    print(f"Created clone voice {args.voice_id} in {voice_dir}")
    return 0


def add_common_options(parser: argparse.ArgumentParser, consent_source: str) -> None:
    parser.add_argument("voice_id")
    parser.add_argument("--name", default=None)
    parser.add_argument("--language", default="en")
    parser.add_argument("--speed", default=1.0, type=float)
    parser.add_argument("--allowed-use", action="append", default=None)
    parser.add_argument("--consent-source", default=consent_source)
    parser.add_argument("--confirm-consent", action="store_true")
    parser.add_argument("--force", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create Hermes OmniVoice profiles")
    parser.add_argument(
        "--voices-dir",
        default=Path("~/.hermes/voices/omnivoice"),
        type=Path,
        help="Directory containing <voice_id>/voice.yaml registries",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    design = subparsers.add_parser("design", help="Create an instruction-designed voice")
    add_common_options(design, "user_created")
    design.add_argument("--instruct", required=True)
    design.set_defaults(func=command_design)

    clone = subparsers.add_parser("clone", help="Create a consented reference-audio voice")
    add_common_options(clone, "user_uploaded")
    clone.add_argument("--ref-audio", required=True, type=Path)
    clone.add_argument("--ref-text", required=True)
    clone.add_argument("--instruct", default="")
    clone.set_defaults(func=command_clone)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, CreateVoiceError) as exc:
        print(f"create-omnivoice-voice: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run())
