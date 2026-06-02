#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
HERMES_ROOT="${HERMES_ROOT:-.}"
RUNTIME_HOME=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/omnivoice-status.sh [options]

Print Hermes TTS provider status without exposing command arguments.

Options:
  --hermes-root <path>     Hermes Agent source root. Defaults to HERMES_ROOT or cwd.
  --runtime-home <path>    HOME to use for Hermes config loading.
  --python-bin <path>      Python executable. Defaults to PYTHON_BIN or python3.
  --dry-run                Accepted for runbook validation; no files are changed.
  -h, --help               Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hermes-root)
      HERMES_ROOT="${2:-}"
      shift 2
      ;;
    --runtime-home)
      RUNTIME_HOME="${2:-}"
      shift 2
      ;;
    --python-bin)
      PYTHON_BIN="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "omnivoice-status: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$HERMES_ROOT" || ! -d "$HERMES_ROOT" ]]; then
  echo "omnivoice-status: Hermes root missing: $HERMES_ROOT" >&2
  exit 1
fi
if [[ ! -f "$HERMES_ROOT/hermes_cli/config.py" ]]; then
  echo "omnivoice-status: Hermes config module missing under $HERMES_ROOT" >&2
  exit 1
fi
if [[ ! -f "$HERMES_ROOT/tools/tts_tool.py" ]]; then
  echo "omnivoice-status: Hermes TTS tool missing under $HERMES_ROOT" >&2
  exit 1
fi
if [[ -n "$RUNTIME_HOME" && ! -d "$RUNTIME_HOME" ]]; then
  echo "omnivoice-status: runtime home missing: $RUNTIME_HOME" >&2
  exit 1
fi

if [[ -n "$RUNTIME_HOME" ]]; then
  export HOME="$RUNTIME_HOME"
fi

"$PYTHON_BIN" - "$HERMES_ROOT" "$DRY_RUN" <<'PY'
from __future__ import annotations

import importlib
from pathlib import Path
import sys

root = Path(sys.argv[1]).expanduser().resolve()
dry_run = sys.argv[2] == "1"
sys.path.insert(0, str(root))

try:
    hermes_config = importlib.import_module("hermes_cli.config")
    load_config = hermes_config.load_config
except Exception as exc:
    print(f"omnivoice-status: cannot import Hermes config API: {exc}", file=sys.stderr)
    sys.exit(1)

try:
    cfg = load_config()
except Exception as exc:
    print(f"omnivoice-status: cannot load Hermes config: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(cfg, dict):
    print("omnivoice-status: Hermes config did not load as a mapping", file=sys.stderr)
    sys.exit(1)

tts = cfg.get("tts")
if not isinstance(tts, dict):
    print("omnivoice-status: tts config missing or invalid", file=sys.stderr)
    sys.exit(1)

providers = tts.get("providers")
if not isinstance(providers, dict):
    providers = {}
omnivoice = providers.get("omnivoice")

print("Hermes TTS status")
if dry_run:
    print("- Mode: dry-run/status only")
config_file = Path(
    getattr(
        hermes_config,
        "CONFIG_PATH",
        getattr(hermes_config, "CONFIG_FILE", Path.home() / ".hermes" / "config.yaml"),
    )
).expanduser()
print(f"- Active provider: {tts.get('provider', '<unset>')}")
print(f"- Config file expected by runbook scripts: {config_file}")
print(f"- OmniVoice provider configured: {isinstance(omnivoice, dict)}")
if isinstance(omnivoice, dict):
    command = omnivoice.get("command")
    command_configured = isinstance(command, str) and bool(command.strip())
    command_configured = command_configured or (
        isinstance(command, list) and any(str(part).strip() for part in command)
    )
    print(f"- OmniVoice type: {omnivoice.get('type', '<unset>')}")
    print(f"- OmniVoice command: {'configured (redacted)' if command_configured else 'missing'}")
    print(f"- OmniVoice voice: {omnivoice.get('voice', '<unset>')}")
    print(f"- OmniVoice timeout: {omnivoice.get('timeout', '<unset>')}")
    print(f"- OmniVoice output_format: {omnivoice.get('output_format', '<unset>')}")
    print(f"- OmniVoice voice_compatible: {omnivoice.get('voice_compatible', '<unset>')}")
    print(f"- OmniVoice max_text_length: {omnivoice.get('max_text_length', '<unset>')}")
PY
