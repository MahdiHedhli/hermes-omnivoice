# OmniVoice Setup

## Local Voice Registry

Create one directory per local voice:

```text
~/.hermes/voices/omnivoice/marvin/
  voice.yaml
  ref.wav
```

The safest way to create local profiles is the helper script. It refuses to
write a usable profile until consent is explicitly confirmed. Created or
imported local profile directories are made private with `0700` permissions;
`voice.yaml` and any copied or imported `ref.wav` are written with `0600`
permissions through same-directory temporary files and atomic replacement.
Forced rewrites replace existing material symlinks instead of following them.
The helpers also refuse symlinked registry roots and final profile-directory
symlinks so a forced write cannot alias another local voice profile.
Non-finite or non-positive `--speed` values are rejected before the helper
creates a profile directory or copies clone reference audio.
Empty `--allowed-use` values are also rejected before local profile writes.
Clone creation also rejects symlinked `--ref-audio` inputs before copying, so a
reference sample path cannot silently alias another local file.

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
write over an existing voice directory unless `--force` is set. Symlinked
reference sample paths are refused before copy. The copied sample is private
local voice material; keep that registry outside the repo.

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

For a remote Mac Studio FastAPI backend over Tailscale, see
`docs/omnivoice-remote-mvp.md`. The current proven Mac Studio route uses
`scripts/hermes-omnivoice-remote.py`, `OMNIVOICE_REMOTE_TRANSPORT=ssh-loopback`,
`OMNIVOICE_REMOTE_SSH_HOST`, `OMNIVOICE_REMOTE_SSH_IDENTITY_FILE`, and
`OMNIVOICE_REMOTE_HELPER`. In helper mode, the bearer token stays in a
protected Mac Studio-local env file and is not copied to Hermes. It is
separate from the local wrapper backend options below.

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

Print safely quoted shell exports for the prepared adapter:

```bash
python scripts/setup-omnivoice-python-env.py --check-only --shell
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
  --speed 1.0 \
  --max-chars 2000
```

The wrapper exits non-zero if the profile is invalid, consent is missing, the
reference audio is missing, `speed` is not finite and greater than zero,
`timeout` is not greater than zero, the input exceeds `--max-chars`, the output
path does not end in `.wav`, the backend command fails, or the output WAV is
not valid. It rejects non-`.wav` output paths before backend or Studio startup.
It rejects symlinked `--text-file` inputs before reading text or starting a
backend.
It also rejects symlinked voice registry roots, voice directories, `voice.yaml`
files, and cloned `ref_audio` files before using registry material.
It removes an existing output-file symlink before synthesis so local backends do
not follow it, passes command backends a private same-directory temporary output
path, and leaves successful generated audio with `0600` permissions. Command
backend stderr, Studio API failure detail, and final wrapper errors are
redacted for common credential-shaped values before they are printed on failure.
Command backend output and built-in Studio API responses are validated before
the wrapper atomically replaces the requested output file.

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
print command arguments. It validates backend command template placeholders,
reports whether a backend command is configured, whether a loopback Studio
`/profiles` endpoint is reachable, whether an `omnivoice-infer` CLI is on
`PATH`, whether auto CLI mode is enabled, and how many local registry profiles
pass the wrapper voice-profile validator. Malformed Studio `/profiles` JSON,
including profile-list entries that are not objects, is reported as `invalid`,
not backend-ready. Its Studio probe `--timeout` must be greater than zero. The
voice registry probe ignores symlinked registry roots, voice directories,
`voice.yaml` files, clone reference audio aliases, missing clone audio, and
invalid consent metadata, so those entries do not make acceptance voice-ready.

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

The helper validates that Studio's published API port is in the valid TCP range
and bound to loopback before `start` runs. By default it uses:

```text
~/.cache/hermes/OmniVoice-Studio
http://127.0.0.1:3900
Docker Compose profile: cpu
```

First startup can pull the Studio image and download model files. Keep those
artifacts in Docker volumes or local caches; do not add them to this repo.
Docker/Git subprocesses are bounded by `--command-timeout 900` by default; set
`--command-timeout 0` only for an intentionally unbounded manual run.
Negative `--command-timeout` values are rejected before Docker or Git commands
can run.
The published `--port` value must be between 1 and 65535 and is rejected before
Docker or Git commands can run.
The health probe `--timeout` must be greater than zero.
The `logs --tail` value must be zero or greater so log inspection stays
bounded by an explicit line count.
For a local-only startup probe that does not pull or build images, use:

```bash
python scripts/omnivoice-studio-local.py start --no-fetch --no-build --pull never
```

That command succeeds only when the Studio image is already available locally.
When the local image is missing, the helper exits before `docker compose up` so
it does not create transient Compose containers, networks, or volumes. Other
failed startup attempts run `docker compose down` by default. Add
`--remove-volumes-on-fail` only when you are sure no existing Studio volume
data should be preserved.

With `--no-build --pull missing` or `--no-build --pull always`, the helper
performs the bounded image pull before `docker compose up`. This keeps registry
or platform failures out of Compose startup; for example, a missing image
manifest fails before Compose creates containers, networks, or volumes.

If the published image is unavailable for the local platform, remove
`--no-build` and let Compose build from the checked-out Studio source. On Apple
Silicon this path can download multi-GB PyTorch runtime layers and may exceed a
short `--command-timeout` while exporting the image. Keep automated runs bounded
and use a longer timeout only when an operator is watching local disk and Docker
state.

## Install Into Hermes

When the real Hermes checkout is available, stage the bridge files first:

```bash
python scripts/find-hermes-source.py --json

python scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --dry-run
```

`find-hermes-source.py` is read-only. It reports candidate source trees and TTS
indicators, skips secret-named files, and marks this bridge repo separately
from a real Hermes Agent checkout.
Keep `--scan-timeout`, `--max-candidates`, `--max-files`, and
`--max-file-bytes` greater than zero, and keep `--max-depth` non-negative so
discovery remains bounded and useful in automation.
Prefer explicit candidate roots or the bounded source finder over broad content
grep across a whole development tree. Generic terms such as `provider`, `voice`,
and `tts` appear in many unrelated repositories and are not sufficient evidence
of a Hermes Agent checkout.

Then install without `--dry-run`. Existing files are not overwritten unless
`--force` is passed. Add `--with-examples` when you want the sample Hermes
config and safe voice templates copied too.
The installer reports missing target `.gitignore` coverage for local voice
material, generated audio, model weights, caches, and local config. Add
`--update-gitignore` only after reviewing the dry-run output; it appends a
managed block and is idempotent. If a managed block already exists but is
missing newer patterns, `--update-gitignore` refreshes that block in place.

## Enable Or Disable The Provider

For a reversible operator trial, add `tts.providers.omnivoice` first while
keeping the current `tts.provider` unchanged. Confirm the provider command,
voice registry, consent metadata, and backend runtime before switching the
active provider.

Check current status without exposing command arguments:

```bash
scripts/omnivoice-status.sh --hermes-root /path/to/hermes-agent --dry-run
```

Dry-run the provider switch first:

```bash
scripts/omnivoice-enable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home \
  --dry-run
```

Enable OmniVoice after reviewing the dry run:

```bash
scripts/omnivoice-enable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home
```

Disable OmniVoice and roll back:

```bash
scripts/omnivoice-disable.sh \
  --hermes-root /path/to/hermes-agent \
  --runtime-home /path/to/runtime-home \
  --provider xtts-v2
```

The enable script validates `tts.providers.omnivoice`, redacts command
arguments in output, requires `timeout >= 600`, and backs up
`~/.hermes/config.yaml` before saving. Run these scripts as the Hermes runtime
user, or pass `--runtime-home` for the home directory whose Hermes config
should be loaded.

Manual enable:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "omnivoice"
save_config(cfg)
```

Manual rollback:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "<previous-provider>"
save_config(cfg)
```

Keep a rollback helper outside the Hermes source checkout before an operator
trial. If Hermes has no long-running service unit and the TTS tool reads config
on invocation, saving config is enough for the next live tool-path smoke. If a
deployment wraps Hermes in a long-running service that caches config, use that
deployment's normal reload or restart command after saving config.

After either switch, run a live Hermes TTS smoke through the real tool path and
confirm the active provider plus generated media before proceeding.

For subjective listening checks after acceptance passes, use:

```bash
scripts/omnivoice-qc-sample.sh --voice <voice_id>
```

Generated QC audio is written outside the repo by default. Score it with
`docs/omnivoice-qc.md`.

Run the smoke test only after configuring a real backend command, Studio URL,
or opt-in CLI backend:

```bash
HERMES_OMNIVOICE_COMMAND_JSON='[...]' scripts/test-omnivoice-tts.sh
```

Without a backend, the smoke test exits `77` to mark the integration as skipped
rather than failed.

The Python unittest integration case is also opt-in so normal test runs do not
download or load model weights:

```bash
PATH="$HOME/.cache/hermes/omnivoice-python/bin:$PATH" \
HERMES_OMNIVOICE_RUN_REAL_TEST=1 \
HERMES_OMNIVOICE_AUTO_CLI=1 \
HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice \
python3 -m unittest tests.test_omnivoice_tts.OmniVoiceIntegrationTests -v
```

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
`--force` is set, rejects empty `--allowed-use` values before network access,
rejects non-positive `--timeout` values before local writes or network access,
quotes allowed-use values in `voice.yaml`, and downloaded reference audio must
be a valid WAV.

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

Preview `--speed` and `--timeout` overrides are validated before the helper
launches the wrapper subprocess. Preview output paths preserve the final path
component so the wrapper can replace an existing output symlink instead of
following it.

Print a Hermes command-provider config example:

```bash
python scripts/hermes-omnivoice-voices.py config narrator
```

Use `--voices-dir` before `config` when printing config for a custom registry;
the generated command includes the same registry path. The voice must validate
successfully before config is printed.
