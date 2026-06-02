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

- Time: 2026-06-02 18:54 America/New_York
- Completed:
  - Confirmed Hermes active provider was `xtts-v2` before testing and after
    rollback.
  - Confirmed the Hermes config backup/rollback path was available and created
    a fresh live-soak backup at
    `/home/claude/.hermes/config.yaml.pre-omnivoice-live-soak-20260602T224827Z.bak`.
  - Confirmed the Mac Studio helper path remained executable from `hermes-01`:
    `/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech`.
  - Ran `scripts/test-omnivoice-remote.sh` from `hermes-01` through SSH helper
    mode: PASS, 2.00s wrapper latency, generated output under
    `/home/claude/.cache/hermes/omnivoice-remote-smoke/`.
  - Ran a 20-prompt direct SSH-helper soak through
    `scripts/hermes-omnivoice-remote.py`: 20 PASS, 0 failures, 0 retries.
  - Ran a 5-prompt live Hermes provider soak after temporarily switching
    `tts.provider` to `omnivoice-remote-ssh-loopback`: 5 PASS, 0 failures, 0
    retries.
  - Rolled Hermes back to `xtts-v2` and ran an `xtts-v2` rollback smoke: PASS.
  - Confirmed the Mac Studio service is listening on `127.0.0.1:8880`; no
    firewall, Tailscale ACL, UniFi, VLAN, or network-policy changes were made.
- Soak results:
  - Direct wrapper soak: latency min/median/max 1.714s / 2.122s / 2.597s;
    output duration range 2.160s-6.760s; artifacts at
    `/home/claude/.cache/hermes/omnivoice-remote-soak/20260602T224637Z/`.
  - Live Hermes provider soak: latency min/median/max 1.949s / 2.059s /
    2.346s; output duration range 1.7565s-4.0665s; artifacts at
    `/home/claude/.cache/hermes/omnivoice-remote-live-soak/20260602T224827Z/`.
  - Rollback smoke: PASS, 53.172s latency, final active provider `xtts-v2`.
- Local review artifact copies:
  - `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-soak-20260602T224637Z/`
  - `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-soak-20260602T224827Z/`
- Subjective QC:
  - Previous and new samples are available locally for review.
  - Human listening was not possible from this Codex execution environment, so
    intelligibility, pacing, pronunciation, consistency, artifacts,
    naturalness, and operator-acceptability scores remain pending.
- Security review:
  - No token value was read, printed, copied, or passed in argv.
  - Mac Studio accessible logs and process args showed no bearer-token pattern
    hits.
  - Hermes history and process args showed no bearer-token pattern hits.
  - Local repo pattern hits were documentation/test/code placeholders and
    ignored bytecode, not observed token values.
  - `git status --short` was clean before doc edits; no generated audio, local
    env files, private keys, model files, caches, or voice samples were staged.
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 226 tests, 3 skipped.
  - `python3 scripts/omnivoice-acceptance.py --require-package-files`: PASS
    for package/static checks; local real-backend and Hermes-source checks are
    blocked as expected in this bridge checkout.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - `python3 scripts/check-omnivoice-artifacts.py`: PASS.
  - Remote `scripts/test-omnivoice-remote.sh` from `hermes-01`: PASS, 2.23s
    wrapper latency.
  - `git diff --check`: PASS.
  - `shellcheck`: not installed on this workstation.
- Recommendation:
  - Reliability gate passed for SSH-loopback helper mode.
  - Do not approve OmniVoice as the unattended default.
  - Do not mark final manual-operator voice quality approved until a human
    listening QC pass records scores. Use only for bounded/manual evaluation
    with explicit rollback available.

## Previous Heartbeat

- Time: 2026-06-02 18:08 America/New_York
- Completed:
  - Added SSH-loopback remote-helper support to
    `scripts/hermes-omnivoice-remote.py` so Hermes can call the Mac Studio
    helper without copying a bearer token to Hermes.
  - Deployed the updated remote wrapper and smoke script to
    `/opt/hermes-local-tts/omnivoice-bridge/scripts/` on `hermes-01`, outside
    the Hermes source checkout.
  - Confirmed preflight active provider was `xtts-v2`, staged
    `tts.providers.omnivoice-remote-ssh-loopback`, and backed up
    `/home/claude/.hermes/config.yaml` before edits.
  - Ran `scripts/test-omnivoice-remote.sh` from `hermes-01` through
    `hermes-ops@100.78.163.62` using the restricted host key and remote helper:
    PASS, generated a 115,724-byte WAV, 2.410s duration, 1.94s wrapper latency.
  - Temporarily switched Hermes to `omnivoice-remote-ssh-loopback`, ran three
    live `tools.tts_tool.text_to_speech_tool` prompts, and rolled back to
    `xtts-v2`.
  - Corrected the remote provider command from `python` to `python3` after the
    first activation attempt failed before synthesis with `/bin/sh: 1: python:
    not found`; rollback passed before retry.
- Live Hermes results:
  - Short: PASS, 2.056s latency, 2.956500s Opus, 24,046 bytes.
  - Medium: PASS, 2.254s latency, 4.196500s Opus, 34,082 bytes.
  - Edge: PASS, 2.579s latency, 5.386500s Opus, 43,769 bytes.
  - Rollback smoke on `xtts-v2`: PASS, 54.308s latency, 4.871167s Opus,
    39,556 bytes.
  - Final active provider: `xtts-v2`.
- Artifacts:
  - Remote host samples:
    `/home/claude/.cache/hermes/omnivoice-remote-live-trial/20260602T220621Z/`.
  - Local review copies:
    `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-20260602T220621Z/`.
  - Generated audio stayed out of git.
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 226 tests, 3 skipped.
  - `python3 scripts/omnivoice-acceptance.py --require-package-files`: PASS
    for package/static checks; local real-backend and Hermes-source checks are
    blocked as expected in this bridge checkout.
  - `scripts/validate-omnivoice-bridge.sh`: PASS.
  - `python3 scripts/check-omnivoice-artifacts.py`: PASS.
  - Remote `scripts/test-omnivoice-remote.sh` from `hermes-01`: PASS.
  - `git diff --check`: PASS.
  - `shellcheck`: not installed on this workstation.
- Blockers:
  - Direct HTTP to `100.78.163.62:8880` remains a separate diagnostic backlog.
  - Subjective listening QC is still pending.
- Next action:
  - Use remote OmniVoice SSH-loopback helper mode for manual operator requests
    when the Mac Studio voice is desired; keep `xtts-v2` as the unattended
    default until QC and a longer soak pass.

## Previous Heartbeat

- Time: 2026-06-02 17:09 America/New_York
- Completed:
  - Retried Mac Studio OmniVoice validation through the approved admin SSH
    route, without using `hermes-ops`, `sudo`, or token/env file reads.
  - The requested `/Volumes/mhedhli/.ssh/colpanicm2_macstudio_admin_ed25519`
    key path was not mounted in this process; the same-named local admin key at
    `/Users/mhedhli/.ssh/colpanicm2_macstudio_admin_ed25519` was present with
    private file permissions and was used for this smoke.
  - Confirmed `/Users/mhedhli/.local/bin/omnivoice-client-smoke health`
    returns `ok=true`, `provider=omnivoice`, `device=mps`,
    `model_id=k2-fsa/OmniVoice`, `sample_rate=24000`, and `voice_count=1`.
  - Confirmed the helper lists `homelab_narrator` as a consent-confirmed
    designed voice with no reference audio.
  - Generated one remote speech sample through the helper using the prompt
    `ColPanicM2 OmniVoice integration smoke test.`
  - Copied back only the generated WAV artifact path returned by the helper to
    `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/`; no token/env
    files were read or copied.
- Tests:
  - Admin SSH helper health: PASS.
  - Admin SSH helper voice list: PASS.
  - Admin SSH helper speech smoke: PASS, HTTP 200, 153,644-byte WAV, 3.200
    seconds audio, 2.166 seconds reported latency, RTF 0.6769.
  - Repo remote wrapper smoke: NOT RUN in this slice; the helper proves the
    Mac Studio service/token path, but the current repo wrapper still needs a
    local token file or a dedicated helper transport.
  - Live Hermes tool-path smoke: NOT RUN.
  - Rollback: NOT NEEDED; Hermes config was not changed.
- Blockers:
  - A Hermes-side command-provider trial still needs either a safe wrapper path
    to call the operator helper or a local protected token file usable by the
    existing SSH loopback wrapper.
  - Direct HTTP to `100.78.163.62:8880` remains a separate diagnostic follow-up.
- Assumptions:
  - Continue to keep Mac Studio token/env files opaque and out of git.
  - Generated audio artifacts remain local-only and outside the repo checkout.
- Next action:
  - Add or configure a Hermes-compatible remote helper transport, then run the
    live Hermes `tools.tts_tool.text_to_speech_tool` path with generated
    samples posted as chat artifacts.

## Previous Heartbeat

- Time: 2026-06-02 15:05 America/New_York
- Completed:
  - Started SSH loopback live validation preflight for
    `hermes-ops@100.78.163.62`.
  - Confirmed repo branch, clean tracked state, and required remote wrapper,
    smoke script, and SSH loopback example files.
  - Confirmed default SSH to `hermes-ops@100.78.163.62` fails with public key
    authentication denied.
  - Confirmed the local Mac Studio admin key can SSH to
    `mhedhli@100.78.163.62`.
  - Confirmed noninteractive `sudo -u hermes-ops` from the admin session
    requires a password and is not usable for unattended smoke.
  - Confirmed Mac Studio loopback TCP on `127.0.0.1:8880` accepts connections
    and unauthenticated `/health` returns HTTP 401.
  - Added `OMNIVOICE_REMOTE_VOICE` as a smoke-script alias for the existing
    test voice variable.
  - Documented the blocked smoke attempt in the remote MVP doc and operator
    runbook.
- Tests:
  - Live SSH loopback smoke: BLOCKED before synthesis because direct
    `hermes-ops` SSH auth is unavailable and no local protected token file is
    present in this process.
  - Direct wrapper sample tests: SKIPPED for the same token/SSH auth blocker.
  - Live Hermes tool-path smoke: SKIPPED because Phase 2 and Phase 3 did not
    pass.
  - Rollback: NOT NEEDED; Hermes config was not changed.
- Blockers:
  - Need `hermes-ops@100.78.163.62` SSH key access or a local mode `600`
    `OMNIVOICE_REMOTE_TOKEN_FILE` usable with an approved SSH route.
  - Direct HTTP to `100.78.163.62:8880` remains a separate network diagnostic
    follow-up and was not changed in this lane.
- Assumptions:
  - Do not print or copy token values into logs; no token value was read or
    printed during this attempt.
  - Generated samples should be posted in chat once a live smoke actually
    generates them; no samples were produced in this attempt.
- Next action:
  - Install or provide safe `hermes-ops` SSH/token access, then rerun
    `scripts/test-omnivoice-remote.sh` with `ssh-loopback` env configured.

## Previous Heartbeat

- Time: 2026-06-02 12:43 America/New_York
- Completed:
  - Added SSH loopback transport support to
    `scripts/hermes-omnivoice-remote.py` while preserving direct `http` mode.
  - Added protected token-file support with token-file precedence over
    `OMNIVOICE_REMOTE_API_TOKEN`.
  - Updated `scripts/test-omnivoice-remote.sh` for `http` and `ssh-loopback`
    smoke tests with health checks, local artifact output, and expected skip
    behavior when env is missing.
  - Added `examples/hermes-tts-omnivoice-remote-ssh-loopback.yaml` and updated
    README, setup, remote MVP, and operator runbook docs.
  - Recorded the current proven Mac Studio route:
    `hermes-ops@100.78.163.62` over SSH to loopback
    `http://127.0.0.1:8880`.
- Tests:
  - `python3 -m unittest discover -s tests -v`: PASS, 224 tests with 3
    expected skips.
  - `python3 scripts/omnivoice-acceptance.py --require-package-files`: PASS.
  - `scripts/validate-omnivoice-bridge.sh`: PASS, including remote smoke skip
    behavior when remote env is unconfigured.
  - `python3 scripts/check-omnivoice-artifacts.py`: PASS.
  - `scripts/test-omnivoice-remote.sh` with remote env cleared: SKIP with
    status 77 as expected.
  - `git diff --check`: PASS.
  - `shellcheck`: not installed on this workstation.
  - Live SSH loopback smoke: SKIPPED locally because
    `OMNIVOICE_REMOTE_SSH_HOST` and token env are not present in this process.
- Blockers:
  - Direct HTTP to `100.78.163.62:8880` still times out and remains a separate
    network diagnostic follow-up.
  - Do not expose the Mac Studio OmniVoice service beyond loopback.
- Assumptions:
  - Mac Studio service remains bearer-authenticated, MPS-backed, and
    loopback-only.
  - Token files are protected mode `600`; real token paths stay out of git.
- Next action:
  - Commit the SSH loopback transport slice, then run live remote smoke from
    an environment with SSH host and token file configured.

## Previous Heartbeat

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
