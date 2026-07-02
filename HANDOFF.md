# Handoff — OmniVoice Hermes plugin: review, fixes, live test

Branch: `feature/omnivoice-native-plugin` (2 commits on top of the spike history).
Nothing has been pushed. Live Hermes: **v0.18.0** (`~/.hermes/hermes-agent`).

## What changed (defects fixed)

| # | Sev | Fix |
|---|-----|-----|
| 1 | High | `backends.py`: studio/service rewritten from a guessed `/generate` multipart to the **proven OpenAI-compatible `/v1/audio/speech` JSON** contract (`{model,input,voice,response_format,speed,language_id}` + bearer). Studio/service select a **server-side `voice` id**; clone-by-local-audio is `local`-only. |
| 2 | High | `_synth_local`: SDK kwarg is **`language_id`**, not `language` (the port always sent the wrong one). Import via documented `from omnivoice import OmniVoice`. |
| 3 | Med | `plugin_api.py`: **all** mutating/compute routes (design/clone/preview/set-active/delete) gated to loopback, not just clone. Peer check uses the socket address, not a spoofable header. |
| 4 | Med | Preview synth runs in a **threadpool** (was blocking the dashboard event loop). |
| 5 | Low | Clone upload **size-capped** (25 MiB). |
| 6 | Low | `provider.synthesize` `format` default aligned to the ABC; `__init__` sys.path `append` (not insert-0). |
| — | Tests | Added dashboard-route coverage, the non-loopback-refusal test, and a `language_id` regression test. **37 pass** (was 26). |

Registry hardening (symlink rejection, WAV validation, consent gate, `0600`,
safe-child) was already solid and was kept.

## Verify-items — resolved with evidence

1. **Local `generate()`** — confirmed against the k2-fsa/OmniVoice release
   (README + PyPI `omnivoice`): `from_pretrained(model, device_map=, dtype=)`,
   `generate(text=, speed=, language_id=, ref_audio=, ref_text=, instruct=)` →
   `list[np.ndarray]` @ 24 kHz. Fixed `language_id`.
2. **Studio HTTP surface** — OpenAI `/v1/audio/speech`, per this repo's own
   proven client (`legacy/scripts/hermes-omnivoice-remote.py`). Rewrote to match.
3. **Loader layout** — top-level `~/.hermes/plugins/omnivoice/` is correct on
   v0.18.0: general plugin loader → `register(ctx)` → `register_tts_provider`
   (plugins.py:800), picker injection (tools_config.py:2287), dashboard scans
   `plugins/<name>/dashboard/manifest.json` (web_server.py:13458). No relocation.

## Live test on Hermes v0.18.0 (11/11)

Installed to `~/.hermes/plugins/omnivoice/`, `hermes plugins enable omnivoice`
(tool-override NOT granted — not needed). Then, via Hermes' own loader/registry:
- provider registers and shows as "OmniVoice" in the picker;
- real SDK name `omnivoice` is **not** shadowed by `ov_core`;
- `provider.synthesize` → studio backend → loopback `/v1/audio/speech` mock
  produced a valid WAV; server received the correct `voice` id + OpenAI payload;
- dashboard tab discovered (label Voices, icon MessageSquare, `has_api: True`);
  the **preview route** returned real audio end-to-end.

All scoped to a temp voices dir + env overrides — the real `~/.hermes/config.yaml`
and voices were untouched, and the active provider stays `xtts-v2`.

## Not yet run (out of scope / needs deps)

- Real in-process **`local`** synthesis — needs `torch` + the OmniVoice SDK
  (multi-GB); not installed here. The code path is unit-tested with a fake SDK.
- **`service`** backend against the live Mac Studio — excluded this session
  (local-only). Note the archived `docs/omnivoice-remote-mvp.md`: direct HTTP to
  the tailnet IP timed out; the proven transport is SSH-loopback, which the
  plugin's direct-HTTP `service` backend does not yet do (see legacy/README.md).
- A visual browser smoke of the Voices tab (`hermes dashboard`).
- Deferred by design (not bugs): `stream()` stub, cross-provider `piper` fallback.

## Publish — awaiting sign-off

Repo restructured in place (spike → `legacy/`, plugin at root). **No git remote
is configured** and nothing is pushed. Outward-facing steps need your decision:
remote/repo target, rename to `hermes-omnivoice`, merge-to-main vs PR, and the
optional additive `ICON_MAP` PR / `hermes-example-plugins` contribution.
