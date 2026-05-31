# OmniVoice Weekend Summary

Status as of 2026-05-30 20:00 America/New_York on branch
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

- `scripts/validate-omnivoice-bridge.sh`: PASS, 82 tests with 1 expected
  opt-in real-backend skip.
- `python scripts/omnivoice-acceptance.py --require-real-backend` after
  evaluating `setup-omnivoice-python-env.py --check-only --shell`: PASS.
- `scripts/test-omnivoice-tts.sh` with the generated adapter exports: PASS,
  generated a valid temporary WAV from "Hermes custom voice synthesis test."
- Installer `.gitignore` safety coverage: PASS. Default dry-runs report missing
  local-artifact coverage without writing, and `--update-gitignore` appends or
  refreshes the managed block while preserving user-owned rules around it. The
  non-JSON installer output now uses human-readable review, append, and refresh
  messages instead of raw action codes.
- Repo artifact scan: PASS, no generated audio, model weights, env files, or
  local voice selection state found in the repo.

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
- Cloned voices require `consent.status: confirmed`, `ref_audio`, `ref_text`,
  and a readable WAV reference file.
- Non-loopback Studio URLs are refused by default.
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
