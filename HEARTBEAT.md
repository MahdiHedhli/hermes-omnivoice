# Hermes OmniVoice Integration Heartbeat

## Current status

Initial heartbeat started against an empty scheduled workspace. The repo now has
a command-provider MVP foundation plus a localhost-only OmniVoice-Studio API
bridge and Studio profile importer.

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

## Latest heartbeat

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

## Open follow-ups

- Locate or clone the actual Hermes Agent source and verify the TTS schema.
- Run the Studio importer against a live local Studio service.
- Configure a real OmniVoice backend command and run `scripts/test-omnivoice-tts.sh`.
- Consider a native Hermes provider only after command-provider synthesis works.
