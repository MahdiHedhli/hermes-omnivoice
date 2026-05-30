# OmniVoice MVP Handoff

## Ready State

The bridge is ready as a command-provider MVP package. It includes:

- A Hermes-facing wrapper at `scripts/hermes-omnivoice-tts.py`.
- A Python API adapter at `scripts/hermes-omnivoice-python-adapter.py` for
  environments where the `omnivoice` package is installed.
- A dry-run/check-first Python environment helper at
  `scripts/setup-omnivoice-python-env.py`.
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
backend acceptance now passes on this machine when the prepared OmniVoice
Python adapter command is exported; the default shell remains unconfigured so
it does not claim backend readiness by accident.

## Current Acceptance Snapshot

As of 2026-05-30 14:30 America/New_York on branch
`feature/omnivoice-custom-voices`:

- `scripts/validate-omnivoice-bridge.sh` passes with 76 tests and 1 expected
  opt-in real-backend skip.
- `scripts/omnivoice-acceptance.py` reports `mvp_static_ready: true`,
  `real_backend_ready: false`, and `hermes_source_ready: false` in the default
  shell environment because no backend command is exported there.
- `scripts/omnivoice-acceptance.py --require-real-backend` passes when
  `HERMES_OMNIVOICE_COMMAND_JSON` is set to the prepared Python adapter command
  and `HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice`.
- `scripts/test-omnivoice-tts.sh` generated a valid temporary WAV through that
  adapter path using the required smoke text.
- `scripts/find-hermes-source.py` still finds only this bridge repo under the
  searched Hermes/Coding roots, so native-provider work remains deferred.
- `scripts/check-omnivoice-runtime.py` reports no default Studio URL, backend
  command, or auto CLI; it now sees one local designed profile under
  `~/.hermes/voices/omnivoice`.
- `scripts/setup-omnivoice-python-env.py --check-only --json` reports the
  isolated venv at `~/.cache/hermes/omnivoice-python` is ready, including
  `omnivoice`, `torch`, `soundfile`, and `omnivoice-infer`.
- The fastest proven real-synthesis path is still the isolated Python
  adapter or explicit CLI path plus a consented local voice profile, not a
  running Studio container.

## Validate

Run the full deterministic contract suite:

```bash
scripts/validate-omnivoice-bridge.sh
```

Summarize static and live readiness:

```bash
python scripts/omnivoice-acceptance.py
python scripts/check-omnivoice-runtime.py
python scripts/setup-omnivoice-python-env.py --check-only
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

Plan or create the isolated adapter environment:

```bash
python scripts/setup-omnivoice-python-env.py --dry-run
python scripts/setup-omnivoice-python-env.py
python scripts/setup-omnivoice-python-env.py --check-only --shell
```

The helper chooses Python 3.10 through 3.13 when available. On this machine,
`python3` may point at a newer interpreter, so pass `--python` if the dry-run
shows an unsupported setup Python.

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
  --instruct "male, american accent, moderate pitch" \
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
- The published Studio image has no `linux/arm64/v8` manifest on this Mac, and
  a source-build attempt exceeded a 300 second heartbeat window while exporting
  the Docker image.
- No real OmniVoice backend command is exported in the default shell, and
  `omnivoice-infer` is not enabled through `HERMES_OMNIVOICE_AUTO_CLI=1`.
- The isolated OmniVoice venv and local `heartbeat_narrator` designed profile
  are ready, but the adapter command still needs to be exported for backend
  readiness in any new shell.
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
