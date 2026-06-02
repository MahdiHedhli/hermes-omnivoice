#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VOICE="${HERMES_OMNIVOICE_QC_VOICE:-}"
VOICES_DIR="${HERMES_OMNIVOICE_QC_VOICES_DIR:-$HOME/.hermes/voices/omnivoice}"
OUT_DIR="${HERMES_OMNIVOICE_QC_OUT_DIR:-$HOME/.cache/hermes/omnivoice-qc/qc-$(date -u +%Y%m%dT%H%M%SZ)}"
SPEED="${HERMES_OMNIVOICE_QC_SPEED:-1.0}"
TIMEOUT="${HERMES_OMNIVOICE_QC_TIMEOUT:-600}"
MAX_CHARS="${HERMES_OMNIVOICE_QC_MAX_CHARS:-2000}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/omnivoice-qc-sample.sh --voice <voice_id> [options]

Generate local OmniVoice QC samples through scripts/hermes-omnivoice-tts.py.
Generated audio and manifests are written under ~/.cache/hermes/omnivoice-qc/
by default, outside the repo.

Options:
  --voice <voice_id>       Required voice profile id.
  --voices-dir <path>      Voice registry root. Defaults to ~/.hermes/voices/omnivoice.
  --out-dir <path>         Output directory. Defaults to omnivoice-output/qc-<timestamp>.
  --speed <value>          Voice speed. Defaults to 1.0.
  --timeout <seconds>      Wrapper/backend timeout. Defaults to 600.
  --max-chars <count>      Wrapper max text length. Defaults to 2000.
  --python-bin <path>      Python executable. Defaults to PYTHON_BIN or python3.
  --dry-run                Print planned commands without generating audio.
  -h, --help               Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --voice)
      VOICE="${2:-}"
      shift 2
      ;;
    --voices-dir)
      VOICES_DIR="${2:-}"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="${2:-}"
      shift 2
      ;;
    --speed)
      SPEED="${2:-}"
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:-}"
      shift 2
      ;;
    --max-chars)
      MAX_CHARS="${2:-}"
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
      echo "omnivoice-qc-sample: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$VOICE" ]]; then
  echo "omnivoice-qc-sample: --voice is required" >&2
  exit 2
fi
if [[ ! -f "$ROOT_DIR/scripts/hermes-omnivoice-tts.py" ]]; then
  echo "omnivoice-qc-sample: wrapper missing at $ROOT_DIR/scripts/hermes-omnivoice-tts.py" >&2
  exit 1
fi

sample_slugs=(
  short-conversation
  medium-assistant
  numbers-abbreviations
  long-paragraph
  punctuation-heavy
)
sample_labels=(
  "Short conversational sentence"
  "Medium assistant response"
  "Numbers and abbreviations"
  "Longer paragraph"
  "Punctuation-heavy sentence"
)
sample_texts=(
  "Hi, this is Hermes testing a custom OmniVoice voice."
  "I checked the runbook, confirmed the rollback path, and generated this sample for operator listening review."
  "Testing numbers and abbreviations: 10 PM, API, VM, CPU, 24 kilohertz, and Proxmox node 01."
  "This longer paragraph checks whether the selected voice stays consistent across multiple clauses, keeps a natural pace, and avoids obvious artifacts during a realistic assistant response."
  "Punctuation test: ready, set, go. Wait... did the provider handle commas, quotes, parentheses, and question marks correctly?"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "OmniVoice QC dry run"
  echo "Voice: $VOICE"
  echo "Voices dir: $VOICES_DIR"
  echo "Output dir: $OUT_DIR"
else
  umask 077
  mkdir -p "$OUT_DIR"
fi

manifest="$OUT_DIR/manifest.md"
if [[ "$DRY_RUN" -eq 0 ]]; then
  {
    echo "# Hermes OmniVoice QC Samples"
    echo
    echo "- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- Voice: \`$VOICE\`"
    echo "- Voices dir: \`$VOICES_DIR\`"
    echo "- Speed: \`$SPEED\`"
    echo "- Timeout: \`$TIMEOUT\`"
    echo
  } >"$manifest"
  chmod 600 "$manifest"
fi

exit_status=0
for idx in "${!sample_slugs[@]}"; do
  slug="${sample_slugs[$idx]}"
  label="${sample_labels[$idx]}"
  text="${sample_texts[$idx]}"
  text_file="$OUT_DIR/$slug.txt"
  out_file="$OUT_DIR/$slug.wav"
  stderr_file="$OUT_DIR/$slug.stderr.txt"
  cmd=(
    "$PYTHON_BIN"
    "$ROOT_DIR/scripts/hermes-omnivoice-tts.py"
    --text-file "$text_file"
    --out "$out_file"
    --voice "$VOICE"
    --voices-dir "$VOICES_DIR"
    --speed "$SPEED"
    --timeout "$TIMEOUT"
    --max-chars "$MAX_CHARS"
  )

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo
    echo "$label:"
    printf '  text: %s\n' "$text"
    printf '  command: '
    printf '%q ' "${cmd[@]}"
    printf '\n'
    continue
  fi

  printf '%s\n' "$text" >"$text_file"
  chmod 600 "$text_file"
  start_time="$("$PYTHON_BIN" -c 'import time; print(f"{time.time():.3f}")')"
  if "${cmd[@]}" 2>"$stderr_file"; then
    result="PASS"
  else
    result="FAIL"
    exit_status=1
  fi
  end_time="$("$PYTHON_BIN" -c 'import time; print(f"{time.time():.3f}")')"
  latency="$("$PYTHON_BIN" - "$start_time" "$end_time" <<'PY'
import sys
print(f"{float(sys.argv[2]) - float(sys.argv[1]):.2f}s")
PY
)"
  size="missing"
  if [[ -f "$out_file" ]]; then
    size="$(wc -c <"$out_file" | tr -d ' ') bytes"
    chmod 600 "$out_file"
  fi
  format="unknown"
  if [[ -f "$out_file" ]] && command -v file >/dev/null 2>&1; then
    format="$(file -b "$out_file" 2>/dev/null || printf 'unknown')"
  fi
  duration="unavailable"
  if [[ -f "$out_file" ]] && command -v ffprobe >/dev/null 2>&1; then
    duration="$(ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "$out_file" 2>/dev/null || printf 'unavailable')"
  fi
  if [[ ! -s "$stderr_file" ]]; then
    rm -f "$stderr_file"
  else
    chmod 600 "$stderr_file"
  fi

  {
    echo "## $label"
    echo
    echo "- Result: $result"
    echo "- Output: \`$out_file\`"
    echo "- Text file: \`$text_file\`"
    echo "- Latency: $latency"
    echo "- Size: $size"
    echo "- Duration: $duration"
    echo "- Format: $format"
    if [[ -s "$stderr_file" ]]; then
      echo "- Stderr: \`$stderr_file\`"
    fi
    echo
    echo '```text'
    echo "$text"
    echo '```'
    echo
  } >>"$manifest"

  echo "$label: $result ($latency, $size)"
done

if [[ "$DRY_RUN" -eq 0 ]]; then
  echo "QC manifest: $manifest"
fi
exit "$exit_status"
