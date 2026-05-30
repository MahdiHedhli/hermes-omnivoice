#!/usr/bin/env python3
"""Read-only diagnostics for local Hermes OmniVoice runtime configuration."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request


LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


class RuntimeCheckError(RuntimeError):
    pass


def validate_studio_url(url: str, allow_remote: bool = False) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeCheckError("Studio URL must be an absolute http(s) URL")
    host = parsed.hostname or ""
    if host not in LOOPBACK_HOSTS and not host.endswith(".localhost") and not allow_remote:
        raise RuntimeCheckError(
            "refusing non-loopback Studio URL; use --allow-remote-studio only after adding auth"
        )
    return url.rstrip("/")


def _executable_hint(command: list[str]) -> dict:
    executable = command[0] if command else ""
    return {
        "executable": Path(executable).name if executable else "",
        "executable_found": bool(shutil.which(executable) or Path(executable).exists()),
        "argument_count": len(command),
    }


def check_backend_command(env: dict[str, str]) -> dict:
    json_template = env.get("HERMES_OMNIVOICE_COMMAND_JSON", "").strip()
    if json_template:
        try:
            command = json.loads(json_template)
        except json.JSONDecodeError as exc:
            raise RuntimeCheckError("HERMES_OMNIVOICE_COMMAND_JSON is not valid JSON") from exc
        if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
            raise RuntimeCheckError("HERMES_OMNIVOICE_COMMAND_JSON must be a JSON string array")
        return {"status": "configured", "mode": "command_json", **_executable_hint(command)}

    string_template = env.get("HERMES_OMNIVOICE_COMMAND", "").strip()
    if string_template:
        try:
            command = shlex.split(string_template)
        except ValueError as exc:
            raise RuntimeCheckError("HERMES_OMNIVOICE_COMMAND is not shell-parseable") from exc
        return {"status": "configured", "mode": "command_string", **_executable_hint(command)}

    return {"status": "missing", "mode": ""}


def check_studio(studio_url: str, timeout: int, allow_remote: bool) -> dict:
    if not studio_url:
        return {"status": "missing", "url": ""}

    base_url = validate_studio_url(studio_url, allow_remote)
    request = urllib.request.Request(
        f"{base_url}/profiles",
        headers={"Accept": "application/json", "User-Agent": "hermes-omnivoice-check/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"status": "unreachable", "url": base_url, "error": f"HTTP {exc.code}"}
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"status": "unreachable", "url": base_url, "error": str(exc)}

    if isinstance(payload, list):
        profile_count = len(payload)
    elif isinstance(payload, dict) and isinstance(payload.get("profiles"), list):
        profile_count = len(payload["profiles"])
    else:
        profile_count = None
    return {"status": "reachable", "url": base_url, "profile_count": profile_count}


def check_omnivoice_cli() -> dict:
    path = shutil.which("omnivoice")
    return {
        "status": "found" if path else "missing",
        "path": path or "",
    }


def check_voices_dir(voices_dir: Path) -> dict:
    root = voices_dir.expanduser()
    if not root.exists():
        return {"status": "missing", "path": str(root), "profile_count": 0}
    if not root.is_dir():
        return {"status": "invalid", "path": str(root), "profile_count": 0}
    profile_count = sum(
        1 for child in root.iterdir() if child.is_dir() and (child / "voice.yaml").exists()
    )
    return {"status": "present", "path": str(root), "profile_count": profile_count}


def build_report(args: argparse.Namespace, env: dict[str, str]) -> dict:
    studio_url = args.studio_url or env.get("HERMES_OMNIVOICE_STUDIO_URL", "")
    return {
        "studio": check_studio(studio_url, args.timeout, args.allow_remote_studio),
        "backend_command": check_backend_command(env),
        "omnivoice_cli": check_omnivoice_cli(),
        "voices_dir": check_voices_dir(args.voices_dir),
    }


def print_human(report: dict) -> None:
    print("Hermes OmniVoice runtime check")
    studio = report["studio"]
    print(f"- Studio API: {studio['status']}")
    if studio.get("url"):
        print(f"  URL: {studio['url']}")
    if "profile_count" in studio and studio["profile_count"] is not None:
        print(f"  Profiles: {studio['profile_count']}")
    if studio.get("error"):
        print(f"  Error: {studio['error']}")

    command = report["backend_command"]
    print(f"- Backend command: {command['status']}")
    if command["status"] == "configured":
        print(f"  Mode: {command['mode']}")
        print(f"  Executable: {command['executable']}")
        print(f"  Executable found: {command['executable_found']}")

    cli = report["omnivoice_cli"]
    print(f"- OmniVoice CLI: {cli['status']}")
    if cli.get("path"):
        print(f"  Path: {cli['path']}")

    voices = report["voices_dir"]
    print(f"- Voices dir: {voices['status']}")
    print(f"  Path: {voices['path']}")
    print(f"  Profiles: {voices['profile_count']}")


def run(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local Hermes OmniVoice runtime configuration")
    parser.add_argument("--studio-url", default="")
    parser.add_argument("--voices-dir", default=Path("~/.hermes/voices/omnivoice"), type=Path)
    parser.add_argument("--timeout", default=5, type=int)
    parser.add_argument("--allow-remote-studio", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    runtime_env = dict(os.environ if env is None else env)
    try:
        report = build_report(args, runtime_env)
    except RuntimeCheckError as exc:
        print(f"check-omnivoice-runtime: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(run())
