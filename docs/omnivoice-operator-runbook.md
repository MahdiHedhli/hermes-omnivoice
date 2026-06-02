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
`scripts/hermes-omnivoice-remote.py` and the `omnivoice-remote` command-provider
example in `docs/omnivoice-remote-mvp.md`. The same operator rules apply:
keep `xtts-v2` as the default, require bearer auth, keep the service reachable
only through Tailscale, run smoke tests first, and roll back explicitly on
failure.
