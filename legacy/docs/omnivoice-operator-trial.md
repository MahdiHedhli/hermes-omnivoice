# OmniVoice Operator Trial

## Summary

A bounded active-provider trial was run on a private Hermes deployment. The
trial temporarily changed `tts.provider` from the existing provider to
`omnivoice`, ran three Hermes TTS requests through the normal
`tools.tts_tool.text_to_speech_tool` path, then rolled back to the previous
provider.

Result: PASS. OmniVoice generated valid Opus output for all three requested
texts. Rollback also passed and the previous provider generated valid Opus
output after restoration.

## What Changed

- `tts.provider` was temporarily set to `omnivoice`.
- No Hermes source files were modified.
- No OmniVoice-Studio or backend service was exposed on the LAN.
- A host-local rollback helper was created outside the Hermes source checkout.
- Generated audio stayed in temporary host-local directories and was not added
  to the repo.

No systemd Hermes service unit was present on the tested host. The live tool
path reads TTS config when `tools.tts_tool.text_to_speech_tool` is invoked, so
saving config was sufficient for this bounded tool-path trial.

## Enable OmniVoice

Stage the provider first under `tts.providers.omnivoice`, keeping the active
provider unchanged until a smoke test passes. The OmniVoice provider should use:

- `type: command`
- `output_format: wav`
- `voice_compatible: true`
- `timeout: 600`
- `max_text_length: 2000`
- a consent-confirmed local voice profile
- a command pointing at `scripts/hermes-omnivoice-tts.py`

After preflight, enable the provider:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "omnivoice"
save_config(cfg)
```

Run a smoke test through Hermes' real tool path:

```python
from tools import tts_tool

tts_tool.text_to_speech_tool(
    "Hermes OmniVoice operator trial one.",
    output_path="/tmp/hermes-omnivoice-trial.wav",
)
```

## Disable OmniVoice

Restore the previous provider:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "xtts-v2"
save_config(cfg)
```

Keep an equivalent rollback helper available outside the Hermes source checkout
before starting an operator trial.

## Trial Results

All tests used:

```text
tools.tts_tool.text_to_speech_tool(text, output_path=...)
```

| Case | Result | Latency | Duration | Size | Format | Temporary Output |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Short | PASS | 49.43s | 2.486s | 20,343 bytes | Ogg Opus, mono, 24000 Hz | `/tmp/hermes-omnivoice-operator-trial-.../short.ogg` |
| Medium | PASS | 78.67s | 4.707s | 38,268 bytes | Ogg Opus, mono, 24000 Hz | `/tmp/hermes-omnivoice-operator-trial-.../medium.ogg` |
| Edge | PASS | 84.56s | 4.976s | 40,361 bytes | Ogg Opus, mono, 24000 Hz | `/tmp/hermes-omnivoice-operator-trial-.../edge.ogg` |

Test text:

- Short: `Hermes OmniVoice operator trial one.`
- Medium: `This is a longer custom voice test to check pacing, clarity, and timeout behavior.`
- Edge: `Testing numbers, punctuation, and abbreviations: 10 PM, API, VM, and Proxmox.`

Post-rollback smoke:

- Result: PASS
- Latency: 49.42s
- Duration: 3.068s
- Size: 25,039 bytes
- Format: Ogg Opus, mono, 24000 Hz

## Fallback Behavior

Hermes did not automatically fall back to the previous provider when an
in-process failing OmniVoice command-provider configuration was injected for a
failure probe. The observed result was a failed TTS response, not fallback
synthesis.

Treat rollback as an explicit operator action:

1. Set `tts.provider` back to the previous provider.
2. Run one TTS smoke test through Hermes.
3. Confirm the active provider and output media.

## Known Latency And Timeout Behavior

- Short text took about 49 seconds.
- Medium and edge texts took about 79-85 seconds.
- A 600 second provider timeout is recommended for real OmniVoice model startup
  and synthesis headroom.
- Output format through Hermes was Opus because the command provider is marked
  `voice_compatible: true` and Hermes converts the provider WAV to Opus for the
  final media path.

## Known Failure Modes

- Missing or invalid voice consent metadata blocks synthesis before backend
  startup.
- Missing backend command, missing local OmniVoice runtime, or invalid command
  template prevents real backend readiness.
- Command-provider failure does not provide automatic fallback to the previous
  provider.
- Very short provider timeouts can fail real model startup or longer prompts.

## Final Recommendation

OmniVoice is ready for manual operator use behind the command-provider MVP when:

- the active provider switch is done by an operator,
- a rollback helper is available,
- `timeout: 600` is used,
- generated audio remains outside git,
- and the operator accepts roughly 50-85 second synthesis latency for the tested
  prompt sizes.

Native provider work is justified only after a clean Hermes source branch is
available. The command-provider path is already sufficient for a reversible MVP
trial.
