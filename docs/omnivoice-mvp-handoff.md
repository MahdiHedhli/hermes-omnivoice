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
- A concise weekend summary that is included in the install manifest for
  operator handoff.

Static MVP acceptance currently passes without a real model backend. Live
backend acceptance now passes on this machine when the prepared OmniVoice
Python adapter command is exported; the default shell remains unconfigured so
it does not claim backend readiness by accident.
Acceptance also reports package-only handoff files separately, so the copied
`scripts/omnivoice-acceptance.py` remains useful after a default install into a
real Hermes checkout.

## Current Acceptance Snapshot

As of 2026-05-31 14:30 America/New_York on branch
`feature/omnivoice-custom-voices`:

- `scripts/validate-omnivoice-bridge.sh` passes with 132 tests and 1 expected
  opt-in real-backend skip.
- `scripts/validate-omnivoice-bridge.sh` now builds its fake-backend smoke
  command from the configured `PYTHON_BIN`, so alternate interpreter runs do
  not silently fall back to `python3` for the wrapper smoke path.
- Shipped README, docs, examples, and scripts are regression-checked for the
  correct OmniVoice-Studio product name in handoff copy.
- Command-template configuration errors are now covered: unknown placeholders,
  unsupported placeholder access, and malformed brace syntax in
  `HERMES_OMNIVOICE_COMMAND_JSON` or
  `HERMES_OMNIVOICE_COMMAND` return wrapper config errors instead of raw Python
  exceptions.
- Runtime diagnostics now validate the same backend command-template
  placeholder contract, so malformed command configuration does not count as
  `real_backend_ready`.
- The wrapper and runtime diagnostics now expose and test the same placeholder
  allowlist, so future command-template changes cannot silently drift between
  synthesis and readiness checks.
- `scripts/omnivoice-acceptance.py` now catches runtime/source diagnostic
  failures and exits with a concise `omnivoice-acceptance:` error instead of a
  traceback when operator runtime config is malformed.
- `scripts/hermes-omnivoice-voices.py` now catches local filesystem and
  subprocess failures at the CLI boundary and exits with a concise
  `hermes-omnivoice-voices:` error instead of a traceback.
- `scripts/import-omnivoice-studio-voice.py` now validates empty
  `--allowed-use` values before network access and quotes imported
  `allowed_uses` values in YAML, matching the local voice creator's safer
  metadata-writing path.
- `scripts/hermes-omnivoice-tts.py` now redacts common credential-shaped values
  from command backend stderr, Studio API failure detail, and final wrapper
  errors before printing failures while preserving useful failure context.
- `scripts/omnivoice-acceptance.py` reports `mvp_static_ready: true`,
  `real_backend_ready: false`, and `hermes_source_ready: false` in the default
  shell environment because no backend command is exported there.
- `scripts/omnivoice-acceptance.py --require-real-backend` passes when
  `HERMES_OMNIVOICE_COMMAND_JSON` is set to the prepared Python adapter command
  and `HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice`.
- `scripts/test-omnivoice-tts.sh` generated a valid temporary WAV through that
  adapter path using the required smoke text.
- `scripts/find-hermes-source.py` still finds only this bridge repo under the
  searched Hermes/Coding roots, so native-provider work remains deferred. Use
  the bounded helper or an explicit candidate root rather than a broad workspace
  grep; generic `voice`, `tts`, and `provider` matches are too noisy to prove a
  real Hermes Agent checkout.
- `scripts/check-omnivoice-runtime.py` reports no default Studio URL, backend
  command, or auto CLI; it now sees one local designed profile under
  `~/.hermes/voices/omnivoice`.
- If a backend command is exported, `scripts/check-omnivoice-runtime.py` now
  rejects unknown placeholders, unsupported placeholder access, and malformed
  brace syntax before reporting the command as configured.
- `scripts/setup-omnivoice-python-env.py --check-only --json` reports the
  isolated venv at `~/.cache/hermes/omnivoice-python` is ready, including
  `omnivoice`, `torch`, `soundfile`, and `omnivoice-infer`.
- The fastest proven real-synthesis path is still the isolated Python
  adapter or explicit CLI path plus a consented local voice profile, not a
  running Studio container.
- Installer `.gitignore` handling is dry-run-first by default; when
  `--update-gitignore` is explicitly requested, it appends the managed safety
  block or refreshes an existing managed block while preserving surrounding
  user-owned rules. Human installer output uses readable review, append, and
  refresh messages; JSON output retains exact action codes for automation.
- The standard validator now calls `scripts/check-omnivoice-artifacts.py` so
  generated audio, model files, top-level artifact/cache/local voice or sample
  directories, `.env*`, and local voice selection state fail validation before
  commit.
- Test coverage now checks that top-level artifact directories forbidden by the
  repo scanner also have matching repo and installer `.gitignore` coverage.
- Package-only validation helpers, including the artifact checker and validator,
  are intentionally excluded from the default runtime install payload.
- Human acceptance output now marks missing package-only extras as
  `INCOMPLETE`, not as default-install blockers; strict package validation still
  uses `--require-package-files`.
- Strict package-file acceptance is covered after a default runtime install: the
  copied acceptance script still exits failed with `--require-package-files`
  when package-only helpers are absent.
- Acceptance required-file coverage is pinned to the default installer runtime
  payload by file membership, preventing silent manifest drift between local
  validation and real-checkout installs.
- Default installer copies preserve executable modes for runtime scripts, so
  direct invocations such as `scripts/test-omnivoice-tts.sh` continue to work in
  an installed checkout.
- Installed smoke testing remains fail-closed by default: a copied
  `scripts/test-omnivoice-tts.sh` exits 77 until Studio, command JSON, command
  string, or explicit auto CLI mode is configured.
- Installed smoke testing also passes when `HERMES_OMNIVOICE_COMMAND_JSON`
  points at an explicit local backend, proving the default install can exercise
  the wrapper contract without package-only test helpers.
- Installed smoke testing now also proves the copied wrapper gives command
  backends a private `.hermes-output.wav.*` temporary file with `0600`
  permissions, rather than the final `hermes-output.wav` path.
- Installed `--with-examples` voice templates validate through the copied voice
  helper: `narrator` is ready as a designed voice, while `marvin` remains
  invalid until a user supplies the consented `ref.wav` reference sample.
- Generated command-provider config from `scripts/hermes-omnivoice-voices.py
  config` now includes the configured `--voices-dir` path and shell-quotes
  static paths, so custom registries do not silently fall back to the default
  user registry.
- Installed `--with-examples` config generation is covered after a real target
  copy: the copied voice helper emits the copied wrapper path and target
  example registry path rather than source-repo paths.
- `scripts/hermes-omnivoice-voices.py config` now validates the requested voice
  before printing Hermes config, and the shipped Hermes TTS config example
  defaults to the ready `narrator` design profile instead of the clone template
  that intentionally lacks reference audio.
- Generated and static command-provider examples now include explicit
  `speed: 1.0` alongside the selected voice, matching the wrapper's speed
  argument and the documented Hermes config surface.
- Generated and static command-provider examples are regression-pinned for
  `output_format: wav`, `timeout: 180`, `voice_compatible: true`, and
  `max_text_length: 2000`, and generated config honors explicit timeout and
  max text length overrides.
- `scripts/hermes-omnivoice-voices.py current` revalidates the selected profile
  before reporting it, so stale local selection state cannot silently stand in
  for current consent/profile readiness. It also rejects malformed local
  selection JSON, including non-object payloads and non-OmniVoice provider
  values, instead of treating it as a valid registry pointer. Reported speed
  and voice registry path come from the revalidated profile context rather than
  stale selection metadata.
- `scripts/hermes-omnivoice-voices.py set` now writes selection metadata through
  a private `0600` same-directory temporary file and atomic replace, replacing a
  destination symlink instead of following it. Failed temp writes are cleaned up
  before the error is returned.
- `scripts/create-omnivoice-voice.py` and
  `scripts/import-omnivoice-studio-voice.py` now create local voice profile
  directories with `0700` permissions and write `voice.yaml` plus copied or
  imported `ref.wav` material with `0600` permissions. Forced rewrites use
  same-directory temporary files and replace existing material symlinks instead
  of following them.
- `scripts/hermes-omnivoice-tts.py` removes an existing output symlink before
  synthesis, passes command backends a private same-directory temp output path,
  makes successful generated output audio `0600`, and validates command or
  Studio response audio before atomically replacing the requested output.
- Command templates fail closed on unknown placeholders, unsupported
  placeholder access, or malformed brace syntax before backend startup; literal
  braces should be written as `{{` and `}}`.

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
Review the `.gitignore` status in the installer report. Add
`--update-gitignore` when you want the installer to append the managed
OmniVoice local-artifact block to the target checkout or refresh an existing
managed block to the current pattern list.

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
