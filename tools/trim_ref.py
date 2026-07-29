#!/usr/bin/env python3
"""Trim a long clone reference to a short one — on a real line boundary.

Reference length is the single biggest factor in how fast a cloned voice
speaks (measured here: a ~10s reference reached the first word 3x sooner than
a 35s one and stopped stalling mid-reply — see README "Speed"). But a naive
`ffmpeg -t 9` cut slices mid-word and leaves the transcript wrong, which hurts
cloning quality. This trims properly:

  1. word-level Whisper timestamps over the full reference
  2. aligned against the TRUE transcript you already have (one spoken line
     per input line — the same text you pasted when cloning)
  3. cut at the end of the last complete line inside the target window
  4. prints the exact transcript the cut contains, ready to paste into a
     re-clone (dashboard Clone tab, or ov_core.registry.create_clone)

Example:
  python tools/trim_ref.py \
      --src ~/.hermes/voices/omnivoice/myvoice/ref.wav \
      --transcript lines.txt --out /tmp/myvoice_short.wav

Deps: transformers (Whisper) — same as tools/qc.py.
Exit codes: 0 ok, 2 no usable boundary / bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
import wave
from pathlib import Path

warnings.filterwarnings("ignore")


def _norm(s: str) -> list[str]:
    return re.sub(r"[^a-z' ]", " ", s.lower()).split()


def align_line_ends(src: str, lines: list[str], asr_model: str) -> dict[int, float]:
    """End timestamp of each true line, via greedy fuzzy word alignment.

    Whisper mishears words; because the line ORDER is known, matching each
    heard word against the next few expected words (exact, or first-two-letter
    fuzzy) is enough to pin line boundaries.
    """
    from transformers import pipeline
    asr = pipeline("automatic-speech-recognition", model=asr_model,
                   return_timestamps="word")
    chunks = asr(src)["chunks"]

    flat: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        for w in _norm(line):
            flat.append((i, w))

    ends: dict[int, float] = {}
    fi = 0
    for chunk in chunks:
        if fi >= len(flat):
            break
        heard = _norm(chunk["text"])
        if not heard:
            continue
        h = heard[0]
        for look in range(3):
            if fi + look >= len(flat):
                break
            li, target = flat[fi + look]
            if h == target or (len(h) > 1 and len(target) > 1 and h[:2] == target[:2]):
                fi = fi + look + 1
                if chunk["timestamp"][1] is not None:
                    ends[li] = float(chunk["timestamp"][1])
                break
    return ends


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--src", required=True, help="the long reference .wav")
    p.add_argument("--transcript", required=True,
                   help="text file: the true transcript, one spoken line per line")
    p.add_argument("--out", required=True, help="where to write the trimmed .wav")
    p.add_argument("--window", default="6,11",
                   help="acceptable cut window in seconds, lo,hi (default 6,11)")
    p.add_argument("--pad", type=float, default=0.20,
                   help="seconds kept after the final word (default 0.20)")
    p.add_argument("--asr-model", default="openai/whisper-tiny.en")
    args = p.parse_args(argv)

    lines = [ln.strip() for ln in Path(args.transcript).read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    if not lines:
        print("transcript file has no lines", file=sys.stderr)
        return 2
    try:
        lo, hi = (float(x) for x in args.window.split(","))
    except ValueError:
        print(f"bad --window {args.window!r}; expected lo,hi", file=sys.stderr)
        return 2

    ends = align_line_ends(args.src, lines, args.asr_model)
    print("line end-times:")
    for i, line in enumerate(lines):
        t = ends.get(i)
        print(f"  {f'{t:6.2f}' if t is not None else '     ?'}  {line}")

    best = None
    for i in sorted(ends):
        if lo <= ends[i] <= hi:
            best = (i, ends[i])
    if best is None:
        print(f"\nno line ends inside {lo}-{hi}s — widen --window using the times above",
              file=sys.stderr)
        return 2

    cut_line, cut_t = best
    cut_t += args.pad
    kept = lines[:cut_line + 1]

    with wave.open(args.src, "rb") as w:
        sr = w.getframerate()
        params = w.getparams()
        frames = w.readframes(int(sr * cut_t))
    with wave.open(args.out, "wb") as o:
        o.setnchannels(params.nchannels)
        o.setsampwidth(params.sampwidth)
        o.setframerate(sr)
        o.writeframes(frames)

    meta = Path(args.out).with_suffix(".json")
    meta.write_text(json.dumps({"cut_s": round(cut_t, 2), "lines": kept}, indent=2))

    print(f"\ncut at {cut_t:.2f}s — end of {lines[cut_line]!r} + {args.pad}s pad")
    print(f"wav  -> {args.out}")
    print(f"meta -> {meta}")
    print("\nre-clone with EXACTLY this transcript:")
    print("\n".join(kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())
