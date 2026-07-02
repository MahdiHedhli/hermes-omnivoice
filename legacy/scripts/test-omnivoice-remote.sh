#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VOICE="${OMNIVOICE_REMOTE_TEST_VOICE:-${OMNIVOICE_REMOTE_VOICE:-homelab_narrator}}"
SPEED="${OMNIVOICE_REMOTE_TEST_SPEED:-1.0}"
FORMAT="${OMNIVOICE_REMOTE_TEST_FORMAT:-wav}"
TIMEOUT="${OMNIVOICE_REMOTE_TEST_TIMEOUT:-600}"
MAX_SENTENCE_CHARS="${OMNIVOICE_REMOTE_TEST_MAX_SENTENCE_CHARS:-${OMNIVOICE_REMOTE_MAX_SENTENCE_CHARS:-}}"
NORMALIZE_PUNCTUATION="${OMNIVOICE_REMOTE_TEST_NORMALIZE_PUNCTUATION:-${OMNIVOICE_REMOTE_NORMALIZE_PUNCTUATION:-}}"
SENTENCE_BREAKS="${OMNIVOICE_REMOTE_TEST_SENTENCE_BREAKS:-${OMNIVOICE_REMOTE_SENTENCE_BREAKS:-}}"
OUT_DIR="${OMNIVOICE_REMOTE_TEST_OUT_DIR:-$HOME/.cache/hermes/omnivoice-remote-smoke}"
TRANSPORT="${OMNIVOICE_REMOTE_TRANSPORT:-http}"
BASE_URL="${OMNIVOICE_REMOTE_BASE_URL:-}"
SSH_HOST="${OMNIVOICE_REMOTE_SSH_HOST:-}"
SSH_PORT="${OMNIVOICE_REMOTE_SSH_PORT:-22}"
SSH_IDENTITY_FILE="${OMNIVOICE_REMOTE_SSH_IDENTITY_FILE:-}"
REMOTE_HELPER="${OMNIVOICE_REMOTE_HELPER:-}"
REMOTE_ARTIFACT_PREFIX="${OMNIVOICE_REMOTE_ARTIFACT_PREFIX:-}"
LOOPBACK_URL="${OMNIVOICE_REMOTE_LOOPBACK_URL:-http://127.0.0.1:8880}"
TOKEN_FILE="${OMNIVOICE_REMOTE_TOKEN_FILE:-}"
TOKEN="${OMNIVOICE_REMOTE_API_TOKEN:-}"

is_truthy() {
  case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

case "$TRANSPORT" in
  http)
    if [[ -z "$BASE_URL" || ( -z "$TOKEN_FILE" && -z "$TOKEN" ) ]]; then
      echo "SKIP: set OMNIVOICE_REMOTE_BASE_URL and OMNIVOICE_REMOTE_TOKEN_FILE or OMNIVOICE_REMOTE_API_TOKEN for HTTP smoke" >&2
      exit 77
    fi
    ;;
  ssh-loopback)
    if [[ -z "$SSH_HOST" ]]; then
      echo "SKIP: set OMNIVOICE_REMOTE_SSH_HOST for SSH loopback smoke" >&2
      exit 77
    fi
    if [[ -z "$REMOTE_HELPER" && -z "$TOKEN_FILE" && -z "$TOKEN" ]]; then
      echo "SKIP: set OMNIVOICE_REMOTE_HELPER, OMNIVOICE_REMOTE_TOKEN_FILE, or OMNIVOICE_REMOTE_API_TOKEN for SSH loopback smoke" >&2
      exit 77
    fi
    ;;
  *)
    echo "FAIL: OMNIVOICE_REMOTE_TRANSPORT must be http or ssh-loopback" >&2
    exit 1
    ;;
esac

umask 077
mkdir -p "$OUT_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
text_file="$OUT_DIR/remote-smoke-$timestamp.txt"
out_file="$OUT_DIR/remote-smoke-$timestamp.$FORMAT"

printf '%s\n' "Hermes OmniVoice remote synthesis test." >"$text_file"

"$PYTHON_BIN" - "$ROOT_DIR" <<'PY'
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys


root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    "hermes_omnivoice_remote",
    root / "scripts" / "hermes-omnivoice-remote.py",
)
if spec is None or spec.loader is None:
    print("remote health failed: unable to load wrapper", file=sys.stderr)
    sys.exit(1)
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)

env = dict(os.environ)
try:
    transport = remote.parse_transport(env.get("OMNIVOICE_REMOTE_TRANSPORT", "http"))
    if transport == "ssh-loopback" and env.get("OMNIVOICE_REMOTE_HELPER", ""):
        print("remote health: SKIP (remote helper workflow)")
        sys.exit(0)
    token = remote.resolve_api_token("", "", env)
    timeout = remote.parse_positive_float(env.get("OMNIVOICE_REMOTE_HEALTH_TIMEOUT", "10"), "health timeout")
    ssh_port = remote.parse_ssh_port(env.get("OMNIVOICE_REMOTE_SSH_PORT", "22"))
    ssh_identity = remote.normalize_optional_identity_file(
        env.get("OMNIVOICE_REMOTE_SSH_IDENTITY_FILE", "")
    )
    status, payload, _content_type = remote.health_check(
        transport=transport,
        http_base_url=env.get("OMNIVOICE_REMOTE_BASE_URL", ""),
        remote_loopback_url=env.get("OMNIVOICE_REMOTE_LOOPBACK_URL", "http://127.0.0.1:8880"),
        token=token,
        timeout=timeout,
        health_path="/health",
        ssh_host=env.get("OMNIVOICE_REMOTE_SSH_HOST", ""),
        ssh_port=ssh_port,
        ssh_identity_file=ssh_identity,
        allow_public_base_url=env.get("OMNIVOICE_REMOTE_ALLOW_PUBLIC") == "1",
    )
except Exception as exc:
    message = str(exc)
    if "HTTP 404" in message:
        print("WARN: /health not available; continuing to speech smoke")
        sys.exit(0)
    print(f"remote health failed: {exc}", file=sys.stderr)
    sys.exit(1)

try:
    json.loads(payload.decode("utf-8"))
except Exception:
    pass
print(f"remote health: PASS ({status})")
PY

wrapper_args=(
  --transport "$TRANSPORT"
  --text-file "$text_file"
  --out "$out_file"
  --voice "$VOICE"
  --speed "$SPEED"
  --format "$FORMAT"
  --timeout "$TIMEOUT"
)

if is_truthy "$NORMALIZE_PUNCTUATION"; then
  wrapper_args+=(--normalize-punctuation)
fi

if is_truthy "$SENTENCE_BREAKS"; then
  wrapper_args+=(--sentence-breaks)
fi

if [[ -n "$MAX_SENTENCE_CHARS" ]]; then
  wrapper_args+=(--max-sentence-chars "$MAX_SENTENCE_CHARS")
fi

case "$TRANSPORT" in
  http)
    wrapper_args+=(--base-url "$BASE_URL")
    ;;
  ssh-loopback)
    wrapper_args+=(--ssh-host "$SSH_HOST" --ssh-port "$SSH_PORT" --remote-url "$LOOPBACK_URL")
    if [[ -n "$SSH_IDENTITY_FILE" ]]; then
      wrapper_args+=(--ssh-identity-file "$SSH_IDENTITY_FILE")
    fi
    if [[ -n "$REMOTE_HELPER" ]]; then
      wrapper_args+=(--remote-helper "$REMOTE_HELPER")
    fi
    if [[ -n "$REMOTE_ARTIFACT_PREFIX" ]]; then
      wrapper_args+=(--remote-artifact-prefix "$REMOTE_ARTIFACT_PREFIX")
    fi
    ;;
esac

start_time="$("$PYTHON_BIN" -c 'import time; print(f"{time.time():.3f}")')"
"$PYTHON_BIN" "$ROOT_DIR/scripts/hermes-omnivoice-remote.py" "${wrapper_args[@]}"
end_time="$("$PYTHON_BIN" -c 'import time; print(f"{time.time():.3f}")')"
latency="$("$PYTHON_BIN" - "$start_time" "$end_time" <<'PY'
import sys
print(f"{float(sys.argv[2]) - float(sys.argv[1]):.2f}s")
PY
)"

test -s "$out_file"
echo "PASS: generated $out_file"
echo "Transport: $TRANSPORT"
echo "Latency: $latency"
if command -v ffprobe >/dev/null 2>&1; then
  ffprobe -v error "$out_file" >/dev/null
  echo "ffprobe: PASS"
elif command -v file >/dev/null 2>&1; then
  file "$out_file"
fi
