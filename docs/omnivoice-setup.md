# OmniVoice Setup

## Local Voice Registry

Create one directory per local voice:

```text
~/.hermes/voices/omnivoice/marvin/
  voice.yaml
  ref.wav
```

The safest way to create local profiles is the helper script. It refuses to
write a usable profile until consent is explicitly confirmed.

Create a designed voice:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --name Narrator \
  --instruct "male, american accent, moderate pitch" \
  --confirm-consent
```

For English designed voices, OmniVoice expects comma-separated tags from its
supported set, such as `male`, `female`, `american accent`, `british accent`,
`young adult`, `middle-aged`, `low pitch`, `moderate pitch`, or `whisper`.
Free-form phrases like `calm narrator` are rejected by the upstream model.

Create a cloned voice from a local WAV reference sample:

```bash
python scripts/create-omnivoice-voice.py clone marvin \
  --name Marvin \
  --ref-audio /path/to/consented-reference.wav \
  --ref-text "Reference transcript for the voice sample." \
  --confirm-consent
```

The clone command copies the reference sample into the local registry as
`ref.wav`, validates that the sample is a readable WAV file, and refuses to
write over an existing voice directory unless `--force` is set. Keep that
registry outside the repo.

Example clone profile:

```yaml
id: marvin
name: Marvin
engine: omnivoice
mode: clone
ref_audio: ref.wav
ref_text: "Reference transcript for the voice sample."
language: en
speed: 1.0
consent:
  status: confirmed
  source: user_uploaded
  allowed_uses:
    - personal_assistant
    - local_generation
```

Example designed profile:

```yaml
id: narrator
name: Narrator
engine: omnivoice
mode: design
instruct: "male, american accent, moderate pitch"
language: en
speed: 1.0
consent:
  status: confirmed
  source: user_created
  allowed_uses:
    - personal_assistant
    - local_generation
```

## Configure A Backend

Option A: point the wrapper at a local OmniVoice-Studio backend:

```bash
export HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900
```

The wrapper refuses non-loopback Studio URLs by default. Only set
`HERMES_OMNIVOICE_ALLOW_REMOTE_STUDIO=1` after Studio is protected by
authentication.

Option B: set a backend command. JSON is recommended:

```bash
export HERMES_OMNIVOICE_COMMAND_JSON='[
  "python",
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

For direct OmniVoice Python API usage, point the command at the packaged
adapter:

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

The adapter imports `omnivoice`, loads `HERMES_OMNIVOICE_MODEL` or
`k2-fsa/OmniVoice`, and writes the WAV through `soundfile`. Set
`HERMES_OMNIVOICE_DEVICE` and `HERMES_OMNIVOICE_DTYPE` if the defaults do not
match the local runtime.

To prepare an isolated local environment outside this repo, start with a
dry-run:

```bash
python scripts/setup-omnivoice-python-env.py --dry-run
```

The helper prefers Python 3.10 through 3.13 when multiple interpreters are
available. If `python3` points at a newer interpreter, pass an explicit
supported interpreter:

```bash
python scripts/setup-omnivoice-python-env.py --python /opt/homebrew/bin/python3.11 --dry-run
```

Then install when the planned venv path and package source look correct:

```bash
python scripts/setup-omnivoice-python-env.py
python scripts/setup-omnivoice-python-env.py --check-only --require-ready
```

The default venv path is `~/.cache/hermes/omnivoice-python`. Model caches remain
under the normal Hugging Face cache unless separately configured; do not add
them to this repo.

Option C: use the official OmniVoice CLI directly. Install OmniVoice so
`omnivoice-infer` is on `PATH`, then opt in:

```bash
export HERMES_OMNIVOICE_AUTO_CLI=1
export HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice
```

The wrapper maps clone profiles to `omnivoice-infer --ref_audio --ref_text`
and designed profiles to `omnivoice-infer --instruct`. Set
`HERMES_OMNIVOICE_DEVICE=mps`, `cuda:0`, or another supported device to
override OmniVoice's device autodetection. First use may download model files;
keep those caches outside this repo.

Then run:

```bash
python scripts/hermes-omnivoice-tts.py \
  --text-file /tmp/hermes-input.txt \
  --out /tmp/hermes-output.wav \
  --voice marvin \
  --speed 1.0
```

The wrapper exits non-zero if the profile is invalid, consent is missing, the
reference audio is missing, the backend command fails, or the output WAV is not
valid.

## Smoke Test

Run all local bridge checks:

```bash
scripts/validate-omnivoice-bridge.sh
python scripts/omnivoice-acceptance.py
```

`omnivoice-acceptance.py` reports static MVP readiness separately from live
backend readiness. Use `--require-real-backend` when a local Studio service,
backend command, or OmniVoice CLI plus at least one local voice profile should
be treated as mandatory.

Check which local runtime path is available without running synthesis:

```bash
python scripts/check-omnivoice-runtime.py
python scripts/setup-omnivoice-python-env.py --check-only
```

The runtime check does not execute configured backend commands and does not
print command arguments. It only reports whether a backend command is configured,
whether a loopback Studio `/profiles` endpoint is reachable, whether an
`omnivoice-infer` CLI is on `PATH`, whether auto CLI mode is enabled, and how
many local registry profiles exist.

## Local Studio With Docker

This repo includes a helper for OmniVoice-Studio's Docker Compose runtime:

```bash
python scripts/omnivoice-studio-local.py check
python scripts/omnivoice-studio-local.py fetch
python scripts/omnivoice-studio-local.py start
python scripts/omnivoice-studio-local.py status
python scripts/omnivoice-studio-local.py logs
python scripts/omnivoice-studio-local.py stop
```

The helper validates that Studio's published API port is bound to loopback
before `start` runs. By default it uses:

```text
~/.cache/hermes/OmniVoice-Studio
http://127.0.0.1:3900
Docker Compose profile: cpu
```

First startup can pull the Studio image and download model files. Keep those
artifacts in Docker volumes or local caches; do not add them to this repo.
Docker/Git subprocesses are bounded by `--command-timeout 900` by default; set
`--command-timeout 0` only for an intentionally unbounded manual run.
For a local-only startup probe that does not pull or build images, use:

```bash
python scripts/omnivoice-studio-local.py start --no-fetch --no-build --pull never
```

That command succeeds only when the Studio image is already available locally.
Failed startup attempts run `docker compose down` by default. Add
`--remove-volumes-on-fail` only when you are sure no existing Studio volume data
should be preserved.

## Install Into Hermes

When the real Hermes checkout is available, stage the bridge files first:

```bash
python scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --dry-run
```

Then install without `--dry-run`. Existing files are not overwritten unless
`--force` is passed. Add `--with-examples` when you want the sample Hermes
config and safe voice templates copied too.

Run the smoke test only after configuring a real backend command, Studio URL,
or opt-in CLI backend:

```bash
HERMES_OMNIVOICE_COMMAND_JSON='[...]' scripts/test-omnivoice-tts.sh
```

Without a backend, the smoke test exits `77` to mark the integration as skipped
rather than failed.

For CI or local contract testing without model weights, use the deterministic
test fixture backend:

```bash
HERMES_OMNIVOICE_COMMAND_JSON='[
  "python3",
  "tests/fixtures/fake_omnivoice_backend.py",
  "--text-file",
  "{text_file}",
  "--out",
  "{out}",
  "--voice-dir",
  "{voice_dir}",
  "--speed",
  "{speed}"
]' scripts/test-omnivoice-tts.sh
```

This verifies Hermes wrapper I/O and WAV validation only. It is not a real
OmniVoice synthesis quality test.

## Import A Studio Voice

After creating a profile in OmniVoice-Studio, import it into the Hermes registry:

```bash
python scripts/import-omnivoice-studio-voice.py \
  --studio-url http://127.0.0.1:3900 \
  --profile-id <studio-profile-id> \
  --voice-id marvin \
  --confirm-consent
```

The importer reads Studio through `GET /profiles/{id}` and
`GET /profiles/{id}/audio`, then writes
`~/.hermes/voices/omnivoice/<voice_id>/voice.yaml` and `ref.wav` when reference
audio is available. It refuses existing non-empty voice directories unless
`--force` is set, and downloaded reference audio must be a valid WAV.

## Inspect And Preview Voices

List local voices:

```bash
python scripts/hermes-omnivoice-voices.py list
```

Inspect one voice and verify consent state:

```bash
python scripts/hermes-omnivoice-voices.py info marvin
```

Generate a short preview:

```bash
python scripts/hermes-omnivoice-voices.py preview marvin --out /tmp/marvin-preview.wav
```

Print a Hermes command-provider config example:

```bash
python scripts/hermes-omnivoice-voices.py config marvin
```
