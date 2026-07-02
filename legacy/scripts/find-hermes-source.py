#!/usr/bin/env python3
"""Read-only discovery helper for locating a Hermes Agent source checkout."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time


DEFAULT_ROOTS = [
    Path("/opt/hermes-agent/source"),
    Path("~/Documents/Coding/hermes"),
    Path("~/Documents/Coding"),
    Path("~/.hermes"),
    Path("~/.config/hermes"),
]
SKIP_DIRS = {
    ".cache",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
}
SENSITIVE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".npmrc",
    ".pypirc",
    "id_rsa",
    "id_ed25519",
}
TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rs",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
TTS_NAME_TERMS = ("tts", "speech", "voice", "audio", "provider")
CONTENT_TERMS = ("tts", "text-to-speech", "speech", "voice", "provider")
EXPIRED_CANDIDATE_INSPECTION_GRACE_SECONDS = 1.0


class SourceDiscoveryError(RuntimeError):
    pass


def validate_scan_timeout(value: int) -> int:
    if value <= 0:
        raise SourceDiscoveryError("scan timeout must be greater than 0")
    return value


def validate_positive_bound(value: int, name: str) -> int:
    if value <= 0:
        raise SourceDiscoveryError(f"{name} must be greater than 0")
    return value


def validate_max_depth(value: int) -> int:
    if value < 0:
        raise SourceDiscoveryError("max depth must be at least 0")
    return value


def safe_resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def depth_from(root: Path, path: Path) -> int:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return 0
    if str(relative) == ".":
        return 0
    return len(relative.parts)


def is_sensitive_file(path: Path) -> bool:
    name = path.name
    if name in SENSITIVE_FILE_NAMES:
        return True
    if name.startswith(".env."):
        return True
    return False


def iter_dirs(root: Path, max_depth: int, deadline: float | None):
    if not root.exists():
        return
    if root.is_file():
        yield root.parent
        return
    for current, dirs, _files in os.walk(root):
        if deadline is not None and time.monotonic() > deadline:
            return
        current_path = Path(current)
        current_depth = depth_from(root, current_path)
        dirs[:] = [
            item
            for item in dirs
            if item not in SKIP_DIRS and current_depth < max_depth
        ]
        yield current_path


def find_candidate_roots(
    search_roots: list[Path],
    max_depth: int,
    max_candidates: int,
    deadline: float | None,
) -> tuple[list[Path], bool]:
    candidates: dict[str, Path] = {}
    truncated = False
    for raw_root in search_roots:
        if len(candidates) >= max_candidates:
            truncated = True
            break
        if deadline is not None and time.monotonic() > deadline:
            truncated = True
            break
        root = safe_resolve(raw_root)
        if not root.exists():
            continue
        for current in iter_dirs(root, max_depth, deadline):
            if len(candidates) >= max_candidates:
                truncated = True
                break
            if deadline is not None and time.monotonic() > deadline:
                truncated = True
                break
            lower_path = str(current).lower()
            if (current / ".git").exists() and "hermes" in lower_path:
                candidates[str(current)] = current
                continue
            lower = current.name.lower()
            if "hermes" in lower and any(
                (current / name).exists()
                for name in ("pyproject.toml", "package.json", "docs", "src", "app")
            ):
                candidates[str(current)] = current
    return sorted(candidates.values(), key=lambda item: str(item)), truncated


def read_small_text(path: Path, max_bytes: int) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES or is_sensitive_file(path):
        return ""
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return ""
    try:
        return data.decode("utf-8", errors="ignore").lower()
    except OSError:
        return ""


def inspect_candidate(
    path: Path,
    max_files: int,
    max_file_bytes: int,
    deadline: float | None = None,
) -> dict:
    indicators: set[str] = set()
    tts_files: list[str] = []
    score = 0
    files_seen = 0
    content_term_seen = False
    tts_name_hits = 0

    path_name = path.name.lower()
    if "hermes" in path_name:
        score += 2
        indicators.add("path_name:hermes")
    if "agent" in path_name:
        score += 2
        indicators.add("path_name:agent")

    is_bridge_repo = (
        (path / "scripts" / "hermes-omnivoice-tts.py").is_file()
        and (path / "docs" / "omnivoice-integration-notes.md").is_file()
    )
    if is_bridge_repo:
        indicators.add("bridge_repo:omnivoice")
        score -= 3

    for current, dirs, files in os.walk(path):
        if deadline is not None and time.monotonic() > deadline:
            indicators.add("scan:truncated")
            break
        dirs[:] = [item for item in dirs if item not in SKIP_DIRS]
        for filename in files:
            if deadline is not None and time.monotonic() > deadline:
                indicators.add("scan:truncated")
                break
            if files_seen >= max_files:
                break
            file_path = Path(current) / filename
            if is_sensitive_file(file_path):
                continue
            files_seen += 1
            relative = str(file_path.relative_to(path))
            lower_relative = relative.lower()
            if any(term in lower_relative for term in TTS_NAME_TERMS):
                if tts_name_hits < 5:
                    score += 2
                tts_name_hits += 1
                indicators.add("tts_file_name")
                if len(tts_files) < 10:
                    tts_files.append(relative)
            if filename in {"pyproject.toml", "package.json", "Cargo.toml"}:
                score += 1
                indicators.add(f"manifest:{filename}")
            content = read_small_text(file_path, max_file_bytes)
            if content and not content_term_seen and any(term in content for term in CONTENT_TERMS):
                score += 1
                indicators.add("content:tts_terms")
                content_term_seen = True
        if files_seen >= max_files:
            break

    has_hermes_path = "hermes" in str(path).lower()
    likely = score >= 5 and has_hermes_path and not is_bridge_repo
    return {
        "path": str(path),
        "score": score,
        "likely_hermes_agent": likely,
        "is_bridge_repo": is_bridge_repo,
        "indicators": sorted(indicators),
        "tts_files": sorted(tts_files),
        "files_seen": files_seen,
    }


def discover(args: argparse.Namespace) -> dict:
    roots = args.root or DEFAULT_ROOTS
    max_depth = validate_max_depth(args.max_depth)
    max_candidates = validate_positive_bound(args.max_candidates, "max candidates")
    max_files = validate_positive_bound(args.max_files, "max files")
    max_file_bytes = validate_positive_bound(args.max_file_bytes, "max file bytes")
    scan_timeout = validate_scan_timeout(args.scan_timeout)
    deadline = time.monotonic() + scan_timeout
    candidate_roots, truncated = find_candidate_roots(
        roots,
        max_depth,
        max_candidates,
        deadline,
    )
    candidates = []
    for path in candidate_roots:
        active_deadline = deadline
        if deadline is not None and time.monotonic() > deadline:
            truncated = True
            if candidates:
                break
            active_deadline = time.monotonic() + EXPIRED_CANDIDATE_INSPECTION_GRACE_SECONDS
        candidate = inspect_candidate(path, max_files, max_file_bytes, active_deadline)
        if "scan:truncated" in candidate["indicators"]:
            truncated = True
        candidates.append(candidate)
    candidates.sort(key=lambda item: (-int(item["score"]), item["path"]))
    likely_count = sum(1 for item in candidates if item["likely_hermes_agent"])
    return {
        "status": "found" if likely_count else "no_likely_hermes_agent",
        "candidate_count": len(candidates),
        "likely_count": likely_count,
        "truncated": truncated,
        "search_roots": [str(safe_resolve(root)) for root in roots],
        "candidates": candidates,
    }


def print_human(report: dict) -> None:
    print(f"Hermes source discovery: {report['status']}")
    print(f"- Candidates: {report['candidate_count']}")
    print(f"- Likely Hermes Agent checkouts: {report['likely_count']}")
    if report["truncated"]:
        print("- Search truncated: true")
    for candidate in report["candidates"]:
        print(f"- {candidate['path']}")
        print(f"  Score: {candidate['score']}")
        print(f"  Likely Hermes Agent: {candidate['likely_hermes_agent']}")
        print(f"  Bridge repo: {candidate['is_bridge_repo']}")
        if candidate["indicators"]:
            print(f"  Indicators: {', '.join(candidate['indicators'])}")
        if candidate["tts_files"]:
            print(f"  TTS files: {', '.join(candidate['tts_files'][:5])}")


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find candidate Hermes Agent source trees")
    parser.add_argument("--root", action="append", type=Path)
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--max-candidates", type=int, default=50)
    parser.add_argument("--max-files", type=int, default=2500)
    parser.add_argument("--max-file-bytes", type=int, default=65536)
    parser.add_argument("--scan-timeout", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = discover(args)
    except SourceDiscoveryError as exc:
        print(f"find-hermes-source: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(run())
