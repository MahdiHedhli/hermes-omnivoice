#!/usr/bin/env python3
"""Prepare or inspect an isolated local OmniVoice Python environment."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VENV = Path("~/.cache/hermes/omnivoice-python")
DEFAULT_PACKAGE = "omnivoice"
PYTHON_CANDIDATES = ("python3.13", "python3.12", "python3.11", "python3.10", "python3")
MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 14)


class SetupError(RuntimeError):
    pass


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_executable(venv_dir: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def detect_python_version(python: str) -> tuple[int, int, int]:
    completed = subprocess.run(
        [
            python,
            "-c",
            "import json, sys; print(json.dumps(list(sys.version_info[:3])))",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip()[:300]
        raise SetupError(f"cannot inspect Python interpreter {python}: {detail}")
    try:
        version = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SetupError(f"invalid Python version probe output for {python}") from exc
    if not isinstance(version, list) or len(version) != 3:
        raise SetupError(f"unexpected Python version probe output for {python}")
    return int(version[0]), int(version[1]), int(version[2])


def is_supported_python(version: tuple[int, int, int]) -> bool:
    major_minor = version[:2]
    return major_minor >= MIN_PYTHON and major_minor < MAX_PYTHON


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def choose_install_python() -> str:
    for candidate in PYTHON_CANDIDATES:
        path = shutil.which(candidate)
        if not path:
            continue
        try:
            version = detect_python_version(path)
        except SetupError:
            continue
        if is_supported_python(version):
            return path
    return sys.executable


def adapter_command_json(venv_dir: Path, adapter_path: Path) -> list[str]:
    return [
        str(venv_python(venv_dir)),
        str(adapter_path),
        "--text-file",
        "{text_file}",
        "--out",
        "{out}",
        "--ref-audio",
        "{ref_audio}",
        "--ref-text",
        "{ref_text}",
        "--instruct",
        "{instruct}",
        "--language",
        "{language}",
        "--speed",
        "{speed}",
    ]


def check_env(venv_dir: Path) -> dict:
    python_path = venv_python(venv_dir)
    cli_path = venv_executable(venv_dir, "omnivoice-infer")
    report = {
        "venv_dir": str(venv_dir),
        "python": str(python_path),
        "python_exists": python_path.is_file(),
        "omnivoice_infer": str(cli_path),
        "omnivoice_infer_exists": cli_path.is_file(),
        "modules": {},
        "ready": False,
    }
    if not python_path.is_file():
        return report

    probe = (
        "import importlib.util, json; "
        "mods={name: importlib.util.find_spec(name) is not None "
        "for name in ['omnivoice','soundfile','torch']}; "
        "print(json.dumps(mods, sort_keys=True))"
    )
    completed = subprocess.run(
        [str(python_path), "-c", probe],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        report["module_error"] = completed.stderr.strip()[:500]
        return report
    try:
        modules = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        report["module_error"] = f"invalid module probe output: {exc}"
        return report
    report["modules"] = modules
    report["ready"] = bool(cli_path.is_file() and all(modules.values()))
    return report


def build_plan(args: argparse.Namespace) -> dict:
    venv_dir = args.venv_dir.expanduser().resolve()
    adapter_path = args.adapter_path.expanduser().resolve()
    python_path = venv_python(venv_dir)
    version = detect_python_version(args.python)
    supported = is_supported_python(version)
    if not supported and not args.allow_unsupported_python:
        raise SetupError(
            f"Python {format_version(version)} is outside the supported setup range "
            "3.10 through 3.13; pass --python pointing to a supported interpreter"
        )
    return {
        "venv_dir": str(venv_dir),
        "python": str(python_path),
        "setup_python": args.python,
        "setup_python_version": format_version(version),
        "setup_python_supported": supported,
        "package": args.package,
        "commands": [
            [args.python, "-m", "venv", str(venv_dir)],
            [str(python_path), "-m", "pip", "install", args.package],
        ],
        "command_json": adapter_command_json(venv_dir, adapter_path),
        "env": {
            "HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(
                adapter_command_json(venv_dir, adapter_path)
            ),
            "HERMES_OMNIVOICE_MODEL": args.model,
        },
    }


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SetupError(f"command failed with exit {completed.returncode}: {' '.join(command)}")


def print_human(report: dict) -> None:
    print("Hermes OmniVoice Python environment")
    print(f"- Venv: {report['venv_dir']}")
    if "status" in report:
        print(f"- Status: {report['status']}")
    if "ready" in report:
        print(f"- Ready: {report['ready']}")
    if "env" in report:
        print("- Configure wrapper:")
        print(f"  export HERMES_OMNIVOICE_COMMAND_JSON={json.dumps(report['env']['HERMES_OMNIVOICE_COMMAND_JSON'])}")
        print(f"  export HERMES_OMNIVOICE_MODEL={report['env']['HERMES_OMNIVOICE_MODEL']}")


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create or inspect an isolated OmniVoice Python environment"
    )
    parser.add_argument("--venv-dir", default=DEFAULT_VENV, type=Path)
    parser.add_argument("--python", default=choose_install_python())
    parser.add_argument("--allow-unsupported-python", action="store_true")
    parser.add_argument("--package", default=DEFAULT_PACKAGE)
    parser.add_argument("--model", default=os.environ.get("HERMES_OMNIVOICE_MODEL", "k2-fsa/OmniVoice"))
    parser.add_argument(
        "--adapter-path",
        default=PROJECT_ROOT / "scripts" / "hermes-omnivoice-python-adapter.py",
        type=Path,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        plan = build_plan(args)
        venv_dir = Path(plan["venv_dir"])
        if args.dry_run:
            report = {"status": "planned", **plan}
        elif args.check_only:
            report = {"status": "checked", **check_env(venv_dir), "env": plan["env"]}
        else:
            for command in plan["commands"]:
                run_checked(command)
            report = {"status": "installed", **check_env(venv_dir), "env": plan["env"]}
    except (OSError, SetupError) as exc:
        print(f"setup-omnivoice-python-env: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    if args.require_ready and not report.get("ready", False):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
