# OmniVoice for Hermes

A native [Hermes](https://github.com/NousResearch/hermes-agent) TTS plugin for
[OmniVoice / OmniVoice-Studio](https://github.com/k2-fsa/OmniVoice): selecting
`tts.provider: omnivoice` routes every `text_to_speech` call, voice-mode reply,
Discord VC utterance, and messaging voice delivery through OmniVoice — plus a
dashboard **Voices** tab for cloning, designing, previewing, and selecting
voices.

**The plugin is [`omnivoice/`](omnivoice/).** Everything else is history:
[`legacy/`](legacy/) is the archived first-attempt bridge (see
[legacy/README.md](legacy/README.md)) — kept for provenance and a few components
still worth harvesting (notably the proven SSH-loopback remote transport).

## What it is

One plugin, three layers, one registry:

- **Provider** (`omnivoice/ov_core/provider.py`) — a `TTSProvider` subclass.
- **Registry** (`omnivoice/ov_core/registry.py`) — single source of truth for
  the `hermes tools` picker and the dashboard tab; clone + design voices with a
  consent gate and path hardening.
- **Backends** (`omnivoice/ov_core/backends.py`) — `local` (in-process SDK),
  `studio` (OpenAI-compatible `/v1/audio/speech`, loopback), `service` (the same
  wire shape over the LAN with bearer auth + a concurrency guard).
- **Dashboard** (`omnivoice/dashboard/`) — a Voices tab backed by FastAPI routes
  at `/api/plugins/omnivoice/`.

## Install

```bash
cp -r omnivoice ~/.hermes/plugins/omnivoice     # top-level location is required
hermes plugins enable omnivoice
# paste omnivoice/config.example.yaml's block under `tts:` in ~/.hermes/config.yaml
# then set tts.provider: omnivoice
```

Full details, backend config, security model, and per-backend dependencies are
in [`omnivoice/README.md`](omnivoice/README.md).

## Status

- Code-complete; **37 offline tests pass** (`cd omnivoice && pytest -q`).
- **Live-tested on Hermes v0.18.0**: provider registers through the real plugin
  loader and appears in the `hermes tools` picker; the dashboard Voices tab and
  its backend routes are discovered; end-to-end synthesis verified against a
  loopback `/v1/audio/speech` mock.
- Not yet exercised on this machine: real in-process `local` synthesis (needs
  `torch` + the OmniVoice SDK) and the networked `service` backend against a live
  server. See [`omnivoice/README.md`](omnivoice/README.md) for those and the
  deferred `stream()` / cross-provider fallback work.

## Security

Loopback is clean; non-loopback needs deliberate gating. The dashboard binds
`127.0.0.1`; every mutating/compute plugin route refuses non-loopback callers
unless `HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE=1`; the `service` backend requires a
bearer token on any non-loopback URL. Clone ingestion enforces consent, WAV
validation, symlink rejection, and `0600` writes.
