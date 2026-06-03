# OmniVoice Subjective QC

Use this workflow after backend acceptance passes and before an operator uses
OmniVoice for routine Hermes responses. It is a listening check, not a
replacement for consent gates or automated bridge tests.

Current tuned QC lane: `OMNIVOICE-PER-VOICE-TUNING-QC-001`.

## Generate Samples

Run the QC generator with the same voice and backend environment that Hermes
will use:

```bash
eval "$(python scripts/setup-omnivoice-python-env.py --check-only --shell)"
scripts/omnivoice-qc-sample.sh --voice narrator
```

The script writes WAV samples, a `manifest.md`, and a `results.json` under
`~/.cache/hermes/omnivoice-qc/qc-<timestamp>/` by default. That keeps generated
audio outside the repo. Do not move QC output into tracked docs, examples,
fixtures, or commits.

New QC samples use voice-labeled filenames:

```text
<voice_id>__<tuning_profile>__<prompt_label>.<ext>
```

Examples:

```text
homelab_narrator__speed_095_sentence_breaks__short_conversation.wav
homelab_narrator__baseline__long_paragraph.wav
calm_operator__speed_095__numbers_abbreviations.wav
fast_assistant__baseline__file_path_sentence.wav
```

Unsafe filename characters in `voice_id` and `tuning_profile` are normalized to
lowercase snake case. Every future tuning, soak, or QC result file must record
`voice_id`. Do not rename old artifacts unless copying them safely into an
ignored local artifact directory. If old artifacts lack voice labels, treat
them as legacy unlabeled samples and avoid per-voice conclusions.

Recommended tuned QC command shape:

```bash
scripts/omnivoice-qc-sample.sh \
  --voice homelab_narrator \
  --voice-label "Homelab Narrator" \
  --speed 0.95 \
  --tuning-profile speed_095_sentence_breaks \
  --normalize-punctuation \
  --sentence-breaks \
  --max-sentence-chars 90
```

For a dry run:

```bash
scripts/omnivoice-qc-sample.sh --voice narrator --dry-run
```

The sample set covers:

- short conversational text,
- a medium assistant response,
- numbers and abbreviations,
- a longer paragraph,
- punctuation-heavy text.

## Scoring Rubric

Use a 1-5 score for each category.

| Score | Meaning |
| --- | --- |
| 5 | Production-ready for the tested text type. |
| 4 | Good; minor issues that do not distract from operator use. |
| 3 | Usable for limited manual use, but the issue should be tracked. |
| 2 | Poor; use only for targeted debugging. |
| 1 | Unusable or unsafe for operator responses. |

Score each sample:

| Category | What To Listen For |
| --- | --- |
| Intelligibility | Words are understandable without replaying. |
| Pacing | Speed, pauses, and clause breaks feel natural enough for an assistant. |
| Pronunciation | Numbers, abbreviations, names, and technical terms are spoken correctly. |
| Voice consistency | The selected voice stays stable across sentence length and punctuation. |
| Artifacts | No distracting clipping, dropouts, metallic sound, or repeated fragments. |
| Latency acceptability | The wait time is acceptable for the intended operator workflow. |
| Operator readiness | The sample is good enough for real manual use with rollback available. |

Group tuning scores by voice:

- scores per voice,
- pacing notes per voice,
- pronunciation notes per voice,
- artifacts/noise notes per voice,
- recommended setting per voice.

## Pass Criteria

Treat OmniVoice as operator-ready for a voice only when:

- all consent metadata is valid,
- automated acceptance and smoke tests pass,
- every category scores at least 4 on the short and medium samples,
- no category scores below 3 on any sample,
- latency fits the planned workflow,
- and rollback to the previous provider has been verified.

If pronunciation or artifacts score below 4, keep `xtts-v2` as the default and
use OmniVoice only for manual trials or debugging.

For tuning recommendations, do not create one blanket recommendation unless the
same setting wins across all reviewed voices. Document one of:

1. A global recommended setting, only if it works well across all reviewed
   voices.
2. Per-voice recommended settings, if voices behave differently.
3. A voice exclusion list, if a voice is too fast, unclear, unstable, or
   otherwise not operator-ready.

## Current QC Status

Human listening QC was completed on 2026-06-03 for the 2026-06-02
SSH-loopback soak artifacts. The reviewer listened to:

- `remote-live-soak-20260602T224827Z/live_01.ogg`
- `remote-live-soak-20260602T224827Z/live_02.ogg`
- `remote-live-soak-20260602T224827Z/live_03.ogg`
- `remote-live-soak-20260602T224827Z/live_04.ogg`
- `remote-live-soak-20260602T224827Z/live_05.ogg`
- `remote-live-soak-20260602T224827Z/rollback_xtts_v2.ogg`
- `remote-soak-20260602T224637Z/soak_01.wav`
- `remote-soak-20260602T224637Z/soak_04.wav`
- `remote-soak-20260602T224637Z/soak_09.wav`
- `remote-soak-20260602T224637Z/soak_13.wav`
- `remote-soak-20260602T224637Z/soak_18.wav`
- `remote-soak-20260602T224637Z/soak_20.wav`

Artifact roots:

- `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-20260602T220621Z/`
- `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-soak-20260602T224637Z/`
- `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-soak-20260602T224827Z/`

Recorded OmniVoice scores:

| Category | Score | Notes |
| --- | ---: | --- |
| Intelligibility | 4/5 | Understandable for operator use. |
| Pacing | 4/5 | One voice was great; one was too fast. |
| Pronunciation | 4/5 | Recurring issue: "Hermes" sounded like "herms". |
| Voice consistency | Not scored | Different voices had different pace issues. |
| Artifacts/noise | N/A | No recurring artifact or noise issue was reported. |
| Naturalness | 4/5 | Good enough for manual operator use. |
| Operator acceptability | 4/5 | Approved for bounded manual operator use. |

Compared with `rollback_xtts_v2.ogg`, the reviewer preferred OmniVoice.
The rollback `xtts-v2` sample was described as terrible quality, robotic, and
much less clear, while OmniVoice was closer to natural speed.

Approval:

- Manual operator use: approved.
- Unattended default: not approved until pacing and consistency issues are
  resolved and fallback behavior is addressed.
- Next lane: voice tuning and pace normalization before considering unattended
  default use.

## Pacing Tuning Matrix

The 2026-06-03 tuning run used the Mac Studio operator SSH helper against the
loopback-only OmniVoice service. It generated 30 WAV samples across 5 prompts
and 6 variants. All generated audio stayed outside the repo under:

`/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-tuning-20260603T145445Z/`

This artifact set predates the per-voice naming requirement. Its filenames and
`results.json` records do not include `voice_id` or `voice_label`, so it is
legacy unlabeled evidence. Use it for objective pacing comparison only; do not
draw per-voice conclusions from it.

Subjective listening for these tuning variants is pending. Objective results:

| Variant | Result | Median Latency | Median Duration | Median WPM |
| --- | --- | ---: | ---: | ---: |
| Baseline | 5 PASS / 0 fail | 2.128s | 5.750s | 156.5 |
| Speed 0.95 | 5 PASS / 0 fail | 1.864s | 6.000s | 148.1 |
| Speed 1.0 explicit | 5 PASS / 0 fail | 1.793s | 5.930s | 151.8 |
| Speed 1.05 | 5 PASS / 0 fail | 1.705s | 5.510s | 158.8 |
| Sentence breaks + max 90 chars | 5 PASS / 0 fail | 1.853s | 5.780s | 155.7 |
| Punctuation normalized | 5 PASS / 0 fail | 1.722s | 5.770s | 156.0 |

Objective conclusion: `speed 0.95` is the only tested control that clearly
slowed delivery. Sentence breaks and max sentence length are still useful as
pause hints for listening review, but they did not materially reduce median
words per minute by themselves.

Provisional manual operator setting:

```text
speed: 0.95
--sentence-breaks
--max-sentence-chars 90
--normalize-punctuation
```

Keep this setting manual and listening-gated. Unattended default use remains
blocked until a human reviewer confirms the tuned variants and Hermes fallback
behavior is addressed.

## OMNIVOICE-PER-VOICE-TUNING-QC-001

Status: pending.

Required listening targets from the legacy matrix:

- `speed_095__short_confirmation.wav`
- `speed_095__longer_paragraph.wav`
- `shorter_chunking__file_path.wav`
- `baseline__short_confirmation.wav`
- `baseline__longer_paragraph.wav`
- `speed_105__short_confirmation.wav`
- `speed_105__longer_paragraph.wav`
- `punctuation_normalized__numbers_abbreviations.wav`
- `shorter_chunking__longer_paragraph.wav`

These samples are acceptable for an initial listening comparison, but they are
not acceptable for per-voice approval because the artifact names and
`results.json` lack voice labels.

Current recommendation table:

| Voice | Recommended setting | Status | Notes |
| --- | --- | --- | --- |
| legacy_unlabeled | `--speed 0.95 --normalize-punctuation --sentence-breaks --max-sentence-chars 90` | pending | Objective matrix favors `speed 0.95`, but old artifacts lack `voice_id`; do not promote as a per-voice default until voice-labeled listening passes. |

Selected tuned manual setting: pending. The candidate remains:

```text
--speed 0.95 --normalize-punctuation --sentence-breaks --max-sentence-chars 90
```

Pacing consistency is not yet approved by this lane because the available
matrix is legacy unlabeled and human listening scores for tuned variants have
not been recorded. Existing manual OmniVoice use remains approved from the
prior soak QC; unattended default remains blocked by per-voice pacing evidence
and missing automatic fallback behavior.

## OMNIVOICE-VOICE-LABELED-TUNING-MATRIX-001

Status: objective matrix complete, human listening pending.

Artifact directory:

```text
~/.cache/hermes/omnivoice-qc/qc-20260603T181620Z/
```

The lane generated voice-labeled WAV files and local `results.json` /
`summary.json` files. These files are local artifacts and must not be
committed.

Preflight summary:

- Branch: `feature/omnivoice-remote-fastapi-mvp`.
- Required commit present: `15b3d77 feat: add per-voice OmniVoice QC artifacts`.
- `scripts/omnivoice-qc-sample.sh` supports voice-labeled output and
  `results.json`.
- `scripts/hermes-omnivoice-remote.py` exists.
- Default `hermes-ops@100.78.163.62` SSH from this workstation was denied;
  the Mac Studio operator helper route `mhedhli@100.78.163.62` was reachable.
- Helper health returned `ok: true`, MPS device, loaded OmniVoice model, and
  one available voice.
- No token files were read, copied, printed, or committed.
- Hermes active provider was not changed in this lane. Prior homelab docs and
  previous live trials record final provider `xtts-v2`; a fresh tailnet SSH
  provider read from this workstation was blocked by SSH public-key denial.

Voices identified:

| Voice | Label | Source | Mode | Consent | Testing Status |
| --- | --- | --- | --- | --- | --- |
| `homelab_narrator` | Homelab Narrator | Mac Studio helper voice list | design | confirmed | tested |
| `heartbeat_narrator` | Heartbeat Narrator | `~/.hermes/voices/omnivoice/heartbeat_narrator/voice.yaml` | design | confirmed | pending; not exposed by the remote helper |
| `narrator` | Narrator | `examples/voices/narrator/voice.yaml` | design | confirmed | example only; not a deployed remote voice |
| `marvin` | Marvin | `examples/voices/marvin/voice.yaml` | clone | confirmed metadata, missing repo reference audio | not tested; example clone material is intentionally absent |
| `legacy_unlabeled` | Unknown mixed samples | 2026-06-02/2026-06-03 legacy artifacts | unknown | unknown | do not use for per-voice conclusions |

Objective results for `homelab_narrator`:

| Voice | Tuning Profile | Samples | Success | Fail | Retry | Latency min/med/max | Duration min/med/max | Median WPM | Warnings |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `homelab_narrator` | `baseline` | 5 | 5 | 0 | 0 | 0.957/1.538/1.974s | 2.880/6.180/9.410s | 165.0 | none |
| `homelab_narrator` | `speed_095` | 5 | 5 | 0 | 0 | 0.968/1.493/2.037s | 3.380/6.520/9.150s | 153.8 | none |
| `homelab_narrator` | `speed_095_normalized` | 5 | 5 | 0 | 0 | 0.984/1.496/1.888s | 3.540/5.980/9.290s | 152.5 | none |
| `homelab_narrator` | `speed_095_sentence_breaks` | 5 | 5 | 0 | 0 | 0.962/1.501/2.041s | 2.810/6.270/9.720s | 149.5 | none |
| `homelab_narrator` | `speed_100_sentence_breaks` | 5 | 5 | 0 | 0 | 0.923/1.506/1.970s | 2.720/6.090/9.550s | 160.1 | none |
| `homelab_narrator` | `speed_105` | 5 | 5 | 0 | 0 | 0.943/1.434/1.980s | 2.470/5.700/9.510s | 176.8 | none |

Per-voice recommendation table:

| Voice | Best Setting | Manual Status | Notes |
| --- | --- | --- | --- |
| `homelab_narrator` | pending listening; objective candidate `speed_095_sentence_breaks` | approved from prior QC, tuning pending | Voice-labeled matrix generated. `speed_095_sentence_breaks` had the lowest median WPM with no failures or retries. Human listening must score pacing, intelligibility, pronunciation, naturalness, and operator acceptability before promotion. |
| `heartbeat_narrator` | pending | pending | Local registry voice only in this lane; not available from the Mac Studio helper. |
| `narrator` | pending | example only | Example designed voice; not a deployed remote voice. |
| `marvin` | not approved for this lane | example clone only | Clone metadata is consent-confirmed, but reference audio is intentionally absent from the repo and was not tested. |
| `legacy_unlabeled` | none | do not use | Existing mixed sample set lacks voice labels. |

Subjective listening status: pending. Do not assign scores from objective
metrics. The operator should listen to the generated
`homelab_narrator__<profile>__<prompt>.wav` files and score each tuning
profile for intelligibility, pacing, pronunciation, naturalness, and operator
acceptability.

Global recommendation status: not approved. Only one real remote voice was
tested, and no human tuned-listening scores have been recorded. A global
setting requires at least two reviewed voices, the same winning profile across
those voices, and no voice degraded by that setting.

Default provider status: unchanged. Keep Hermes on `xtts-v2`; unattended
OmniVoice default remains blocked until per-voice tuned listening passes and
fallback behavior is designed and tested.

## Notes To Record

For each QC run, record locally:

- voice id,
- voice label when available,
- tuning profile,
- backend mode,
- sample directory,
- per-sample scores,
- per-voice recommendation,
- observed latency range,
- reviewer initials or operator name,
- final recommendation.

Keep private hostnames, runtime paths, and generated audio out of public docs.
