#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
HERMES_ROOT="${HERMES_ROOT:-.}"
RUNTIME_HOME=""
BACKUP_DIR=""
TARGET_PROVIDER="${HERMES_OMNIVOICE_ROLLBACK_PROVIDER:-xtts-v2}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/omnivoice-disable.sh [options]

Switch Hermes tts.provider back to a rollback provider. Defaults to xtts-v2.
Backs up ~/.hermes/config.yaml before any real write.

Options:
  --provider <name>        Rollback provider. Defaults to xtts-v2.
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
    --provider)
      TARGET_PROVIDER="${2:-}"
      shift 2
      ;;
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
      echo "omnivoice-disable: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$TARGET_PROVIDER" ]]; then
  echo "omnivoice-disable: --provider must not be empty" >&2
  exit 2
fi
if [[ -z "$HERMES_ROOT" || ! -d "$HERMES_ROOT" ]]; then
  echo "omnivoice-disable: Hermes root missing: $HERMES_ROOT" >&2
  exit 1
fi
if [[ ! -f "$HERMES_ROOT/hermes_cli/config.py" ]]; then
  echo "omnivoice-disable: Hermes config module missing under $HERMES_ROOT" >&2
  exit 1
fi
if [[ ! -f "$HERMES_ROOT/tools/tts_tool.py" ]]; then
  echo "omnivoice-disable: Hermes TTS tool missing under $HERMES_ROOT" >&2
  exit 1
fi
if [[ -n "$RUNTIME_HOME" && ! -d "$RUNTIME_HOME" ]]; then
  echo "omnivoice-disable: runtime home missing: $RUNTIME_HOME" >&2
  exit 1
fi
if [[ -n "$BACKUP_DIR" && ! -d "$BACKUP_DIR" ]]; then
  echo "omnivoice-disable: backup dir missing: $BACKUP_DIR" >&2
  exit 1
fi

if [[ -n "$RUNTIME_HOME" ]]; then
  export HOME="$RUNTIME_HOME"
fi

"$PYTHON_BIN" - "$HERMES_ROOT" "$DRY_RUN" "$BACKUP_DIR" "$TARGET_PROVIDER" <<'PY'
from __future__ import annotations

from datetime import datetime, timezone
import importlib
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).expanduser().resolve()
dry_run = sys.argv[2] == "1"
backup_dir_arg = sys.argv[3]
target = sys.argv[4]
sys.path.insert(0, str(root))

try:
    hermes_config = importlib.import_module("hermes_cli.config")
    load_config = hermes_config.load_config
    save_config = hermes_config.save_config
except Exception as exc:
    print(f"omnivoice-disable: cannot import Hermes config API: {exc}", file=sys.stderr)
    sys.exit(1)

try:
    cfg = load_config()
except Exception as exc:
    print(f"omnivoice-disable: cannot load Hermes config: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(cfg, dict):
    print("omnivoice-disable: Hermes config did not load as a mapping", file=sys.stderr)
    sys.exit(1)

tts = cfg.get("tts")
if not isinstance(tts, dict):
    print("omnivoice-disable: tts config missing or invalid", file=sys.stderr)
    sys.exit(1)
if not str(target).strip():
    print("omnivoice-disable: target provider must not be empty", file=sys.stderr)
    sys.exit(1)

current = tts.get("provider", "<unset>")
config_file = Path(
    getattr(
        hermes_config,
        "CONFIG_PATH",
        getattr(hermes_config, "CONFIG_FILE", Path.home() / ".hermes" / "config.yaml"),
    )
).expanduser()
backup_dir = Path(backup_dir_arg).expanduser() if backup_dir_arg else config_file.parent
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup_file = backup_dir / f"config.yaml.pre-omnivoice-disable-{timestamp}"

print("Hermes OmniVoice disable")
print(f"- Hermes root: {root}")
print(f"- Config file: {config_file}")
print(f"- Current provider: {current}")
print(f"- Target provider: {target}")
print(f"- Backup path: {backup_file}")
if current == target:
    print("- No change needed: provider is already the rollback provider")
    sys.exit(0)
if dry_run:
    print("- Dry run: no backup or config write performed")
    sys.exit(0)
if not config_file.is_file():
    print(f"omnivoice-disable: cannot back up missing config file: {config_file}", file=sys.stderr)
    sys.exit(1)
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(config_file, backup_file)
backup_file.chmod(0o600)
tts["provider"] = target
try:
    save_config(cfg)
except Exception as exc:
    print(f"omnivoice-disable: failed to save Hermes config: {exc}", file=sys.stderr)
    sys.exit(1)
print("- Saved provider switch")
PY
