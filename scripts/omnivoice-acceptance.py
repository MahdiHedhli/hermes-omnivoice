#!/usr/bin/env python3
"""Acceptance summary for the Hermes OmniVoice bridge MVP."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_CHECK_PATH = PROJECT_ROOT / "scripts" / "check-omnivoice-runtime.py"
SOURCE_FINDER_PATH = PROJECT_ROOT / "scripts" / "find-hermes-source.py"
REQUIRED_FILES = [
    "scripts/hermes-omnivoice-tts.py",
    "scripts/hermes-omnivoice-python-adapter.py",
    "scripts/setup-omnivoice-python-env.py",
    "scripts/create-omnivoice-voice.py",
    "scripts/import-omnivoice-studio-voice.py",
    "scripts/hermes-omnivoice-voices.py",
    "scripts/find-hermes-source.py",
    "scripts/check-omnivoice-runtime.py",
    "scripts/install-hermes-omnivoice-bridge.py",
    "scripts/omnivoice-studio-local.py",
    "scripts/test-omnivoice-tts.sh",
    "scripts/validate-omnivoice-bridge.sh",
    "docs/omnivoice-integration-notes.md",
    "docs/omnivoice-mvp-handoff.md",
    "docs/omnivoice-setup.md",
    "docs/omnivoice-studio-bridge.md",
    "docs/omnivoice-acceptance.md",
    "docs/tts-custom-voices.md",
    "examples/hermes-tts-omnivoice.yaml",
    "examples/voices/marvin/voice.yaml",
    "examples/voices/narrator/voice.yaml",
    "HEARTBEAT.md",
]


def load_runtime_check():
    spec = importlib.util.spec_from_file_location("check_omnivoice_runtime", RUNTIME_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runtime check module: {RUNTIME_CHECK_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_source_finder():
    spec = importlib.util.spec_from_file_location("find_hermes_source", SOURCE_FINDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load source finder module: {SOURCE_FINDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_required_files(root: Path) -> dict:
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    return {
        "status": "pass" if not missing else "fail",
        "missing": missing,
        "required_count": len(REQUIRED_FILES),
    }


def evaluate_runtime(runtime_report: dict) -> dict:
    studio_ready = runtime_report["studio"]["status"] == "reachable"
    command_ready = runtime_report["backend_command"]["status"] == "configured"
    cli_ready = (
        runtime_report["omnivoice_cli"]["status"] == "found"
        and runtime_report["omnivoice_cli"].get("auto_enabled") is True
    )
    voices_ready = runtime_report["voices_dir"]["profile_count"] > 0
    return {
        "backend_ready": studio_ready or command_ready or cli_ready,
        "voices_ready": voices_ready,
        "studio_ready": studio_ready,
        "command_ready": command_ready,
        "cli_ready": cli_ready,
    }


def build_report(args: argparse.Namespace, env: dict[str, str]) -> dict:
    runtime_check = load_runtime_check()
    source_finder = load_source_finder()
    runtime_args = argparse.Namespace(
        studio_url=args.studio_url,
        voices_dir=args.voices_dir,
        timeout=args.timeout,
        allow_remote_studio=args.allow_remote_studio,
    )
    runtime_report = runtime_check.build_report(runtime_args, env)
    source_args = argparse.Namespace(
        root=args.source_root,
        max_depth=args.source_max_depth,
        max_candidates=args.source_max_candidates,
        max_files=args.source_max_files,
        max_file_bytes=args.source_max_file_bytes,
        scan_timeout=args.source_scan_timeout,
    )
    source_report = source_finder.discover(source_args)
    static = check_required_files(PROJECT_ROOT)
    runtime = evaluate_runtime(runtime_report)
    mvp_ready = static["status"] == "pass"
    real_backend_ready = runtime["backend_ready"] and runtime["voices_ready"]
    hermes_source_ready = source_report["likely_count"] > 0
    return {
        "mvp_static_ready": mvp_ready,
        "real_backend_ready": real_backend_ready,
        "hermes_source_ready": hermes_source_ready,
        "required_files": static,
        "runtime": runtime,
        "runtime_report": runtime_report,
        "source_discovery": source_report,
    }


def print_human(report: dict) -> None:
    print("Hermes OmniVoice acceptance")
    print(f"- Static MVP files: {'PASS' if report['mvp_static_ready'] else 'FAIL'}")
    if report["required_files"]["missing"]:
        print("  Missing:")
        for path in report["required_files"]["missing"]:
            print(f"  - {path}")
    print(f"- Real backend ready: {'PASS' if report['real_backend_ready'] else 'BLOCKED'}")
    runtime = report["runtime"]
    print(f"  Backend path available: {runtime['backend_ready']}")
    print(f"  Local voice profiles available: {runtime['voices_ready']}")
    print(f"  Studio reachable: {runtime['studio_ready']}")
    print(f"  Command configured: {runtime['command_ready']}")
    print(f"  OmniVoice CLI found: {runtime['cli_ready']}")
    source = report["source_discovery"]
    print(f"- Hermes source ready: {'PASS' if report['hermes_source_ready'] else 'BLOCKED'}")
    print(f"  Source status: {source['status']}")
    print(f"  Likely Hermes Agent checkouts: {source['likely_count']}")
    print(f"  Candidate checkouts: {source['candidate_count']}")
    print(f"  Search truncated: {source['truncated']}")
    if source["candidates"]:
        top_candidate = source["candidates"][0]
        print(f"  Top candidate: {top_candidate['path']}")
        print(f"  Top candidate bridge repo: {top_candidate['is_bridge_repo']}")


def run(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize Hermes OmniVoice MVP acceptance")
    parser.add_argument("--studio-url", default="")
    parser.add_argument("--voices-dir", default=Path("~/.hermes/voices/omnivoice"), type=Path)
    parser.add_argument("--timeout", default=5, type=int)
    parser.add_argument("--allow-remote-studio", action="store_true")
    parser.add_argument("--require-real-backend", action="store_true")
    parser.add_argument("--source-root", action="append", type=Path)
    parser.add_argument("--source-max-depth", default=5, type=int)
    parser.add_argument("--source-max-candidates", default=20, type=int)
    parser.add_argument("--source-max-files", default=2500, type=int)
    parser.add_argument("--source-max-file-bytes", default=65536, type=int)
    parser.add_argument("--source-scan-timeout", default=5, type=int)
    parser.add_argument("--require-hermes-source", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(args, dict(os.environ if env is None else env))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)

    if not report["mvp_static_ready"]:
        return 1
    if args.require_real_backend and not report["real_backend_ready"]:
        return 1
    if args.require_hermes_source and not report["hermes_source_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
