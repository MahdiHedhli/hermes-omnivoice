# Hermes OmniVoice Integration Heartbeat

## Current Status

This repo delivers a command-provider MVP for using OmniVoice and
OmniVoice-Studio managed voices from Hermes Agent TTS. It includes:

- A Hermes-facing TTS wrapper.
- A local voice registry with consent gates.
- Designed and cloned voice profile helpers.
- A loopback-only OmniVoice-Studio import path.
- A direct OmniVoice Python adapter.
- Runtime diagnostics, installer, acceptance checks, and regression tests.

The command-provider path has been validated on a private Hermes deployment
with OmniVoice configured as the active TTS provider for a temporary smoke test.
That test generated valid audio through Hermes' normal TTS tool path and then
restored the previous provider.

## Latest Heartbeat

- Time: 2026-06-02 10:30 America/New_York
- Completed:
  - Started the remote FastAPI MVP lane on
    `feature/omnivoice-remote-fastapi-mvp`.
  - Added a remote Hermes command-provider client for an authenticated
    OmniVoice FastAPI service over Tailscale.
  - Added a remote smoke script, sample Hermes remote provider config,
    `.env.example`, and remote MVP docs.
  - Reviewed `diogod2r/OmniVoice-FastAPI` at
    `930cb452437f4c4987d9b184e9a0074fbfd3bb37` and documented why it needs
    auth hardening before use.
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 218 tests with 3
    expected skips.
  - `python3 scripts/omnivoice-acceptance.py --require-package-files`: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS, including remote smoke skip
    behavior when remote env is unconfigured.
  - `python3 scripts/check-omnivoice-artifacts.py`: PASS.
  - `scripts/test-omnivoice-remote.sh`: SKIP with status 77 because
    `OMNIVOICE_REMOTE_BASE_URL` and `OMNIVOICE_REMOTE_API_TOKEN` are not
    configured in this repo environment.
  - `git diff --check`: PASS.
  - `shellcheck`: not installed on this workstation.
- Blockers:
  - Mac Studio FastAPI availability and bearer token are not yet confirmed in
    this repo environment.
  - The candidate FastAPI service lacks auth in the reviewed revision; do not
    expose it without a fork/proxy auth layer and Tailscale ACLs.
- Assumptions:
  - Remote samples must be posted in chat as artifacts when generated and kept
    outside the repo.
- Next action:
  - Deploy or proxy the authenticated FastAPI service on the stronger
    Tailscale host, configure `OMNIVOICE_REMOTE_BASE_URL` and
    `OMNIVOICE_REMOTE_API_TOKEN`, then run the remote smoke and post generated
    samples in chat as artifacts.

## Previous Heartbeat

- Time: 2026-06-02 10:04 America/New_York
- Completed:
  - Added an operator-ready runbook for the validated command-provider MVP.
  - Added a repeatable subjective QC sample generator and listening rubric.
  - Added conservative provider status, enable, and disable scripts with
    dry-run mode, config-shape validation, redacted command reporting, and
    backup-before-write behavior.
  - Updated README/setup docs to state that OmniVoice is validated for manual
    operator use while `xtts-v2` remains the default.
  - Generated five local QC WAV samples with a consent-confirmed designed
    voice, moved them outside the repo, and posted them in chat as local
    artifacts.
- Tests:
  - `python3 scripts/omnivoice-acceptance.py --require-real-backend`: PASS.
  - `scripts/test-omnivoice-tts.sh`: PASS with real backend command exports.
  - `scripts/validate-omnivoice-bridge.sh`: PASS, 206 tests with one expected
    opt-in real-backend skip; fake smoke passed and unconfigured smoke skipped
    with status 77.
  - `python3 scripts/check-omnivoice-artifacts.py`: PASS after QC samples were
    moved outside the repo.
  - Operator script dry-runs with a temporary Hermes config fixture: PASS for
    status, enable, disable, and QC planning.
  - `git diff --check`: PASS.
  - `shellcheck`: not installed on this workstation.
- Blockers:
  - Native provider and `/voice` UX remain explicitly out of scope for this
    lane.
  - Automatic provider fallback is not available; rollback remains explicit
    operator action.
  - Subjective human listening/scoring is still pending.
- Assumptions:
  - Public docs should stay free of private hostnames, IPs, local operator
    paths, generated audio, and backend command details.
- Next action:
  - Commit docs and safe scripts only.

## Previous Heartbeat

- Time: 2026-06-02 09:45 America/New_York
- Completed:
  - Added `.gitignore` coverage for private operator/environment detail files.
  - Ran a bounded active-provider trial on a private Hermes deployment.
  - Confirmed preflight state: previous active provider was `xtts-v2`,
    `tts.providers.omnivoice` existed, the bridge and voice profile were
    present, and consent metadata was confirmed.
  - Created a host-local rollback helper outside the Hermes source checkout.
  - Temporarily switched `tts.provider` to `omnivoice`.
  - Ran three requested live Hermes TTS requests through
    `tools.tts_tool.text_to_speech_tool`.
  - Rolled back to `xtts-v2` and confirmed rollback with a post-rollback TTS
    smoke.
- Tests:
  - Short OmniVoice trial: PASS, 49.43s latency, 2.486s Opus output.
  - Medium OmniVoice trial: PASS, 78.67s latency, 4.707s Opus output.
  - Edge OmniVoice trial: PASS, 84.56s latency, 4.976s Opus output.
  - Fallback probe: no automatic fallback observed for a failing command
    provider.
  - Rollback provider smoke: PASS, active provider restored to `xtts-v2`.
- Blockers:
  - Native provider work remains deferred until a clean Hermes source branch is
    available.
  - Automatic provider fallback is not available; rollback is explicit operator
    action.
- Assumptions:
  - Operator-trial docs should remain public-safe and avoid private hostnames,
    IPs, workstation paths, or operator-specific runtime paths.
- Next action:
  - Run package validation and commit the docs/ignore update.

## Earlier Heartbeat

- Time: 2026-06-02 09:15 America/New_York
- Completed:
  - Temporarily switched a private Hermes deployment from its previous TTS
    provider to `omnivoice`.
  - Ran Hermes' normal TTS tool path without an in-memory provider override.
  - Verified the generated output was valid Opus audio.
  - Restored the previous TTS provider after the test.
  - Started public-release hardening for README, install docs, and status
    records.
- Tests:
  - Active-provider Hermes smoke: PASS, valid Opus output, about 49 seconds.
  - Previous installed-bridge acceptance: PASS for static MVP, real backend,
    and Hermes source readiness.
  - Previous local validator: PASS, 206 tests with 1 expected opt-in
    real-backend skip.
- Blockers:
  - Native Hermes provider work is deferred until it can be done against a
    clean Hermes source branch.
  - A live OmniVoice-Studio API is not required for the MVP; the proven route is
    the local OmniVoice Python backend through the command-provider wrapper.
- Assumptions:
  - Public documentation should not include private hostnames, private IPs,
    local workstation paths, or operator-specific runtime paths.
  - The command-provider MVP is the right public baseline before a native
    provider.
- Next action:
  - Finish public-facing documentation cleanup, run validation and artifact
    scans, then publish the repository to GitHub.

## Decision Log

- Keep the first Hermes integration as a command provider. It is compatible
  with existing Hermes TTS provider configuration and avoids invasive source
  changes.
- Keep OmniVoice-Studio on loopback by default. Remote Studio URLs require an
  explicit override and separate security review.
- Require confirmed consent metadata for cloned voices before synthesis.
- Keep generated audio, reference samples, model files, caches, environment
  files, local config, and local voice selections out of git.
- Prefer the packaged Python adapter for real local synthesis when the
  `omnivoice` package is installed.
- Use longer provider timeouts for real OmniVoice model startup and inference;
  public examples use 600 seconds.
