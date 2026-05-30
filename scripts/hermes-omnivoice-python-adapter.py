#!/usr/bin/env python3
"""Command adapter that calls the OmniVoice Python API directly."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


class PythonAdapterError(RuntimeError):
    pass


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _load_backend():
    try:
        import soundfile as sf  # type: ignore
        import torch  # type: ignore
        from omnivoice.models.omnivoice import OmniVoice  # type: ignore
    except ImportError as exc:
        raise PythonAdapterError(
            "OmniVoice Python API is not installed; install omnivoice in this "
            "environment or use Studio/CLI command mode"
        ) from exc
    return OmniVoice, sf, torch


def _get_best_device(torch_module) -> str:
    if torch_module.cuda.is_available():
        return "cuda"
    if torch_module.backends.mps.is_available():
        return "mps"
    return "cpu"


def _resolve_dtype(torch_module, dtype_name: str):
    normalized = dtype_name.strip().lower()
    dtypes = {
        "float16": getattr(torch_module, "float16", None),
        "fp16": getattr(torch_module, "float16", None),
        "bfloat16": getattr(torch_module, "bfloat16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
        "float32": getattr(torch_module, "float32", None),
        "fp32": getattr(torch_module, "float32", None),
    }
    dtype = dtypes.get(normalized)
    if dtype is None:
        raise PythonAdapterError(f"unsupported dtype: {dtype_name}")
    return dtype


def synthesize(args: argparse.Namespace) -> None:
    text_file = args.text_file.expanduser().resolve()
    output_path = args.out.expanduser().resolve()
    ref_audio = _optional(args.ref_audio)
    ref_text = _optional(args.ref_text)
    instruct = _optional(args.instruct)
    language = _optional(args.language)

    if not text_file.is_file():
        raise PythonAdapterError(f"text file not found: {text_file}")
    if ref_audio:
        ref_audio_path = Path(ref_audio).expanduser().resolve()
        if not ref_audio_path.is_file():
            raise PythonAdapterError(f"ref_audio not found: {ref_audio_path}")
        if not ref_text:
            raise PythonAdapterError("ref_text is required when ref_audio is provided")
        ref_audio = str(ref_audio_path)
    if not ref_audio and not instruct:
        raise PythonAdapterError("provide ref_audio/ref_text for clone mode or instruct for design mode")

    OmniVoice, soundfile, torch_module = _load_backend()
    device = args.device
    if device == "auto":
        device = _get_best_device(torch_module)
    dtype = _resolve_dtype(torch_module, args.dtype)

    model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=dtype)
    generate_kwargs = {
        "text": text_file.read_text(encoding="utf-8"),
        "speed": args.speed,
    }
    if language:
        generate_kwargs["language"] = language
    if ref_audio:
        generate_kwargs["ref_audio"] = ref_audio
        generate_kwargs["ref_text"] = ref_text
    if instruct:
        generate_kwargs["instruct"] = instruct

    audios = model.generate(**generate_kwargs)
    if not audios:
        raise PythonAdapterError("OmniVoice did not return audio")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sampling_rate = int(getattr(model, "sampling_rate", args.sample_rate))
    soundfile.write(str(output_path), audios[0], sampling_rate)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize audio with the OmniVoice Python API")
    parser.add_argument("--text-file", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--ref-audio", default="")
    parser.add_argument("--ref-text", default="")
    parser.add_argument("--instruct", default="")
    parser.add_argument("--language", default="")
    parser.add_argument("--speed", default=1.0, type=float)
    parser.add_argument("--sample-rate", default=24000, type=int)
    parser.add_argument("--model", default=os.environ.get("HERMES_OMNIVOICE_MODEL", "k2-fsa/OmniVoice"))
    parser.add_argument("--device", default=os.environ.get("HERMES_OMNIVOICE_DEVICE", "auto"))
    parser.add_argument("--dtype", default=os.environ.get("HERMES_OMNIVOICE_DTYPE", "float16"))
    args = parser.parse_args(argv)

    try:
        synthesize(args)
    except (OSError, PythonAdapterError) as exc:
        print(f"hermes-omnivoice-python-adapter: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
