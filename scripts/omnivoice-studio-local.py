#!/usr/bin/env python3
"""Manage a local loopback-only OmniVoice-Studio Docker Compose runtime."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error
import urllib.request


DEFAULT_REPO_URL = "https://github.com/debpalash/OmniVoice-Studio.git"
DEFAULT_STUDIO_DIR = Path("~/.cache/hermes/OmniVoice-Studio")
SERVICE_BY_PROFILE = {"cpu": "omnivoice", "gpu": "omnivoice-gpu"}
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class StudioLocalError(RuntimeError):
    pass


def normalize_command_timeout(timeout: int | None) -> int | None:
    if timeout is None:
        return None
    if timeout < 0:
        raise StudioLocalError("command timeout must be greater than or equal to 0")
    if timeout == 0:
        return None
    return timeout


def run_command(
    argv: list[str],
    *,
    cwd: Path | None = None,
    capture: bool = False,
    timeout: int | None = None,
) -> str:
    command_timeout = normalize_command_timeout(timeout)
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            check=False,
            text=True,
            capture_output=capture,
            timeout=command_timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise StudioLocalError(
            f"{argv[0]} timed out after {timeout}s: {' '.join(argv)}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() if capture and completed.stderr else "command failed"
        raise StudioLocalError(f"{argv[0]} exited {completed.returncode}: {detail}")
    return completed.stdout if capture else ""


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise StudioLocalError(f"required command not found: {name}")
    return path


def fetch_source(
    studio_dir: Path,
    repo_url: str,
    update: bool,
    command_timeout: int | None = None,
) -> None:
    target = studio_dir.expanduser()
    if target.exists():
        if not (target / ".git").is_dir():
            raise StudioLocalError(f"Studio directory exists but is not a git repo: {target}")
        if update:
            run_command(
                ["git", "-C", str(target), "pull", "--ff-only"],
                timeout=command_timeout,
            )
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        ["git", "clone", "--depth", "1", repo_url, str(target)],
        timeout=command_timeout,
    )


def compose_file(studio_dir: Path) -> Path:
    path = studio_dir.expanduser() / "deploy" / "docker-compose.yml"
    if not path.is_file():
        raise StudioLocalError(f"Compose file not found: {path}")
    return path


def compose_config(path: Path, profile: str, command_timeout: int | None = None) -> dict:
    output = run_command(
        ["docker", "compose", "-f", str(path), "--profile", profile, "config", "--format", "json"],
        capture=True,
        timeout=command_timeout,
    )
    return json.loads(output)


def validate_loopback_ports(config: dict, profile: str, published_port: int) -> None:
    service_name = SERVICE_BY_PROFILE[profile]
    services = config.get("services")
    if not isinstance(services, dict) or service_name not in services:
        raise StudioLocalError(f"Compose service missing for profile {profile}: {service_name}")
    ports = services[service_name].get("ports", [])
    if not isinstance(ports, list):
        raise StudioLocalError(f"Compose service has invalid ports for {service_name}")
    for port in ports:
        if not isinstance(port, dict):
            continue
        if int(port.get("target", 0)) != 3900:
            continue
        host_ip = str(port.get("host_ip") or "")
        published = str(port.get("published") or "")
        if host_ip not in LOOPBACK_HOSTS:
            raise StudioLocalError(f"Studio port is not loopback-only: {host_ip or '<all>'}")
        if published != str(published_port):
            raise StudioLocalError(f"Studio published port is {published}, expected {published_port}")
        return
    raise StudioLocalError(f"Studio port 3900 is not published on loopback port {published_port}")


def service_image(config: dict, profile: str) -> str:
    services = config.get("services")
    if not isinstance(services, dict):
        return ""
    service = services.get(SERVICE_BY_PROFILE[profile], {})
    if not isinstance(service, dict):
        return ""
    image = service.get("image", "")
    return str(image) if image else ""


def local_image_exists(image: str, command_timeout: int | None = None) -> bool:
    try:
        run_command(
            ["docker", "image", "inspect", image],
            capture=True,
            timeout=command_timeout,
        )
    except StudioLocalError:
        return False
    return True


def pull_image(image: str, command_timeout: int | None = None) -> None:
    run_command(["docker", "pull", image], capture=True, timeout=command_timeout)


def validate_health_timeout(timeout: int) -> int:
    if timeout <= 0:
        raise StudioLocalError("health timeout must be greater than 0")
    return timeout


def preflight_start(args: argparse.Namespace, config: dict) -> None:
    image = service_image(config, args.profile)
    if args.no_build and args.pull == "never" and image and not local_image_exists(
        image,
        args.command_timeout,
    ):
        raise StudioLocalError(
            f"Studio image is not available locally: {image}; "
            "allow a pull or build before using --pull never --no-build"
        )
    if args.no_build and args.pull in {"always", "missing"} and image:
        image_exists = local_image_exists(image, args.command_timeout)
        if args.pull == "always" or not image_exists:
            pull_image(image, args.command_timeout)


def compose_args(args: argparse.Namespace) -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        str(compose_file(args.studio_dir)),
        "--profile",
        args.profile,
    ]


def compose_up_args(args: argparse.Namespace) -> list[str]:
    command = compose_args(args) + ["up", "-d"]
    if args.no_build:
        command.append("--no-build")
    if args.pull:
        command.extend(["--pull", args.pull])
    return command


def compose_down_args(args: argparse.Namespace, remove_volumes: bool = False) -> list[str]:
    command = compose_args(args) + ["down"]
    if remove_volumes:
        command.append("-v")
    return command


def studio_health(url: str, timeout: int) -> dict:
    timeout = validate_health_timeout(timeout)
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/health", timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")[:200]
    except (OSError, urllib.error.URLError) as exc:
        return {"status": "unreachable", "error": str(exc)}
    return {"status": "reachable", "body": body}


def command_check(args: argparse.Namespace) -> int:
    report: dict[str, object] = {
        "docker": bool(shutil.which("docker")),
        "git": bool(shutil.which("git")),
        "studio_dir": str(args.studio_dir.expanduser()),
        "profile": args.profile,
        "studio_url": args.studio_url,
    }
    try:
        path = compose_file(args.studio_dir)
        config = compose_config(path, args.profile, args.command_timeout)
        validate_loopback_ports(config, args.profile, args.port)
        report["compose"] = "loopback-ok"
    except (OSError, json.JSONDecodeError, StudioLocalError) as exc:
        report["compose"] = "not-ready"
        report["compose_error"] = str(exc)
    report["health"] = studio_health(args.studio_url, args.timeout)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else human_report(report))
    return 0


def human_report(report: dict[str, object]) -> str:
    lines = [
        "OmniVoice-Studio local runtime",
        f"- Docker available: {report['docker']}",
        f"- Git available: {report['git']}",
        f"- Studio dir: {report['studio_dir']}",
        f"- Profile: {report['profile']}",
        f"- Compose: {report['compose']}",
        f"- Studio URL: {report['studio_url']}",
    ]
    if report.get("compose_error"):
        lines.append(f"  Compose error: {report['compose_error']}")
    health = report["health"]
    if isinstance(health, dict):
        lines.append(f"- Health: {health['status']}")
        if health.get("error"):
            lines.append(f"  Error: {health['error']}")
    return "\n".join(lines)


def command_fetch(args: argparse.Namespace) -> int:
    require_binary("git")
    fetch_source(args.studio_dir, args.repo_url, args.update, args.command_timeout)
    print(f"Studio source ready: {args.studio_dir.expanduser()}")
    return 0


def command_start(args: argparse.Namespace) -> int:
    require_binary("docker")
    if args.fetch:
        require_binary("git")
        fetch_source(args.studio_dir, args.repo_url, args.update, args.command_timeout)
    path = compose_file(args.studio_dir)
    config = compose_config(path, args.profile, args.command_timeout)
    validate_loopback_ports(config, args.profile, args.port)
    preflight_start(args, config)
    try:
        run_command(compose_up_args(args), timeout=args.command_timeout)
    except StudioLocalError:
        if args.cleanup_on_fail:
            try:
                run_command(
                    compose_down_args(args, args.remove_volumes_on_fail),
                    timeout=args.command_timeout,
                )
            except StudioLocalError:
                pass
        raise
    print(f"Studio started at {args.studio_url}")
    return 0


def command_stop(args: argparse.Namespace) -> int:
    require_binary("docker")
    run_command(compose_down_args(args), timeout=args.command_timeout)
    return 0


def command_status(args: argparse.Namespace) -> int:
    require_binary("docker")
    run_command(compose_args(args) + ["ps"], timeout=args.command_timeout)
    return 0


def command_logs(args: argparse.Namespace) -> int:
    require_binary("docker")
    run_command(compose_args(args) + ["logs", "--tail", str(args.tail)], timeout=args.command_timeout)
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--studio-dir",
        default=Path(os.environ.get("OMNIVOICE_STUDIO_DIR", str(DEFAULT_STUDIO_DIR))),
        type=Path,
    )
    parser.add_argument("--profile", choices=sorted(SERVICE_BY_PROFILE), default="cpu")
    parser.add_argument("--port", type=int, default=3900)
    parser.add_argument("--studio-url", default="http://127.0.0.1:3900")
    parser.add_argument("--timeout", type=int, default=3)
    parser.add_argument(
        "--command-timeout",
        type=int,
        default=900,
        help="Seconds before Docker/Git commands are aborted; set 0 to disable",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local OmniVoice-Studio on loopback")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Check Docker, Compose, and Studio health")
    add_common(check)
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=command_check)

    fetch = subparsers.add_parser("fetch", help="Clone or update OmniVoice-Studio source")
    add_common(fetch)
    fetch.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    fetch.add_argument("--update", action="store_true")
    fetch.set_defaults(func=command_fetch)

    start = subparsers.add_parser("start", help="Start loopback-only Studio with Docker Compose")
    add_common(start)
    start.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    start.add_argument("--fetch", action="store_true", default=True)
    start.add_argument("--no-fetch", action="store_false", dest="fetch")
    start.add_argument("--update", action="store_true")
    start.add_argument(
        "--no-build",
        action="store_true",
        help="Do not build the Studio image during startup",
    )
    start.add_argument(
        "--pull",
        choices=["always", "missing", "never"],
        default="missing",
        help="Docker Compose pull policy for startup",
    )
    start.add_argument(
        "--keep-failed",
        action="store_false",
        dest="cleanup_on_fail",
        default=True,
        help="Leave failed Compose startup resources for debugging",
    )
    start.add_argument(
        "--remove-volumes-on-fail",
        action="store_true",
        help="Also remove Compose volumes when startup fails",
    )
    start.set_defaults(func=command_start)

    stop = subparsers.add_parser("stop", help="Stop local Studio")
    add_common(stop)
    stop.set_defaults(func=command_stop)

    status = subparsers.add_parser("status", help="Show local Studio containers")
    add_common(status)
    status.set_defaults(func=command_status)

    logs = subparsers.add_parser("logs", help="Show recent local Studio logs")
    add_common(logs)
    logs.add_argument("--tail", type=int, default=120)
    logs.set_defaults(func=command_logs)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.command_timeout = normalize_command_timeout(args.command_timeout)
        return args.func(args)
    except (OSError, json.JSONDecodeError, StudioLocalError) as exc:
        print(f"omnivoice-studio-local: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run())
