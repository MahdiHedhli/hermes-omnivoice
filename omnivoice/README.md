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

The **Gallery** tab is the quickest start: 24 ready-made designed voices,
grouped by use case, added to your registry in one click. They ship inside the
plugin (`data/gallery.json`) so the tab works offline; *Refresh from gallery* is
the only outbound call and only on click. Presets are re-validated against the
attribute vocabulary before being offered, and installing one goes through the
same `create_design()` path as the Design tab — same id rules, same validation,
same consent record.

Setting a voice active also writes `tts.provider: omnivoice` (a surgical
one-line edit that preserves the rest of your config, comments included), so the
voice applies to every Hermes surface rather than just this plugin's own tabs.
A gateway restart applies it to running sessions.

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
  `.generate(text=, speed=, language=, ref_audio=, ref_text=, instruct=)` →
  `list[np.ndarray]` @ 24 kHz. Verified against **omnivoice 0.1.5**: the SDK
  kwarg is **`language`** (the `language_id` name below is the *HTTP wire*
  field, a different layer). See `ov_core/backends.py::_synth_local`.
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

### Networked `service` transports

`tts.omnivoice.service.transport` selects how the `service` backend reaches the node:

- **`http`** (default) — direct HTTP(S) to `service.url`; a non-loopback URL
  requires a bearer token.
- **`ssh-loopback`** — SSH to `service.ssh_host`, which calls its own loopback
  OmniVoice service (`service.url`, e.g. `http://127.0.0.1:8880`). The proven Mac
  Studio path: direct HTTP to the tailnet IP was observed to time out, and the
  token travels over the SSH-encrypted channel, not the network. Requires
  `ssh_host` + a token. Ported from `legacy/scripts/hermes-omnivoice-remote.py`.

### Still to confirm against YOUR server

- Whether your OmniVoice-Studio exposes a streaming endpoint (for `stream()`)
  and the exact `voice` ids it holds. The `ssh-loopback` transport is unit-tested
  (response framing, routing, host/token guards) but not yet run against the live
  Mac Studio.

## Deferred / rough edges

- **Streaming** (`stream()`) is stubbed — it raises `NotImplementedError`, so
  Hermes falls back to `synthesize()` + read-whole-file. Wire it to the service's
  chunked endpoint for time-to-first-audio.
- **Fallback provider** on backend failure (e.g. `piper`) is a Phase 5 item; the
  provider currently raises on failure per the ABC contract.
- **No preview before adding a gallery preset.** Over `studio`/`service` the
  OpenAI-compatible body sends `voice: <id>` — a *server-side* id — so an
  un-saved voice can't be synthesized there (it would work only on `local`).
  Rather than ship a button that silently fails on the common setup, add the
  voice first and preview it from the Voices tab.
- **Gallery presets only.** The upstream gallery schema also allows recorded
  reference clips; those are skipped on purpose, since pulling third-party audio
  of real people would bypass the consent gate the clone path enforces.
