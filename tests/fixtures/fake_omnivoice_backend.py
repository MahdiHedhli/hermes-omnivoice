#!/usr/bin/env python3
"""Deterministic local backend for testing the Hermes OmniVoice wrapper."""

from __future__ import annotations

import argparse
import math
import struct
import wave


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--voice-dir", default="")
    parser.add_argument("--speed", default="1.0")
    parser.add_argument("--voice", default="")
    args = parser.parse_args()

    with open(args.text_file, "r", encoding="utf-8") as handle:
        text = handle.read().strip()
    if not text:
        raise SystemExit("text input is empty")

    sample_rate = 16000
    duration = 0.12
    frames = int(sample_rate * duration)
    amplitude = 5000
    frequency = 440.0

    with wave.open(args.out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for index in range(frames):
            value = int(amplitude * math.sin(2.0 * math.pi * frequency * index / sample_rate))
            wav.writeframesraw(struct.pack("<h", value))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
