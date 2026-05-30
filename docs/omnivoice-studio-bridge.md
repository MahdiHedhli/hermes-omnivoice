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

The wrapper consumes a stable local registry and delegates synthesis to an
explicit command configured by the operator. That command can point to:

- an OmniVoice CLI adapter
- a Python module importing OmniVoice
- a local OmniVoice-Studio FastAPI endpoint adapter

This avoids taking a dependency on Studio's database layout before its backend
API is inspected.

## Follow-Up

Inspect `debpalash/OmniVoice-Studio` backend routes and storage model, then add
a small importer such as:

```text
scripts/import-omnivoice-studio-voice.py --studio-url http://127.0.0.1:PORT --voice <id>
```

The importer should write only metadata and user-approved reference audio into
`~/.hermes/voices/omnivoice/<voice_id>/`.
