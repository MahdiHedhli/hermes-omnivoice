# OmniVoice Subjective QC

Use this workflow after backend acceptance passes and before an operator uses
OmniVoice for routine Hermes responses. It is a listening check, not a
replacement for consent gates or automated bridge tests.

## Generate Samples

Run the QC generator with the same voice and backend environment that Hermes
will use:

```bash
eval "$(python scripts/setup-omnivoice-python-env.py --check-only --shell)"
scripts/omnivoice-qc-sample.sh --voice narrator
```

The script writes WAV samples and a `manifest.md` under
`~/.cache/hermes/omnivoice-qc/qc-<timestamp>/` by default. That keeps generated
audio outside the repo. Do not move QC output into tracked docs, examples,
fixtures, or commits.

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

## Notes To Record

For each QC run, record locally:

- voice id,
- backend mode,
- sample directory,
- per-sample scores,
- observed latency range,
- reviewer initials or operator name,
- final recommendation.

Keep private hostnames, runtime paths, and generated audio out of public docs.
