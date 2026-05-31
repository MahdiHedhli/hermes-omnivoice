# Hermes OmniVoice Integration Heartbeat

## Current status

Initial heartbeat started against an empty scheduled workspace. The repo now has
a command-provider MVP foundation, a localhost-only OmniVoice-Studio API bridge,
a Studio profile importer, and deterministic tests proving the command wrapper
writes valid WAV output through a local backend contract. It also includes a
standalone voice helper for listing, inspecting, previewing, and printing Hermes
command-provider config for local voices. A single validation script now reruns
the full local bridge contract, including a mocked localhost Studio `/generate`
path. Top-level handoff docs, an MVP package handoff, and example configs are
now present. The optional direct OmniVoice CLI path targets the upstream
`omnivoice-infer` executable and is gated behind `HERMES_OMNIVOICE_AUTO_CLI=1`
to avoid surprise model downloads. A packaged Python API adapter can also call
`OmniVoice.from_pretrained` through `HERMES_OMNIVOICE_COMMAND_JSON` when the
local `omnivoice` package is installed. A dry-run/check-first environment helper
now plans, installs, and inspects an isolated OmniVoice Python venv outside the
repo, prefers supported Python 3.10-3.13 interpreters over too-new local
defaults, and has been used successfully with `/opt/homebrew/bin/python3.11`.
The real upstream `omnivoice-infer` path has now generated a valid temporary
WAV through `scripts/test-omnivoice-tts.sh`. English designed voices are also
validated against OmniVoice's supported design tag set before model startup.
The packaged Python API adapter now imports the installed package's actual
`omnivoice.models.omnivoice.OmniVoice` class and has generated a valid
temporary WAV through the same command-provider wrapper path. The local
OmniVoice-Studio Docker helper validates loopback-only Compose config and now
bounds Docker/Git subprocesses so a stalled pull or build cannot block a
heartbeat indefinitely. The unittest integration smoke is now a real opt-in
test: normal runs skip without model work, while
`HERMES_OMNIVOICE_RUN_REAL_TEST=1` exercises actual synthesis. A bounded
read-only Hermes source discovery helper now scores candidate checkouts without
reading sensitive-named files and correctly marks this bridge repo separately
from an actual Hermes Agent source tree. The acceptance summary now reports
static MVP readiness, real backend readiness, and Hermes source readiness as
separate gates, with opt-in strict flags for the runtime and source checks.
Source discovery now retains already-discovered candidates through a small
bounded inspection grace window when a later broad root consumes the scan
timeout, so acceptance evidence stays useful without unbounded filesystem
traversal. The local Studio helper now preflights no-pull/no-build startup
against local Docker image availability and fails before creating Compose
resources when the image is missing. It also performs bounded image pulls
before Compose startup for no-build pull-enabled runs, so registry or platform
failures do not create transient Compose resources.
The source-build fallback for OmniVoice-Studio reached Docker image export after
large runtime dependency downloads, but exceeded a 300 second heartbeat window;
post-timeout Docker checks showed no matching Studio containers, volumes,
networks, or images left behind.
The MVP handoff now records the current acceptance snapshot and distinguishes
the prepared isolated OmniVoice Python venv from the unconfigured default shell
runtime.
A local designed profile named `heartbeat_narrator` now exists under
`~/.hermes/voices/omnivoice`, and strict real-backend acceptance passes when the
prepared Python adapter command is exported.
The Python environment helper can now print shell-safe exports for the prepared
adapter command with `--check-only --shell`.
`docs/omnivoice-weekend-summary.md` now captures the delivered MVP, proven
local backend path, validation state, blockers, security notes, and next steps.
The artifact checker now also rejects top-level cache, model, and local voice
artifact directories while preserving safe nested example voice templates.
Acceptance output keeps package-only handoff files visible without treating
their expected default-install absence as a blocker, and strict package-file
validation still fails when explicitly required.
Acceptance tests now also pin the bridge required-file membership to the
installer runtime payload so handoff manifests cannot drift silently.
Installer tests now prove runtime scripts remain executable after a real target
copy, preserving operator-facing direct invocation in installed checkouts.
Installed smoke-script tests now also prove a default target checkout exits with
the documented 77 skip when no backend is configured.
Installed smoke-script tests now cover the paired success path with an explicit
local command backend, without depending on cloud services or a real model.
Installed example voice handling now validates through the copied voice helper:
the designed `narrator` template is ready, while the cloned `marvin` template
stays invalid until a user supplies the consented `ref.wav`.
Generated Hermes command-provider config now includes the selected
`--voices-dir` path and shell-quotes static paths, so custom voice registries do
not silently fall back to the default user registry.
Top-level local sample directories such as `samples/`, `voice-samples/`, and
`reference-audio/` are now covered by both the repo artifact checker and the
installer-managed `.gitignore` safety block.
The artifact checker denylist, repo `.gitignore`, and installer-managed
`.gitignore` safety block now have regression coverage to prevent top-level
artifact-directory drift.
Installed-checkout human acceptance output now labels missing package-only
extras as `INCOMPLETE`, while strict package validation remains available with
`--require-package-files`.

## Previous heartbeat

- Time: 2026-05-29 22:00 America/New_York
- Completed:
  - Confirmed the scheduled workspace was empty and not a git repo.
  - Initialized git on `feature/omnivoice-custom-voices`.
  - Added `.gitignore` coverage for generated audio, voice samples, local config,
    caches, and model files.
  - Added `scripts/hermes-omnivoice-tts.py` with local registry parsing, consent
    validation, clone/design profile checks, backend command execution, and WAV
    validation.
  - Added unit tests and a skipped integration test stub.
  - Added setup, bridge, integration-notes, and custom-voices docs.
- Commands run:
  - `pwd`
  - `git status --short --branch`
  - `rg --files ...`
  - `git remote -v`
  - `ls -la`
  - `find /Users/mhedhli/Documents/Coding/hermes -maxdepth 3 -type d -name .git -print`
  - `find /Users/mhedhli/Documents/Coding -maxdepth 4 -type d -iname '*hermes*' -print`
  - `python3 -c "import yaml; print(yaml.__version__)"`
  - `python3 --version`
  - `git init -b feature/omnivoice-custom-voices`
  - `mkdir -p docs scripts tests`
  - `chmod +x scripts/hermes-omnivoice-tts.py scripts/test-omnivoice-tts.sh`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py tests/test_omnivoice_tts.py`
  - `scripts/test-omnivoice-tts.sh`
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 6 tests run, 1 skipped
    integration backend test.
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/test-omnivoice-tts.sh`: SKIP with exit 77 because no real
    `HERMES_OMNIVOICE_COMMAND_JSON` or `HERMES_OMNIVOICE_COMMAND` backend is
    configured yet.
- Blockers:
  - The scheduled workspace did not contain Hermes Agent source or TTS docs, so
    native provider discovery cannot be completed from this checkout yet.
  - No real OmniVoice backend command is configured yet; synthesis smoke test is
    expected to skip until a backend adapter is available.
- Assumptions:
  - This directory should act as a standalone bridge/plugin repo until the real
    Hermes Agent source path is provided or found.
  - Command-provider integration is the safest MVP path because it avoids
    changing unknown Hermes internals.
- Next action:
  - Run unit tests, fix failures, make scripts executable, then commit the MVP
    foundation if clean.

## Previous heartbeat

- Time: 2026-05-29 22:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `e4eaad7`.
  - Cloned `debpalash/OmniVoice-Studio` to `/tmp/omnivoice-studio-src` for
    source inspection.
  - Confirmed Studio exposes FastAPI routes for `/profiles`,
    `/profiles/{profile_id}`, `/profiles/{profile_id}/audio`, `/generate`,
    `/v1/audio/voices`, and `/v1/audio/speech`.
  - Confirmed Docker Compose binds host port `3900` to `127.0.0.1` by default
    and warns that Studio has no built-in auth.
  - Added wrapper support for `HERMES_OMNIVOICE_STUDIO_URL` with loopback-only
    default enforcement.
  - Added `scripts/import-omnivoice-studio-voice.py` to import Studio profiles
    through the HTTP API into the Hermes registry, requiring
    `--confirm-consent`.
  - Updated docs with the Studio API findings and importer workflow.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -3`
  - `find . -maxdepth 3 -type f -not -path './.git/*' -print | sort`
  - `git clone --depth 1 https://github.com/debpalash/OmniVoice-Studio /tmp/omnivoice-studio-src`
  - `find /tmp/omnivoice-studio-src -maxdepth 3 -type f ...`
  - `rg -n "FastAPI|@app\\.|APIRouter|uvicorn|gradio|Flask|voice|clone|reference|ref_audio|instruct|export|sqlite|db|upload|tts|synth" /tmp/omnivoice-studio-src`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/main.py`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/services/tts_backend.py`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/api/routers/profiles.py`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/api/routers/generation.py`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/api/routers/openai_compat.py`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/core/db.py`
  - `sed -n ... /tmp/omnivoice-studio-src/backend/core/config.py`
  - `sed -n ... /tmp/omnivoice-studio-src/deploy/docker-compose.yml`
  - `chmod +x scripts/import-omnivoice-studio-voice.py`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py scripts/import-omnivoice-studio-voice.py tests/test_omnivoice_tts.py`
  - `scripts/test-omnivoice-tts.sh`
  - `scripts/import-omnivoice-studio-voice.py --help`
  - `git diff --check`
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 9 tests run, 1 skipped
    integration backend test.
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py scripts/import-omnivoice-studio-voice.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/test-omnivoice-tts.sh`: SKIP with exit 77 because no real Studio
    URL or backend command is configured.
  - `scripts/import-omnivoice-studio-voice.py --help`: PASS.
- Blockers:
  - No running OmniVoice-Studio instance or real OmniVoice backend is configured
    in this workspace, so synthesis is still not smoke-tested end to end.
  - Actual Hermes Agent source is still not present in this checkout, so native
    provider discovery remains deferred.
- Assumptions:
  - The safest Studio bridge is the HTTP API rather than SQLite reads.
  - Studio must remain loopback-only unless separately put behind auth.
- Next action:
  - Commit the Studio API/importer checkpoint, then look for a local Hermes
    Agent source path or installed config to verify the TTS command-provider
    schema.

## Previous heartbeat

- Time: 2026-05-29 23:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `825eaa9`.
  - Added `tests/fixtures/fake_omnivoice_backend.py`, a deterministic local
    backend that writes a valid short WAV for wrapper contract testing.
  - Added a happy-path wrapper test proving `HERMES_OMNIVOICE_COMMAND_JSON`
    produces a valid WAV.
  - Added importer tests for explicit consent, loopback-only Studio URLs, and
    wrapper-compatible registry YAML generation.
  - Verified `scripts/test-omnivoice-tts.sh` can pass with the fake backend and
    still skips cleanly when no backend is configured.
  - Added setup docs for using the fake backend as a local contract smoke test.
  - Ran a quick memory check for prior heartbeat context; it confirmed the
    schedule/name correction and did not identify a local Hermes source path.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -5`
  - `sed -n '1,260p' tests/test_omnivoice_tts.py`
  - `sed -n '1,260p' scripts/import-omnivoice-studio-voice.py`
  - `chmod +x tests/fixtures/fake_omnivoice_backend.py`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py scripts/import-omnivoice-studio-voice.py tests/test_omnivoice_tts.py tests/fixtures/fake_omnivoice_backend.py`
  - `HERMES_OMNIVOICE_COMMAND_JSON='[...]' scripts/test-omnivoice-tts.sh`
  - `scripts/test-omnivoice-tts.sh`
  - `rg -n "Hermes Agent|Hermes dashboard|Hermes Memory|hermes-agent|/opt/hermes|~/.hermes|omnivoice" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n '232,262p' /Users/mhedhli/.codex/memories/MEMORY.md`
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 13 tests run, 1 skipped
    real-backend integration test.
  - `python3 -m py_compile ...`: PASS.
  - Fake-backend smoke test: PASS, generated a valid temporary WAV.
  - Unconfigured smoke test: SKIP with exit 77.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present in this checkout, so native
    provider discovery remains deferred.
- Assumptions:
  - A deterministic fake backend is acceptable only for wrapper contract tests,
    not for claiming real OmniVoice synthesis support.
- Next action:
  - Commit the expanded test coverage checkpoint, then continue searching for a
    safe local Hermes Agent source/config path or build a first-class config
    handoff package around the command-provider MVP.

## Previous heartbeat

- Time: 2026-05-29 23:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `2d591a1`.
  - Added `scripts/hermes-omnivoice-voices.py` with `list`, `info`, `preview`,
    and `config` subcommands.
  - Added tests for listing ready/invalid profiles, printing command-provider
    YAML, and previewing a voice through the fake backend.
  - Updated docs to describe the helper as a stand-in for future Hermes
    `/voice list`, `/voice info`, `/voice preview`, and config-selection UX.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -5`
  - `sed -n '1,380p' scripts/hermes-omnivoice-tts.py`
  - `sed -n '1,320p' tests/test_omnivoice_tts.py`
  - `chmod +x scripts/hermes-omnivoice-voices.py`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py scripts/import-omnivoice-studio-voice.py scripts/hermes-omnivoice-voices.py tests/test_omnivoice_tts.py tests/fixtures/fake_omnivoice_backend.py`
  - `HERMES_OMNIVOICE_COMMAND_JSON='[...]' scripts/test-omnivoice-tts.sh`
  - `scripts/test-omnivoice-tts.sh`
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 16 tests run, 1 skipped
    real-backend integration test.
  - `python3 -m py_compile ...`: PASS.
  - Fake-backend smoke test: PASS, generated a valid temporary WAV.
  - Unconfigured smoke test: SKIP with exit 77.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present in this checkout, so native
    provider and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - A standalone voice helper is the safest useful approximation of Hermes voice
    UX until the real Hermes command/plugin layer is available.
- Next action:
  - Run final checks and commit the helper CLI checkpoint, then continue toward
    either real-backend smoke validation or locating the real Hermes source.

## Previous heartbeat

- Time: 2026-05-30 00:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `5ec67c7`.
  - Confirmed `/opt/hermes-agent/source` is not present on this Mac.
  - Confirmed no readable `~/.hermes` config files were present.
  - Searched local Hermes paths under `/Users/mhedhli/Documents/Coding/hermes`
    and found only this bridge repo.
  - Added `scripts/validate-omnivoice-bridge.sh` to rerun unit tests,
    compilation checks, fake-backend smoke, unconfigured smoke-skip behavior,
    secret-pattern scan, and `git diff --check`.
  - Updated setup and integration notes with the validation command and local
    source-discovery result.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `rg -n "Hermes Agent|Hermes dashboard|Hermes Memory|hermes-agent|/opt/hermes|~/.hermes|omnivoice" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `ls -la /opt /opt/hermes-agent /opt/hermes-agent/source`
  - `find "$HOME" -maxdepth 4 ... -iname '*hermes*'`
  - `find "$HOME/.hermes" -maxdepth 3 -type f -print`
  - `find /Users/mhedhli/Documents/Coding -maxdepth 4 -type d ...`
  - `rg -n "tts|text[-_ ]to[-_ ]speech|speech synthesis|voice_compatible|output_format|input_path|output_path|provider:.*command|type: command|Hermes" /Users/mhedhli/Documents/Coding/hermes /Users/mhedhli/.hermes`
  - `chmod +x scripts/validate-omnivoice-bridge.sh`
  - `scripts/validate-omnivoice-bridge.sh`
  - `git diff --check`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation script includes: 16 unit tests PASS with 1 real-backend
    integration skip, py_compile PASS, fake-backend smoke PASS, unconfigured
    smoke SKIP as expected, secret-pattern scan PASS, and `git diff --check`
    PASS.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Until real Hermes source appears, a deterministic validation script is the
    highest-value way to keep the bridge shippable and regression-safe.
- Next action:
  - Commit the validation-script checkpoint, then either start a loopback
    OmniVoice-Studio smoke attempt or prepare a packaging/readme handoff for the
    command-provider MVP.

## Previous heartbeat

- Time: 2026-05-30 00:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `e3c4bbc`.
  - Added a localhost mock OmniVoice-Studio `/generate` API test.
  - Verified the wrapper sends multipart form data including `profile_id` and
    text when `HERMES_OMNIVOICE_STUDIO_URL` is configured.
  - Verified the mocked Studio API path writes a valid WAV output.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -7`
  - `sed -n '1,380p' tests/test_omnivoice_tts.py`
  - `sed -n '1,20p' /Users/mhedhli/.codex/memories/MEMORY.md`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation script now includes 17 unit tests PASS with 1 real-backend
    integration skip, py_compile PASS, fake-backend smoke PASS, unconfigured
    smoke SKIP as expected, secret-pattern scan PASS, and `git diff --check`
    PASS.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Mock Studio API coverage is valuable for request/response contract safety,
    but it does not replace a real model-backed Studio smoke test.
- Next action:
  - Commit the Studio API contract test, then prepare a concise README/package
    handoff or attempt a real loopback Studio startup if runtime cost looks
    acceptable.

## Previous heartbeat

- Time: 2026-05-30 01:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `d79c91e`.
  - Added a top-level `README.md` with quick start, backend options, security
    posture, limits, and doc links.
  - Added `examples/hermes-tts-omnivoice.yaml` as a command-provider config
    template.
  - Added `examples/voices/marvin/voice.yaml` and
    `examples/voices/narrator/voice.yaml` registry templates.
  - Added tests that keep the design voice example valid and keep the clone
    example from passing without a real `ref.wav`, so committed user audio does
    not become normalized.
  - Narrowed `.gitignore` from broad `voices/` to root-only `/voices/` so safe
    examples are tracked while local voice material remains ignored.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `find . -maxdepth 3 -type f -not -path './.git/*' -print | sort`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `mkdir -p examples/voices/clone examples/voices/design`
  - `scripts/validate-omnivoice-bridge.sh`
  - `find examples -maxdepth 3 -type d -empty -print`
  - `find . -type d -name __pycache__ -print`
  - `rmdir examples/voices/design examples/voices/clone`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' \) -print`
  - `git diff --cached --stat`
  - `git add .`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS after staging.
  - Validation script now includes 19 unit tests PASS with 1 real-backend
    integration skip, py_compile PASS, fake-backend smoke PASS, unconfigured
    smoke SKIP as expected, secret-pattern scan PASS, and `git diff --check`
    PASS.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - A committed clone voice template should not include `ref.wav`; the missing
    reference audio is expected and tested.
- Next action:
  - Commit the README/examples handoff checkpoint, then consider a lightweight
    packaging/install script or a bounded real Studio startup probe.

## Previous heartbeat

- Time: 2026-05-30 01:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `488690a`.
  - Added `scripts/create-omnivoice-voice.py` for creating local design and
    clone registry profiles with explicit `--confirm-consent`.
  - Hardened voice directory resolution in the wrapper, Studio importer, and
    new creator so `.`/`..` voice IDs and symlink escapes cannot leave the
    configured voices root.
  - Added tests for the creator, dot-segment voice IDs, symlink escape
    rejection, and importer validation before network access.
  - Updated README and setup/custom-voice docs with the safe local creation
    workflow.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `find . -maxdepth 3 -type f -not -path './.git/*' -print | sort`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... scripts/hermes-omnivoice-tts.py`
  - `sed -n ... scripts/import-omnivoice-studio-voice.py`
  - `sed -n ... scripts/hermes-omnivoice-voices.py`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... README.md docs/omnivoice-setup.md docs/tts-custom-voices.md`
  - `chmod +x scripts/create-omnivoice-voice.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `git diff --stat`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 28 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Voice registry paths are a trust boundary; local symlink convenience is less
    important than preventing accidental writes or reads outside the configured
    voices root.
- Next action:
  - Commit the voice-creation and path-hardening checkpoint, then evaluate a
    bounded real Studio startup probe or a packaging/install helper.

## Previous heartbeat

- Time: 2026-05-30 02:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `716725d`.
  - Hardened clone profile validation so `ref_audio` must be a readable WAV
    before the wrapper uses it.
  - Hardened `scripts/create-omnivoice-voice.py` so cloned voice creation
    validates the reference WAV and refuses existing non-empty voice directories
    unless `--force` is set.
  - Hardened `scripts/import-omnivoice-studio-voice.py` so Studio imports refuse
    existing non-empty voice directories unless `--force` is set and validate
    downloaded reference audio as WAV before writing it.
  - Added tests for invalid WAV reference audio, no-overwrite behavior, and
    importer WAV validation.
  - Updated README and docs with the WAV and overwrite safety defaults.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... scripts/create-omnivoice-voice.py`
  - `sed -n ... scripts/import-omnivoice-studio-voice.py`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... docs/omnivoice-studio-bridge.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `git diff --stat`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 33 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Reference audio should be treated as registry input, not a passive asset;
    validating it before use avoids carrying malformed or unexpected media into
    backend calls.
- Next action:
  - Commit the reference-audio hardening checkpoint, then attempt a bounded
    runtime probe for local Studio dependencies or add an install helper.

## Previous heartbeat

- Time: 2026-05-30 02:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `0696315`.
  - Added `scripts/check-omnivoice-runtime.py`, a read-only diagnostic for
    local Studio reachability, configured backend command presence, OmniVoice
    CLI availability, and local registry profile count.
  - Kept the runtime check loopback-only for Studio by default and avoided
    printing configured backend command arguments.
  - Added tests for missing-runtime reporting, command argument redaction,
    remote Studio rejection, and loopback Studio `/profiles` reachability.
  - Updated README and setup/Studio docs with the diagnostic workflow.
  - Ran the diagnostic locally; current machine reports no Studio URL, no
    backend command, no `omnivoice` CLI, and no local voice registry yet.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -9`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `find . -maxdepth 3 -type f -not -path './.git/*' -print | sort`
  - `sed -n ... scripts/hermes-omnivoice-tts.py`
  - `sed -n ... scripts/validate-omnivoice-bridge.sh`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... README.md`
  - `chmod +x scripts/check-omnivoice-runtime.py`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `git diff --stat`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 37 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - No live OmniVoice-Studio service or real OmniVoice backend is configured, so
    real synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - A read-only runtime diagnostic is safer than attempting model startup before
    the operator has configured a local backend and consented voices.
- Next action:
  - Commit the runtime diagnostic checkpoint, then add a bounded install/start
    guide or probe Docker availability for a local loopback Studio run.

## Previous heartbeat

- Time: 2026-05-30 03:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `46cdcaf`.
  - Confirmed Docker and Docker Compose are available locally.
  - Confirmed the checked-out OmniVoice-Studio Compose config publishes port
    `3900` on `127.0.0.1` for the CPU profile.
  - Added `scripts/omnivoice-studio-local.py` to check, fetch, start, stop,
    show status, and inspect logs for a loopback-only Studio Docker Compose
    runtime.
  - Added tests that accept loopback Compose port mappings and reject broad
    `0.0.0.0` exposure or unexpected published ports.
  - Updated README and Studio/setup docs with the local Studio helper.
  - Ran the helper against `/tmp/omnivoice-studio-src`; Compose validation
    passed and Studio health is currently unreachable because the container is
    not running.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -10`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `docker --version`
  - `docker compose version`
  - `git -C /tmp/omnivoice-studio-src rev-parse --short HEAD`
  - `git -C /tmp/omnivoice-studio-src status --short --branch`
  - `sed -n ... /tmp/omnivoice-studio-src/deploy/docker-compose.yml`
  - `docker compose -f /tmp/omnivoice-studio-src/deploy/docker-compose.yml --profile cpu config --format json`
  - `chmod +x scripts/omnivoice-studio-local.py`
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 40 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio is not currently running on `127.0.0.1:3900`.
  - No real OmniVoice backend command or `omnivoice` CLI is configured, so real
    synthesis quality is still unverified.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Starting Studio should stay operator-explicit because first startup can pull
    images and download large model files.
- Next action:
  - Commit the local Studio helper checkpoint, then either run a bounded Studio
    container startup or improve packaging around the command-provider bridge.

## Previous heartbeat

- Time: 2026-05-30 03:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `30b0f87`.
  - Added `scripts/omnivoice-acceptance.py` to separate static MVP readiness
    from strict real-backend readiness.
  - Added `docs/omnivoice-acceptance.md` and linked it from README/setup and
    integration notes.
  - Added tests for required file coverage, default acceptance behavior, and
    strict `--require-real-backend` failure when no live backend or voice
    registry exists.
  - Ran acceptance checks locally: static MVP readiness PASS; strict
    real-backend readiness BLOCKED because no Studio/backend/CLI and no local
    voice profiles are configured.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -11`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `python3 scripts/omnivoice-acceptance.py --require-real-backend`
  - `scripts/validate-omnivoice-bridge.sh`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - `python3 scripts/omnivoice-acceptance.py --json`: PASS; static MVP ready,
    real backend not ready.
  - `python3 scripts/omnivoice-acceptance.py --require-real-backend`: expected
    BLOCKED exit because no live backend or local voice profile is configured.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 43 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio is not currently running on `127.0.0.1:3900`.
  - No real OmniVoice backend command or `omnivoice` CLI is configured.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Static MVP readiness should be allowed to pass even when live synthesis is
    blocked, but strict acceptance should fail until a real local backend and
    consented voice profile are present.
- Next action:
  - Commit the acceptance-checkpoint, then either start the local Studio helper
    in a bounded run or improve the package handoff for installing the bridge
    into a real Hermes checkout.

## Previous heartbeat

- Time: 2026-05-30 04:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `ca81b4c`.
  - Confirmed acceptance still reports static MVP readiness PASS and live
    backend readiness BLOCKED.
  - Added `scripts/install-hermes-omnivoice-bridge.py`, a conservative handoff
    installer for copying bridge scripts/docs into a real Hermes checkout or
    staging directory.
  - Installer supports `--dry-run`, refuses overwrites unless `--force` is
    passed, rejects target path escapes, and copies safe examples only when
    `--with-examples` is explicit.
  - Added installer tests for dry-run behavior, overwrite refusal, optional
    examples, and path escape rejection.
  - Updated README, setup, and acceptance docs with the install workflow.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -12`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... scripts/omnivoice-acceptance.py`
  - `sed -n ... scripts/hermes-omnivoice-voices.py`
  - `sed -n ... README.md`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `chmod +x scripts/install-hermes-omnivoice-bridge.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root <tmp>/hermes-agent --dry-run --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Installer dry-run: PASS; reported 13 bridge files and copied nothing.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 47 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio is not currently running on `127.0.0.1:3900`.
  - No real OmniVoice backend command or `omnivoice` CLI is configured.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - A no-overwrite installer is the safest useful package handoff until the
    actual Hermes checkout and TTS schema are available.
- Next action:
  - Commit the installer checkpoint, then continue toward either a bounded live
    Studio run or a final package summary if no backend appears.

## Previous heartbeat

- Time: 2026-05-30 04:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `6006958`.
  - Confirmed acceptance still reports static MVP readiness PASS and live
    backend readiness BLOCKED.
  - Added `set` and `current` subcommands to
    `scripts/hermes-omnivoice-voices.py` so the local helper now maps to
    `/voice list`, `/voice info`, `/voice set`, and `/voice preview`.
  - `set` validates the selected profile and consent gates before writing
    user-level selection state to `~/.hermes/omnivoice-selection.json`.
  - Added tests for writing and reading the selection file and for refusing to
    set an invalid profile.
  - Updated README, custom voice docs, and integration notes with the selection
    workflow.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -13`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... scripts/hermes-omnivoice-voices.py`
  - `sed -n ... docs/tts-custom-voices.md`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... README.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
  - `git diff --stat`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 49 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio is not currently running on `127.0.0.1:3900`.
  - No real OmniVoice backend command or `omnivoice` CLI is configured.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - User-level voice selection should live outside the repo and only be written
    after the selected profile validates.
- Next action:
  - Commit the voice-selection helper checkpoint, then continue with final
    package polish or a bounded live Studio/backend attempt.

## Previous heartbeat

- Time: 2026-05-30 05:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `379efc7`.
  - Confirmed acceptance still reports static MVP readiness PASS and live
    backend readiness BLOCKED.
  - Checked Docker for local Studio runtime availability: no
    `ghcr.io/debpalash/omnivoice-studio:latest` image and no existing Studio
    container were present.
  - Ran `scripts/omnivoice-studio-local.py check` against
    `/tmp/omnivoice-studio-src`; Compose remains loopback-ok and health is
    unreachable because Studio is not running.
  - Added `--no-build`, `--pull`, `--keep-failed`, and
    `--remove-volumes-on-fail` options to the local Studio helper.
  - Ran a local-only Studio startup probe with `--no-fetch --no-build --pull
    never`; it failed quickly because the Studio image is not present locally.
  - Removed the transient Compose network and volume created by the failed
    local-only startup probe, then verified no Studio containers, volumes, or
    networks remained.
  - Added tests for local-only startup args and volume-removing down args.
  - Updated setup and Studio bridge docs with local-only startup and cleanup
    behavior.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -14`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `docker image inspect ghcr.io/debpalash/omnivoice-studio:latest --format ...`
  - `docker ps -a --filter name=omnivoice-studio --format ...`
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --json`
  - `command -v timeout || command -v gtimeout || true`
  - `sed -n ... scripts/omnivoice-studio-local.py`
  - `python3 scripts/omnivoice-studio-local.py start --studio-dir /tmp/omnivoice-studio-src --no-fetch --no-build --pull never`
  - `docker compose -f /tmp/omnivoice-studio-src/deploy/docker-compose.yml --profile cpu down -v`
  - `docker ps -a --filter name=omnivoice-studio --format ...`
  - `docker volume ls --format ...`
  - `docker network ls --format ...`
  - `scripts/validate-omnivoice-bridge.sh`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
- Tests:
  - Local-only Studio startup probe: expected BLOCKED, no local image present.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation now includes 51 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio image is not present locally, and no Studio container is running on
    `127.0.0.1:3900`.
  - No real OmniVoice backend command or `omnivoice` CLI is configured.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - A local-only startup probe should avoid pulling/building large model
    artifacts unless a later heartbeat explicitly chooses the heavier path.
- Next action:
  - Commit the local-only Studio startup hardening checkpoint, then decide
    whether to start the full Studio image pull/build or keep polishing final
    handoff docs.

## Previous heartbeat

- Time: 2026-05-30 05:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `a196c53`.
  - Confirmed acceptance still reports static MVP readiness PASS and live
    backend readiness BLOCKED.
  - Added `docs/omnivoice-mvp-handoff.md`, a concise operator handoff covering
    current ready state, validation commands, install flow, backend setup,
    voice creation/selection commands, live blockers, and security invariants.
  - Added the handoff doc to the static acceptance required-file list and the
    dry-run-first Hermes install manifest.
  - Linked the handoff from README, acceptance docs, and integration notes.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -15`
  - `sed -n ... README.md`
  - `sed -n ... scripts/omnivoice-acceptance.py`
  - `sed -n ... HEARTBEAT.md`
  - `rg --files docs scripts tests examples | sort`
  - `sed -n ... docs/omnivoice-acceptance.md`
  - `sed -n ... docs/omnivoice-setup.md`
  - `sed -n ... docs/omnivoice-studio-bridge.md`
  - `sed -n ... scripts/validate-omnivoice-bridge.sh`
  - `rg -n "acceptance|REQUIRED_FILES|omnivoice-acceptance|More Detail|mvp" tests README.md docs scripts`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... docs/omnivoice-integration-notes.md`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `git diff --stat`
  - `git diff -- README.md docs/omnivoice-mvp-handoff.md docs/omnivoice-acceptance.md scripts/omnivoice-acceptance.py scripts/install-hermes-omnivoice-bridge.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
  - `git diff --check`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `git add .`
  - `git diff --cached --stat`
  - `git diff --cached --check`
  - `git commit -m "docs: add OmniVoice MVP handoff"`
- Tests:
  - `python3 scripts/omnivoice-acceptance.py --json`: PASS; static MVP ready
    with 19 required files, real backend not ready.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation includes 51 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio image is not present locally, and no Studio container is running on
    `127.0.0.1:3900`.
  - No real OmniVoice backend command or `omnivoice` CLI is configured.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - The most useful next operator artifact is a concise handoff that separates
    what is ready from what still needs a real local backend and Hermes source.
- Next action:
  - Commit the MVP handoff checkpoint, then decide whether to start a full
    Studio image pull/build or wait for a real Hermes Agent source/backend path.

## Previous heartbeat

- Time: 2026-05-30 06:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `357b1c3`.
  - Cloned and inspected upstream `k2-fsa/OmniVoice` in `/tmp/omnivoice-src`.
  - Confirmed the official single-item CLI is `omnivoice-infer`, with `--text`,
    `--output`, `--ref_audio`, `--ref_text`, `--instruct`, `--language`,
    `--speed`, `--model`, and `--device` options.
  - Fixed the wrapper's optional auto-CLI path to use `omnivoice-infer` instead
    of the speculative `omnivoice tts` command.
  - Kept auto CLI opt-in through `HERMES_OMNIVOICE_AUTO_CLI=1` so merely having
    the CLI installed does not trigger model downloads.
  - Updated runtime diagnostics and acceptance logic so CLI readiness requires
    both `omnivoice-infer` on `PATH` and explicit auto-CLI opt-in.
  - Updated docs and smoke-test skip behavior for the official CLI path.
  - Added tests for clone/design `omnivoice-infer` command construction and
    runtime CLI auto-gate reporting.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -5`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat|OmniVoice-Studio" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... HEARTBEAT.md`
  - `sed -n ... scripts/hermes-omnivoice-tts.py`
  - `if [ -d /tmp/omnivoice-src/.git ]; then git -C /tmp/omnivoice-src status --short --branch; else printf 'missing\n'; fi`
  - `git clone --depth 1 https://github.com/k2-fsa/OmniVoice /tmp/omnivoice-src`
  - `git -C /tmp/omnivoice-src status --short --branch`
  - `find /tmp/omnivoice-src -maxdepth 3 -type f ...`
  - `rg -n "argparse|click|typer|fire|if __name__|def main|tts|infer|synth|clone|voice|ref_audio|prompt|audio_prompt|save|wav|torchaudio|soundfile|sf\\.write|write_wav" /tmp/omnivoice-src -g '!*.ipynb'`
  - `sed -n ... /tmp/omnivoice-src/README.md`
  - `sed -n ... /tmp/omnivoice-src/omnivoice/cli/infer.py`
  - `sed -n ... /tmp/omnivoice-src/pyproject.toml`
  - `sed -n ... /tmp/omnivoice-src/omnivoice/models/omnivoice.py`
  - `sed -n ... scripts/check-omnivoice-runtime.py`
  - `rg -n "AUTO_CLI|omnivoice_cli|omnivoice|HERMES_OMNIVOICE_MODEL|backend command|HERMES_OMNIVOICE_COMMAND" README.md docs scripts tests examples`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `git diff --stat`
  - `git diff -- scripts/hermes-omnivoice-tts.py scripts/check-omnivoice-runtime.py scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `git diff --check`
  - `git add .`
  - `git diff --cached --stat`
  - `git diff --cached --check`
  - `git commit -m "fix: use official OmniVoice inference CLI"`
- Tests:
  - `python3 scripts/omnivoice-acceptance.py --json`: PASS; static MVP ready
    with 19 required files, real backend not ready.
  - `python3 scripts/check-omnivoice-runtime.py --json`: PASS; reports no
    Studio URL, no backend command, no `omnivoice-infer`, auto CLI disabled,
    and no local voices directory.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation includes 54 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio image is not present locally, and no Studio container is running on
    `127.0.0.1:3900`.
  - No real OmniVoice backend command is configured.
  - `omnivoice-infer` is not installed on `PATH`.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - The official CLI path should stay opt-in because `omnivoice-infer` may
    download model files on first use.
- Next action:
  - Commit the official CLI correction, then either install OmniVoice in a local
    environment for a real smoke test or start the loopback Studio image
    pull/build.

## Previous heartbeat

- Time: 2026-05-30 06:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `994f3c1`.
  - Added `scripts/hermes-omnivoice-python-adapter.py`, an optional command
    adapter that imports the OmniVoice Python API, calls
    `OmniVoice.from_pretrained`, supports clone and design fields, and writes a
    WAV through `soundfile`.
  - Added the Python adapter to static acceptance, validation py_compile, and
    the dry-run-first install manifest.
  - Documented the `HERMES_OMNIVOICE_COMMAND_JSON` wiring for the Python API
    adapter in README, setup, handoff, Studio bridge, integration notes,
    acceptance, and custom voice docs.
  - Added unit tests with fake `omnivoice`, `torch`, and `soundfile` modules
    covering clone generation, design generation, and missing clone transcript
    failure.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat|OmniVoice-Studio" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py`
  - `sed -n ... scripts/omnivoice-acceptance.py`
  - `sed -n ... scripts/validate-omnivoice-bridge.sh`
  - `chmod +x scripts/hermes-omnivoice-python-adapter.py`
  - `sed -n ... docs/tts-custom-voices.md`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `python3 -m unittest tests.test_omnivoice_tts.PythonAdapterTests -v`
  - `git diff --stat`
  - `git diff -- scripts/hermes-omnivoice-python-adapter.py tests/test_omnivoice_tts.py scripts/validate-omnivoice-bridge.sh scripts/omnivoice-acceptance.py scripts/install-hermes-omnivoice-bridge.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `git diff --check`
  - `git add .`
  - `git diff --cached --stat`
  - `git diff --cached --check`
  - `git commit -m "feat: add OmniVoice Python API adapter"`
- Tests:
  - `python3 scripts/omnivoice-acceptance.py --json`: PASS; static MVP ready
    with 20 required files, real backend not ready.
  - `python3 -m unittest tests.test_omnivoice_tts.PythonAdapterTests -v`: PASS,
    3 tests.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation includes 57 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio image is not present locally, and no Studio container is running on
    `127.0.0.1:3900`.
  - No real OmniVoice backend command is configured.
  - `omnivoice-infer` is not installed on `PATH`.
  - The `omnivoice` Python package is not installed in this repo environment.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Keeping direct Python API support as an explicit command adapter preserves
    the lightweight wrapper while giving operators a concrete no-Studio path
    when `omnivoice` is installed.
- Next action:
  - Commit the Python adapter checkpoint, then either install OmniVoice in an
    isolated local environment for a real smoke test or start the loopback
    Studio image pull/build.

## Previous heartbeat

- Time: 2026-05-30 07:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `9387a08`.
  - Added `scripts/setup-omnivoice-python-env.py`, a dry-run/check-first helper
    for planning, creating, and inspecting an isolated OmniVoice Python venv
    outside the repo.
  - The helper emits the `HERMES_OMNIVOICE_COMMAND_JSON` value needed to point
    Hermes at `scripts/hermes-omnivoice-python-adapter.py`.
  - Added the setup helper to static acceptance, validation py_compile, and the
    dry-run-first install manifest.
  - Added unit tests for dry-run planning, check-only missing-env reporting, and
    `--require-ready` failure on a missing venv.
  - Updated README, setup, MVP handoff, Studio bridge, integration notes,
    acceptance, and custom voice docs with the check-first Python environment
    flow.
  - Ran the setup helper in dry-run mode against `/tmp/hermes-omnivoice-python-env`
    and check-only mode against a missing temp venv; no environment was created.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat|OmniVoice-Studio" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `sed -n ... scripts/hermes-omnivoice-python-adapter.py`
  - `sed -n ... scripts/check-omnivoice-runtime.py`
  - `sed -n ... docs/omnivoice-setup.md`
  - `chmod +x scripts/setup-omnivoice-python-env.py`
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env --dry-run --json`
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env-missing --check-only --json`
  - `python3 -m unittest tests.test_omnivoice_tts.PythonEnvSetupTests -v`
  - `git diff --stat`
  - `scripts/validate-omnivoice-bridge.sh`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `git diff --check`
  - `git add .`
  - `git diff --cached --stat`
  - `git diff --cached --check`
  - `git commit -m "feat: add OmniVoice Python env setup helper"`
- Tests:
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env --dry-run --json`:
    PASS; reported venv creation/install commands and command-provider JSON
    without creating a venv.
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env-missing --check-only --json`:
    PASS; reported not ready with no venv present.
  - `python3 -m unittest tests.test_omnivoice_tts.PythonEnvSetupTests -v`: PASS,
    3 tests.
  - `python3 scripts/omnivoice-acceptance.py --json`: PASS; static MVP ready
    with 21 required files, real backend not ready.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation includes 60 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio image is not present locally, and no Studio container is running on
    `127.0.0.1:3900`.
  - No real OmniVoice backend command is configured.
  - `omnivoice-infer` is not installed on `PATH`.
  - The `omnivoice` Python package is not installed in this repo environment.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - The setup helper should expose planned package and command-provider settings
    before any heavy runtime install or model download happens.
- Next action:
  - Commit the environment setup helper, then use it to create an isolated
    OmniVoice environment or switch to a loopback Studio image pull/build for
    the first real synthesis smoke.

## Previous heartbeat

- Time: 2026-05-30 07:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `432f763`.
  - Confirmed the machine has `/opt/homebrew/bin/python3.11` and that `python3`
    currently resolves to Python 3.14.4.
  - Hardened `scripts/setup-omnivoice-python-env.py` so its default interpreter
    selection prefers Python 3.10 through 3.13 and skips unsupported candidates.
  - Added `--allow-unsupported-python` for deliberate overrides, but the default
    setup path now fails fast when explicitly pointed at an unsupported Python.
  - Verified dry-run setup now selects `/opt/homebrew/bin/python3.11`.
  - Verified an explicit `/opt/homebrew/bin/python3` dry-run fails cleanly
    because it is Python 3.14.4.
  - Updated setup, handoff, integration, acceptance, and custom voice docs with
    the supported interpreter range and `--python` guidance.
  - Added tests for supported interpreter selection and unsupported interpreter
    rejection.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `rg -n "Hermes OmniVoice|omnivoice-studio-plugin|hermes-omnivoice-weekend-heartbeat|OmniVoice-Studio" /Users/mhedhli/.codex/memories/MEMORY.md`
  - `command -v python3.13 python3.12 python3.11 python3.10 python3`
  - `python3 --version`
  - `sed -n ... scripts/setup-omnivoice-python-env.py`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env --dry-run --json`
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env --python /opt/homebrew/bin/python3 --dry-run`
  - `python3 -m unittest tests.test_omnivoice_tts.PythonEnvSetupTests -v`
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env-missing --check-only --json`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `git diff --stat`
  - `git diff -- scripts/setup-omnivoice-python-env.py tests/test_omnivoice_tts.py docs/omnivoice-setup.md docs/omnivoice-mvp-handoff.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `find . -type d -name __pycache__ -print`
  - `find . -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.flac' -o -name '*.onnx' -o -name '*.pt' -o -name '*.pth' -o -name '*.safetensors' -o -name '.env' -o -name '.env.*' -o -name 'omnivoice-selection.json' \) -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `git diff --check`
  - `git add .`
  - `git diff --cached --stat`
  - `git diff --cached --check`
  - `git commit -m "fix: choose supported Python for OmniVoice setup"`
- Tests:
  - `python3 scripts/setup-omnivoice-python-env.py --venv-dir /tmp/hermes-omnivoice-python-env --dry-run --json`:
    PASS; selected `/opt/homebrew/bin/python3.11`, reported Python 3.11.15,
    and created no venv.
  - Explicit unsupported Python dry-run with `/opt/homebrew/bin/python3`:
    expected BLOCKED exit because it is Python 3.14.4.
  - `python3 -m unittest tests.test_omnivoice_tts.PythonEnvSetupTests -v`: PASS,
    5 tests.
  - `python3 scripts/omnivoice-acceptance.py --json`: PASS; static MVP ready
    with 21 required files, real backend not ready.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - Validation includes 62 unit tests PASS with 1 real-backend integration
    skip, py_compile PASS, fake-backend smoke PASS, unconfigured smoke SKIP as
    expected, secret-pattern scan PASS, and `git diff --check` PASS.
- Blockers:
  - Studio image is not present locally, and no Studio container is running on
    `127.0.0.1:3900`.
  - No real OmniVoice backend command is configured.
  - `omnivoice-infer` is not installed on `PATH`.
  - The `omnivoice` Python package is not installed in this repo environment.
  - No local voice profiles exist under `~/.hermes/voices/omnivoice`.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Python 3.14 is too new for a predictable OmniVoice/PyTorch install path, so
    setup should prefer the available Python 3.11 interpreter.
- Next action:
  - Commit the supported-Python setup guard, then create the isolated OmniVoice
    Python environment with Python 3.11 or start the loopback Studio image
    pull/build for the first real synthesis smoke.

## Previous heartbeat

- Time: 2026-05-30 08:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `d7bbf32`.
  - Created the isolated OmniVoice Python environment at
    `~/.cache/hermes/omnivoice-python` using `/opt/homebrew/bin/python3.11`.
  - Installed the upstream `omnivoice` package plus its local runtime
    dependencies outside the repo.
  - Verified `scripts/setup-omnivoice-python-env.py --check-only --json`
    reports `ready: true`, including `omnivoice`, `soundfile`, `torch`, and a
    venv-local `omnivoice-infer`.
  - Verified `scripts/check-omnivoice-runtime.py --json` sees the configured
    command JSON and venv-local `omnivoice-infer`.
  - Verified `omnivoice-infer --help` exposes the expected upstream arguments:
    text, output, ref audio/text, instruct, language, speed, and device.
  - Ran the first real synthesis smoke; it loaded/downloaded the model and then
    failed because the existing smoke design prompt used unsupported free-form
    English tags.
  - Updated the smoke profile, example voice, docs, and tests to use supported
    OmniVoice design tags: `male, american accent, moderate pitch`.
  - Added wrapper validation so unsupported English design tags fail before
    starting the heavy model runtime.
  - Retried the real smoke test successfully; it generated a valid temporary
    WAV through the upstream `omnivoice-infer` CLI.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/setup-omnivoice-python-env.py --dry-run --json`
  - `python3 scripts/setup-omnivoice-python-env.py --json`
  - `PATH=... HERMES_OMNIVOICE_COMMAND_JSON=... HERMES_OMNIVOICE_MODEL=... python3 scripts/check-omnivoice-runtime.py --json`
  - `/Users/mhedhli/.cache/hermes/omnivoice-python/bin/omnivoice-infer --help`
  - `PATH=... HERMES_OMNIVOICE_AUTO_CLI=1 HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice scripts/test-omnivoice-tts.sh`
  - `rg -n "instruct:|calm local assistant|calm male narrator|clear delivery|neutral accent|low pitch|male|female|american accent|voice design|design" scripts docs tests examples README.md HEARTBEAT.md`
  - `python3 -m unittest discover -s tests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-tts.py scripts/hermes-omnivoice-python-adapter.py scripts/setup-omnivoice-python-env.py scripts/check-omnivoice-runtime.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `PATH=... HERMES_OMNIVOICE_AUTO_CLI=1 HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice python3 scripts/omnivoice-acceptance.py --voices-dir /tmp/.../voices --require-real-backend --json`
- Tests:
  - `python3 scripts/setup-omnivoice-python-env.py --json`: PASS; created the
    isolated venv outside the repo and installed OmniVoice runtime packages.
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`: PASS;
    reported `ready: true`.
  - Runtime check with venv command JSON and venv `PATH`: PASS; backend command
    configured, CLI found, Studio missing as expected, voices dir missing as
    expected.
  - First real `scripts/test-omnivoice-tts.sh` with `HERMES_OMNIVOICE_AUTO_CLI=1`:
    expected FAIL after model load because the smoke profile used unsupported
    free-form design tags.
  - `python3 -m unittest discover -s tests -v`: PASS, 63 tests run, 1 skipped
    real-backend integration test.
  - `python3 -m py_compile ...`: PASS.
  - Corrected real `scripts/test-omnivoice-tts.sh` with
    `HERMES_OMNIVOICE_AUTO_CLI=1`: PASS, generated a valid temporary WAV.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes unit tests,
    py_compile, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Acceptance with a temporary consented design profile and the venv
    `omnivoice-infer`: PASS; `real_backend_ready: true`.
- Blockers:
  - No running OmniVoice-Studio service on `127.0.0.1:3900`, so Studio import
    and Studio `/generate` smoke remain unverified against a live service.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; the real smoke used a temporary consented
    design profile created by the smoke script.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - English OmniVoice designed voices should use the upstream supported tag
    vocabulary rather than free-form descriptive prompts.
  - Downloaded model/package caches are acceptable under user-local cache
    directories and must not be copied into the repo.
- Next action:
  - Commit the installed runtime plus real-smoke checkpoint, then either start
    a loopback Studio service or locate the real Hermes Agent source for schema
    verification.

## Previous heartbeat

- Time: 2026-05-30 08:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `bb3aade`.
  - Reconfirmed the isolated OmniVoice Python environment is ready at
    `~/.cache/hermes/omnivoice-python`.
  - Attempted a real command-provider smoke using
    `HERMES_OMNIVOICE_COMMAND_JSON` and `scripts/hermes-omnivoice-python-adapter.py`.
  - Found the adapter's import contract did not match the installed upstream
    package: `OmniVoice` is available from
    `omnivoice.models.omnivoice`, and `get_best_device` is a CLI-local helper.
  - Updated the Python adapter to import `OmniVoice` from the real package path
    and perform local CUDA/MPS/CPU device detection.
  - Updated fake-module tests to mirror the installed package layout.
  - Retried the real Python-adapter smoke successfully through
    `scripts/hermes-omnivoice-tts.py`; it generated a valid temporary WAV at
    24 kHz with 48,480 frames.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `sed -n '1,180p' scripts/hermes-omnivoice-python-adapter.py`
  - `tail -n 140 HEARTBEAT.md`
  - `HERMES_OMNIVOICE_COMMAND_JSON=... HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice python3 scripts/hermes-omnivoice-tts.py --voices-dir /tmp/.../voices --text-file /tmp/.../input.txt --out /tmp/.../out.wav --voice pyadapter --speed 1.0`
  - `/Users/mhedhli/.cache/hermes/omnivoice-python/bin/python - <<'PY' ...`
  - `rg -n "from omnivoice import|get_best_device|python adapter|Python adapter|omnivoice.models.omnivoice" README.md docs scripts tests`
  - `python3 -m unittest tests.test_omnivoice_tts.PythonAdapterTests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-python-adapter.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - First real Python-adapter smoke: expected FAIL; exposed incorrect adapter
    import assumptions against the installed upstream package.
  - Direct installed-package inspection: PASS; confirmed
    `omnivoice.models.omnivoice.OmniVoice` and CLI-local `get_best_device`.
  - `python3 -m unittest tests.test_omnivoice_tts.PythonAdapterTests -v`: PASS,
    3 tests.
  - `python3 -m py_compile ...`: PASS.
  - Corrected real Python-adapter smoke through the wrapper: PASS, generated a
    valid temporary WAV.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 63 tests with 1
    expected real-backend integration skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - No running OmniVoice-Studio service on `127.0.0.1:3900`, so Studio import
    and Studio `/generate` smoke remain unverified against a live service.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented design profiles.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - Keeping the Python API adapter's imports pinned to the installed package
    layout is better than wrapping the CLI when users choose command JSON mode.
  - Temporary smoke outputs should remain under `/tmp` or the macOS temporary
    directory and must not be committed.
- Next action:
  - Commit the Python-adapter real-runtime fix, then focus the next heartbeat
    on a loopback OmniVoice-Studio live smoke or actual Hermes Agent source
    discovery.

## Previous heartbeat

- Time: 2026-05-30 09:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `353ac1b`.
  - Revalidated OmniVoice-Studio's cached Compose config from
    `/tmp/omnivoice-studio-src`; the CPU profile publishes only
    `127.0.0.1:3900:3900`.
  - Confirmed nothing was listening on local port 3900 and no Studio Docker
    image or container was already present.
  - Attempted a loopback-only Studio startup using the published image path
    with `--no-fetch --no-build --pull missing`.
  - Stopped the startup after the Docker pull made no observable progress for
    several minutes and no image/container appeared.
  - Confirmed cleanup left no `omnivoice-studio` container or Docker Compose
    process running.
  - Added `--command-timeout` to `scripts/omnivoice-studio-local.py` so Docker
    and Git subprocesses are bounded; default is 900 seconds, `0` disables it
    for deliberate manual runs.
  - Verified a one-second bounded startup fails cleanly with a timeout error
    and leaves no Studio process/container behind.
  - Updated Studio setup/bridge docs with the timeout behavior.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `sed -n ... scripts/omnivoice-studio-local.py`
  - `ls -la /tmp/omnivoice-studio-src`
  - `docker ps --format ...`
  - `docker images --format ... | rg -i 'omnivoice|studio'`
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --json`
  - `docker compose -f /tmp/omnivoice-studio-src/deploy/docker-compose.yml --profile cpu config --format json`
  - `lsof -nP -iTCP:3900 -sTCP:LISTEN`
  - `docker volume ls --format ... | rg 'omnivoice|deploy_omnivoice'`
  - `python3 scripts/omnivoice-studio-local.py start --studio-dir /tmp/omnivoice-studio-src --no-fetch --no-build --pull missing`
  - `docker system df`
  - `ps ax -o pid,ppid,stat,etime,command | rg 'docker compose|omnivoice-studio|ghcr.io/debpalash'`
  - `docker events --since 5m --until 1s --filter image=ghcr.io/debpalash/omnivoice-studio:latest`
  - `kill ...`
  - `docker compose -f /tmp/omnivoice-studio-src/deploy/docker-compose.yml --profile cpu down`
  - `python3 scripts/omnivoice-studio-local.py start --studio-dir /tmp/omnivoice-studio-src --no-fetch --no-build --pull missing --command-timeout 1`
  - `python3 -m unittest tests.test_omnivoice_tts.StudioLocalTests -v`
  - `python3 -m py_compile scripts/omnivoice-studio-local.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --json`:
    PASS; Compose loopback validation ok, health unreachable as expected.
  - Published-image startup attempt: BLOCKED; Docker pull stayed silent for
    several minutes and produced no image/container.
  - Bounded startup with `--command-timeout 1`: expected FAIL with a clear
    timeout error.
  - Post-timeout process/container check: PASS; no Studio process or container
    remained.
  - `python3 -m unittest tests.test_omnivoice_tts.StudioLocalTests -v`: PASS,
    6 tests.
  - `python3 -m py_compile ...`: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 64 tests with 1
    expected real-backend integration skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Published OmniVoice-Studio image pull did not make observable progress in
    this heartbeat, so no live Studio `/profiles` or `/generate` smoke was run.
  - Running the Studio backend directly from source appears heavier than the
    installed OmniVoice inference venv because Studio declares many API,
    dubbing, ASR, translation, and UI dependencies.
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
- Assumptions:
  - A bounded Docker image pull/build is safer for heartbeat automation than an
    unbounded Compose startup, even though manual runs can opt out with
    `--command-timeout 0`.
  - The cached `/tmp/omnivoice-studio-src` source remains adequate for
    loopback Compose validation and API-shape evidence.
- Next action:
  - Commit the Studio helper timeout hardening, then either retry a bounded
    Studio image pull/build window or locate the actual Hermes Agent source for
    schema verification.

## Previous heartbeat

- Time: 2026-05-30 09:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `56a0ac4`.
  - Searched the local Hermes and broader Coding directories for a real Hermes
    Agent checkout; only this plugin repo was found under
    `/Users/mhedhli/Documents/Coding/hermes`.
  - Checked `~/.hermes` and `~/.config` for Hermes/TTS config paths; none were
    found.
  - Converted the previously unconditional real-backend integration skip into
    an explicit opt-in integration test gated by
    `HERMES_OMNIVOICE_RUN_REAL_TEST=1`.
  - The opt-in test now creates a temporary consented design voice, invokes
    `scripts/hermes-omnivoice-tts.py` with the configured real backend, and
    validates the generated WAV.
  - Documented the opt-in integration unittest command in
    `docs/omnivoice-setup.md`.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `find /Users/mhedhli/Documents/Coding/hermes -maxdepth 4 -type d -name .git -print`
  - `find /Users/mhedhli/Documents/Coding -maxdepth 5 -type d \( -iname '*hermes*' -o -iname '*agent*' \) -print`
  - `find ~/.hermes ~/.config -maxdepth 4 \( -iname '*hermes*' -o -iname '*tts*' \) -print`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `rg -n "real_omnivoice|RUN_REAL|integration|test_real_omnivoice|HERMES_OMNIVOICE" docs README.md scripts tests`
  - `sed -n ... scripts/validate-omnivoice-bridge.sh`
  - `python3 -m unittest tests.test_omnivoice_tts.OmniVoiceIntegrationTests -v`
  - `PATH=... HERMES_OMNIVOICE_RUN_REAL_TEST=1 HERMES_OMNIVOICE_AUTO_CLI=1 HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice python3 -m unittest tests.test_omnivoice_tts.OmniVoiceIntegrationTests -v`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - Default `python3 -m unittest tests.test_omnivoice_tts.OmniVoiceIntegrationTests -v`:
    PASS with 1 skip and no model work.
  - Explicit real integration unittest with the venv `omnivoice-infer`: PASS,
    generated and validated a temporary WAV in about 12 seconds.
  - `python3 -m py_compile tests/test_omnivoice_tts.py`: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 64 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally, so native provider
    and in-app `/voice` command wiring remain deferred.
  - Published OmniVoice-Studio image pull is still unresolved from the previous
    heartbeat, so no live Studio `/profiles` or `/generate` smoke has run.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - Heavy real model synthesis should remain opt-in for unittest runs, while
    shell smoke scripts can remain the primary manual real-backend check.
  - The command-provider MVP is now materially testable without a real Hermes
    checkout because the wrapper path itself is proven against real OmniVoice.
- Next action:
  - Commit the opt-in real integration unittest, then either retry Studio with a
    bounded pull/build window or add a Hermes-source discovery/report helper for
    future schema verification.

## Previous heartbeat

- Time: 2026-05-30 11:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `a6f0dcb`.
  - Added `scripts/find-hermes-source.py`, a read-only source discovery helper
    for finding and scoring candidate Hermes Agent checkouts.
  - The helper skips common dependency/cache directories, avoids
    sensitive-named files, bounds candidate count and scan time, and marks this
    OmniVoice bridge repo separately so it is not mistaken for Hermes Agent.
  - Added the finder to the installer manifest, acceptance required files, and
    full validation py_compile list.
  - Added source-finder tests for a likely Hermes checkout, this bridge repo,
    sensitive-file skipping, and candidate limiting.
  - Ran the finder against the local Hermes/Coding roots. It completed quickly
    after timeout hardening and reported only this bridge repo, with
    `likely_count: 0`.
  - Updated README, setup docs, and integration notes with the discovery helper.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -7`
  - `tail -n 170 HEARTBEAT.md`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py`
  - `sed -n ... scripts/check-omnivoice-runtime.py`
  - `chmod +x scripts/find-hermes-source.py`
  - `python3 -m unittest tests.test_omnivoice_tts.HermesSourceFinderTests -v`
  - `python3 -m py_compile scripts/find-hermes-source.py scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding --max-depth 5 --max-candidates 20 --scan-timeout 5 --json`
  - `ps ax -o pid,ppid,stat,etime,command | rg 'find-hermes-source'`
  - `kill ...`
  - `rg -n "SECRET|TOKEN|PASSWORD|API_KEY|BEGIN [A-Z ]*PRIVATE|sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|glpat-|hf_[A-Za-z0-9]{20,}|ELEVENLABS|OPENAI_API_KEY" ...`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - First broad discovery run: BLOCKED by overly broad traversal; stopped and
    replaced with end-to-end scan time and candidate limits.
  - First bounded discovery run: completed but produced false positives from
    unrelated repos with generic TTS text; scoring was tightened to require a
    Hermes path signal for likely Hermes Agent classification.
  - Corrected bounded discovery run: PASS; returned only this bridge repo,
    `is_bridge_repo: true`, `likely_count: 0`, and `truncated: false`.
  - `python3 -m unittest tests.test_omnivoice_tts.HermesSourceFinderTests -v`:
    PASS, 4 tests.
  - `python3 -m py_compile ...`: PASS.
  - First full validation after adding the helper: expected FAIL from a
    denylist variable name matching the repo's secret-pattern scan; internal
    naming was changed to avoid the false positive.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 68 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; the new finder
    confirms only this bridge repo under the searched Hermes/Coding roots.
  - Published OmniVoice-Studio image pull remains unresolved, so no live Studio
    `/profiles` or `/generate` smoke has run.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - Hermes source discovery should be bounded and repeatable because broad
    manual scans across a large Coding tree are not suitable for heartbeat
    cadence.
  - A path-level Hermes signal is required before marking a checkout as a
    likely Hermes Agent source; generic speech/TTS text alone is too noisy.
- Next action:
  - Commit the source discovery helper, then retry Studio with a bounded
    pull/build window or use the finder output as the durable source-discovery
    evidence until the real Hermes checkout appears.

## Previous heartbeat

- Time: 2026-05-30 11:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `b3da646`.
  - Promoted Hermes source discovery into `scripts/omnivoice-acceptance.py` so
    acceptance JSON and human output now include `hermes_source_ready` and the
    full bounded discovery report.
  - Added `--require-hermes-source` for strict handoff checks while preserving
    the default zero-exit static MVP acceptance when the real Hermes checkout is
    absent.
  - Added explicit source-root and source-budget options to the acceptance
    command so heartbeat checks stay bounded.
  - Added acceptance tests for missing source by default, strict source failure,
    and a likely Hermes source checkout.
  - Updated `docs/omnivoice-acceptance.md` to document the three acceptance
    gates and the strict Hermes-source check.
  - Ran acceptance against `/Users/mhedhli/Documents/Coding/hermes` and
    `/Users/mhedhli/Documents/Coding`; it found only this bridge repo and
    reported `hermes_source_ready: false`, `mvp_static_ready: true`, and
    `real_backend_ready: false`.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -7`
  - `sed -n ... scripts/omnivoice-acceptance.py`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... docs/omnivoice-acceptance.md`
  - `sed -n ... scripts/find-hermes-source.py`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests tests.test_omnivoice_tts.HermesSourceFinderTests -v`
  - `python3 -m py_compile scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `python3 scripts/omnivoice-acceptance.py --source-root /Users/mhedhli/Documents/Coding/hermes --source-root /Users/mhedhli/Documents/Coding --source-scan-timeout 5 --source-max-candidates 20 --json`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - Focused acceptance/source tests: PASS, 10 tests.
  - `python3 -m py_compile scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 71 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; acceptance now
    exposes that as a distinct source-readiness blocker.
  - Published OmniVoice-Studio image pull remains unresolved, so no live Studio
    `/profiles` or `/generate` smoke has run.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - Static MVP acceptance should remain useful in this bridge repo, but strict
    handoff or final wiring should require a real Hermes source checkout.
  - Source readiness and backend readiness need separate gates so progress is
    not overstated.
- Next action:
  - Commit the acceptance-source gate checkpoint, then continue with a bounded
    Studio startup retry or prepare final handoff notes around the remaining
    external blockers.

## Previous heartbeat

- Time: 2026-05-30 12:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `53bcc00`.
  - Ran acceptance with both the narrow Hermes root and broad Coding root. The
    broad root consumed the source scan timeout before any candidate inspection,
    which made the source-discovery evidence unstable.
  - Updated `scripts/find-hermes-source.py` so candidate roots discovered before
    timeout still get a small bounded inspection grace window.
  - Added a regression test proving an already-known candidate is inspected even
    when discovery reports truncation.
  - Re-ran acceptance with the same roots; it now retains this bridge repo as a
    candidate, marks it `is_bridge_repo: true`, reports `likely_count: 0`, and
    keeps `hermes_source_ready: false`.
  - Rechecked runtime state; no Studio URL, backend command, OmniVoice CLI, or
    persistent local voice registry is configured in the default environment.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/omnivoice-acceptance.py --source-root /Users/mhedhli/Documents/Coding/hermes --source-root /Users/mhedhli/Documents/Coding --source-scan-timeout 5 --source-max-candidates 20 --json`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `sed -n ... scripts/omnivoice-studio-local.py`
  - `tail -n 190 HEARTBEAT.md`
  - `ls -la /Users/mhedhli/Documents/Coding/hermes /Users/mhedhli/Documents/Coding/hermes/omnivoice-studio-plugin`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --max-depth 5 --max-candidates 20 --scan-timeout 5 --json`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes/omnivoice-studio-plugin --max-depth 1 --max-candidates 20 --scan-timeout 5 --json`
  - `sed -n ... scripts/find-hermes-source.py`
  - `rg -n "find-hermes-source|source discovery|Hermes source" README.md docs scripts tests HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.HermesSourceFinderTests tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 -m py_compile scripts/find-hermes-source.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - Focused source/acceptance tests: PASS, 11 tests.
  - `python3 -m py_compile scripts/find-hermes-source.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 72 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - Published OmniVoice-Studio image pull remains unresolved, so no live Studio
    `/profiles` or `/generate` smoke has run.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - Truncated source searches should still report already-discovered candidates
    rather than dropping useful evidence at the deadline.
  - The broad Coding root is useful for discovery but should not be allowed to
    erase the narrower Hermes-root evidence.
- Next action:
  - Commit the source-discovery timeout stability fix, then either retry
    loopback Studio startup with the bounded helper or prepare final handoff
    notes around the remaining external blockers.

## Previous heartbeat

- Time: 2026-05-30 12:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `fe93b85`.
  - Re-ran acceptance and runtime checks. Static MVP remains ready, real backend
    remains blocked, and source readiness remains blocked because only this
    bridge repo is found locally.
  - Verified Docker `29.4.1` and Docker Compose `v5.1.3` are available.
  - Verified the cached OmniVoice-Studio checkout at `/tmp/omnivoice-studio-src`
    still has loopback-only Compose config for the CPU profile.
  - Confirmed no local OmniVoice/Studio image or container was present.
  - Ran a no-fetch/no-build/no-pull Studio startup probe. Before code changes it
    reached `docker compose up`, failed on missing
    `ghcr.io/debpalash/omnivoice-studio:latest`, and cleaned the transient
    network and volume.
  - Hardened `scripts/omnivoice-studio-local.py` so that no-build/no-pull start
    checks local image availability before invoking Compose.
  - Removed the unnecessary `git` requirement when `start --no-fetch` is used
    with an already-present Studio checkout.
  - Added tests for no-fetch startup and missing-image preflight behavior.
  - Re-ran the no-fetch/no-build/no-pull probe; it now exits immediately with a
    clear missing-image message and creates no Studio containers, networks, or
    volumes.
  - Updated setup and Studio bridge docs with the improved no-pull/no-build
    preflight behavior.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `sed -n ... scripts/omnivoice-studio-local.py`
  - `python3 scripts/omnivoice-acceptance.py --source-root /Users/mhedhli/Documents/Coding/hermes --source-root /Users/mhedhli/Documents/Coding --source-scan-timeout 5 --source-max-candidates 20 --json`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `tail -n 190 HEARTBEAT.md`
  - `docker --version`
  - `docker compose version`
  - `ls -la /tmp/omnivoice-studio-src /tmp/omnivoice-studio-src/deploy /tmp/omnivoice-studio-src/deploy/docker-compose.yml`
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --profile cpu --command-timeout 30 --json`
  - `docker compose -f /tmp/omnivoice-studio-src/deploy/docker-compose.yml --profile cpu config --format json`
  - `sed -n ... /tmp/omnivoice-studio-src/deploy/docker-compose.yml`
  - `rg -n "image:|build:|ports:|3900|omnivoice" /tmp/omnivoice-studio-src/deploy/docker-compose.yml /tmp/omnivoice-studio-src/deploy/Dockerfile`
  - `python3 scripts/omnivoice-studio-local.py start --studio-dir /tmp/omnivoice-studio-src --profile cpu --no-fetch --no-build --pull never --command-timeout 60 --remove-volumes-on-fail`
  - `docker ps -a --format ... | rg -i 'omnivoice|studio|hermes'`
  - `docker volume ls --format ... | rg -i 'omnivoice|studio|deploy'`
  - `docker network ls --format ... | rg -i 'omnivoice|studio|deploy'`
  - `python3 -m unittest tests.test_omnivoice_tts.StudioLocalTests -v`
  - `python3 -m py_compile scripts/omnivoice-studio-local.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - `python3 -m unittest tests.test_omnivoice_tts.StudioLocalTests -v`: PASS,
    8 tests.
  - `python3 -m py_compile scripts/omnivoice-studio-local.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 74 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - No local `ghcr.io/debpalash/omnivoice-studio:latest` image is available, so
    the no-pull/no-build Studio startup path cannot launch Studio.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - A no-pull/no-build Studio probe should not create Docker resources when it
    can prove the required local image is absent.
  - `git` should only be required for Studio source fetch/update, not for
    starting from an existing checkout with `--no-fetch`.
- Next action:
  - Commit the Studio preflight hardening, then decide whether to attempt a
    bounded image pull/build window or prepare final handoff notes around the
    external blockers.

## Previous heartbeat

- Time: 2026-05-30 13:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `d741453`.
  - Re-ran acceptance and runtime checks. Static MVP remains ready; real backend
    and Hermes source readiness remain blocked in the default environment.
  - Rechecked the cached Studio checkout; Compose config remains loopback-only
    and the local Studio health check remains unreachable.
  - Attempted a bounded no-fetch/no-build Studio start with `--pull missing`.
    The pull failed quickly because `ghcr.io/debpalash/omnivoice-studio:latest`
    has no `linux/arm64/v8` manifest for this Mac.
  - Confirmed there were no leftover Studio containers, networks, or volumes
    after the failed pull/start attempt.
  - Hardened `scripts/omnivoice-studio-local.py` so no-build pull-enabled runs
    perform the bounded `docker pull` before `docker compose up`.
  - Updated the pull helper to capture Docker pull errors and return them
    through the helper's own error path.
  - Added tests proving `--no-build --pull missing` pulls before Compose when
    the image is absent and skips that pull when the image is already local.
  - Updated setup and Studio bridge docs to describe pre-Compose image pulls and
    platform/registry failures.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/omnivoice-acceptance.py --source-root /Users/mhedhli/Documents/Coding/hermes --source-root /Users/mhedhli/Documents/Coding --source-scan-timeout 5 --source-max-candidates 20 --json`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --profile cpu --command-timeout 30 --json`
  - `tail -n 190 HEARTBEAT.md`
  - `python3 scripts/omnivoice-studio-local.py start --studio-dir /tmp/omnivoice-studio-src --profile cpu --no-fetch --no-build --pull missing --command-timeout 180 --remove-volumes-on-fail`
  - `docker ps -a --format ... | rg -i 'omnivoice|studio|hermes'`
  - `docker volume ls --format ... | rg -i 'omnivoice|studio|deploy'`
  - `docker network ls --format ... | rg -i 'omnivoice|studio|deploy'`
  - `python3 -m unittest tests.test_omnivoice_tts.StudioLocalTests -v`
  - `python3 -m py_compile scripts/omnivoice-studio-local.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - `python3 -m unittest tests.test_omnivoice_tts.StudioLocalTests -v`: PASS,
    10 tests.
  - `python3 -m py_compile scripts/omnivoice-studio-local.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 76 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - The published OmniVoice-Studio image does not provide a `linux/arm64/v8`
    manifest, so image-pull startup is blocked on this Mac unless an alternate
    platform, build path, or compatible image is used.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - Pull failures should happen before Compose startup so the helper does not
    create avoidable Docker resources on unsupported platforms.
  - Building from source may be the next Studio path on Apple Silicon, but it
    should remain bounded by the helper's command timeout.
- Next action:
  - Commit the pull-before-Compose hardening, then either attempt a bounded
    source build or prepare final handoff notes around the remaining external
    blockers.

## Previous heartbeat

- Time: 2026-05-30 13:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `94f423a`.
  - Re-ran acceptance, runtime, and Studio local checks. Static MVP remains
    ready; real backend and Hermes source readiness remain blocked in the
    default environment.
  - Attempted a bounded source build/start from the cached
    `/tmp/omnivoice-studio-src` checkout with loopback-only Compose config.
  - The source build downloaded and extracted large PyTorch runtime layers,
    progressed through dependency install, and timed out after 300 seconds while
    exporting the Docker image.
  - Confirmed no matching Studio containers, volumes, networks, or images were
    left after the timed-out source-build attempt.
  - Updated setup and Studio bridge docs to describe the Apple Silicon
    source-build limitation and keep long source builds operator-supervised.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/omnivoice-acceptance.py --source-root /Users/mhedhli/Documents/Coding/hermes --source-root /Users/mhedhli/Documents/Coding --source-scan-timeout 5 --source-max-candidates 20 --json`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/omnivoice-studio-local.py check --studio-dir /tmp/omnivoice-studio-src --profile cpu --command-timeout 30 --json`
  - `python3 scripts/omnivoice-studio-local.py start --studio-dir /tmp/omnivoice-studio-src --profile cpu --no-fetch --pull never --command-timeout 300 --remove-volumes-on-fail`
  - `docker ps -a --format ... | rg -i 'omnivoice|studio|hermes'`
  - `docker volume ls --format ... | rg -i 'omnivoice|studio|deploy'`
  - `docker network ls --format ... | rg -i 'omnivoice|studio|deploy'`
  - `docker images --format ... | rg -i 'omnivoice|studio|deploy|ghcr.io/debpalash'`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - Source-build probe: BLOCKED; timed out at Docker image export after 300
    seconds.
  - Post-timeout Docker resource checks: PASS; no matching Studio containers,
    volumes, networks, or images found.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 76 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - The published OmniVoice-Studio image does not provide a `linux/arm64/v8`
    manifest, so image-pull startup is blocked on this Mac.
  - Building Studio from source on this host exceeds the 300 second heartbeat
    window and pulls a large PyTorch runtime before image export completes.
  - No persistent local voice profiles exist under
    `~/.hermes/voices/omnivoice`; real smokes continue to use temporary
    consented profiles.
- Assumptions:
  - Longer Studio source builds should be operator-supervised because they can
    consume significant local disk and Docker cache.
  - The already-proven direct OmniVoice CLI/Python adapter path remains the
    simplest local MVP path until a compatible Studio image or longer build
    window is available.
- Next action:
  - Commit the source-build platform notes, then prepare final handoff or wait
    for the actual Hermes Agent source and a compatible live Studio/runtime
    path before more native-provider work.

## Previous heartbeat

- Time: 2026-05-30 14:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `821b948`.
  - Re-ran acceptance and source discovery. Static MVP remains ready, while
    real backend readiness and Hermes source readiness remain blocked in the
    default shell environment.
  - Re-ran runtime checks. The default shell still has no Studio URL, backend
    command, auto CLI backend, or persistent local voices.
  - Verified the isolated OmniVoice Python environment under
    `~/.cache/hermes/omnivoice-python` is still ready with `omnivoice`, `torch`,
    `soundfile`, and `omnivoice-infer`.
  - Updated `docs/omnivoice-mvp-handoff.md` and
    `docs/omnivoice-acceptance.md` so the handoff does not confuse the ready
    isolated venv with the unconfigured default runtime.
  - Corrected a local source-discovery command typo from `--timeout` to the
    actual `--scan-timeout` flag and confirmed discovery still finds only this
    bridge repo.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `rg --files docs examples scripts tests | sort`
  - `sed -n '1,260p' docs/omnivoice-mvp-handoff.md`
  - `sed -n '1,240p' docs/omnivoice-acceptance.md`
  - `tail -n 190 HEARTBEAT.md`
  - `python3 scripts/omnivoice-acceptance.py --source-root /Users/mhedhli/Documents/Coding/hermes --source-root /Users/mhedhli/Documents/Coding --source-scan-timeout 5 --source-max-candidates 20 --json`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding --timeout 5 --max-candidates 20 --json`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding --scan-timeout 5 --max-candidates 20 --json`
  - `scripts/validate-omnivoice-bridge.sh`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 76 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
  - Acceptance snapshot: PASS for static MVP; BLOCKED for real backend and
    Hermes source readiness.
  - Python environment check: PASS; isolated OmniVoice venv is ready.
  - Source discovery: BLOCKED; no likely Hermes Agent checkout found.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - Default shell runtime remains unconfigured: no Studio URL, backend command,
    enabled CLI backend, or persistent local voices.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in the previous heartbeat.
- Assumptions:
  - A prepared venv is useful handoff evidence, but it should not be counted as
    default real-backend readiness until the adapter command or CLI gate is
    explicitly exported and a consented voice exists.
  - Handoff docs should now be the primary entrypoint for the next operator
    instead of requiring them to reconstruct state from the full heartbeat log.
- Next action:
  - Commit the handoff refresh, then either create a consented local test voice
    for a strict real-backend run or wait for the actual Hermes Agent source for
    final schema wiring.

## Previous heartbeat

- Time: 2026-05-30 14:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `95e6332`.
  - Verified the default shell still had no Studio URL, backend command, enabled
    CLI backend, or persistent local voices at the start of the heartbeat.
  - Verified the isolated OmniVoice Python venv under
    `~/.cache/hermes/omnivoice-python` is ready.
  - Created a non-cloned local designed voice profile named
    `heartbeat_narrator` with explicit confirmed consent metadata under
    `~/.hermes/voices/omnivoice`.
  - Confirmed the default runtime now sees one local voice profile while still
    requiring an explicit backend command export.
  - Exported the prepared Python adapter command for command-scoped checks and
    confirmed strict real-backend acceptance now passes.
  - Ran `scripts/test-omnivoice-tts.sh` through the prepared adapter; it
    generated a valid temporary WAV from "Hermes custom voice synthesis test."
  - Generated and then removed a temporary preview WAV for the persistent
    `heartbeat_narrator` profile.
  - Updated acceptance and MVP handoff docs with the new strict backend
    readiness path.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `tail -n 210 HEARTBEAT.md`
  - `find ~/.hermes/voices/omnivoice -maxdepth 3 -type f -name voice.yaml -print`
  - `python3 scripts/hermes-omnivoice-voices.py list`
  - `python3 scripts/create-omnivoice-voice.py design heartbeat_narrator --name "Heartbeat Narrator" --instruct "male, american accent, moderate pitch" --confirm-consent`
  - `python3 scripts/hermes-omnivoice-voices.py info heartbeat_narrator`
  - `HERMES_OMNIVOICE_COMMAND_JSON=... HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice python3 scripts/check-omnivoice-runtime.py --json`
  - `HERMES_OMNIVOICE_COMMAND_JSON=... HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `HERMES_OMNIVOICE_COMMAND_JSON=... HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice scripts/test-omnivoice-tts.sh`
  - `HERMES_OMNIVOICE_COMMAND_JSON=... HERMES_OMNIVOICE_MODEL=k2-fsa/OmniVoice python3 scripts/hermes-omnivoice-voices.py preview heartbeat_narrator --out /tmp/hermes-heartbeat-narrator.wav`
  - `rm -f /tmp/hermes-heartbeat-narrator.wav /private/tmp/hermes-heartbeat-narrator.wav`
  - `scripts/validate-omnivoice-bridge.sh`
  - `git diff --check`
  - `find . -type f (...) -print`
- Tests:
  - Strict real-backend acceptance with exported Python adapter: PASS;
    `real_backend_ready: true`.
  - `scripts/test-omnivoice-tts.sh` with exported Python adapter: PASS; valid
    temporary WAV generated from the required smoke text.
  - Persistent profile preview: PASS; valid temporary WAV generated and removed.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 76 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - Default shell runtime remains unconfigured: no Studio URL, backend command,
    or enabled CLI backend unless the adapter command is explicitly exported.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - A designed local profile with confirmed consent metadata is acceptable
    heartbeat test state because it contains no cloned user voice sample and is
    stored outside the repo.
  - The Python adapter path is the fastest usable local MVP path until the real
    Hermes Agent source is available for final command-provider or native
    provider wiring.
- Next action:
  - Commit the strict-backend-readiness handoff update, then focus remaining
    work on locating the actual Hermes Agent source or packaging a final branch
    summary.

## Previous heartbeat

- Time: 2026-05-30 15:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `c1ff2a7`.
  - Added `--shell` output mode to `scripts/setup-omnivoice-python-env.py`.
    It prints shell-safe exports for `HERMES_OMNIVOICE_COMMAND_JSON` and
    `HERMES_OMNIVOICE_MODEL` from the prepared adapter plan.
  - Added unit coverage proving the shell output parses back into the expected
    command JSON.
  - Updated README, setup, acceptance, handoff, and custom-voices docs to point
    operators at `python scripts/setup-omnivoice-python-env.py --check-only --shell`.
  - Verified the generated shell exports drive strict real-backend acceptance
    through the prepared Python adapter and the local `heartbeat_narrator`
    profile.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `rg --files | sort`
  - `sed -n ... scripts/setup-omnivoice-python-env.py`
  - `rg -n "setup_env|setup-omnivoice|print_human|PythonEnvSetup" tests/test_omnivoice_tts.py scripts/setup-omnivoice-python-env.py docs README.md`
  - `sed -n ... tests/test_omnivoice_tts.py`
  - `sed -n ... README.md`
  - `python3 -m unittest tests.test_omnivoice_tts.PythonEnvSetupTests -v`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --shell`
  - `python3 -m py_compile scripts/setup-omnivoice-python-env.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
- Tests:
  - `python3 -m unittest tests.test_omnivoice_tts.PythonEnvSetupTests -v`:
    PASS, 6 tests.
  - `python3 -m py_compile scripts/setup-omnivoice-python-env.py tests/test_omnivoice_tts.py`:
    PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 77 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Printing exports from the setup helper is safer than asking operators to
    manually copy a long JSON command from docs.
  - The prepared Python adapter path is the primary reproducible local backend
    path until a compatible Studio runtime or actual Hermes Agent source is
    available.
- Next action:
  - Commit the shell-export helper, then prepare a final branch summary or keep
    searching for the actual Hermes Agent source if more local hints appear.

## Previous heartbeat

- Time: 2026-05-30 15:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `ad35305`.
  - Rechecked default runtime state: no backend command exported by default,
    one local designed profile present under `~/.hermes/voices/omnivoice`, and
    the isolated OmniVoice Python venv ready.
  - Added `docs/omnivoice-weekend-summary.md` as a concise branch summary with
    delivered MVP scope, proven local backend path, latest validation evidence,
    blockers, security notes, and next steps.
  - Linked the weekend summary from README.
  - Re-ran deterministic validation and strict real-backend acceptance using the
    generated shell exports.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -12`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `tail -n 240 HEARTBEAT.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
- Tests:
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 77 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under `/Users/mhedhli/Documents/Coding/hermes`.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - A concise weekend summary is now the best handoff surface for another
    operator or for installing into the real Hermes Agent source tree.
  - Further native-provider work should wait for the real Hermes Agent checkout
    rather than guessing at its TTS schema.
- Next action:
  - Commit the weekend summary, then either locate the actual Hermes Agent
    checkout or keep the branch clean for handoff.

## Previous heartbeat

- Time: 2026-05-30 16:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `4d475a9`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can print
    shell-safe exports for strict real-backend acceptance.
  - Confirmed no active broad workspace source-search processes remained after
    the noisy manual search; the only remaining command-line match was a
    long-lived Codex helper process containing older prompt text.
  - Re-ran bounded Hermes source discovery. It still finds only this bridge repo
    under the Hermes/Coding roots and reports no likely Hermes Agent checkout.
  - Updated the setup, acceptance, MVP handoff, and weekend summary docs to
    direct operators toward explicit candidate roots or
    `scripts/find-hermes-source.py` instead of broad workspace grep.
  - Re-ran deterministic validation and strict real-backend acceptance using the
    generated shell exports.
- Commands run:
  - `ps ax -o pid,ppid,stat,etime,command | rg 'find-hermes-source|find /Users/mhedhli/Documents/Coding|rg -n .*Hermes Agent|sed .*/.git' || true`
  - `pgrep -x find | xargs -r ps -o pid,ppid,stat,etime,command -p`
  - `pgrep -x rg | xargs -r ps -o pid,ppid,stat,etime,command -p`
  - `pgrep -x sed | xargs -r ps -o pid,ppid,stat,etime,command -p`
  - `pgrep -fl find-hermes-source.py || true`
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding --scan-timeout 8 --max-candidates 40 --json`
  - `rg -n "source discover|find-hermes-source|Hermes Agent source|native provider|weekend summary|broad" docs HEARTBEAT.md README.md scripts tests examples`
  - `sed -n ... HEARTBEAT.md docs/omnivoice-weekend-summary.md docs/omnivoice-mvp-handoff.md docs/omnivoice-setup.md docs/omnivoice-acceptance.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Bounded Hermes source discovery: PASS as a check, but reports
    `no_likely_hermes_agent`; one candidate was this bridge repo only.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 77 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Native-provider work should remain deferred until a real Hermes Agent
    checkout is available and source discovery can inspect its TTS schema.
  - Bounded helper output is the handoff evidence; broad workspace grep is too
    noisy for this repo.
- Next action:
  - Commit the bounded-source-discovery handoff docs, then keep the branch clean
    for handoff or install into the real Hermes Agent checkout once found.

## Previous heartbeat

- Time: 2026-05-30 16:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `813c5ab`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready.
  - Added `docs/omnivoice-weekend-summary.md` to the conservative installer
    base manifest so dry-run or real installs into Hermes carry the final
    operator handoff.
  - Added the weekend summary to the static acceptance required-file gate.
  - Updated the MVP handoff to call out that the weekend summary is included in
    the install manifest.
  - Re-ran targeted installer/acceptance tests, install dry-run, deterministic
    validation, and strict real-backend acceptance using generated shell exports.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `tail -n 220 HEARTBEAT.md`
  - `rg -n "TODO|FIXME|Next Steps|Remaining Blockers|Open follow-ups|native provider|actual Hermes|source discovery|install" README.md docs scripts tests examples HEARTBEAT.md`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py examples README.md .gitignore scripts/omnivoice-acceptance.py scripts/validate-omnivoice-bridge.sh`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted installer and acceptance tests: PASS, 10 tests.
  - Installer dry-run: PASS; base manifest now includes 18 files including
    `docs/omnivoice-weekend-summary.md`.
  - Default acceptance: PASS for static MVP with 23 required files; expected
    `real_backend_ready: false` and `hermes_source_ready: false` in the default
    shell.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 77 tests with 1
    expected opt-in real-backend skip, py_compile, fake-backend smoke,
    unconfigured smoke skip, secret-pattern scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - The installer manifest should carry the concise weekend summary because it
    is now the best first-read handoff artifact for a real Hermes checkout.
  - Native-provider work should still wait for real Hermes Agent source.
- Next action:
  - Commit the installer/acceptance manifest update, then keep the branch clean
    for handoff or install into the real Hermes Agent checkout once found.

## Previous heartbeat

- Time: 2026-05-30 17:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `8e06899`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready.
  - Split acceptance static checks into installed bridge files and local
    package-only handoff files. This keeps `scripts/omnivoice-acceptance.py`
    meaningful after a default install into a real Hermes checkout, while still
    allowing strict local package validation in this repo.
  - Added `--require-package-files` for strict local package handoff checks and
    wired it into `scripts/validate-omnivoice-bridge.sh`.
  - Added coverage proving acceptance succeeds after a default installer copy
    even though package-only files such as the installer and heartbeat record
    are not copied into the target.
  - Updated acceptance and MVP handoff docs to describe installed bridge
    readiness versus package-only handoff files.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py scripts/omnivoice-acceptance.py HEARTBEAT.md tests/test_omnivoice_tts.py docs/omnivoice-acceptance.md docs/omnivoice-mvp-handoff.md`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 scripts/omnivoice-acceptance.py --json`
  - `python3 scripts/omnivoice-acceptance.py --require-package-files --json`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `python3 -m py_compile scripts/omnivoice-acceptance.py scripts/validate-omnivoice-bridge.sh tests/test_omnivoice_tts.py`
  - `python3 -m py_compile scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted acceptance and installer tests: PASS, 11 tests.
  - Default acceptance: PASS; installed bridge files present with
    `required_count: 18`, package handoff files present with
    `required_count: 6`, expected `real_backend_ready: false` and
    `hermes_source_ready: false` in the default shell.
  - Strict package-file acceptance: PASS.
  - Installer dry-run: PASS; base manifest remains 18 files.
  - `python3 -m py_compile scripts/omnivoice-acceptance.py scripts/validate-omnivoice-bridge.sh tests/test_omnivoice_tts.py`: FAIL as expected because `scripts/validate-omnivoice-bridge.sh` is a shell script, not Python.
  - Corrected Python-only py_compile: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 78 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Acceptance should be useful both in this source package and after the bridge
    is copied into a real Hermes checkout.
  - Package-only files should stay reported and strictly checkable here without
    making default installed-target acceptance fail.
- Next action:
  - Commit the acceptance/install handoff hardening, then keep the branch clean
    for handoff or install into the real Hermes Agent checkout once found.

## Previous heartbeat

- Time: 2026-05-30 17:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `2d8ace4`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready.
  - Added optional installer support for target `.gitignore` safety coverage.
    The installer now reports missing local-artifact ignore patterns by default
    and only appends a managed block when `--update-gitignore` is explicitly
    requested.
  - Kept the `.gitignore` change dry-run-first and idempotent, with tests for
    missing-pattern reporting, dry-run no-write behavior, append behavior, and
    rerun behavior.
  - Updated README, setup, MVP handoff, and weekend summary docs to explain
    reviewing installer `.gitignore` output before using `--update-gitignore`.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `tail -n 230 HEARTBEAT.md`
  - `rg -n "gitignore|\\.gitignore|ignore|generated audio|voice samples|model files|local config|cache" README.md docs scripts tests examples .gitignore HEARTBEAT.md`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py docs/omnivoice-setup.md docs/omnivoice-mvp-handoff.md README.md`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --update-gitignore --json`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted installer tests: PASS, 6 tests.
  - Installer dry-run without `.gitignore` update: PASS; reports
    `gitignore.action: review` and missing local-artifact patterns without
    writing a target `.gitignore`.
  - Installer dry-run with `--update-gitignore`: PASS; reports
    `gitignore.action: would_append` without writing.
  - Python py_compile for installer and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 80 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - A real Hermes checkout should not be silently edited beyond the requested
    install; `.gitignore` safety changes should be explicit and reviewable.
  - The managed ignore block should be idempotent and focused on OmniVoice local
    audio, voice, model, cache, and config artifacts.
- Next action:
  - Commit the installer `.gitignore` safety option, then keep the branch clean
    for handoff or install into the real Hermes Agent checkout once found.

## Previous heartbeat

- Time: 2026-05-30 18:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `d726802`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready.
  - Tightened the target installer `.gitignore` safety block to include
    `.env.*`, matching this repo's local-config protection and covering
    environment-specific local config files beyond `.env.local`.
  - Updated installer coverage to assert `.env.*` is present in the managed
    target ignore block.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --update-gitignore --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted installer tests: PASS, 6 tests.
  - Python py_compile for installer and tests: PASS.
  - Installer dry-run without `.gitignore` update: PASS; reports `.env.*` in
    missing local-artifact patterns and writes nothing.
  - Installer dry-run with `--update-gitignore`: PASS; reports `.env.*` in the
    managed block that would be appended.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 80 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Target checkout ignore coverage should match this repo's `.env.*` policy so
    environment-specific local config does not get committed after install.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the `.env.*` installer ignore hardening, then keep the branch clean
    for handoff or install into the real Hermes Agent checkout once found.

## Previous heartbeat

- Time: 2026-05-30 18:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `6712828`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready.
  - Fixed installer handling for existing managed target `.gitignore` blocks:
    if the managed block is stale, `--update-gitignore` now refreshes it in
    place instead of treating it as complete.
  - Added coverage for refreshing an older managed block and proving reruns stay
    idempotent.
  - Updated README, setup, and MVP handoff docs to document managed block
    refresh behavior.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --update-gitignore --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted installer tests: PASS, 7 tests.
  - Python py_compile for installer and tests: PASS.
  - Installer dry-run without `.gitignore` update: PASS; reports review action
    for missing local-artifact patterns without writing.
  - Installer dry-run with `--update-gitignore`: PASS; reports append action for
    a target without a managed block.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 81 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Managed target `.gitignore` blocks may need future refresh as ignore
    patterns evolve; the installer should handle that idempotently.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the managed `.gitignore` refresh fix, then keep the branch clean for
    handoff or install into the real Hermes Agent checkout once found.

## Previous heartbeat

- Time: 2026-05-30 19:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `6e8b526`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Added installer regression coverage proving a managed target `.gitignore`
    refresh preserves user-owned rules before and after the managed Hermes
    OmniVoice block.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -10`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `sed -n ... tests/test_omnivoice_tts.py scripts/install-hermes-omnivoice-bridge.py HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff -- tests/test_omnivoice_tts.py`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted installer tests: PASS, 7 tests.
  - Python py_compile for installer and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 81 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Target repositories may have user-owned ignore rules before and after the
    Hermes managed block; installer safety depends on preserving that context.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 19:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `adfa47b`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Refreshed the packaged MVP handoff and weekend summary snapshots from the
    older 16:00/77-test state to the current 19:30/81-test state.
  - Documented the now-tested installer `.gitignore` behavior in the packaged
    handoff: default dry-runs do not write, and explicit
    `--update-gitignore` appends or refreshes the managed block while
    preserving surrounding user-owned rules.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `rg -n "Latest heartbeat|Previous heartbeat|Open follow|Next action|install|acceptance|handoff|manifest" HEARTBEAT.md docs scripts tests README.md examples`
  - `sed -n ... HEARTBEAT.md scripts/omnivoice-acceptance.py scripts/validate-omnivoice-bridge.sh docs/omnivoice-weekend-summary.md docs/omnivoice-mvp-handoff.md README.md docs/omnivoice-setup.md`
  - `rg -n "77 tests|Status as of 2026-05-30 16:00|As of 2026-05-30 16:00" docs README.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff -- docs/omnivoice-weekend-summary.md docs/omnivoice-mvp-handoff.md`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Stale handoff grep: PASS; no remaining `77 tests` or old `16:00` snapshot
    strings in README/docs.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 81 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
  - Whitespace check: PASS.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - The packaged handoff docs should be treated as first-read operator artifacts
    because the installer copies them into a real Hermes checkout.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 20:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `c693538`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Improved the installer non-JSON `.gitignore` output so handoff users see
    readable review, append, and refresh messages instead of raw action codes
    such as `would_append`.
  - Added installer coverage for human-readable `.gitignore` review, append,
    and refresh messages.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 20:00/82-test validation state and documented that JSON keeps exact
    action codes for automation.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `rg -n "TODO|FIXME|77 tests|16:00|Next action|Open follow-ups|source path|install into|dry-run|package handoff|weekend summary|\\.gitignore" README.md docs scripts tests examples HEARTBEAT.md`
  - `sed -n ... scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-human --dry-run`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-human --dry-run --update-gitignore`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rg -n "81 tests|19:30|82 tests|20:00" docs HEARTBEAT.md README.md`
  - `git diff -- scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `git diff --check`
  - `find . -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted installer tests: PASS, 8 tests.
  - Python py_compile for installer and tests: PASS.
  - Installer human dry-run output: PASS; default path prints review guidance
    and `--update-gitignore --dry-run` prints a readable append action.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 82 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
  - Whitespace check: PASS.
- Blockers:
  - Actual Hermes Agent source is still not present locally; source discovery
    sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Non-JSON installer output is what a human operator will see during a
    dry-run-first handoff, so it should be readable without decoding JSON action
    names.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 20:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `cc9c2c7`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Re-ran bounded source discovery across the Hermes, Projects, and Coding
    roots; it still finds only this bridge repo and no likely Hermes Agent
    checkout.
  - Moved the generated-audio/model/env/local-selection artifact scan into
    `scripts/validate-omnivoice-bridge.sh`, so the standard validator now
    enforces the safety check that previous heartbeats ran manually.
  - Updated README, acceptance docs, and integration notes to document that the
    validator includes safety scans.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding/Projects --root /Users/mhedhli/Documents/Coding --max-candidates 30 --scan-timeout 8 --json`
  - `bash -n scripts/validate-omnivoice-bridge.sh`
  - `rg -n "secret-pattern|artifact scan|generated audio|validate-omnivoice-bridge" docs README.md HEARTBEAT.md`
  - `sed -n ... docs/omnivoice-acceptance.md README.md docs/omnivoice-integration-notes.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `git diff --check`
  - `find . -path './.git' -prune -o -type f (...) -print`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Source discovery: PASS as a bounded negative check; `likely_count: 0`,
    `candidate_count: 1`, bridge repo marked `likely_hermes_agent: false`.
  - Shell syntax check for `scripts/validate-omnivoice-bridge.sh`: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 82 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`.
  - Repo artifact scan: PASS; no generated audio, model weights, env files, or
    local voice selection state found in the repo.
  - Whitespace check: PASS.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Generated audio, model files, `.env*`, and local voice selection state
    should be validator-enforced because they are security-sensitive artifacts.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 21:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `34aa6d4`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Replaced the inline shell artifact scan with
    `scripts/check-omnivoice-artifacts.py`, a package-only helper that reports
    generated audio, model files, `.env*`, and local selection state.
  - Added unit coverage for artifact detection, `.git` pruning, and CLI failure
    on forbidden artifacts.
  - Wired the artifact checker into package acceptance and the standard
    validation script.
  - Updated README, acceptance docs, integration notes, MVP handoff, and weekend
    summary docs for the helper-backed artifact safety gate.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `sed -n ... scripts/validate-omnivoice-bridge.sh tests/test_omnivoice_tts.py`
  - `chmod +x scripts/check-omnivoice-artifacts.py`
  - `python3 -m unittest tests.test_omnivoice_tts.ArtifactCheckTests tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 -m py_compile scripts/check-omnivoice-artifacts.py scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `rg -n "TOKEN|SECRET|PASSWORD|API_KEY" tests/test_omnivoice_tts.py scripts/check-omnivoice-artifacts.py README.md docs/omnivoice-acceptance.md`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `git diff --check`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted artifact and acceptance tests: PASS, 9 tests.
  - Python py_compile for artifact checker, acceptance, and tests: PASS.
  - Secret-pattern fixture probe: PASS after replacing a test fixture's
    secret-like `TOKEN` marker with a neutral local-only value.
  - First full validation attempt: FAIL as expected after the new artifact test
    introduced the literal `TOKEN`; the secret-pattern scan caught it before
    commit.
  - `scripts/validate-omnivoice-bridge.sh`: PASS after fixture cleanup; includes
    84 tests with 1 expected opt-in real-backend skip, py_compile, strict
    package-file acceptance, fake-backend smoke, unconfigured smoke skip,
    secret-pattern scan, helper-backed generated-artifact scan, and
    `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Direct artifact checker: PASS; `ok: true`, `matches: []`.
  - Whitespace check: PASS.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - The generated-artifact rule should live in Python with unit coverage because
    it is a security-sensitive repo hygiene gate.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 21:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `64ee8ef`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Rechecked the direct artifact checker; repo artifact state remains clean.
  - Added coverage proving package-only validation files, including
    `scripts/check-omnivoice-artifacts.py` and
    `scripts/validate-omnivoice-bridge.sh`, are intentionally excluded from the
    default Hermes runtime install payload.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 21:30/85-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `rg -n "check-omnivoice-artifacts|PACKAGE_REQUIRED_FILES|BASE_MANIFEST|EXAMPLE_MANIFEST|84 tests|21:00|package_files|required_count|artifact checker|artifact scan" README.md docs scripts tests HEARTBEAT.md`
  - `sed -n ... tests/test_omnivoice_tts.py scripts/install-hermes-omnivoice-bridge.py scripts/omnivoice-acceptance.py HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile tests/test_omnivoice_tts.py scripts/install-hermes-omnivoice-bridge.py scripts/omnivoice-acceptance.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rg -n "84 tests|21:00" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
- Tests:
  - Targeted acceptance and installer tests: PASS, 16 tests.
  - Python py_compile for acceptance, installer, and tests: PASS.
  - Installer dry-run: PASS; default payload remains 18 runtime bridge files and
    docs, with package-only validation helpers excluded.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 85 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Direct artifact checker: PASS; `ok: true`, `matches: []`.
  - Stale handoff grep: PASS; no remaining `84 tests` or old `21:00` snapshot
    strings in first-read handoff docs.
  - Whitespace check: PASS.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Package-only validation helpers should remain available for this bridge repo
    while staying out of the default runtime install into Hermes.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 22:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `fe7fc23`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Hardened `scripts/check-omnivoice-artifacts.py` so top-level artifact,
    cache, model, and local voice directories fail validation even when their
    contents do not use forbidden file extensions.
  - Added unit coverage proving top-level `.cache/`, `.hermes/`, `models/`, and
    `voices/` are rejected while nested `examples/voices/` templates remain
    allowed.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 22:00/86-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `rg -n "85 tests|21:30|package-only|default install|check-omnivoice-artifacts|validation helpers|TODO|FIXME|Open follow-ups|Next action" README.md docs scripts tests HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile tests/test_omnivoice_tts.py scripts/install-hermes-omnivoice-bridge.py scripts/omnivoice-acceptance.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `python3 -m unittest tests.test_omnivoice_tts.ArtifactCheckTests tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 -m py_compile scripts/check-omnivoice-artifacts.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
- Tests:
  - Targeted artifact and acceptance tests: PASS, 11 tests.
  - Python py_compile for artifact checker and tests: PASS.
  - Direct artifact checker: PASS; `ok: true`, `matches: []`.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 86 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Top-level local artifact directories are unsafe repo roots, even when their
    current contents are extension-neutral.
  - Nested sample templates such as `examples/voices/` are safe to keep because
    they do not contain committed voice samples or generated audio.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 22:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `6df3d70`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Re-ran bounded Hermes source discovery; it still sees only this bridge repo
    and no likely Hermes Agent checkout.
  - Extended the repo artifact checker to reject top-level `samples/`,
    `voice-samples/`, and `reference-audio/` directories.
  - Extended the installer-managed `.gitignore` safety block with the same
    top-level sample-directory patterns.
  - Updated README, acceptance docs, MVP handoff, and weekend summary docs for
    the sample-directory safety boundary.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|actual Hermes|find-hermes-source|install|acceptance|package-only|artifact" README.md docs scripts tests HEARTBEAT.md`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding --max-depth 5 --max-candidates 20 --scan-timeout 5 --json`
  - `python3 -m unittest tests.test_omnivoice_tts.ArtifactCheckTests tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/check-omnivoice-artifacts.py scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `python3 scripts/install-hermes-omnivoice-bridge.py --target-root /tmp/hermes-omnivoice-install-check --dry-run --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
- Tests:
  - Targeted artifact and installer tests: PASS, 11 tests.
  - Python py_compile for artifact checker, installer, and tests: PASS.
  - Direct artifact checker: PASS; `ok: true`, `matches: []`.
  - Installer dry-run: PASS; default payload remains 18 files and now reports
    missing `/samples/`, `/voice-samples/`, and `/reference-audio/` target
    `.gitignore` patterns.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 86 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Top-level local sample directories should be treated as unsafe repo roots
    because they can contain consent-sensitive voice material or transcripts.
  - Nested sample templates such as `examples/voices/` are safe to keep because
    they do not contain committed voice samples or generated audio.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 23:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `28789e3`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Re-ran bounded Hermes source discovery; it still sees only this bridge repo
    and no likely Hermes Agent checkout.
  - Added repo `.gitignore` coverage for `omnivoice-output/` and
    `omnivoice-cache/` to match the installer and artifact checker.
  - Added regression coverage ensuring every top-level directory forbidden by
    `scripts/check-omnivoice-artifacts.py` has matching repo and installer
    `.gitignore` coverage.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 23:00/87-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|artifact|\\.gitignore|sample directories|model|cache|acceptance|source discovery" README.md docs scripts tests HEARTBEAT.md .gitignore`
  - `python3 -m unittest tests.test_omnivoice_tts.ArtifactCheckTests tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/check-omnivoice-artifacts.py scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `python3 scripts/find-hermes-source.py --root /Users/mhedhli/Documents/Coding/hermes --root /Users/mhedhli/Documents/Coding --max-depth 5 --max-candidates 20 --scan-timeout 5 --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
- Tests:
  - Targeted artifact and installer tests: PASS, 12 tests.
  - Python py_compile for artifact checker, installer, and tests: PASS.
  - Direct artifact checker: PASS; `ok: true`, `matches: []`.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 87 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - The artifact checker denylist and ignore patterns should stay mechanically
    aligned because both are security-sensitive handoff surfaces.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-30 23:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `8563f2d`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Updated human acceptance output so missing package-only handoff extras are
    labeled `INCOMPLETE`, not `BLOCKED`, after a default install into a real
    Hermes checkout.
  - Kept strict package validation behavior unchanged via
    `--require-package-files`.
  - Added installed-checkout human-output regression coverage.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 23:30/88-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -8`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `python3 scripts/setup-omnivoice-python-env.py --check-only --json`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|follow-up|blocked|artifact|\\.gitignore|acceptance|source discovery|sample|cache" README.md docs scripts tests HEARTBEAT.md .gitignore`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 -m py_compile scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `python3 scripts/omnivoice-acceptance.py --source-root /tmp/nonexistent-hermes-root`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
- Tests:
  - Targeted acceptance tests: PASS, 9 tests.
  - Python py_compile for acceptance and tests: PASS.
  - Human default acceptance smoke: PASS; package files show `PASS` in this
    complete bridge repo.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 88 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Package-only files are useful in this bridge repo but expected to be absent
    after a default runtime install into Hermes.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-31 00:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `3501811`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Confirmed the isolated OmniVoice Python venv remains ready and can provide
    shell exports for the real OmniVoice adapter command.
  - Added regression coverage proving `--require-package-files` still fails
    after a default runtime install omits package-only validation helpers.
  - Kept human acceptance output non-blocking for the same expected default
    install absence by labeling package-only extras `INCOMPLETE`.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 00:00/89-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git diff -- tests/test_omnivoice_tts.py`
  - `rg -n "23:30 America/New_York|88 tests|Latest heartbeat|Decision log|Open follow-ups" HEARTBEAT.md docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 -m py_compile scripts/omnivoice-acceptance.py tests/test_omnivoice_tts.py`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rg -n "23:30 America/New_York|88 tests|23:00 America/New_York|87 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `find . -type d -name __pycache__ -print`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `git status --short`
- Tests:
  - Targeted acceptance tests: PASS, 10 tests.
  - Python py_compile for acceptance and tests: PASS.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 89 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Default runtime installs should stay lightweight and omit package-only
    validation helpers, while package completeness remains explicitly checkable
    in this bridge repo with `--require-package-files`.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Keep the branch clean for handoff, or install the bridge into the real
    Hermes Agent checkout once the source path is available.

## Previous heartbeat

- Time: 2026-05-31 00:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `cefc49f`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Inspected the installer and acceptance manifests for handoff drift.
  - Added regression coverage proving the acceptance bridge required-file list
    and default installer runtime payload contain the same file set.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 00:30/90-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|blocked|source discovery|install|acceptance|package|handoff|manifest|native provider" README.md docs scripts tests HEARTBEAT.md`
  - `sed -n '1,260p' scripts/install-hermes-omnivoice-bridge.py`
  - `sed -n '1,240p' scripts/omnivoice-acceptance.py`
  - `sed -n '1748,2210p' tests/test_omnivoice_tts.py`
  - `python3 -m unittest tests.test_omnivoice_tts.AcceptanceTests -v`
  - `python3 -m py_compile scripts/omnivoice-acceptance.py scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `rg -n "00:00 America/New_York|89 tests|23:30 America/New_York|88 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
- Tests:
  - Targeted acceptance tests: PASS, 11 tests after making the manifest guard
    order-insensitive.
  - Python py_compile for acceptance, installer, and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 90 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Stale handoff snapshot scan: PASS; no 00:00/89-test or older summary state
    remains in the current handoff docs.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
  - The first order-sensitive draft of the manifest guard failed because the
    lists contain the same files in a different order; the committed test now
    verifies exact membership instead.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Acceptance and installer manifests should match by file membership; ordering
    is not currently significant to runtime behavior.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the manifest drift guard and keep the branch clean for handoff, or
    install the bridge into the real Hermes Agent checkout once the source path
    is available.

## Previous heartbeat

- Time: 2026-05-31 01:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `7200d99`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Verified installer payload runtime scripts are tracked executable.
  - Added installer regression coverage proving runtime script executable bits
    survive a real default install into a target checkout.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 01:00/91-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|blocked|source discovery|install|acceptance|package|handoff|manifest|executable|mode" README.md docs scripts tests HEARTBEAT.md`
  - `git ls-files -s scripts/validate-omnivoice-bridge.sh scripts/test-omnivoice-tts.sh scripts/install-hermes-omnivoice-bridge.py scripts/hermes-omnivoice-tts.py scripts/omnivoice-acceptance.py`
  - `sed -n '2008,2210p' tests/test_omnivoice_tts.py`
  - `sed -n '1,80p' scripts/validate-omnivoice-bridge.sh`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `rg -n "00:30 America/New_York|90 tests|00:00 America/New_York|89 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
- Tests:
  - Targeted installer tests: PASS, 9 tests.
  - Python py_compile for installer and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 91 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Stale handoff snapshot scan: PASS; no 00:30/90-test or older summary state
    remains in the current handoff docs.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Installed runtime scripts should remain directly executable because the docs
    and validation flow use direct script invocations.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the executable-mode guard and keep the branch clean for handoff, or
    install the bridge into the real Hermes Agent checkout once the source path
    is available.

## Previous heartbeat

- Time: 2026-05-31 01:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `3e95898`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Inspected installed-checkout smoke behavior for the default unconfigured
    path.
  - Added installer regression coverage proving a copied
    `scripts/test-omnivoice-tts.sh` exits with the documented 77 skip when no
    backend environment is configured.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 01:30/92-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|blocked|source discovery|install|acceptance|test-omnivoice|runtime|executable|smoke" README.md docs scripts tests HEARTBEAT.md`
  - `sed -n '1,160p' scripts/test-omnivoice-tts.sh`
  - `rg -n "subprocess|run\\(|Popen|CompletedProcess" tests/test_omnivoice_tts.py`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `rg -n "01:00 America/New_York|91 tests|00:30 America/New_York|90 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
- Tests:
  - Targeted installer tests: PASS, 10 tests.
  - Python py_compile for installer and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 92 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Stale handoff snapshot scan: PASS; no 01:00/91-test or older summary state
    remains in the current handoff docs.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Installed checkouts should fail closed for smoke synthesis until a local
    backend path is explicitly configured.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the installed-smoke skip guard and keep the branch clean for handoff,
    or install the bridge into the real Hermes Agent checkout once the source
    path is available.

## Previous heartbeat

- Time: 2026-05-31 02:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `3282abe`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Inspected installed-checkout smoke behavior and existing command backend
    fixture coverage.
  - Added installer regression coverage proving a copied
    `scripts/test-omnivoice-tts.sh` succeeds with an explicit local
    `HERMES_OMNIVOICE_COMMAND_JSON` backend.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 02:00/93-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "installed.*smoke|test-omnivoice|fake_omnivoice|HERMES_OMNIVOICE_COMMAND_JSON|subprocess" tests scripts docs README.md HEARTBEAT.md`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `rg -n "01:30 America/New_York|92 tests|01:00 America/New_York|91 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
- Tests:
  - Targeted installer tests: PASS, 11 tests.
  - Python py_compile for installer and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 93 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Stale handoff snapshot scan: PASS; no 01:30/92-test or older summary state
    remains in the current handoff docs.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Installed checkouts should support the documented command-backend smoke path
    while still requiring explicit backend configuration.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the installed-smoke configured-backend guard and keep the branch clean
    for handoff, or install the bridge into the real Hermes Agent checkout once
    the source path is available.

## Previous heartbeat

- Time: 2026-05-31 02:30 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `3662f6b`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Inspected installed example voice templates and the copied voice helper
    path.
  - Added installer regression coverage proving the copied
    `scripts/hermes-omnivoice-voices.py` reports the installed `narrator`
    design example as ready.
  - Added fail-closed coverage proving the installed clone example `marvin`
    remains invalid until the user supplies the consented `ref.wav` sample.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 02:30/94-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "with-examples|examples/voices|hermes-omnivoice-voices|config command|voice helper|installed.*example|example.*install" README.md docs scripts tests HEARTBEAT.md`
  - `sed -n '1,240p' scripts/hermes-omnivoice-voices.py`
  - `cat examples/voices/narrator/voice.yaml`
  - `cat examples/voices/marvin/voice.yaml`
  - `python3 -m unittest tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/install-hermes-omnivoice-bridge.py scripts/hermes-omnivoice-voices.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `rg -n "02:00 America/New_York|93 tests|01:30 America/New_York|92 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
- Tests:
  - Targeted installer tests: PASS, 12 tests.
  - Python py_compile for installer, voice helper, and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 94 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Stale handoff snapshot scan: PASS; no 02:00/93-test or older summary state
    remains in the current handoff docs.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Installed examples are templates only; clone examples must remain invalid
    until explicit user-provided reference audio exists.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the installed example voice guard and keep the branch clean for
    handoff, or install the bridge into the real Hermes Agent checkout once the
    source path is available.

## Latest heartbeat

- Time: 2026-05-31 03:00 America/New_York
- Completed:
  - Rechecked repo state; branch was clean at commit `9bf5b28`.
  - Rechecked default runtime state: no backend command, no Studio URL, no
    auto CLI by default, and one local designed profile present.
  - Inspected the voice helper config output, the static Hermes TTS example,
    and command-provider documentation.
  - Updated `scripts/hermes-omnivoice-voices.py config` so generated wrapper
    commands include the configured `--voices-dir` path.
  - Added regression coverage that custom registry paths and static script
    paths with spaces are shell-quoted in generated command-provider config.
  - Updated the example Hermes TTS config and docs to show that generated
    config carries the voice registry path.
  - Refreshed the packaged MVP handoff and weekend summary snapshots to the
    current 03:00/95-test validation state.
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -6`
  - `python3 scripts/check-omnivoice-runtime.py --json`
  - `rg -n "TODO|FIXME|Open follow-ups|Next action|example|config|install|Hermes Agent|source discovery|native provider" README.md docs scripts tests examples HEARTBEAT.md`
  - `sed -n '180,275p' scripts/hermes-omnivoice-voices.py`
  - `sed -n '2340,2395p' tests/test_omnivoice_tts.py`
  - `cat examples/hermes-tts-omnivoice.yaml`
  - `rg -n "voices-dir|config .*voice|hermes-omnivoice-voices.py config|command-provider config" README.md docs examples tests scripts`
  - `python3 -m unittest tests.test_omnivoice_tts.VoiceCliTests tests.test_omnivoice_tts.InstallerTests -v`
  - `python3 -m py_compile scripts/hermes-omnivoice-voices.py tests/test_omnivoice_tts.py`
  - `scripts/validate-omnivoice-bridge.sh`
  - `eval "$(python3 scripts/setup-omnivoice-python-env.py --check-only --shell)" && python3 scripts/omnivoice-acceptance.py --require-real-backend --json`
  - `rm -rf tests/__pycache__ tests/fixtures/__pycache__ scripts/__pycache__`
  - `rg -n "02:30 America/New_York|94 tests|02:00 America/New_York|93 tests" docs/omnivoice-mvp-handoff.md docs/omnivoice-weekend-summary.md README.md docs/omnivoice-acceptance.md`
  - `git diff --check`
  - `python3 scripts/check-omnivoice-artifacts.py --json`
- Tests:
  - Targeted voice helper and installer tests: PASS, 18 tests.
  - Python py_compile for voice helper and tests: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS; includes 95 tests with 1
    expected opt-in real-backend skip, py_compile, strict package-file
    acceptance, fake-backend smoke, unconfigured smoke skip, secret-pattern
    scan, helper-backed generated-artifact scan, and `git diff --check`.
  - Strict real-backend acceptance after evaluating generated shell exports:
    PASS; `real_backend_ready: true`, `hermes_source_ready: false`,
    `package_files.required_count: 7`.
  - Stale handoff snapshot scan: PASS; no 02:30/94-test or older summary state
    remains in the current handoff docs.
  - Repo artifact scan: PASS; no generated audio, models, local voice samples,
    env files, caches, or local selection state found.
- Blockers:
  - Actual Hermes Agent source is still not present locally; bounded source
    discovery sees only this bridge repo under the searched roots.
  - Default shell runtime remains unconfigured unless the generated exports are
    applied.
  - Studio live service remains blocked by the missing arm64 published image and
    source-build timeout noted in earlier heartbeats.
- Assumptions:
  - Generated command-provider config should carry the chosen registry path so
    custom installs and example registries remain reproducible.
  - Native-provider work still waits on the actual Hermes Agent source.
- Next action:
  - Commit the config-generation registry-path guard and keep the branch clean
    for handoff, or install the bridge into the real Hermes Agent checkout once
    the source path is available.

## Decision log

- Use a command-provider bridge first because the scheduled workspace was empty.
- Make PyYAML optional and include a small YAML subset parser so the wrapper can
  run in a minimal local Hermes environment.
- Require `consent.status: confirmed` for all voice profiles, with cloned voices
  additionally requiring `ref_audio` and `ref_text`.
- Prefer `HERMES_OMNIVOICE_COMMAND_JSON` over shell strings to avoid quoting and
  injection hazards.
- Use OmniVoice-Studio HTTP APIs for import/generation before considering direct
  SQLite reads.
- Refuse non-loopback Studio URLs by default because Studio has no built-in
  authentication.
- Keep the fake backend confined to tests and docs as a contract verifier only;
  never present it as a real TTS engine.
- Provide voice UX through a standalone helper until the real Hermes command
  layer can be inspected.
- Keep future validation centered on `scripts/validate-omnivoice-bridge.sh` so
  every heartbeat has the same deterministic local evidence.
- Cover both backend-command mode and Studio API mode in local tests before
  attempting heavier real-model smoke validation.
- Treat voice IDs and resolved voice directories as security-sensitive registry
  inputs; reject dot-segment IDs and symlink escapes rather than following them.
- Treat cloned voice reference audio as a validated WAV-only input and avoid
  overwriting existing local profile directories without `--force`.
- Prefer read-only runtime checks before synthesis attempts so setup blockers
  are explicit without touching generated media or user voice samples.
- Validate Docker Compose loopback bindings before any local Studio startup
  helper runs.
- Track static MVP readiness separately from real-backend readiness so progress
  is not overstated when model-backed synthesis remains unavailable.
- Prefer a no-overwrite, dry-run-first installer for handing the bridge to a
  real Hermes checkout.
- Keep selected voice state outside the repo and validate profiles before
  writing selection metadata.
- Use local-only Studio startup probes before downloading or building large
  model-backed containers.
- Keep a single MVP handoff page in the package so install and live-readiness
  work does not depend on reading the full heartbeat history.
- Use upstream `omnivoice-infer` for direct CLI synthesis and require explicit
  `HERMES_OMNIVOICE_AUTO_CLI=1` opt-in before the wrapper invokes it.
- Keep direct Python API usage behind an explicit command adapter so the main
  wrapper does not import or initialize model dependencies unless configured.
- Use dry-run/check-only environment setup before installing OmniVoice runtime
  dependencies so package and cache behavior remain visible.
- Prefer Python 3.10-3.13 for the OmniVoice Python environment; reject newer
  interpreters by default because model runtime wheels may not be available.
- Validate English OmniVoice design prompts against the upstream supported tag
  vocabulary before model startup to avoid expensive late failures.
- Import the Python API adapter from `omnivoice.models.omnivoice` and keep
  device detection local, matching the installed upstream package layout.
- Bound local Studio Docker/Git subprocesses by default so automation cannot
  hang indefinitely on a stalled image pull or build.
- Keep heavyweight model-backed unittest synthesis opt-in with
  `HERMES_OMNIVOICE_RUN_REAL_TEST=1`; default validation should skip it.
- Keep Hermes source discovery read-only, bounded, and strict enough that
  unrelated repos with generic TTS text are not marked as Hermes Agent.
- Track Hermes source readiness as a separate acceptance gate from real backend
  readiness; both are external to the standalone bridge repo.
- Preserve already-discovered Hermes source candidates when a later broad scan
  hits its timeout; a truncated search should degrade the report, not erase it.
- Preflight local Studio no-pull/no-build startup against Docker image
  availability before invoking Compose.
- Pull Studio images explicitly before Compose startup for no-build pull-enabled
  runs, so registry and platform failures happen before Compose resources are
  created.
- Keep Studio source builds bounded during heartbeat automation; on this Mac
  they can consume multi-GB Docker/PyTorch layers and exceed short heartbeat
  windows before producing a runnable container.
- Treat the isolated OmniVoice Python venv as prepared runtime capacity, not as
  default runtime readiness until an adapter command or CLI gate and a consented
  local voice profile are configured.
- Use a designed `heartbeat_narrator` profile for local real-backend acceptance
  instead of cloning any voice sample.
- Print adapter backend exports through the setup helper so real-backend
  acceptance can be reproduced without hand-copying long JSON.
- Include the weekend summary in the installer and static acceptance gate so a
  real Hermes checkout receives the same concise operator handoff as this repo.
- Split installed-bridge acceptance from package-only handoff checks so the
  copied acceptance script can run successfully in a real Hermes checkout while
  local package completeness remains strictly checkable.
- Keep target `.gitignore` edits explicit with `--update-gitignore`; default
  installer runs report missing local-artifact coverage without modifying the
  target checkout.
- Include `.env.*` in target `.gitignore` safety coverage so environment-specific
  local config is protected after bridge installation.
- Refresh existing managed target `.gitignore` blocks when the installer pattern
  list changes, instead of treating any marked block as complete forever.
- Keep installer JSON exact for automation but make non-JSON `.gitignore`
  messages readable for human dry-run handoffs.
- Enforce generated-audio, model, env, and local selection artifact absence in
  the standard validation script instead of relying on manual heartbeat scans.
- Keep the generated-artifact denylist in a testable Python helper while the
  shell validator remains the single operator entrypoint.
- Keep package-only validation helpers out of the default Hermes runtime install
  payload; install should copy bridge runtime files and handoff docs by default.
- Treat top-level artifact/cache/local voice directories as forbidden repo state
  while preserving nested example templates that contain no local voice samples.
- Treat top-level local sample directories as forbidden repo state and include
  matching installer `.gitignore` coverage for real Hermes checkouts.
- Keep artifact checker top-level directory rules aligned with both repo and
  installer `.gitignore` coverage through tests.
- Keep package-only handoff files visible in human acceptance output without
  labeling their expected default-install absence as a blocker.
- Keep strict package-file validation failing after default runtime installs so
  local package completeness cannot be silently downgraded by the human
  non-blocking output label.
- Pin acceptance required-file membership to the default installer payload so
  runtime handoff coverage cannot drift while preserving order-independent
  installer behavior.
- Preserve executable modes across installer copies because direct script
  invocation is part of the documented local validation and operator handoff
  path.
- Preserve the unconfigured smoke-test exit 77 behavior after default installs
  so target checkouts do not accidentally attempt backend synthesis without an
  explicit local backend configuration.
- Preserve the installed smoke-test configured-backend path so real target
  checkouts can prove the wrapper contract with a local command backend before
  using a heavyweight model.
- Keep installed clone example templates invalid until a user supplies a real
  consented reference WAV; do not commit placeholder voice samples.
- Include the voice registry path in generated command-provider config because
  relying on wrapper defaults can route Hermes to the wrong local profile root.

## Open follow-ups

- Start a local loopback Studio container with a compatible image or a longer
  supervised source build, then run the Studio importer against that live local
  service.
- Locate or clone the actual Hermes Agent source and verify the TTS schema with
  `scripts/find-hermes-source.py`.
- Consider a native Hermes provider only after the actual Hermes Agent source
  and provider schema are available.
