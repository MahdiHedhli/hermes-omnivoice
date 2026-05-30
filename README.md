# Hermes OmniVoice Studio Bridge

Local command-provider bridge for using OmniVoice or OmniVoice-Studio voices
from Hermes Agent TTS.

This repo is intentionally conservative:

- Voice samples, generated audio, model weights, caches, and local config stay
  out of git.
- Cloned voices require `consent.status: confirmed`.
- Cloned voice reference files are validated as readable WAV audio before use.
- OmniVoice-Studio is treated as loopback-only by default because it has no
  built-in authentication.
- The first integration path is a command provider, not a native Hermes patch,
  because the real Hermes Agent source is not present in this checkout.

## What Is Included

- `scripts/hermes-omnivoice-tts.py`: Hermes TTS command-provider wrapper.
- `scripts/hermes-omnivoice-python-adapter.py`: optional command adapter for
  calling the OmniVoice Python API directly.
- `scripts/setup-omnivoice-python-env.py`: dry-run/check-first helper for an
  isolated local OmniVoice Python environment outside this repo.
- `scripts/create-omnivoice-voice.py`: creates local design or clone voice
  registry profiles with explicit consent metadata.
- `scripts/import-omnivoice-studio-voice.py`: imports a Studio profile into the
  Hermes local registry after explicit consent confirmation.
- `scripts/hermes-omnivoice-voices.py`: list, inspect, preview, and print sample
  config for local voices.
- `scripts/check-omnivoice-runtime.py`: read-only diagnostics for local backend,
  Studio, CLI, and voice registry availability.
- `scripts/install-hermes-omnivoice-bridge.py`: copies bridge files into a real
  Hermes checkout or staging directory without overwriting by default.
- `scripts/omnivoice-studio-local.py`: helper for checking, fetching, starting,
  stopping, and inspecting loopback-only OmniVoice-Studio with Docker Compose.
- `scripts/omnivoice-acceptance.py`: summarizes static MVP readiness and live
  backend readiness.
- `scripts/validate-omnivoice-bridge.sh`: deterministic local validation.
- `docs/`: setup, Studio bridge notes, integration findings, and custom voice
  usage.
- `examples/`: sample Hermes config and voice registry templates.

## Quick Start

Validate the bridge locally:

```bash
scripts/validate-omnivoice-bridge.sh
python scripts/omnivoice-acceptance.py
```

Create or import a voice under:

```text
~/.hermes/voices/omnivoice/<voice_id>/voice.yaml
```

Create a designed voice profile:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --instruct "male, american accent, moderate pitch" \
  --confirm-consent
```

Point the wrapper at local OmniVoice-Studio:

```bash
export HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900
```

Check the local runtime without generating audio:

```bash
python scripts/check-omnivoice-runtime.py
python scripts/setup-omnivoice-python-env.py --check-only
```

Check or start a local loopback-only Studio container:

```bash
python scripts/omnivoice-studio-local.py check
python scripts/omnivoice-studio-local.py start
```

Install the bridge into a real Hermes checkout or staging directory:

```bash
python scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --dry-run
```

Generate a preview:

```bash
python scripts/hermes-omnivoice-voices.py set narrator
python scripts/hermes-omnivoice-voices.py current
python scripts/hermes-omnivoice-voices.py preview marvin --out /tmp/marvin-preview.wav
```

Print a Hermes command-provider config for a selected voice:

```bash
python scripts/hermes-omnivoice-voices.py config marvin
```

## Backend Options

Use exactly one of these local backend paths:

- `HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900`
- `HERMES_OMNIVOICE_COMMAND_JSON='[...]'`
- `HERMES_OMNIVOICE_COMMAND='...'`
- `HERMES_OMNIVOICE_AUTO_CLI=1` with `omnivoice-infer` on `PATH`

Prefer `HERMES_OMNIVOICE_COMMAND_JSON` for custom adapters because it avoids
shell quoting hazards. The auto CLI path is opt-in because the first
`omnivoice-infer` run may download model files.

## Current Limits

- Real model-backed synthesis has not been run in this checkout.
- Native Hermes provider wiring is deferred until the real Hermes Agent source
  and TTS schema are available.
- The fake backend in `tests/fixtures` verifies wrapper I/O only. It is not a
  TTS engine.

## More Detail

- [Setup](docs/omnivoice-setup.md)
- [MVP handoff](docs/omnivoice-mvp-handoff.md)
- [Studio bridge](docs/omnivoice-studio-bridge.md)
- [Acceptance checklist](docs/omnivoice-acceptance.md)
- [Integration notes](docs/omnivoice-integration-notes.md)
- [Hermes custom voices](docs/tts-custom-voices.md)
