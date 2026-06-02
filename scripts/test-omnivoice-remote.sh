#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VOICE="${OMNIVOICE_REMOTE_TEST_VOICE:-homelab_narrator}"
SPEED="${OMNIVOICE_REMOTE_TEST_SPEED:-1.0}"
FORMAT="${OMNIVOICE_REMOTE_TEST_FORMAT:-wav}"
TIMEOUT="${OMNIVOICE_REMOTE_TEST_TIMEOUT:-600}"
OUT_DIR="${OMNIVOICE_REMOTE_TEST_OUT_DIR:-$HOME/.cache/hermes/omnivoice-remote-smoke}"
BASE_URL="${OMNIVOICE_REMOTE_BASE_URL:-}"
TOKEN="${OMNIVOICE_REMOTE_API_TOKEN:-}"

if [[ -z "$BASE_URL" || -z "$TOKEN" ]]; then
  echo "SKIP: set OMNIVOICE_REMOTE_BASE_URL and OMNIVOICE_REMOTE_API_TOKEN to run remote OmniVoice smoke" >&2
  exit 77
fi

umask 077
mkdir -p "$OUT_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
text_file="$OUT_DIR/remote-smoke-$timestamp.txt"
out_file="$OUT_DIR/remote-smoke-$timestamp.$FORMAT"

printf '%s\n' "Hermes OmniVoice remote synthesis test." >"$text_file"

"$PYTHON_BIN" - "$BASE_URL" "$TOKEN" <<'PY'
from __future__ import annotations

import json
import sys
from urllib import error, request

base_url = sys.argv[1].rstrip("/")
token = sys.argv[2]
req = request.Request(
    f"{base_url}/health",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
)
try:
    with request.urlopen(req, timeout=10) as response:
        payload = response.read(4096)
except error.HTTPError as exc:
    if exc.code == 404:
        print("WARN: /health not available; continuing to speech smoke")
        sys.exit(0)
    print(f"remote health failed: HTTP {exc.code}", file=sys.stderr)
    sys.exit(1)
except Exception as exc:
    print(f"remote health failed: {exc}", file=sys.stderr)
    sys.exit(1)

try:
    json.loads(payload.decode("utf-8"))
except Exception:
    pass
print("remote health: PASS")
PY

start_time="$("$PYTHON_BIN" -c 'import time; print(f"{time.time():.3f}")')"
"$PYTHON_BIN" "$ROOT_DIR/scripts/hermes-omnivoice-remote.py" \
  --text-file "$text_file" \
  --out "$out_file" \
  --voice "$VOICE" \
  --speed "$SPEED" \
  --format "$FORMAT" \
  --timeout "$TIMEOUT"
end_time="$("$PYTHON_BIN" -c 'import time; print(f"{time.time():.3f}")')"
latency="$("$PYTHON_BIN" - "$start_time" "$end_time" <<'PY'
import sys
print(f"{float(sys.argv[2]) - float(sys.argv[1]):.2f}s")
PY
)"

test -s "$out_file"
echo "PASS: generated $out_file"
echo "Latency: $latency"
if command -v ffprobe >/dev/null 2>&1; then
  ffprobe -v error "$out_file" >/dev/null
  echo "ffprobe: PASS"
elif command -v file >/dev/null 2>&1; then
  file "$out_file"
fi
