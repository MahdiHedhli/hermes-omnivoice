# OmniVoice-Studio Bridge

## Goal

Hermes should use voices created or managed in OmniVoice-Studio without coupling
Hermes to unstable internal storage.

## Preferred Integration Order

1. Export or import a Studio voice into the Hermes registry format.
2. Call a documented local Studio API bound to `127.0.0.1`.
3. Call the underlying OmniVoice CLI or Python API directly.
4. Read Studio internals only if no API/export path exists and the schema is
   reviewed in the current Studio version.

## Security Boundary

- Keep OmniVoice-Studio bound to localhost by default.
- Do not expose unauthenticated Studio services on the LAN.
- Do not commit user voice samples, generated audio, local config, secrets,
  model weights, or caches.
- Preserve consent metadata when importing or exporting voices.
- Refuse cloned voices unless `consent.status` is `confirmed`.

## Current Bridge Shape

The wrapper consumes a stable local registry and can synthesize through either:

- `HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900`
- `HERMES_OMNIVOICE_COMMAND_JSON`
- `HERMES_OMNIVOICE_COMMAND`

The command path can point to:

- an OmniVoice CLI adapter
- a Python module importing OmniVoice
- a local OmniVoice-Studio FastAPI endpoint adapter

This avoids taking a dependency on Studio's database layout before its backend
API is inspected.

## API Evidence

Current OmniVoice-Studio source exposes:

- `POST /generate` for direct Studio synthesis from text and profile or
  reference-audio form fields.
- `GET /profiles` and `GET /profiles/{profile_id}` for saved profile metadata.
- `GET /profiles/{profile_id}/audio` for profile audio.
- `GET /v1/audio/voices` and `POST /v1/audio/speech` for OpenAI-compatible
  clients.

Studio stores profile metadata in SQLite, but the HTTP API is the safer bridge
contract.

## Importer

Use:

```text
scripts/import-omnivoice-studio-voice.py --studio-url http://127.0.0.1:3900 --profile-id <id> --voice-id <voice> --confirm-consent
```

The importer writes only metadata and user-confirmed reference audio into
`~/.hermes/voices/omnivoice/<voice_id>/`. It refuses non-loopback Studio URLs
unless explicitly overridden. It also refuses to overwrite an existing non-empty
voice directory without `--force` and validates downloaded reference audio as
WAV before writing it into the registry.

## Validation

`scripts/validate-omnivoice-bridge.sh` includes a localhost mock Studio
`/generate` contract test. That verifies request shape and WAV response handling
without downloading model weights. A real model-backed Studio smoke test is
still required before claiming synthesis quality.
