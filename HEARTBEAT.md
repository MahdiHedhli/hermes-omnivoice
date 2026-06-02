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
