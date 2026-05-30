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
now plans and inspects an isolated OmniVoice Python venv outside the repo.

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

## Latest heartbeat

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

## Open follow-ups

- Locate or clone the actual Hermes Agent source and verify the TTS schema.
- Start a local loopback Studio container and run the Studio importer against a
  live local Studio service.
- Configure a real OmniVoice backend command or install `omnivoice-infer`, then
  run `scripts/test-omnivoice-tts.sh`.
- Install `omnivoice` in an isolated local environment and smoke-test the
  Python adapter with a consented designed or cloned voice profile.
- Use `scripts/setup-omnivoice-python-env.py` for the isolated install/check
  flow before running a real Python API smoke test.
- Locate the actual Hermes Agent source before wiring native `/voice` commands.
- Consider a native Hermes provider only after command-provider synthesis works.
