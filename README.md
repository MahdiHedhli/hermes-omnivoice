# Hermes OmniVoice Studio Bridge

Local command-provider bridge for using OmniVoice or OmniVoice-Studio voices
from Hermes Agent TTS.

This repo is intentionally conservative:

- Voice samples, generated audio, model weights, caches, and local config stay
  out of git.
- Cloned voices require `consent.status: confirmed`, a non-empty
  `consent.source`, and at least one non-empty `consent.allowed_uses` entry.
- Cloned voice reference files are validated as readable WAV audio before use.
- Local voice profile directories are written private by default; registry YAML
  and copied/imported `ref.wav` files are `0600`.
- Runtime profile loading rejects symlinked voice directories, `voice.yaml`
  files, and cloned `ref_audio` files.
- Create/import helpers refuse final voice-directory symlinks so forced writes
  cannot alias another profile.
- The Studio importer validates profile JSON shape before requesting audio or
  writing local voice material.
- Generated output audio is validated before final replacement, written as
  `0600`, and an existing output symlink is replaced instead of followed.
- OmniVoice-Studio is treated as loopback-only by default because it has no
  built-in authentication.
- The first integration path is a command provider, not a native Hermes patch,
  because the real Hermes Agent source is not present in this checkout.

## What Is Included

- `scripts/hermes-omnivoice-tts.py`: Hermes TTS command-provider wrapper.
- `scripts/hermes-omnivoice-python-adapter.py`: optional command adapter for
  calling the OmniVoice Python API directly.
- `scripts/setup-omnivoice-python-env.py`: dry-run/check-first helper for an
  isolated local OmniVoice Python environment outside this repo.
- `scripts/create-omnivoice-voice.py`: creates local design or clone voice
  registry profiles with explicit consent metadata.
- `scripts/import-omnivoice-studio-voice.py`: imports a Studio profile into the
  Hermes local registry after explicit consent confirmation.
- `scripts/hermes-omnivoice-voices.py`: list, inspect, preview, and print sample
  config for local voices.
- `scripts/find-hermes-source.py`: read-only helper for finding and scoring
  candidate Hermes Agent source trees before native-provider work.
- `scripts/check-omnivoice-runtime.py`: read-only diagnostics for local backend,
  Studio, CLI, and voice registry availability. Malformed Studio `/profiles`
  payloads and non-object profile-list entries are reported as invalid, not
  ready.
- `scripts/install-hermes-omnivoice-bridge.py`: copies bridge files into a real
  Hermes checkout or staging directory without overwriting by default.
- `scripts/omnivoice-studio-local.py`: helper for checking, fetching, starting,
  stopping, and inspecting loopback-only OmniVoice-Studio with Docker Compose.
- `scripts/omnivoice-acceptance.py`: summarizes static MVP readiness and live
  backend readiness.
- `scripts/validate-omnivoice-bridge.sh`: deterministic local validation,
  including unit tests, smoke checks, secret scanning, artifact scanning, and
  whitespace checks.
- `scripts/check-omnivoice-artifacts.py`: validates that generated audio,
  model files, local sample directories, env files, and local voice selection
  state are absent from the repo.
- `docs/`: setup, Studio bridge notes, integration findings, and custom voice
  usage.
- `examples/`: sample Hermes config and voice registry templates.

## Quick Start

Validate the bridge locally:

```bash
scripts/validate-omnivoice-bridge.sh
python scripts/omnivoice-acceptance.py
```

Create or import a voice under:

```text
~/.hermes/voices/omnivoice/<voice_id>/voice.yaml
```

Create a designed voice profile:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --instruct "male, american accent, moderate pitch" \
  --confirm-consent
```

Point the wrapper at local OmniVoice-Studio:

```bash
export HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900
```

Check the local runtime without generating audio:

```bash
python scripts/check-omnivoice-runtime.py
python scripts/setup-omnivoice-python-env.py --check-only
```

Print shell exports for the prepared Python adapter backend:

```bash
python scripts/setup-omnivoice-python-env.py --check-only --shell
```

Check or start a local loopback-only Studio container:

```bash
python scripts/omnivoice-studio-local.py check
python scripts/omnivoice-studio-local.py start
```

Install the bridge into a real Hermes checkout or staging directory:

```bash
python scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --dry-run
```

Add `--update-gitignore` after reviewing the dry-run output when you want the
installer to append the OmniVoice local-artifact ignore block to the target
checkout. If that managed block already exists, the same flag refreshes it to
the current pattern list.

Generate a preview:

```bash
python scripts/hermes-omnivoice-voices.py set narrator
python scripts/hermes-omnivoice-voices.py current
python scripts/hermes-omnivoice-voices.py preview marvin --out /tmp/marvin-preview.wav
```

Print a Hermes command-provider config for a selected voice:

```bash
python scripts/hermes-omnivoice-voices.py config narrator
```

Pass `--voices-dir` before `config` when generating config for a non-default
registry; the emitted command includes that registry path. The voice must be a
valid profile with confirmed consent.

## Backend Options

Use exactly one of these local backend paths:

- `HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900`
- `HERMES_OMNIVOICE_COMMAND_JSON='[...]'`
- `HERMES_OMNIVOICE_COMMAND='...'`
- `HERMES_OMNIVOICE_AUTO_CLI=1` with `omnivoice-infer` on `PATH`

Prefer `HERMES_OMNIVOICE_COMMAND_JSON` for custom adapters because it avoids
shell quoting hazards. Use `scripts/setup-omnivoice-python-env.py --shell` to
print safely quoted exports for the packaged Python adapter. The auto CLI path
is opt-in because the first `omnivoice-infer` run may download model files.
Unknown placeholders, unsupported placeholder access, and invalid brace syntax
are treated as wrapper configuration errors before any backend command is
invoked; escape literal braces in command templates as `{{` and `}}`.
The wrapper currently supports WAV output only and rejects non-`.wav` output
paths before backend or Studio startup.

## Current Limits

- Real model-backed synthesis works through the prepared local Python adapter
  when its shell exports are applied and a consented local voice profile exists.
- Native Hermes provider wiring is deferred until the real Hermes Agent source
  and TTS schema are available.
- The fake backend in `tests/fixtures` verifies wrapper I/O only. It is not a
  TTS engine.

## More Detail

- [Setup](docs/omnivoice-setup.md)
- [MVP handoff](docs/omnivoice-mvp-handoff.md)
- [Weekend summary](docs/omnivoice-weekend-summary.md)
- [Studio bridge](docs/omnivoice-studio-bridge.md)
- [Acceptance checklist](docs/omnivoice-acceptance.md)
- [Integration notes](docs/omnivoice-integration-notes.md)
- [Hermes custom voices](docs/tts-custom-voices.md)
