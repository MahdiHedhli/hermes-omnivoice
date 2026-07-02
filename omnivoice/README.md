# OmniVoice for Hermes

OmniVoice / OmniVoice-Studio as a native Hermes TTS provider, with a voice
registry (clone + design), a local / Studio-HTTP / networked-service backend,
and a dashboard tab for cloning, previewing, and selecting voices.

One plugin, three layers, one registry:

- **Provider** (`ov_core/provider.py`) — a `TTSProvider` so `tts.provider:
  omnivoice` routes every `text_to_speech` call, voice-mode reply, Discord VC
  utterance, and messaging voice delivery through OmniVoice automatically.
- **Registry** (`ov_core/registry.py`) — the single source of truth for both
  the `hermes tools` picker and the dashboard tab. Clone (reference sample) and
  design (instruct string) voices, with a consent gate and path hardening.
- **Backends** (`ov_core/backends.py`) — `local` (in-process SDK), `studio`
  (OmniVoice-Studio over HTTP, loopback), or `service` (a shared voice engine
  on a capable node over the LAN, with auth + a concurrency guard).
- **Dashboard** (`dashboard/`) — a **Voices** tab (clone / design / preview /
  select) backed by FastAPI routes at `/api/plugins/omnivoice/`.

The shared Python package is named `ov_core` on purpose: it must not shadow the
real OmniVoice SDK, which imports as `from omnivoice.models.omnivoice import
OmniVoice`.

## Install

```bash
# The whole directory is the plugin. Top-level location is required so the
# dashboard discovers dashboard/manifest.json.
cp -r omnivoice ~/.hermes/plugins/omnivoice

hermes plugins enable omnivoice
```

Add the provider config (see `config.example.yaml`) under `tts:` in
`~/.hermes/config.yaml`, then set `tts.provider: omnivoice`.

Backend dependencies are per-backend — see `requirements.txt`. `local` needs the
OmniVoice SDK + torch + soundfile; `studio`/`service` need nothing beyond the
stdlib.

## Create and select voices

**From the dashboard** (recommended): run `hermes dashboard`, open the
**Voices** tab. Clone from a `.wav` reference (with transcript + consent),
design from an instruct string, preview any voice, and set the active one.

**From the CLI/registry**: voices live at
`~/.hermes/voices/omnivoice/<id>/voice.yaml`. The active voice is recorded in
`~/.hermes/voices/omnivoice/.active` and is what synthesis uses when no explicit
voice is passed.

## Networked / shared voice service (Mode B)

Run OmniVoice on a capable node and point thin agents at it:

```yaml
tts:
  provider: omnivoice
  omnivoice:
    backend: service
    service:
      url: http://mac-studio.local:3900   # or a tailnet IP
      auth_token_env: HERMES_OMNIVOICE_SERVICE_TOKEN
      max_concurrency: 2
```

Set the token in the environment (`HERMES_OMNIVOICE_SERVICE_TOKEN`). The client
sends it as a bearer token and caps concurrent requests so the node isn't
overrun. No per-token cost, no rate limits, reference audio stays on your
infrastructure.

## Security

Loopback is clean; non-loopback needs deliberate gating.

- The dashboard binds `127.0.0.1` by default. Plugin API routes bypass the
  dashboard session-auth gate, so **do not** expose the dashboard with `--host
  0.0.0.0` on an untrusted network while this plugin is installed.
- The clone-upload route accepts a file and runs a model. It refuses
  non-loopback callers unless you set `HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE=1` on
  a trusted network.
- The `service` backend authenticates callers and should bind a LAN/VPN address,
  never rely on "127.0.0.1 = safe." Prefer a tailnet.
- Clone ingestion enforces consent (confirmed status, non-empty source, at least
  one allowed use), validates the reference is a real WAV, rejects symlinks, and
  writes registry files `0600`.

## Tests

```bash
cd ~/.hermes/plugins/omnivoice
pytest -q          # runs without the OmniVoice SDK / torch / soundfile / Hermes
```

## Verified contracts (were "verify-before-run", now resolved)

- **Local SDK** — `from omnivoice import OmniVoice`,
  `OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=, dtype=)` then
  `.generate(text=, speed=, language_id=, ref_audio=, ref_text=, instruct=)` →
  `list[np.ndarray]` @ 24 kHz. Note the kwarg is **`language_id`** (not
  `language`). See `ov_core/backends.py::_synth_local`.
- **Studio / service HTTP** — OpenAI-compatible `POST {url}{speech_path}`
  (`speech_path` defaults to `/v1/audio/speech`) with a JSON body
  `{model, input, voice, response_format, speed, language_id}` and bearer auth.
  The `voice` is a **server-side voice id**; local clone reference audio cannot
  be sent over HTTP (clone-by-ref is a `local`-backend feature). See
  `ov_core/backends.py::_http_payload` / `_synth_studio` / `_synth_service`.
- **Loader layout** — this plugin installs top-level at
  `~/.hermes/plugins/omnivoice/` and registers via `register(ctx)` →
  `ctx.register_tts_provider(...)`, which is how Hermes ≥ 0.18 surfaces plugin
  TTS providers in `hermes tools` and routing. (The ABC's `plugins/tts/<name>/`
  note is legacy; the general plugin loader + dashboard both use top-level.)

### Still to confirm against YOUR server

- Whether your OmniVoice-Studio exposes a streaming endpoint (for `stream()`)
  and the exact `voice` ids it holds. On the Mac Studio deployment, direct HTTP
  to a tailnet IP was observed to time out; the proven transport there is
  SSH-loopback (see the archived spike's `hermes-omnivoice-remote.py`). The
  `service` backend here speaks the direct-HTTP wire shape — for the
  SSH-loopback transport, use the spike wrapper as a command provider or port it
  into a future backend.

## Deferred / rough edges

- **Streaming** (`stream()`) is stubbed — it raises `NotImplementedError`, so
  Hermes falls back to `synthesize()` + read-whole-file. Wire it to the service's
  chunked endpoint for time-to-first-audio.
- **Fallback provider** on backend failure (e.g. `piper`) is a Phase 5 item; the
  provider currently raises on failure per the ABC contract.
