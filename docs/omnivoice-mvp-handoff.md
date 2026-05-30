# OmniVoice MVP Handoff

## Ready State

The bridge is ready as a command-provider MVP package. It includes:

- A Hermes-facing wrapper at `scripts/hermes-omnivoice-tts.py`.
- A Python API adapter at `scripts/hermes-omnivoice-python-adapter.py` for
  environments where the `omnivoice` package is installed.
- Local voice registry tools for creating, importing, listing, selecting, and
  previewing voice profiles.
- Consent and reference-audio validation for cloned voices.
- Localhost-only Studio API support through `HERMES_OMNIVOICE_STUDIO_URL`.
- Backend command support through `HERMES_OMNIVOICE_COMMAND_JSON`.
- Opt-in official CLI support through `HERMES_OMNIVOICE_AUTO_CLI=1` and
  `omnivoice-infer`.
- Runtime diagnostics, acceptance checks, deterministic contract tests, and a
  dry-run-first installer for a real Hermes checkout.

Static MVP acceptance currently passes without a real model backend. Live
backend acceptance is still blocked until this machine has a local Studio
service, an OmniVoice command adapter, or the OmniVoice CLI plus at least one
consented voice profile.

## Validate

Run the full deterministic contract suite:

```bash
scripts/validate-omnivoice-bridge.sh
```

Summarize static and live readiness:

```bash
python scripts/omnivoice-acceptance.py
python scripts/check-omnivoice-runtime.py
```

Use strict acceptance only after a real backend and local voice profile should
exist:

```bash
python scripts/omnivoice-acceptance.py --require-real-backend
```

## Install Into Hermes

Dry-run the install into a real Hermes checkout or staging directory:

```bash
python scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --dry-run
```

Then rerun without `--dry-run`. Existing files are not overwritten unless
`--force` is passed. Add `--with-examples` to copy the sample config and safe
voice templates.

## Configure A Real Backend

Use one backend path at a time.

For local Studio:

```bash
export HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900
```

For a local adapter command:

```bash
export HERMES_OMNIVOICE_COMMAND_JSON='[
  "python3",
  "-m",
  "your_omnivoice_adapter",
  "--text-file",
  "{text_file}",
  "--out",
  "{out}",
  "--voice-dir",
  "{voice_dir}",
  "--speed",
  "{speed}"
]'
```

For the packaged Python API adapter:

```bash
export HERMES_OMNIVOICE_COMMAND_JSON='[
  "python3",
  "scripts/hermes-omnivoice-python-adapter.py",
  "--text-file",
  "{text_file}",
  "--out",
  "{out}",
  "--ref-audio",
  "{ref_audio}",
  "--ref-text",
  "{ref_text}",
  "--instruct",
  "{instruct}",
  "--language",
  "{language}",
  "--speed",
  "{speed}"
]'
```

For the official OmniVoice CLI:

```bash
export HERMES_OMNIVOICE_AUTO_CLI=1
export HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice
```

This uses `omnivoice-infer` and passes clone profiles as `--ref_audio` plus
`--ref_text`, or designed profiles as `--instruct`.

Studio must stay on loopback unless it is explicitly protected by
authentication. Do not expose an unauthenticated Studio API to the LAN.

## Create Or Select Voices

Create a designed voice:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --instruct "calm local assistant voice" \
  --confirm-consent
```

Create a cloned voice from a consented WAV sample:

```bash
python scripts/create-omnivoice-voice.py clone marvin \
  --ref-audio /path/to/consented-reference.wav \
  --ref-text "Reference transcript for the voice sample." \
  --confirm-consent
```

Import a Studio profile:

```bash
python scripts/import-omnivoice-studio-voice.py \
  --studio-url http://127.0.0.1:3900 \
  --profile-id <studio-profile-id> \
  --voice-id <hermes-voice-id> \
  --confirm-consent
```

Select and preview a local voice:

```bash
python scripts/hermes-omnivoice-voices.py set narrator
python scripts/hermes-omnivoice-voices.py current
python scripts/hermes-omnivoice-voices.py preview narrator --out /tmp/narrator.wav
```

## Remaining Live Blockers

- No local Studio service is running on `127.0.0.1:3900`.
- No local Studio image is present for a no-pull startup probe.
- No real OmniVoice backend command is configured and `omnivoice-infer` is not
  available as an enabled local CLI backend.
- The `omnivoice` Python package is not installed in this repo environment.
- No local consented voice profiles exist under
  `~/.hermes/voices/omnivoice`.
- The real Hermes Agent source is not present in this checkout, so native
  provider wiring and in-app `/voice` commands are deferred.

## Security Invariants

- Do not commit voice samples, generated audio, model files, caches, secrets,
  or user-level selection state.
- Cloned voices require explicit `consent.status: confirmed` metadata and a
  readable WAV reference file.
- Treat the fake backend in tests as a contract fixture only, never as real
  synthesis evidence.
- Keep Studio on loopback by default and prefer HTTP APIs or import/export over
  direct SQLite coupling.
