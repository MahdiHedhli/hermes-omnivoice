#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VOICE="${HERMES_OMNIVOICE_QC_VOICE:-}"
VOICE_LABEL="${HERMES_OMNIVOICE_QC_VOICE_LABEL:-}"
VOICES_DIR="${HERMES_OMNIVOICE_QC_VOICES_DIR:-$HOME/.hermes/voices/omnivoice}"
OUT_DIR="${HERMES_OMNIVOICE_QC_OUT_DIR:-$HOME/.cache/hermes/omnivoice-qc/qc-$(date -u +%Y%m%dT%H%M%SZ)}"
SPEED="${HERMES_OMNIVOICE_QC_SPEED:-1.0}"
TUNING_PROFILE="${HERMES_OMNIVOICE_QC_TUNING_PROFILE:-baseline}"
NORMALIZE_PUNCTUATION="${HERMES_OMNIVOICE_QC_NORMALIZE_PUNCTUATION:-0}"
SENTENCE_BREAKS="${HERMES_OMNIVOICE_QC_SENTENCE_BREAKS:-0}"
MAX_SENTENCE_CHARS="${HERMES_OMNIVOICE_QC_MAX_SENTENCE_CHARS:-}"
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
  --voice-label <label>    Human-readable voice label for manifests.
  --voices-dir <path>      Voice registry root. Defaults to ~/.hermes/voices/omnivoice.
  --out-dir <path>         Output directory. Defaults to ~/.cache/hermes/omnivoice-qc/qc-<timestamp>.
  --speed <value>          Voice speed. Defaults to 1.0.
  --tuning-profile <name>  Tuning profile label for filenames/results. Defaults to baseline.
  --normalize-punctuation  Mark this QC run as using punctuation normalization.
  --sentence-breaks        Mark this QC run as using sentence-break pacing hints.
  --max-sentence-chars <n> Mark max sentence chunk length used by the tuning profile.
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
    --voice-label)
      VOICE_LABEL="${2:-}"
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
    --tuning-profile)
      TUNING_PROFILE="${2:-}"
      shift 2
      ;;
    --normalize-punctuation)
      NORMALIZE_PUNCTUATION=1
      shift
      ;;
    --sentence-breaks)
      SENTENCE_BREAKS=1
      shift
      ;;
    --max-sentence-chars)
      MAX_SENTENCE_CHARS="${2:-}"
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
if [[ -z "$VOICE_LABEL" ]]; then
  VOICE_LABEL="$VOICE"
fi

snake_case() {
  "$PYTHON_BIN" - "$1" <<'PY'
import re
import sys

value = sys.argv[1].strip().lower()
value = re.sub(r"[^a-z0-9]+", "_", value)
value = re.sub(r"_+", "_", value).strip("_")
print(value or "unknown")
PY
}

VOICE_SAFE="$(snake_case "$VOICE")"
TUNING_PROFILE_SAFE="$(snake_case "$TUNING_PROFILE")"

sample_slugs=(
  short_conversation
  medium_assistant
  numbers_abbreviations
  long_paragraph
  punctuation_heavy
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
  echo "Voice label: $VOICE_LABEL"
  echo "Voice filename id: $VOICE_SAFE"
  echo "Tuning profile: $TUNING_PROFILE"
  echo "Tuning profile filename id: $TUNING_PROFILE_SAFE"
  echo "Voices dir: $VOICES_DIR"
  echo "Output dir: $OUT_DIR"
else
  umask 077
  mkdir -p "$OUT_DIR"
fi

manifest="$OUT_DIR/manifest.md"
results_json="$OUT_DIR/results.json"
results_tmp="$OUT_DIR/.results.jsonl"
if [[ "$DRY_RUN" -eq 0 ]]; then
  {
    echo "# Hermes OmniVoice QC Samples"
    echo
    echo "- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- Voice: \`$VOICE\`"
    echo "- Voice label: \`$VOICE_LABEL\`"
    echo "- Tuning profile: \`$TUNING_PROFILE\`"
    echo "- Voices dir: \`$VOICES_DIR\`"
    echo "- Speed: \`$SPEED\`"
    echo "- Normalize punctuation: \`$NORMALIZE_PUNCTUATION\`"
    echo "- Sentence breaks: \`$SENTENCE_BREAKS\`"
    echo "- Max sentence chars: \`${MAX_SENTENCE_CHARS:-unset}\`"
    echo "- Timeout: \`$TIMEOUT\`"
    echo "- Results JSON: \`$results_json\`"
    echo
  } >"$manifest"
  : >"$results_tmp"
  chmod 600 "$manifest"
  chmod 600 "$results_tmp"
fi

exit_status=0
for idx in "${!sample_slugs[@]}"; do
  slug="${sample_slugs[$idx]}"
  label="${sample_labels[$idx]}"
  text="${sample_texts[$idx]}"
  sample_base="${VOICE_SAFE}__${TUNING_PROFILE_SAFE}__${slug}"
  text_file="$OUT_DIR/$sample_base.txt"
  out_file="$OUT_DIR/$sample_base.wav"
  stderr_file="$OUT_DIR/$sample_base.stderr.txt"
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
  latency_value="$("$PYTHON_BIN" - "$start_time" "$end_time" <<'PY'
import sys
print(f"{float(sys.argv[2]) - float(sys.argv[1]):.3f}")
PY
)"
  latency="${latency_value}s"
  size="missing"
  size_bytes="0"
  if [[ -f "$out_file" ]]; then
    size_bytes="$(wc -c <"$out_file" | tr -d ' ')"
    size="$size_bytes bytes"
    chmod 600 "$out_file"
  fi
  format="unknown"
  if [[ -f "$out_file" ]] && command -v file >/dev/null 2>&1; then
    format="$(file -b "$out_file" 2>/dev/null || printf 'unknown')"
  fi
  duration="unavailable"
  duration_value=""
  if [[ -f "$out_file" ]] && command -v ffprobe >/dev/null 2>&1; then
    duration_value="$(ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "$out_file" 2>/dev/null || true)"
    if [[ -n "$duration_value" ]]; then
      duration="$duration_value"
    fi
  fi
  stderr_present=0
  if [[ ! -s "$stderr_file" ]]; then
    rm -f "$stderr_file"
  else
    chmod 600 "$stderr_file"
    stderr_present=1
  fi

  "$PYTHON_BIN" - \
    "$results_tmp" \
    "$VOICE" \
    "$VOICE_LABEL" \
    "$TUNING_PROFILE" \
    "$slug" \
    "$text" \
    "$SPEED" \
    "$NORMALIZE_PUNCTUATION" \
    "$SENTENCE_BREAKS" \
    "$MAX_SENTENCE_CHARS" \
    "$out_file" \
    "$latency_value" \
    "$duration_value" \
    "$size_bytes" \
    "$result" \
    "$stderr_present" \
    "$stderr_file" <<'PY'
import json
import math
import sys

(
    results_tmp,
    voice_id,
    voice_label,
    tuning_profile,
    prompt_label,
    prompt_text,
    speed,
    normalize_punctuation,
    sentence_breaks,
    max_sentence_chars,
    output_path,
    latency,
    duration,
    file_size,
    status,
    stderr_present,
    stderr_file,
) = sys.argv[1:]


def maybe_float(value):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def maybe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def truthy(value):
    return value.strip().lower() in {"1", "true", "yes", "on"}


warnings = []
if stderr_present == "1":
    warnings.append(f"stderr captured at {stderr_file}")

record = {
    "voice_id": voice_id,
    "voice_label": voice_label or voice_id,
    "tuning_profile": tuning_profile,
    "prompt_label": prompt_label,
    "prompt_text": prompt_text,
    "speed": maybe_float(speed),
    "normalize_punctuation": truthy(normalize_punctuation),
    "sentence_breaks": truthy(sentence_breaks),
    "max_sentence_chars": maybe_int(max_sentence_chars),
    "output_path": output_path,
    "latency": maybe_float(latency),
    "duration": maybe_float(duration),
    "file_size": maybe_int(file_size),
    "success": status == "PASS",
    "status": status,
    "retry_count": 0,
    "warnings": warnings,
}

with open(results_tmp, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(record, sort_keys=True) + "\n")
PY

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
  "$PYTHON_BIN" - "$results_tmp" "$results_json" "$VOICE" "$VOICE_LABEL" "$TUNING_PROFILE" <<'PY'
import json
import sys
from pathlib import Path

results_tmp = Path(sys.argv[1])
results_json = Path(sys.argv[2])
voice_id = sys.argv[3]
voice_label = sys.argv[4] or voice_id
tuning_profile = sys.argv[5]

records = [
    json.loads(line)
    for line in results_tmp.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
payload = {
    "schema_version": 1,
    "voice_id": voice_id,
    "voice_label": voice_label,
    "tuning_profile": tuning_profile,
    "samples": records,
}
results_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
results_tmp.unlink(missing_ok=True)
PY
  chmod 600 "$results_json"
  echo "QC manifest: $manifest"
  echo "QC results: $results_json"
fi
exit "$exit_status"
