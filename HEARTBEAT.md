# Hermes OmniVoice Integration Heartbeat

## Current status

Initial heartbeat started against an empty scheduled workspace. I initialized a
fresh bridge repo on `feature/omnivoice-custom-voices` and implemented the
least-invasive command-provider MVP foundation.

## Latest heartbeat

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

## Decision log

- Use a command-provider bridge first because the scheduled workspace was empty.
- Make PyYAML optional and include a small YAML subset parser so the wrapper can
  run in a minimal local Hermes environment.
- Require `consent.status: confirmed` for all voice profiles, with cloned voices
  additionally requiring `ref_audio` and `ref_text`.
- Prefer `HERMES_OMNIVOICE_COMMAND_JSON` over shell strings to avoid quoting and
  injection hazards.

## Open follow-ups

- Locate or clone the actual Hermes Agent source and verify the TTS schema.
- Inspect OmniVoice-Studio backend routes and storage before adding an importer.
- Configure a real OmniVoice backend command and run `scripts/test-omnivoice-tts.sh`.
- Consider a native Hermes provider only after command-provider synthesis works.
