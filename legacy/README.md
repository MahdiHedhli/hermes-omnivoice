# legacy/ — archived first attempt (do not build on this)

This directory is the **original OmniVoice → Hermes bridge**: a GPT/Codex
command-provider spike that predates the native plugin now living at the repo
root (`../omnivoice/`). It is kept for provenance and because a few components
are worth harvesting into the plugin later. **It is not the shipped artifact and
is not maintained.**

The original top-level README is preserved here as
[`ORIGINAL_README.md`](ORIGINAL_README.md).

## Why it was replaced

The spike was built against a Hermes integration surface that does not exist the
way it assumed, and it reimplemented subsystems Hermes already ships natively
(the command-provider runner, installer/source-finder/Docker scaffolding). The
replacement is one native Hermes plugin — a `TTSProvider` subclass, one voice
registry, three backends, and a dashboard tab — see `../omnivoice/`.

## What was harvested into the plugin

- `scripts/hermes-omnivoice-python-adapter.py` → `omnivoice/ov_core/backends.py`
  (`_synth_local`): the OmniVoice `generate()` contract. **Note:** the plugin
  corrected the local kwarg to `language_id` (the SDK's real name); the adapter
  only avoided the bug because its `--language` defaulted empty.
- The OpenAI-compatible HTTP client in `scripts/hermes-omnivoice-remote.py`
  (`build_speech_payload`, `/v1/audio/speech`) → `backends.py` `_http_payload` /
  `_synth_studio` / `_synth_service`. This is the **proven** Studio wire shape;
  the plugin's first cut had guessed a bespoke `/generate` multipart endpoint.
- `voice.yaml` schema + consent validators and path hardening (symlink
  rejection, WAV validation, `0600`, safe-child) → `omnivoice/ov_core/registry.py`.

## Worth keeping / integrating in the future

These have no equivalent in the plugin yet and are the reason this stays around:

- **SSH-loopback remote transport** (`scripts/hermes-omnivoice-remote.py`,
  `--transport ssh-loopback`): the *proven* path to the Mac Studio OmniVoice
  service, used because direct HTTP to the tailnet IP timed out. The plugin's
  `service` backend speaks direct HTTP only; porting SSH-loopback into a fourth
  backend (or keeping this wrapper as a `type: command` provider) is the real
  Mode-B deployment story. See [`docs/omnivoice-remote-mvp.md`](docs/omnivoice-remote-mvp.md).
- **Pacing controls** (punctuation normalization, sentence breaks, long-span
  wrapping) in `hermes-omnivoice-remote.py::prepare_text_for_pacing`.
- **QC harness** (`scripts/omnivoice-qc-sample.sh`, per-voice tuning matrices in
  `docs/`) for repeatable listening review.

Everything else here (installer, source-finder, Docker lifecycle, env-setup,
artifact scanners, the 5k-line runner test) is reference-only.
