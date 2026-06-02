#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
HERMES_ROOT="${HERMES_ROOT:-.}"
RUNTIME_HOME=""
BACKUP_DIR=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/omnivoice-enable.sh [options]

Switch Hermes tts.provider to omnivoice after validating the staged provider.
Backs up ~/.hermes/config.yaml before any real write.

Options:
  --hermes-root <path>     Hermes Agent source root. Defaults to HERMES_ROOT or cwd.
  --runtime-home <path>    HOME to use for Hermes config loading.
  --backup-dir <path>      Directory for config backups. Defaults beside config.
  --python-bin <path>      Python executable. Defaults to PYTHON_BIN or python3.
  --dry-run                Validate and print the planned change without saving.
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
    --backup-dir)
      BACKUP_DIR="${2:-}"
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
      echo "omnivoice-enable: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$HERMES_ROOT" || ! -d "$HERMES_ROOT" ]]; then
  echo "omnivoice-enable: Hermes root missing: $HERMES_ROOT" >&2
  exit 1
fi
if [[ ! -f "$HERMES_ROOT/hermes_cli/config.py" ]]; then
  echo "omnivoice-enable: Hermes config module missing under $HERMES_ROOT" >&2
  exit 1
fi
if [[ ! -f "$HERMES_ROOT/tools/tts_tool.py" ]]; then
  echo "omnivoice-enable: Hermes TTS tool missing under $HERMES_ROOT" >&2
  exit 1
fi
if [[ -n "$RUNTIME_HOME" && ! -d "$RUNTIME_HOME" ]]; then
  echo "omnivoice-enable: runtime home missing: $RUNTIME_HOME" >&2
  exit 1
fi
if [[ -n "$BACKUP_DIR" && ! -d "$BACKUP_DIR" ]]; then
  echo "omnivoice-enable: backup dir missing: $BACKUP_DIR" >&2
  exit 1
fi

if [[ -n "$RUNTIME_HOME" ]]; then
  export HOME="$RUNTIME_HOME"
fi

"$PYTHON_BIN" - "$HERMES_ROOT" "$DRY_RUN" "$BACKUP_DIR" <<'PY'
from __future__ import annotations

from datetime import datetime, timezone
import importlib
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).expanduser().resolve()
dry_run = sys.argv[2] == "1"
backup_dir_arg = sys.argv[3]
sys.path.insert(0, str(root))

try:
    hermes_config = importlib.import_module("hermes_cli.config")
    load_config = hermes_config.load_config
    save_config = hermes_config.save_config
except Exception as exc:
    print(f"omnivoice-enable: cannot import Hermes config API: {exc}", file=sys.stderr)
    sys.exit(1)

try:
    cfg = load_config()
except Exception as exc:
    print(f"omnivoice-enable: cannot load Hermes config: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(cfg, dict):
    print("omnivoice-enable: Hermes config did not load as a mapping", file=sys.stderr)
    sys.exit(1)

tts = cfg.get("tts")
if not isinstance(tts, dict):
    print("omnivoice-enable: tts config missing or invalid", file=sys.stderr)
    sys.exit(1)
providers = tts.get("providers")
if not isinstance(providers, dict):
    print("omnivoice-enable: tts.providers missing or invalid", file=sys.stderr)
    sys.exit(1)
omnivoice = providers.get("omnivoice")
if not isinstance(omnivoice, dict):
    print("omnivoice-enable: tts.providers.omnivoice missing or invalid", file=sys.stderr)
    sys.exit(1)
if omnivoice.get("type") != "command":
    print("omnivoice-enable: tts.providers.omnivoice.type must be command", file=sys.stderr)
    sys.exit(1)
command = omnivoice.get("command")
command_configured = isinstance(command, str) and bool(command.strip())
command_configured = command_configured or (
    isinstance(command, list) and any(str(part).strip() for part in command)
)
if not command_configured:
    print("omnivoice-enable: OmniVoice command is missing", file=sys.stderr)
    sys.exit(1)
if not str(omnivoice.get("voice", "")).strip():
    print("omnivoice-enable: OmniVoice voice is missing", file=sys.stderr)
    sys.exit(1)
if omnivoice.get("output_format") != "wav":
    print("omnivoice-enable: OmniVoice output_format must be wav", file=sys.stderr)
    sys.exit(1)
if omnivoice.get("voice_compatible") is not True:
    print("omnivoice-enable: OmniVoice voice_compatible must be true", file=sys.stderr)
    sys.exit(1)
try:
    timeout = float(omnivoice.get("timeout"))
except (TypeError, ValueError):
    print("omnivoice-enable: OmniVoice timeout must be numeric", file=sys.stderr)
    sys.exit(1)
if timeout < 600:
    print("omnivoice-enable: OmniVoice timeout should be at least 600 seconds", file=sys.stderr)
    sys.exit(1)

current = tts.get("provider", "<unset>")
target = "omnivoice"
config_file = Path(
    getattr(
        hermes_config,
        "CONFIG_PATH",
        getattr(hermes_config, "CONFIG_FILE", Path.home() / ".hermes" / "config.yaml"),
    )
).expanduser()
backup_dir = Path(backup_dir_arg).expanduser() if backup_dir_arg else config_file.parent
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup_file = backup_dir / f"config.yaml.pre-omnivoice-enable-{timestamp}"

print("Hermes OmniVoice enable")
print(f"- Hermes root: {root}")
print(f"- Config file: {config_file}")
print(f"- Current provider: {current}")
print(f"- Target provider: {target}")
print("- OmniVoice command: configured (redacted)")
print(f"- Backup path: {backup_file}")
if current == target:
    print("- No change needed: provider is already omnivoice")
    sys.exit(0)
if dry_run:
    print("- Dry run: no backup or config write performed")
    sys.exit(0)
if not config_file.is_file():
    print(f"omnivoice-enable: cannot back up missing config file: {config_file}", file=sys.stderr)
    sys.exit(1)
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(config_file, backup_file)
backup_file.chmod(0o600)
tts["provider"] = target
try:
    save_config(cfg)
except Exception as exc:
    print(f"omnivoice-enable: failed to save Hermes config: {exc}", file=sys.stderr)
    sys.exit(1)
print("- Saved provider switch")
PY
