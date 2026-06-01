# OmniVoice Weekend Summary

Status as of 2026-06-01 16:30 America/New_York on branch
`feature/omnivoice-custom-voices`.

## Delivered MVP

- Hermes command-provider wrapper: `scripts/hermes-omnivoice-tts.py`.
- Local voice registry with consent gates under
  `~/.hermes/voices/omnivoice/<voice_id>/voice.yaml`.
- Designed and cloned voice creation helper with WAV validation and symlink
  rejection for cloned reference samples.
- OmniVoice-Studio profile importer using loopback-only HTTP APIs by default.
- Direct OmniVoice Python API adapter and opt-in official CLI support.
- Runtime diagnostics, acceptance checks, install helper, voice helper CLI, and
  deterministic validation suite.
- Studio Docker helper with loopback Compose validation, bounded subprocesses,
  no-pull image preflight, and pre-Compose image pull handling.

## Proven Local Path

The prepared local package path is the Python adapter, not Studio Docker:

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

The bridge has also been deployed to the homelab Hermes host:

- Runtime install:
  `/opt/hermes-local-tts/omnivoice-bridge`.
- Isolated backend runtime:
  `/home/claude/.cache/hermes/omnivoice-python`.
- Voice registry:
  `/home/claude/.hermes/voices/omnivoice`.
- Validation voice:
  `homelab_narrator`, a designed voice with confirmed consent metadata and no
  cloned reference sample.
- Live Hermes config:
  `tts.providers.omnivoice` points at the installed wrapper and packaged Python
  adapter with `timeout: 600`, `output_format: wav`,
  `voice_compatible: true`, `max_text_length: 2000`, and
  `voice: homelab_narrator`.
- Active Hermes provider remains `xtts-v2`; the OmniVoice provider is staged
  and validated without changing default production TTS behavior.

## Latest Validation

- Homelab live Hermes command-provider smoke: PASS. Hermes'
  `tools.tts_tool.text_to_speech_tool` was run with provider `omnivoice`,
  called the installed wrapper and real OmniVoice Python backend, and returned
  a valid Opus file through Hermes' existing voice-compatible conversion path.
- Homelab installed acceptance:
  `scripts/omnivoice-acceptance.py --require-real-backend` PASS for static MVP
  readiness, real backend readiness, and Hermes source readiness.
- Homelab installed smoke script: PASS. `scripts/test-omnivoice-tts.sh`
  generated a valid temporary WAV from "Hermes custom voice synthesis test."
  after the real model runtime was installed.
- Homelab disk after backend install: `/` had about 37 GB free; the isolated
  OmniVoice venv used about 5.5 GB and the Hugging Face cache used about
  6.1 GB.
- Homelab source checkout state: unchanged by the bridge install. The Hermes
  source checkout already had unrelated modified and untracked files, so bridge
  files were installed outside it.
- `scripts/validate-omnivoice-bridge.sh`: PASS, 206 tests with 1 expected
  opt-in real-backend skip.
- Runtime voice readiness guard: PASS. Runtime diagnostics reuse the wrapper
  voice-profile validator so acceptance does not count unsafe registry aliases,
  cloned `ref_audio` symlinks, missing clone audio, or invalid consent metadata
  as voice-ready.
- Runtime registry symlink guard: PASS. Symlinked voice registry roots, voice
  directories, `voice.yaml` files, and cloned `ref_audio` files are rejected
  before synthesis uses local registry material.
- Wrapper WAV output guard: PASS. Non-`.wav` output paths are rejected before
  command backend execution or Studio API network access.
- Studio runtime profile-list shape: PASS. Runtime diagnostics report malformed
  Studio `/profiles` payloads and non-object profile-list entries as `invalid`,
  so acceptance does not treat them as backend-ready.
- Studio profile payload shape: PASS. Non-object Studio profile JSON is
  rejected before profile audio is requested or local voice material is
  written.
- Voice directory symlink guard: PASS. Create/import helpers refuse symlinked
  registry roots and final voice-directory symlinks before local profile
  material writes, while forced rewrites still replace `voice.yaml` and
  `ref.wav` symlinks instead of following them.
- Clone reference input symlink guard: PASS. The local voice creation helper
  rejects symlinked clone `--ref-audio` source paths before copying reference
  audio into the local registry.
- Studio import write staging: PASS. Existing occupied target directories are
  still rejected before network access, while failed Studio fetches and invalid
  design payloads no longer create empty target voice directories.
- Studio import profile validation: PASS. Empty Studio profile IDs fail before
  local writes or network access, and downloaded clone profiles must include
  `ref_text` before imported `ref.wav` or `voice.yaml` material is written.
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
  of trusting stale selection metadata, and refuses symlinked selection files
  before reading.
- Selection-state writes: PASS. `scripts/hermes-omnivoice-voices.py set`
  writes the local selection file with `0600` permissions through a
  same-directory temporary file and atomic replace, and replaces destination
  symlinks instead of following them. Failed temp writes are cleaned up before
  the error is returned.
- Voice helper registry listing: PASS. `scripts/hermes-omnivoice-voices.py
  list` refuses symlinked voice registry roots before enumerating profile names.
- Voice profile writes: PASS. Create/import helpers write local profile
  directories with `0700` permissions and `voice.yaml` plus copied or imported
  `ref.wav` material with `0600` permissions. Forced rewrites replace existing
  material symlinks instead of following them, and symlinked registry roots
  plus final voice-directory symlinks are refused before writes.
- Generated audio writes: PASS. The wrapper removes an existing output symlink
  before backend synthesis, passes command backends a private temporary output
  path, leaves successful output audio with `0600` permissions, and validates
  command or Studio response audio before atomic replacement.
- Preview output symlink guard: PASS. The voice helper preview command
  preserves the final output path when invoking the wrapper, so preview output
  symlinks are replaced instead of followed.
- Text input symlink guard: PASS. The wrapper rejects symlinked `--text-file`
  inputs before reading text or starting a backend, so the Hermes text temp
  path cannot alias another local file.
- Command templates fail closed on unknown placeholders, unsupported
  placeholder access, or malformed brace syntax before backend startup; literal
  braces should be escaped as `{{` and `}}`.

## Remaining Blockers

- The actual Hermes Agent source is not present in this local bridge checkout;
  source discovery sees only this bridge repo here. Homelab Hermes source was
  validated remotely, but native provider wiring and in-app `/voice` commands
  remain deferred to avoid touching an unrelated dirty source tree.
- The default shell does not claim real-backend readiness until the generated
  adapter exports are applied.
- A live OmniVoice-Studio service is still not running on the homelab Hermes
  host. The proven path is direct OmniVoice Python backend synthesis through
  the command-provider wrapper and local Hermes voice registry.

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
- Symlinked text input files are refused before the wrapper reads text or
  starts a backend.
- The fake backend is a contract fixture only and is not real synthesis
  evidence.

## Next Steps

1. For an operator trial, switch live Hermes `tts.provider` from `xtts-v2` to
   `omnivoice`, run a short TTS request, and switch back if latency or quality
   is not acceptable.
2. Keep the command-provider MVP as the rollout path until the dirty homelab
   Hermes source tree can be isolated or a clean checkout is available for
   native-provider work.
3. Add a small user-facing voice-selection workflow if Hermes has a safe
   command/plugin surface for `/voice list`, `/voice set`, `/voice preview`,
   and `/voice info`.
4. If Studio integration is still required, run a loopback-only Studio service
   on the target host and test import/export through HTTP APIs rather than
   direct database coupling.
