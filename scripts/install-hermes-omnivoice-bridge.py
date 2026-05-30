#!/usr/bin/env python3
"""Install the Hermes OmniVoice command-provider bridge into a target tree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MANIFEST = [
    "scripts/hermes-omnivoice-tts.py",
    "scripts/create-omnivoice-voice.py",
    "scripts/import-omnivoice-studio-voice.py",
    "scripts/hermes-omnivoice-voices.py",
    "scripts/check-omnivoice-runtime.py",
    "scripts/omnivoice-studio-local.py",
    "scripts/omnivoice-acceptance.py",
    "scripts/test-omnivoice-tts.sh",
    "docs/omnivoice-integration-notes.md",
    "docs/omnivoice-setup.md",
    "docs/omnivoice-studio-bridge.md",
    "docs/omnivoice-acceptance.md",
    "docs/tts-custom-voices.md",
]
EXAMPLE_MANIFEST = [
    "examples/hermes-tts-omnivoice.yaml",
    "examples/voices/marvin/voice.yaml",
    "examples/voices/narrator/voice.yaml",
]


class InstallError(RuntimeError):
    pass


def resolve_target(root: Path, relative_path: str) -> Path:
    target_root = root.expanduser().resolve()
    target = (target_root / relative_path).resolve()
    try:
        target.relative_to(target_root)
    except ValueError as exc:
        raise InstallError(f"target path escapes install root: {relative_path}") from exc
    return target


def install_manifest(
    *,
    target_root: Path,
    manifest: list[str],
    force: bool,
    dry_run: bool,
) -> list[dict]:
    actions: list[dict] = []
    for relative_path in manifest:
        source = PROJECT_ROOT / relative_path
        if not source.is_file():
            raise InstallError(f"source file missing: {relative_path}")
        target = resolve_target(target_root, relative_path)
        action = "copy"
        if target.exists():
            if not force:
                raise InstallError(f"target exists; use --force to overwrite: {target}")
            action = "overwrite"
        actions.append({"action": action, "source": str(source), "target": str(target)})
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return actions


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Hermes OmniVoice bridge files")
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--with-examples", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    manifest = list(BASE_MANIFEST)
    if args.with_examples:
        manifest.extend(EXAMPLE_MANIFEST)

    try:
        actions = install_manifest(
            target_root=args.target_root,
            manifest=manifest,
            force=args.force,
            dry_run=args.dry_run,
        )
    except (OSError, InstallError) as exc:
        print(f"install-hermes-omnivoice-bridge: {exc}", file=sys.stderr)
        return 1

    report = {
        "target_root": str(args.target_root.expanduser().resolve()),
        "dry_run": args.dry_run,
        "files": len(actions),
        "actions": actions,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        mode = "Would install" if args.dry_run else "Installed"
        print(f"{mode} {len(actions)} Hermes OmniVoice bridge files into {report['target_root']}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
