# OmniVoice Operator Runbook

This runbook covers the command-provider MVP only. Native Hermes provider work
and `/voice` UX are deferred.

## Current Architecture

```text
Hermes Agent
  -> tts.providers.omnivoice command provider
  -> scripts/hermes-omnivoice-tts.py
  -> local voice registry and consent checks
  -> OmniVoice Python adapter, local CLI, or loopback OmniVoice-Studio API
  -> WAV output returned to Hermes
  -> Hermes final media conversion when configured
```

For the proven Mac Studio remote path:

```text
Hermes Agent on hermes-01
  -> tts.providers.omnivoice-remote-ssh-loopback command provider
  -> scripts/hermes-omnivoice-remote.py --transport ssh-loopback
  -> ssh hermes-ops@100.78.163.62
  -> /Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech
  -> Mac Studio loopback service at http://127.0.0.1:8880
  -> generated WAV copied back and returned to Hermes
```

The active default should remain `xtts-v2` unless an operator intentionally
starts a bounded OmniVoice trial. Keep OmniVoice-Studio and any backend service
bound to loopback unless a separate authentication and network review has been
completed.

## Enable OmniVoice

Preflight:

```bash
scripts/omnivoice-status.sh --hermes-root /path/to/hermes-agent
scripts/omnivoice-enable.sh --hermes-root /path/to/hermes-agent --dry-run
```

Run the scripts as the Hermes runtime user. If the runtime config lives under a
specific home directory, pass it explicitly:

```bash
scripts/omnivoice-enable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home \
  --dry-run
```

After reviewing dry-run output, enable:

```bash
scripts/omnivoice-enable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home
```

The script refuses to enable OmniVoice unless `tts.providers.omnivoice` exists,
uses `type: command`, has a configured command and voice, uses
`output_format: wav`, sets `voice_compatible: true`, and has `timeout >= 600`.
It backs up `~/.hermes/config.yaml` before saving.

Manual equivalent:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "omnivoice"
save_config(cfg)
```

If the deployment runs Hermes in a long-running service that caches config, use
the deployment's normal reload or restart after saving config. Do not edit the
remote Hermes source checkout for this MVP.

## Disable Or Roll Back

Dry-run rollback:

```bash
scripts/omnivoice-disable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home \
  --provider xtts-v2 \
  --dry-run
```

Apply rollback:

```bash
scripts/omnivoice-disable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home \
  --provider xtts-v2
```

Manual equivalent:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "xtts-v2"
save_config(cfg)
```

Always run a smoke test after rollback and confirm the active provider is no
longer `omnivoice`.

## Smoke Test

Use Hermes' real TTS tool path:

```python
from tools import tts_tool

tts_tool.text_to_speech_tool(
    "Hermes OmniVoice operator smoke test.",
    output_path="/tmp/hermes-omnivoice-smoke.wav",
)
```

For wrapper-only smoke:

```bash
eval "$(python scripts/setup-omnivoice-python-env.py --check-only --shell)"
scripts/test-omnivoice-tts.sh
```

## Acceptance Commands

Run from the bridge repo before an operator trial:

```bash
python scripts/omnivoice-acceptance.py --require-real-backend
scripts/test-omnivoice-tts.sh
scripts/validate-omnivoice-bridge.sh
scripts/omnivoice-qc-sample.sh --voice <voice_id> --dry-run
```

Use `docs/omnivoice-qc.md` for the subjective listening rubric after samples
are generated.

## Expected Latency

The active-provider trial produced valid Opus output through Hermes:

| Prompt | Latency | Audio Duration | Size |
| --- | ---: | ---: | ---: |
| Short sentence | 49.43s | 2.486s | 20,343 bytes |
| Medium sentence | 78.67s | 4.707s | 38,268 bytes |
| Numbers and abbreviations | 84.56s | 4.976s | 40,361 bytes |

Expect roughly 50-85 seconds for similar prompt sizes on the tested runtime.
Use `timeout: 600` for the command provider to allow model startup and longer
operator prompts.

## Failure Behavior

No automatic fallback was observed when the OmniVoice command provider was
forced to fail. Treat failures as hard TTS failures until the operator rolls
back to `xtts-v2` or another known-good provider.

Known failure modes:

- missing backend command, Studio URL, or opt-in CLI backend,
- missing or invalid voice profile,
- cloned voice without `consent.status: confirmed`,
- missing clone `ref_audio`,
- timeout too short for model startup,
- backend command exits non-zero,
- generated output is not a valid WAV.

## Safety Rules

- Do not expose OmniVoice-Studio or backend services on the LAN by default.
- Do not create or use cloned voices without explicit confirmed consent
  metadata.
- Do not commit generated audio, reference voice samples, model weights,
  caches, `.env` files, local Hermes config, private hostnames, or private
  operator notes.
- Keep generated samples under `~/.cache/hermes/omnivoice-qc/` or another
  ignored local path outside the repo.
- Keep rollback commands available before enabling OmniVoice.

## When To Use OmniVoice

Use OmniVoice when a manual operator wants a specific consented custom voice
and accepts high synthesis latency. It is appropriate for demonstrations,
voice-quality trials, and deliberate custom-voice responses.

Keep `xtts-v2` as the default for routine low-latency use, unattended flows,
and cases where automatic fallback is required.

Native provider work is justified after the command-provider MVP remains useful
in manual operation and a clean Hermes source branch is available.

## Remote Mac Studio Variant

For a faster remote backend over Tailscale, use
`scripts/hermes-omnivoice-remote.py` with `--transport ssh-loopback` and the
`omnivoice-remote-ssh-loopback` command-provider example in
`docs/omnivoice-remote-mvp.md`.

Current proven Mac Studio route:

```bash
export OMNIVOICE_REMOTE_TRANSPORT=ssh-loopback
export OMNIVOICE_REMOTE_SSH_HOST=hermes-ops@100.78.163.62
export OMNIVOICE_REMOTE_LOOPBACK_URL=http://127.0.0.1:8880
export OMNIVOICE_REMOTE_SSH_IDENTITY_FILE=/home/claude/.ssh/hermes_ops_macstudio_ed25519
export OMNIVOICE_REMOTE_HELPER=/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech
export OMNIVOICE_REMOTE_ARTIFACT_PREFIX=/Users/hermes-ops/Services/omnivoice/
export OMNIVOICE_REMOTE_VOICE=homelab_narrator
scripts/test-omnivoice-remote.sh
```

Optional manual pacing controls:

```bash
export OMNIVOICE_REMOTE_TEST_SPEED=0.95
export OMNIVOICE_REMOTE_TEST_NORMALIZE_PUNCTUATION=1
export OMNIVOICE_REMOTE_TEST_SENTENCE_BREAKS=1
export OMNIVOICE_REMOTE_TEST_MAX_SENTENCE_CHARS=90
scripts/test-omnivoice-remote.sh
```

For Hermes command-provider config, use the same controls as explicit wrapper
arguments:

```text
--speed {speed} --normalize-punctuation --sentence-breaks --max-sentence-chars 90
```

Keep these controls opt-in for manual operator runs. Do not promote them to an
unattended default until tuned samples pass listening review and fallback
behavior is addressed.

Per-voice tuning gate: `OMNIVOICE-PER-VOICE-TUNING-QC-001`.

All future tuning, soak, and QC artifacts must include the voice id in the
filename and `results.json` record:

```text
<voice_id>__<tuning_profile>__<prompt_label>.<ext>
```

The old 2026-06-03 tuning matrix is legacy unlabeled. It can support objective
speed comparison, but it must not be used for per-voice approval. Do not create
one global tuning recommendation unless the same setting wins across every
reviewed voice.

Current tuning recommendation table:

| Voice | Recommended setting | Status | Notes |
| --- | --- | --- | --- |
| legacy_unlabeled | `--speed 0.95 --normalize-punctuation --sentence-breaks --max-sentence-chars 90` | pending | Objective matrix favors `speed 0.95`; per-voice listening must be rerun with voice-labeled artifacts before this becomes a documented manual default. |

The Mac Studio service remains loopback-only, bearer auth is required, and the
proven helper reads the token from a protected Mac Studio-local file. Do not
copy that token to Hermes for the helper workflow. Direct HTTP mode remains
supported but is not the proven path while direct Tailscale HTTP to
`100.78.163.62:8880` times out. The same operator rules apply: keep `xtts-v2`
as the default, run smoke tests first, do not rely on automatic fallback, and
roll back explicitly on failure.

Historical access note from 2026-06-02: direct SSH to
`hermes-ops@100.78.163.62` failed from this workstation, while
`mhedhli@100.78.163.62` succeeded with the Mac Studio admin key.
Loopback TCP accepted connections and unauthenticated `/health` returned HTTP
401, but noninteractive `sudo -u hermes-ops` required a password and no local
protected token file was available. This was superseded by the later
Hermes-host helper workflow, which uses the restricted
`/home/claude/.ssh/hermes_ops_macstudio_ed25519` key from `hermes-01`.

Follow-up admin helper smoke from 2026-06-02: the Mac Studio now has
`/Users/mhedhli/.local/bin/omnivoice-client-smoke`, which reads its bearer
token from a protected Mac Studio-local env file. From ColPanicM2, use only
the admin SSH route to `mhedhli@100.78.163.62`; do not SSH as `hermes-ops`, do
not use `sudo`, and do not read or copy the helper env file. The helper passed
health, voice-list, and speech smoke with `homelab_narrator`; the generated
WAV was 153,644 bytes, 3.200 seconds audio, with 2.166 seconds reported
latency. That validated the Mac Studio service and helper path before the live
Hermes command-provider trial below.

Live Hermes SSH-loopback helper trial from 2026-06-02: Hermes was backed up,
temporarily switched from `xtts-v2` to
`omnivoice-remote-ssh-loopback`, ran three
`tools.tts_tool.text_to_speech_tool` prompts, and was rolled back to
`xtts-v2`. The final active provider was confirmed as `xtts-v2`.

| Case | Result | Latency | Duration | Size |
| --- | --- | ---: | ---: | ---: |
| Short | PASS | 2.056s | 2.956500s | 24,046 bytes |
| Medium | PASS | 2.254s | 4.196500s | 34,082 bytes |
| Edge | PASS | 2.579s | 5.386500s | 43,769 bytes |
| Rollback `xtts-v2` | PASS | 54.308s | 4.871167s | 39,556 bytes |

An initial activation attempt failed before synthesis because the provider
command used `python` and Hermes' command-provider PATH did not include that
binary. The provider command was corrected to `python3`; rollback succeeded
before the successful second attempt. Use `python3` in the provider command.

Remote OmniVoice SSH-loopback helper mode has passed reliability soak for
bounded manual operator evaluation. Human listening QC on 2026-06-03 approved
SSH-loopback OmniVoice for bounded manual operator use. Keep `xtts-v2` as the
default for routine unattended use until pacing consistency and fallback
behavior are addressed.

Reliability soak from 2026-06-02:

| Path | Prompts | Result | Latency min / median / max | Duration range |
| --- | ---: | --- | ---: | ---: |
| Direct SSH-helper wrapper | 20 | 20 PASS, 0 fail, 0 retry | 1.714s / 2.122s / 2.597s | 2.160s-6.760s |
| Live Hermes provider | 5 | 5 PASS, 0 fail, 0 retry | 1.949s / 2.059s / 2.346s | 1.7565s-4.0665s |

Rollback after the live provider soak passed with final provider `xtts-v2`.
The rollback smoke took 53.172s. Samples are available for local operator
review under
`/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-soak-20260602T224637Z/`
and
`/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-soak-20260602T224827Z/`.

Human QC summary from 2026-06-03:

| Category | Result |
| --- | --- |
| Samples reviewed | `live_01`-`live_05`, `rollback_xtts_v2`, `soak_01`, `soak_04`, `soak_09`, `soak_13`, `soak_18`, `soak_20` |
| Intelligibility | 4/5 |
| Pacing | 4/5; one voice was great, one was too fast |
| Pronunciation | 4/5; "Hermes" sounded like "herms" |
| Voice consistency | Not scored; different voices had different pace issues |
| Artifacts/noise | N/A; no recurring artifact/noise issue reported |
| Naturalness | 4/5 |
| Operator acceptability | 4/5 |
| Preference vs rollback `xtts-v2` | OmniVoice preferred; rollback sample described as terrible quality, robotic, and much less clear |
| Approval | Manual operator use approved; unattended default not approved |

Pacing tuning matrix from 2026-06-03:

| Variant | Result | Median Latency | Median Duration | Median WPM |
| --- | --- | ---: | ---: | ---: |
| Baseline | 5 PASS / 0 fail | 2.128s | 5.750s | 156.5 |
| Speed 0.95 | 5 PASS / 0 fail | 1.864s | 6.000s | 148.1 |
| Speed 1.0 explicit | 5 PASS / 0 fail | 1.793s | 5.930s | 151.8 |
| Speed 1.05 | 5 PASS / 0 fail | 1.705s | 5.510s | 158.8 |
| Sentence breaks + max 90 chars | 5 PASS / 0 fail | 1.853s | 5.780s | 155.7 |
| Punctuation normalized | 5 PASS / 0 fail | 1.722s | 5.770s | 156.0 |

Recommended manual setting after the objective matrix: `speed: 0.95` plus
`--normalize-punctuation --sentence-breaks --max-sentence-chars 90` for longer
operator responses. Subjective listening for the tuned variants remains
pending, and the existing matrix is legacy unlabeled. This recommendation is
not a documented per-voice default and is not an unattended-default approval.
