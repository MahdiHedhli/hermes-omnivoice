# OmniVoice Weekend Summary

Status as of 2026-06-01 01:30 America/New_York on branch
`feature/omnivoice-custom-voices`.

## Delivered MVP

- Hermes command-provider wrapper: `scripts/hermes-omnivoice-tts.py`.
- Local voice registry with consent gates under
  `~/.hermes/voices/omnivoice/<voice_id>/voice.yaml`.
- Designed and cloned voice creation helper with WAV validation for cloned
  reference samples.
- OmniVoice-Studio profile importer using loopback-only HTTP APIs by default.
- Direct OmniVoice Python API adapter and opt-in official CLI support.
- Runtime diagnostics, acceptance checks, install helper, voice helper CLI, and
  deterministic validation suite.
- Studio Docker helper with loopback Compose validation, bounded subprocesses,
  no-pull image preflight, and pre-Compose image pull handling.

## Proven Local Path

The prepared local path is the Python adapter, not Studio Docker:

```bash
python scripts/setup-omnivoice-python-env.py --check-only --require-ready
eval "$(python scripts/setup-omnivoice-python-env.py --check-only --shell)"
python scripts/omnivoice-acceptance.py --require-real-backend
scripts/test-omnivoice-tts.sh
```

This path uses the isolated venv at `~/.cache/hermes/omnivoice-python` and the
local designed profile `heartbeat_narrator` under
`~/.hermes/voices/omnivoice`. The profile is not cloned from a user voice
sample and contains explicit confirmed consent metadata.

## Latest Validation

- `scripts/validate-omnivoice-bridge.sh`: PASS, 181 tests with 1 expected
  opt-in real-backend skip.
- Studio import URL preflight: PASS. Non-loopback and credential-bearing
  Studio URLs are rejected before local registry directory creation or Studio
  network access.
- Consent metadata validation: PASS. Voice profile validation now requires
  non-empty `consent.source` and at least one non-empty
  `consent.allowed_uses` entry, and the voice creation helper rejects empty
  `--consent-source` values before writing profile material.
- Setup and auto-CLI model validation: PASS. Empty setup `--model` and
  `--package` values fail before export or pip command planning, and wrapper
  auto-CLI mode rejects an empty model before command construction.
- Python adapter required-field validation: PASS. Empty `--model`, `--device`,
  and `--dtype` values are rejected before loading the OmniVoice Python
  backend.
- Python adapter backend sample-rate handling: PASS. Invalid sample rates
  reported by the backend become concise adapter errors instead of raw
  conversion exceptions.
- Python adapter bounds validation: PASS. Non-finite or non-positive
  `--speed` values and non-positive `--sample-rate` values are rejected before
  loading the OmniVoice Python backend.
- Studio helper port validation: PASS. Invalid published `--port` values are
  rejected before Docker can run.
- Validator interpreter alignment: PASS. The fake-backend smoke command now
  uses the configured `PYTHON_BIN` instead of hardcoded `python3`, so full
  validation runs stay on the selected interpreter.
- Product-name terminology guard: PASS. Shipped README, docs, examples, and
  scripts are scanned so handoff copy keeps the OmniVoice-Studio name.
- Command-template error handling: PASS. Unknown placeholders, unsupported
  placeholder access, and malformed brace syntax in
  `HERMES_OMNIVOICE_COMMAND_JSON` or
  `HERMES_OMNIVOICE_COMMAND` now return wrapper config errors instead of raw
  Python exceptions.
- Runtime command diagnostics: PASS. `scripts/check-omnivoice-runtime.py`
  validates the same command-template placeholder contract before reporting a
  backend command as configured, keeping acceptance readiness fail-closed.
- Runtime timeout validation: PASS. `scripts/check-omnivoice-runtime.py`
  rejects non-positive `--timeout` values before any Studio URL probe.
- Acceptance runtime timeout handling: PASS. Invalid acceptance `--timeout`
  values produce concise `omnivoice-acceptance:` errors instead of tracebacks.
- Placeholder contract drift guard: PASS. Runtime diagnostics and the synthesis
  wrapper now expose the same placeholder allowlist and the test suite pins
  them together.
- Acceptance diagnostic failure handling: PASS. Malformed runtime command
  configuration now makes `scripts/omnivoice-acceptance.py` exit cleanly with a
  concise error instead of a traceback.
- Source discovery bounds validation: PASS. `scripts/find-hermes-source.py`
  and acceptance source discovery reject non-positive scan timeouts,
  candidate/file limits, and negative max-depth values before walking the
  filesystem, keeping automation bounded.
- Voice helper diagnostic failure handling: PASS. Local filesystem and
  subprocess failures in `scripts/hermes-omnivoice-voices.py` now exit with a
  concise helper-prefixed error instead of a traceback.
- Preview input validation: PASS. `scripts/hermes-omnivoice-voices.py preview`
  rejects non-positive `--timeout` and non-positive or non-finite `--speed`
  overrides before spawning the wrapper subprocess.
- Studio helper health timeout validation: PASS.
  `scripts/omnivoice-studio-local.py check` rejects non-positive health
  `--timeout` values while preserving `--command-timeout 0` as an explicit
  unbounded manual escape hatch for Docker/Git commands.
- Studio helper command-timeout validation: PASS. Negative `--command-timeout`
  values are rejected before Docker or Git commands can run.
- Studio helper log-tail validation: PASS. Negative `logs --tail` values are
  rejected before Docker can run.
- Studio import allowed-use metadata handling: PASS. Empty `--allowed-use`
  values are rejected before network access, and imported allowed-use values are
  quoted in `voice.yaml` so CLI input cannot reshape consent metadata.
- Voice creation speed validation: PASS. Non-finite or non-positive
  `--speed` values are rejected before profile directory creation or clone
  reference-audio copy.
- Voice creation metadata validation: PASS. Empty `--allowed-use` values are
  rejected before profile directory creation or clone reference-audio copy.
- Studio import timeout validation: PASS. Non-positive importer `--timeout`
  values are rejected before local voice directory creation or Studio network
  access.
- Wrapper failure redaction: PASS. Command backend stderr, Studio API failure
  detail, and final wrapper errors keep useful context but redact common
  credential-shaped values before printing.
- Studio URL userinfo rejection: PASS. The wrapper, importer, and runtime
  diagnostics reject userinfo in Studio URLs so credential-bearing URLs do not
  enter local config, diagnostics, or logs.
- Wrapper speed/timeout validation: PASS. The TTS wrapper rejects non-finite or
  non-positive speed and non-positive timeout values before backend or Studio
  startup.
- Wrapper max text length validation: PASS. Generated and static
  command-provider examples pass `--max-chars` alongside Hermes
  `max_text_length`, and oversized input files fail before backend startup.
- Generated config bounds validation: PASS. The voice helper refuses
  non-positive `--timeout` and `--max-text-length` values before emitting
  command-provider YAML.
- `python scripts/omnivoice-acceptance.py --require-real-backend` after
  evaluating `setup-omnivoice-python-env.py --check-only --shell`: PASS.
- `scripts/test-omnivoice-tts.sh` with the generated adapter exports: PASS,
  generated a valid temporary WAV from "Hermes custom voice synthesis test."
- Installer `.gitignore` safety coverage: PASS. Default dry-runs report missing
  local-artifact coverage without writing, and `--update-gitignore` appends or
  refreshes the managed block while preserving user-owned rules around it. The
  non-JSON installer output now uses human-readable review, append, and refresh
  messages instead of raw action codes.
- Repo artifact scan: PASS, no generated audio, model weights, top-level
  artifact/cache/local voice or sample directories, env files, or local voice
  selection state found in the repo. This check is now enforced by
  `scripts/check-omnivoice-artifacts.py` through the standard validator.
- Repo/installer ignore alignment: PASS. The forbidden top-level artifact
  directory set now has matching repo and installer `.gitignore` coverage.
- Default installer payload boundary: PASS. Package-only validation helpers
  such as `scripts/check-omnivoice-artifacts.py` are not copied into a real
  Hermes checkout by default.
- Installed-checkout acceptance clarity: PASS. Human output now labels missing
  package-only extras as `INCOMPLETE` rather than a default-install blocker.
- Strict installed-checkout package gate: PASS. The copied acceptance script
  still exits failed with `--require-package-files` after a default runtime
  install omits package-only helpers.
- Acceptance/installer manifest drift guard: PASS. The bridge required-file
  set now must match the default installer runtime payload.
- Installer executable-mode preservation: PASS. Runtime scripts remain directly
  executable after a default install into a target checkout.
- Installed smoke-skip behavior: PASS. A copied smoke script exits 77 without a
  configured backend instead of attempting synthesis.
- Installed smoke configured-backend behavior: PASS. A copied smoke script can
  generate a temporary WAV through an explicit local command backend.
- Installed smoke output isolation: PASS. A copied smoke script now proves the
  installed wrapper gives command backends a private `.hermes-output.wav.*`
  temporary file with `0600` permissions, not the final output path.
- Installed example voice handling: PASS. A copied voice helper validates the
  installed `narrator` design template as ready and keeps the `marvin` clone
  template invalid until a user supplies the consented `ref.wav` sample.
- Config generation for custom registries: PASS. The voice helper emits
  `--voices-dir` in generated command-provider config and shell-quotes static
  paths.
- Installed config generation: PASS. After `--with-examples`, the copied voice
  helper emits the copied wrapper path and target example registry path.
- Config consent/profile gate: PASS. The voice helper refuses missing or invalid
  profiles before printing config, and the static Hermes TTS example uses the
  ready `narrator` design profile.
- Config speed field: PASS. Generated and static command-provider examples now
  include explicit `speed: 1.0` for the selected voice.
- Command-provider config surface: PASS. Generated and static examples are
  pinned for `output_format: wav`, `timeout: 180`, `voice_compatible: true`,
  `max_text_length: 2000`, and wrapper `--max-chars 2000`; generated config
  honors explicit valid timeout and max-text-length overrides and refuses
  non-positive generated-config bounds.
- Selection-state validation: PASS. `scripts/hermes-omnivoice-voices.py
  current` revalidates the selected profile and fails closed if the selected
  voice no longer has valid consent/profile inputs or malformed registry
  pointer metadata, including non-object selection JSON and non-OmniVoice
  provider values. It reports profile-derived speed and registry path instead
  of trusting stale selection metadata.
- Selection-state writes: PASS. `scripts/hermes-omnivoice-voices.py set`
  writes the local selection file with `0600` permissions through a
  same-directory temporary file and atomic replace, and replaces destination
  symlinks instead of following them. Failed temp writes are cleaned up before
  the error is returned.
- Voice profile writes: PASS. Create/import helpers write local profile
  directories with `0700` permissions and `voice.yaml` plus copied or imported
  `ref.wav` material with `0600` permissions. Forced rewrites replace existing
  material symlinks instead of following them.
- Generated audio writes: PASS. The wrapper removes an existing output symlink
  before backend synthesis, passes command backends a private temporary output
  path, leaves successful output audio with `0600` permissions, and validates
  command or Studio response audio before atomic replacement.
- Command templates fail closed on unknown placeholders, unsupported
  placeholder access, or malformed brace syntax before backend startup; literal
  braces should be escaped as `{{` and `}}`.

## Remaining Blockers

- The actual Hermes Agent source is not present locally; source discovery sees
  only this bridge repo, so native provider wiring and in-app `/voice` commands
  remain deferred.
- The default shell does not claim real-backend readiness until the generated
  adapter exports are applied.
- A live OmniVoice-Studio service is still blocked on this Mac: the published
  image lacks a `linux/arm64/v8` manifest, and source build exceeded the
  bounded heartbeat window while exporting the Docker image.

## Security Notes

- No voice samples, generated audio, model files, caches, secrets, local config,
  or local voice selection state are committed.
- Cloned voices require `consent.status: confirmed`, non-empty
  `consent.source`, non-empty `consent.allowed_uses`, `ref_audio`, `ref_text`,
  and a readable WAV reference file.
- Created/imported local voice profile files are private by default and should
  stay under `~/.hermes/voices/omnivoice`, outside the repo.
- Generated output audio is private by default and should stay in Hermes/temp
  output locations, not in the repo.
- Non-loopback Studio URLs are refused by default.
- Studio URLs containing userinfo are refused. The importer rejects invalid
  Studio URL policy before local registry directory creation.
- Non-finite or non-positive speed values and non-positive wrapper timeouts are
  refused before backend startup.
- Oversized text input is refused by the wrapper before backend startup.
- The fake backend is a contract fixture only and is not real synthesis
  evidence.

## Next Steps

1. Locate or clone the real Hermes Agent source and run
   `python scripts/find-hermes-source.py --root /path/to/hermes --json`.
   Prefer explicit candidate roots or the bounded helper over broad content grep
   across `~/Documents/Coding`; generic terms such as `provider`, `voice`, and
   `tts` create noisy false positives in unrelated repositories.
2. Dry-run the bridge installer against that checkout:
   `python scripts/install-hermes-omnivoice-bridge.py --target-root /path/to/hermes --dry-run`.
   Review the reported `.gitignore` coverage before adding
   `--update-gitignore` to append the managed local-artifact ignore block.
   If the managed block already exists, `--update-gitignore` refreshes it in
   place to the current safety patterns without removing surrounding user rules.
3. Wire Hermes to the command-provider config first; defer a native provider
   until the real TTS schema is inspected.
4. If Studio integration is still required, run a longer supervised source
   build or use a compatible loopback-only Studio image, then test the importer
   against the live local service.
