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
- Do not place credentials in Studio URLs; bridge tools reject URL userinfo.
- Do not commit user voice samples, generated audio, local config, secrets,
  model weights, or caches.
- Preserve consent metadata when importing or exporting voices.
- Refuse cloned voices unless `consent.status` is `confirmed`.

## Current Bridge Shape

The wrapper consumes a stable local registry and can synthesize through either:

- `HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900`
- `HERMES_OMNIVOICE_COMMAND_JSON`
- `HERMES_OMNIVOICE_COMMAND`
- `HERMES_OMNIVOICE_AUTO_CLI=1` with `omnivoice-infer` on `PATH`

The command path can point to:

- an OmniVoice CLI adapter
- a Python module importing OmniVoice
- a local OmniVoice-Studio FastAPI endpoint adapter
- the official `omnivoice-infer` CLI when auto CLI mode is explicitly enabled

This repo ships `scripts/hermes-omnivoice-python-adapter.py` as the concrete
Python API adapter. Use it through `HERMES_OMNIVOICE_COMMAND_JSON` when the
local Python environment has `omnivoice`, `torch`, and `soundfile` installed.
Use `scripts/setup-omnivoice-python-env.py --dry-run` to inspect the venv path
and command JSON before creating that environment.

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
unless explicitly overridden, and it rejects Studio URLs containing userinfo.
It also refuses to overwrite an existing non-empty voice directory without
`--force` and validates downloaded reference audio as WAV before writing it
into the registry. Import consent `allowed_uses` are validated before network
access and written as quoted YAML scalars so CLI input cannot reshape the
stored registry metadata. Non-positive importer timeouts are rejected before
local writes or network access.

## Validation

`scripts/validate-omnivoice-bridge.sh` includes a localhost mock Studio
`/generate` contract test. That verifies request shape and WAV response handling
without downloading model weights. A real model-backed Studio smoke test is
still required before claiming synthesis quality.

Use `scripts/check-omnivoice-runtime.py --studio-url http://127.0.0.1:3900` as
a read-only probe before a real smoke test. It checks Studio `/profiles`
reachability and keeps the same loopback-only default as the synthesis wrapper.

For Docker-based local Studio runs, use:

```bash
python scripts/omnivoice-studio-local.py check
python scripts/omnivoice-studio-local.py start
```

The helper validates the Compose port mapping before startup and rejects a
configuration that publishes Studio beyond loopback.

Use `python scripts/omnivoice-studio-local.py start --no-fetch --no-build --pull never`
for a local-only startup probe that will not pull or build Docker images.
If the Studio image is missing locally, the helper fails before invoking
`docker compose up`, avoiding transient Compose resources. Other failed startup
attempts clean up containers and networks by default while preserving volumes
unless `--remove-volumes-on-fail` is explicitly set.
For `--no-build --pull missing` and `--no-build --pull always`, the helper runs
the bounded image pull before Compose startup. Registry or platform failures
therefore fail before Compose creates transient resources.
Docker/Git commands are bounded by `--command-timeout` seconds, defaulting to
900, so a stalled image pull or build does not block a heartbeat indefinitely.
On Apple Silicon, the published image may be unavailable for the local platform.
Building from source is possible but can pull multi-GB PyTorch runtime layers
and may exceed short automation windows before the image export finishes. Keep
source builds bounded in automation and reserve longer or unbounded timeouts for
operator-supervised runs.
