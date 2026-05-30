#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ -z "${HERMES_OMNIVOICE_COMMAND_JSON:-}${HERMES_OMNIVOICE_COMMAND:-}" ]]; then
  echo "SKIP: set HERMES_OMNIVOICE_COMMAND_JSON or HERMES_OMNIVOICE_COMMAND to run the OmniVoice smoke test" >&2
  exit 77
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

VOICE_DIR="$TMP_DIR/voices/smoke"
mkdir -p "$VOICE_DIR"
cat >"$VOICE_DIR/ref.wav" <<'WAV'
placeholder
WAV
cat >"$VOICE_DIR/voice.yaml" <<'YAML'
id: smoke
name: Smoke Test Voice
engine: omnivoice
mode: clone
ref_audio: ref.wav
ref_text: "Reference transcript for the smoke test voice."
language: en
speed: 1.0
consent:
  status: confirmed
  source: user_uploaded
  allowed_uses:
    - personal_assistant
    - local_generation
YAML

printf '%s\n' "Hermes custom voice synthesis test." >"$TMP_DIR/input.txt"

"$PYTHON_BIN" "$ROOT_DIR/scripts/hermes-omnivoice-tts.py" \
  --voices-dir "$TMP_DIR/voices" \
  --text-file "$TMP_DIR/input.txt" \
  --out "$TMP_DIR/hermes-output.wav" \
  --voice smoke \
  --speed 1.0

test -s "$TMP_DIR/hermes-output.wav"
echo "PASS: generated $TMP_DIR/hermes-output.wav"
