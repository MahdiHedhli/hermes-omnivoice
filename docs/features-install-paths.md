# Features And Install Paths

This is the detailed inventory for the Hermes OmniVoice-Studio bridge. It
captures what the repo currently ships, where the pieces install, and which
paths are local-only operational state.

## Feature Inventory

| Area | Feature | Files |
| --- | --- | --- |
| Hermes command provider | Local TTS wrapper for OmniVoice-compatible voices | `scripts/hermes-omnivoice-tts.py` |
| Remote TTS | Authenticated direct HTTP and SSH-loopback FastAPI wrapper | `scripts/hermes-omnivoice-remote.py` |
| Remote pacing | Opt-in speed, punctuation normalization, sentence breaks, and max sentence length | `scripts/hermes-omnivoice-remote.py`, `scripts/test-omnivoice-remote.sh` |
| Python API mode | Direct OmniVoice Python API adapter | `scripts/hermes-omnivoice-python-adapter.py` |
| Runtime setup | Isolated local Python runtime planning/install/checks | `scripts/setup-omnivoice-python-env.py` |
| Voice registry | Designed and cloned voice profile creation | `scripts/create-omnivoice-voice.py` |
| Studio bridge | Import OmniVoice-Studio profiles into Hermes registry | `scripts/import-omnivoice-studio-voice.py` |
| Voice CLI | List, inspect, select, preview, and print provider config | `scripts/hermes-omnivoice-voices.py` |
| Runtime diagnostics | Backend, Studio, CLI, and registry readiness checks | `scripts/check-omnivoice-runtime.py` |
| Installer | Dry-run-first copy into a Hermes checkout or staging root | `scripts/install-hermes-omnivoice-bridge.py` |
| Studio local helper | Loopback-only Docker Compose helper for OmniVoice-Studio | `scripts/omnivoice-studio-local.py` |
| Operator controls | Status, enable, and rollback scripts | `scripts/omnivoice-status.sh`, `scripts/omnivoice-enable.sh`, `scripts/omnivoice-disable.sh` |
| QC workflow | Repeatable voice-labeled sample generation and listening rubric | `scripts/omnivoice-qc-sample.sh`, `docs/omnivoice-qc.md` |
| Smoke tests | Local and remote TTS smoke tests | `scripts/test-omnivoice-tts.sh`, `scripts/test-omnivoice-remote.sh` |
| Acceptance | Static package readiness and live backend summary | `scripts/omnivoice-acceptance.py` |
| Validation | Unit tests, smoke checks, artifact guard, secret hygiene, diff check | `scripts/validate-omnivoice-bridge.sh` |
| Artifact guard | Detect generated audio, local env, model files, caches, local voices | `scripts/check-omnivoice-artifacts.py` |
| Hermes discovery | Read-only scoring of candidate Hermes source checkouts | `scripts/find-hermes-source.py` |

## Public Defaults

These paths are safe defaults or templates for new installs.

| Path | Purpose | Commit? |
| --- | --- | --- |
| `/path/to/hermes-agent` | Real Hermes Agent checkout | No |
| `/opt/hermes-local-tts/omnivoice-bridge` | Suggested bridge install root outside Hermes source | No |
| `~/.hermes/config.yaml` | Hermes runtime config | No |
| `~/.hermes/voices/omnivoice/<voice_id>/voice.yaml` | Voice profile metadata | No |
| `~/.hermes/voices/omnivoice/<voice_id>/ref.wav` | Optional clone reference audio | No |
| `~/.hermes/omnivoice-selection.json` | Current local OmniVoice selection | No |
| `~/.hermes/omnivoice-remote.env` | Optional remote env file | No |
| `~/.cache/hermes/omnivoice-python` | Optional isolated OmniVoice Python runtime | No |
| `~/.cache/hermes/omnivoice-qc/qc-<timestamp>/` | Voice-labeled QC/tuning samples and local result JSON | No |
| `~/.cache/hermes/omnivoice-remote-smoke/` | Remote smoke generated samples | No |
| `omnivoice-output/` | Local generated output scratch dir | No |
| `omnivoice-cache/` | Local cache scratch dir | No |

## Validated Homelab Paths

These paths describe the tested private deployment. They are useful for
operator runbooks, but they are not required for a generic install.

| Path | Purpose |
| --- | --- |
| `/opt/hermes-agent/source` | Hermes source checkout on `hermes-01` |
| `/opt/hermes-local-tts/omnivoice-bridge` | Installed bridge symlink/root on `hermes-01` |
| `/home/claude/.hermes/config.yaml` | Live Hermes runtime config |
| `/home/claude/.hermes/voices/omnivoice` | Live Hermes OmniVoice voice registry |
| `/home/claude/.ssh/hermes_ops_macstudio_ed25519` | Restricted SSH identity used by Hermes host |
| `/home/claude/.cache/hermes/omnivoice-remote-smoke/` | Remote smoke output on Hermes |
| `/home/claude/.cache/hermes/omnivoice-remote-soak/` | Direct SSH-helper soak output on Hermes |
| `/home/claude/.cache/hermes/omnivoice-remote-live-soak/` | Live provider soak output on Hermes |
| `/Users/hermes-ops/Services/omnivoice` | Mac Studio OmniVoice service root |
| `/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech` | Mac Studio helper called over SSH |
| `/Users/hermes-ops/Services/omnivoice/config/omnivoice.env` | Protected Mac Studio token env file; never print or copy values |
| `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/` | Local review copies outside git |

## Voice Profile Shape

Designed voices:

```yaml
engine: omnivoice
kind: design
voice_id: narrator
instruct: "male, american accent, moderate pitch"
consent:
  status: confirmed
  source: user_created
  allowed_uses:
    - personal_assistant
```

Cloned voices:

```yaml
engine: omnivoice
kind: clone
voice_id: marvin
ref_audio: ref.wav
ref_text: "Reference transcript for the consented voice sample."
consent:
  status: confirmed
  source: user_created
  allowed_uses:
    - personal_assistant
```

Cloned voices must have `consent.status: confirmed`, non-empty
`consent.source`, non-empty `consent.allowed_uses`, readable WAV reference
audio, and non-empty `ref_text`.

## Backend Modes

| Mode | Config |
| --- | --- |
| Studio loopback | `HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:<port>` |
| Custom command JSON | `HERMES_OMNIVOICE_COMMAND_JSON='[...]'` |
| Custom command string | `HERMES_OMNIVOICE_COMMAND='...'` |
| Auto CLI | `HERMES_OMNIVOICE_AUTO_CLI=1` with `omnivoice-infer` on `PATH` |
| Direct HTTP remote | `OMNIVOICE_REMOTE_TRANSPORT=http` |
| SSH loopback remote | `OMNIVOICE_REMOTE_TRANSPORT=ssh-loopback` |
| SSH helper remote | `OMNIVOICE_REMOTE_HELPER=/absolute/remote/helper` |

Prefer command JSON over command strings for custom adapters because it avoids
shell quoting hazards.

## Git Hygiene

Do not commit:

- generated audio: `*.wav`, `*.mp3`, `*.flac`, `*.ogg`, `*.m4a`,
- voice samples or reference audio,
- model weights or inference caches,
- `.env`, `.env.*`, populated runtime env files, or token files,
- private SSH keys,
- local Hermes config or voice selection state,
- private operator notes.

Run the guard before publishing:

```bash
python3 scripts/check-omnivoice-artifacts.py
git diff --check
```

## Current Approval Boundary

- Manual/bounded evaluation: reliability passed.
- Human voice-quality approval: passed for bounded manual operator use.
- Unattended default: not approved until pacing consistency and fallback
  behavior are addressed.
- Native provider: deferred.
- `/voice` UX: deferred.
