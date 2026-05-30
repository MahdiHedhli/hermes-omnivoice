#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$ROOT_DIR"

"$PYTHON_BIN" -m unittest discover -s tests -v
"$PYTHON_BIN" -m py_compile \
  scripts/hermes-omnivoice-tts.py \
  scripts/import-omnivoice-studio-voice.py \
  scripts/hermes-omnivoice-voices.py \
  tests/test_omnivoice_tts.py \
  tests/fixtures/fake_omnivoice_backend.py

HERMES_OMNIVOICE_COMMAND_JSON='["python3","tests/fixtures/fake_omnivoice_backend.py","--text-file","{text_file}","--out","{out}","--voice-dir","{voice_dir}","--speed","{speed}"]' \
  scripts/test-omnivoice-tts.sh

set +e
env -u HERMES_OMNIVOICE_COMMAND_JSON \
  -u HERMES_OMNIVOICE_COMMAND \
  -u HERMES_OMNIVOICE_STUDIO_URL \
  scripts/test-omnivoice-tts.sh
skip_status=$?
set -e
if [[ "$skip_status" -ne 77 ]]; then
  echo "expected unconfigured smoke test to skip with 77, got $skip_status" >&2
  exit 1
fi

if command -v rg >/dev/null 2>&1; then
  set +e
  rg -n \
    "(API_KEY|TOKEN|SECRET|PASSWORD|BEGIN [A-Z ]*PRIVATE|sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|glpat-[A-Za-z0-9]|hf_[A-Za-z0-9]{20,}|ELEVENLABS|OPENAI_API_KEY)" \
    . \
    --glob '!HEARTBEAT.md' \
    --glob '!scripts/validate-omnivoice-bridge.sh'
  rg_status=$?
  set -e
  if [[ "$rg_status" -eq 0 ]]; then
    echo "secret-like pattern scan found matches" >&2
    exit 1
  fi
  if [[ "$rg_status" -ne 1 ]]; then
    echo "secret-like pattern scan failed with status $rg_status" >&2
    exit "$rg_status"
  fi
fi

git diff --check
