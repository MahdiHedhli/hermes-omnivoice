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
    "scripts/hermes-omnivoice-remote.py",
    "scripts/hermes-omnivoice-python-adapter.py",
    "scripts/setup-omnivoice-python-env.py",
    "scripts/create-omnivoice-voice.py",
    "scripts/import-omnivoice-studio-voice.py",
    "scripts/hermes-omnivoice-voices.py",
    "scripts/find-hermes-source.py",
    "scripts/check-omnivoice-runtime.py",
    "scripts/omnivoice-studio-local.py",
    "scripts/omnivoice-status.sh",
    "scripts/omnivoice-enable.sh",
    "scripts/omnivoice-disable.sh",
    "scripts/omnivoice-qc-sample.sh",
    "scripts/omnivoice-acceptance.py",
    "scripts/test-omnivoice-tts.sh",
    "scripts/test-omnivoice-remote.sh",
    "docs/omnivoice-integration-notes.md",
    "docs/omnivoice-mvp-handoff.md",
    "docs/omnivoice-setup.md",
    "docs/omnivoice-studio-bridge.md",
    "docs/omnivoice-weekend-summary.md",
    "docs/omnivoice-acceptance.md",
    "docs/features-install-paths.md",
    "docs/omnivoice-operator-runbook.md",
    "docs/omnivoice-qc.md",
    "docs/omnivoice-remote-mvp.md",
    "docs/omnivoice-fastapi-fork-review.md",
    "docs/tts-custom-voices.md",
]
EXAMPLE_MANIFEST = [
    "examples/hermes-tts-omnivoice.yaml",
    "examples/hermes-tts-omnivoice-remote.yaml",
    "examples/hermes-tts-omnivoice-remote-ssh-loopback.yaml",
    "examples/voices/marvin/voice.yaml",
    "examples/voices/narrator/voice.yaml",
]
GITIGNORE_START = "# BEGIN Hermes OmniVoice local artifacts"
GITIGNORE_END = "# END Hermes OmniVoice local artifacts"
GITIGNORE_PATTERNS = [
    ".hermes/",
    "omnivoice-output/",
    "omnivoice-cache/",
    "/voices/",
    "/samples/",
    "/voice-samples/",
    "/reference-audio/",
    "*.wav",
    "*.mp3",
    "*.flac",
    "*.ogg",
    "*.m4a",
    "models/",
    "checkpoints/",
    "cache/",
    ".cache/",
    "*.ckpt",
    "*.pt",
    "*.pth",
    "*.onnx",
    "*.safetensors",
    ".env",
    ".env.*",
    "!.env.example",
    ".env.local",
    "*.local",
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


def read_gitignore(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_gitignore_block() -> str:
    lines = [
        GITIGNORE_START,
        "# Generated audio, local voices, model files, caches, and local config.",
        *GITIGNORE_PATTERNS,
        GITIGNORE_END,
    ]
    return "\n".join(lines) + "\n"


def replace_gitignore_block(existing: str) -> str:
    start = existing.index(GITIGNORE_START)
    end = existing.index(GITIGNORE_END, start)
    end_line = existing.find("\n", end)
    if end_line == -1:
        end_line = len(existing)
    else:
        end_line += 1
    return existing[:start] + build_gitignore_block() + existing[end_line:]


def update_gitignore(*, target_root: Path, dry_run: bool, requested: bool) -> dict:
    target = resolve_target(target_root, ".gitignore")
    existing = read_gitignore(target)
    existing_lines = set(existing.splitlines())
    missing = [pattern for pattern in GITIGNORE_PATTERNS if pattern not in existing_lines]
    report = {
        "target": str(target),
        "update_requested": requested,
        "missing_patterns": missing,
        "action": "none",
        "status": "covered" if not missing else "missing_patterns",
    }
    managed = GITIGNORE_START in existing and GITIGNORE_END in existing
    if managed and not missing:
        report["status"] = "managed"
        return report
    if managed:
        report["status"] = "managed_missing_patterns"
        if not requested:
            report["action"] = "review"
            return report
        report["action"] = "would_update" if dry_run else "update"
        if dry_run:
            return report
        target.write_text(replace_gitignore_block(existing), encoding="utf-8")
        return report
    if not requested:
        report["action"] = "review"
        return report

    report["action"] = "would_append" if dry_run else "append"
    if dry_run:
        return report

    target.parent.mkdir(parents=True, exist_ok=True)
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    separator = "" if not existing else "\n"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(prefix)
        handle.write(separator)
        handle.write(build_gitignore_block())
    return report


def describe_gitignore(gitignore: dict, *, requested: bool) -> str | None:
    status = gitignore["status"]
    action = gitignore["action"]
    if status != "covered" and not requested:
        return (
            "Review target .gitignore: missing OmniVoice local-artifact patterns; "
            "rerun with --update-gitignore after reviewing the dry-run output."
        )
    if action in {"append", "would_append"}:
        verb = "Would append" if action == "would_append" else "Appended"
        return f"{verb} target .gitignore OmniVoice safety block."
    if action in {"update", "would_update"}:
        verb = "Would refresh" if action == "would_update" else "Refreshed"
        return f"{verb} target .gitignore OmniVoice safety block."
    if status == "managed":
        return "Target .gitignore already has the managed OmniVoice safety block."
    if status == "covered":
        return "Target .gitignore already covers OmniVoice local-artifact patterns."
    return None


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Hermes OmniVoice bridge files")
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--with-examples", action="store_true")
    parser.add_argument("--update-gitignore", action="store_true")
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
        gitignore = update_gitignore(
            target_root=args.target_root,
            dry_run=args.dry_run,
            requested=args.update_gitignore,
        )
    except (OSError, InstallError) as exc:
        print(f"install-hermes-omnivoice-bridge: {exc}", file=sys.stderr)
        return 1

    report = {
        "target_root": str(args.target_root.expanduser().resolve()),
        "dry_run": args.dry_run,
        "files": len(actions),
        "actions": actions,
        "gitignore": gitignore,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        mode = "Would install" if args.dry_run else "Installed"
        print(f"{mode} {len(actions)} Hermes OmniVoice bridge files into {report['target_root']}")
        gitignore_message = describe_gitignore(gitignore, requested=args.update_gitignore)
        if gitignore_message:
            print(gitignore_message)
    return 0


if __name__ == "__main__":
    sys.exit(run())
