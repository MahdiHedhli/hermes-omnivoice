# OmniVoice Weekend Summary

Status as of 2026-05-31 07:30 America/New_York on branch
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

- `scripts/validate-omnivoice-bridge.sh`: PASS, 107 tests with 1 expected
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
  and `max_text_length: 2000`, and generated config honors explicit timeout
  and max-text-length overrides.
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
