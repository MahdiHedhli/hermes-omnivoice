#!/usr/bin/env python3
"""Fail if repo-local OmniVoice artifacts should not be committed."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


FORBIDDEN_SUFFIXES = (
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".m4a",
    ".ckpt",
    ".pt",
    ".pth",
    ".onnx",
    ".safetensors",
)
FORBIDDEN_NAMES = {
    ".env",
    "omnivoice-selection.json",
}
FORBIDDEN_ROOT_DIRS = {
    ".cache",
    ".hermes",
    "cache",
    "checkpoints",
    "models",
    "omnivoice-cache",
    "omnivoice-output",
    "reference-audio",
    "samples",
    "voice-samples",
    "voices",
}
SKIP_DIRS = {
    ".git",
}


def is_forbidden_artifact(path: Path) -> bool:
    name = path.name
    return (
        name in FORBIDDEN_NAMES
        or name.startswith(".env.")
        or name.endswith(FORBIDDEN_SUFFIXES)
    )


def find_forbidden_artifacts(root: Path) -> list[str]:
    root = root.resolve()
    matches: list[str] = []
    for current_root, dirnames, filenames in os.walk(root):
        current = Path(current_root)
        allowed_dirnames: list[str] = []
        for dirname in dirnames:
            if dirname in SKIP_DIRS:
                continue
            path = current / dirname
            relative = path.relative_to(root)
            if len(relative.parts) == 1 and dirname in FORBIDDEN_ROOT_DIRS:
                matches.append(f"{relative.as_posix()}/")
                continue
            allowed_dirnames.append(dirname)
        dirnames[:] = allowed_dirnames
        for filename in filenames:
            path = current / filename
            if is_forbidden_artifact(path):
                matches.append(path.relative_to(root).as_posix())
    return sorted(matches)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that OmniVoice generated artifacts are absent from the repo"
    )
    parser.add_argument("--root", default=Path("."), type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    matches = find_forbidden_artifacts(args.root)
    if args.json:
        print(json.dumps({"matches": matches, "ok": not matches}, indent=2, sort_keys=True))
    if matches:
        print(
            "generated audio, model, cache, env, local voice/sample, or selection artifacts found:",
            file=sys.stderr,
        )
        for match in matches:
            print(match, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
