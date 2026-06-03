# 🎙️ Hermes OmniVoice-Studio Bridge

Command-provider bridge for using custom OmniVoice and OmniVoice-Studio voices
from Hermes Agent TTS.

This project is built around a conservative MVP: keep Hermes internals
unchanged, register an OmniVoice command provider, enforce local voice consent
metadata, and make rollback to the existing TTS provider explicit.

## ✅ Current Status

| Area | Status |
| --- | --- |
| Local command-provider MVP | ✅ Implemented and tested |
| Custom voice registry | ✅ Designed and cloned profiles with consent gates |
| OmniVoice-Studio import path | ✅ Documented and loopback-first |
| Mac Studio SSH-loopback backend | ✅ Reliability soak passed |
| Hermes active default | ✅ Remains `xtts-v2` |
| Human listening QC | ✅ Manual operator use approved |
| Native Hermes provider | ⏸️ Deferred |
| `/voice` runtime UX | ⏸️ Deferred |
| Unattended OmniVoice default | ❌ Not approved until pacing/fallback are addressed |

The validated remote path passed a 20-prompt SSH-helper soak and a 5-prompt
live Hermes provider soak, then rolled Hermes back to `xtts-v2`. A human
listening pass approved OmniVoice SSH-loopback for bounded manual operator use.

## ✨ Feature Highlights

| Feature | What it does |
| --- | --- |
| 🎛️ Hermes TTS wrappers | Local and remote command-provider entrypoints for Hermes |
| 🗣️ Voice registry | `~/.hermes/voices/omnivoice/<voice_id>/voice.yaml` profiles |
| ✅ Consent gates | Cloned voices require confirmed consent metadata |
| 🎨 Designed voices | Prompt/instruction-based voice profiles |
| 🧬 Cloned voices | Reference-audio profiles with `ref_audio` and `ref_text` |
| 🧪 QC samples | Repeatable local sample generation for listening review |
| 🧰 Operator scripts | Status, enable, disable, smoke, acceptance, and validation helpers |
| 🔌 Studio bridge | Import/export guidance for OmniVoice-Studio-managed voices |
| 🐍 Python adapter | Optional direct OmniVoice Python API adapter |
| 🌐 Remote FastAPI | Authenticated HTTP transport for hardened deployments |
| 🔐 SSH-loopback helper | Mac Studio helper path that keeps bearer tokens off Hermes |
| 📦 Installer | Dry-run-first bridge installer for real Hermes checkouts |
| 🧹 Artifact guard | Prevents generated audio, model files, env files, and caches in git |

## 📍 Install Paths

Recommended/default paths:

| Path | Purpose |
| --- | --- |
| `/path/to/hermes-agent` | Real Hermes Agent source checkout |
| `/opt/hermes-local-tts/omnivoice-bridge` | Suggested bridge install path outside Hermes source |
| `~/.hermes/config.yaml` | Hermes runtime config |
| `~/.hermes/voices/omnivoice/<voice_id>/voice.yaml` | Voice registry profile |
| `~/.hermes/voices/omnivoice/<voice_id>/ref.wav` | Optional cloned voice reference audio |
| `~/.hermes/omnivoice-selection.json` | Current local voice selection |
| `~/.cache/hermes/omnivoice-python` | Optional isolated OmniVoice Python runtime |
| `~/.cache/hermes/omnivoice-qc/` | Local QC sample output |
| `~/.cache/hermes/omnivoice-remote-smoke/` | Remote smoke-test output |

Mac Studio lane path pattern. Replace service users, hosts, and key paths for
your deployment:

| Path | Purpose |
| --- | --- |
| `/opt/hermes-agent/source` | Hermes source checkout |
| `/opt/hermes-local-tts/omnivoice-bridge` | Installed bridge root |
| `~/.hermes/voices/omnivoice` | Hermes-side voice registry |
| `~/.ssh/<restricted-omnivoice-key>` | Restricted SSH identity used by Hermes host |
| `/Users/<omnivoice-service-user>/Services/omnivoice` | Mac Studio OmniVoice service root |
| `/Users/<omnivoice-service-user>/Services/omnivoice/bin/omnivoice-remote-speech` | Mac Studio helper |
| `/Users/<omnivoice-service-user>/Services/omnivoice/config/omnivoice.env` | Protected Mac Studio token env file; value is never copied or logged |
| `~/.cache/hermes/omnivoice-chat-artifacts/` | Local review copies outside git |

For the full inventory, see
[`docs/features-install-paths.md`](docs/features-install-paths.md).

## 🚀 Quick Start

Validate the bridge locally:

```bash
scripts/validate-omnivoice-bridge.sh
python3 scripts/omnivoice-acceptance.py --require-package-files
```

Create a designed voice profile:

```bash
python3 scripts/create-omnivoice-voice.py design narrator \
  --instruct "male, american accent, moderate pitch" \
  --confirm-consent
```

Create a cloned voice profile:

```bash
python3 scripts/create-omnivoice-voice.py clone marvin \
  --ref-audio /path/to/consented-reference.wav \
  --ref-text "Reference transcript for the voice sample." \
  --consent-source user_created \
  --consent-allowed-use personal_assistant \
  --confirm-consent
```

Check local runtime readiness:

```bash
python3 scripts/check-omnivoice-runtime.py
python3 scripts/setup-omnivoice-python-env.py --check-only
```

Install into a real Hermes checkout:

```bash
python3 scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --with-examples \
  --update-gitignore \
  --dry-run
```

Remove `--dry-run` only after reviewing the planned files and gitignore block.

## 🧩 Hermes Config

Stage the provider first. Keep the active provider unchanged until smoke tests
and rollback are verified:

```yaml
tts:
  provider: xtts-v2
  providers:
    omnivoice:
      type: command
      command: "python3 /opt/hermes-local-tts/omnivoice-bridge/scripts/hermes-omnivoice-tts.py --voices-dir ~/.hermes/voices/omnivoice --voice {voice} --speed {speed} --max-chars 2000 --text-file {input_path} --out {output_path}"
      voice: narrator
      speed: 1.0
      output_format: wav
      timeout: 600
      voice_compatible: true
      max_text_length: 2000
```

The validated placeholders are `{input_path}`, `{output_path}`, `{voice}`, and
`{speed}`.

## 🖥️ Mac Studio SSH-Loopback Backend

The current proven remote path keeps OmniVoice bound to Mac Studio loopback and
uses SSH only as a transport:

```bash
export OMNIVOICE_REMOTE_TRANSPORT=ssh-loopback
export OMNIVOICE_REMOTE_SSH_HOST=<service-user>@<mac-studio-tailnet-ip>
export OMNIVOICE_REMOTE_LOOPBACK_URL=http://127.0.0.1:8880
export OMNIVOICE_REMOTE_SSH_IDENTITY_FILE=/path/to/restricted-omnivoice-ssh-key
export OMNIVOICE_REMOTE_HELPER=/Users/<service-user>/Services/omnivoice/bin/omnivoice-remote-speech
export OMNIVOICE_REMOTE_ARTIFACT_PREFIX=/Users/<service-user>/Services/omnivoice/
export OMNIVOICE_REMOTE_VOICE=homelab_narrator

scripts/test-omnivoice-remote.sh
```

The helper reads its token from a protected Mac Studio-local file. Do not copy
that token to Hermes, place it in argv, or commit it.

## 🛡️ Security Rules

- Generated audio, voice samples, model weights, caches, local config, token
  files, and private keys stay out of git.
- Cloned voices require `consent.status: confirmed`, `consent.source`, and
  non-empty `consent.allowed_uses`.
- Registry roots, voice directories, `voice.yaml`, text inputs, preview output
  paths, and clone `ref_audio` files are checked for symlink abuse.
- Generated audio is written with private permissions and validated before
  final replacement.
- OmniVoice-Studio and OmniVoice FastAPI are loopback-first. Do not expose them
  on the LAN without a separate auth and network review.
- No automatic Hermes provider fallback was observed for a failing command
  provider. Rollback is an explicit operator action.

## 🧰 Script Map

| Script | Purpose |
| --- | --- |
| `scripts/hermes-omnivoice-tts.py` | Local Hermes TTS command-provider wrapper |
| `scripts/hermes-omnivoice-remote.py` | Remote HTTP / SSH-loopback TTS wrapper |
| `scripts/hermes-omnivoice-python-adapter.py` | Direct OmniVoice Python API adapter |
| `scripts/setup-omnivoice-python-env.py` | Isolated Python runtime planner/installer |
| `scripts/create-omnivoice-voice.py` | Create design or clone voice profiles |
| `scripts/import-omnivoice-studio-voice.py` | Import Studio profiles into the Hermes registry |
| `scripts/hermes-omnivoice-voices.py` | List, inspect, select, preview, and print config |
| `scripts/check-omnivoice-runtime.py` | Runtime readiness diagnostics |
| `scripts/install-hermes-omnivoice-bridge.py` | Dry-run-first installer |
| `scripts/omnivoice-studio-local.py` | Loopback-only Studio Docker helper |
| `scripts/omnivoice-status.sh` | Provider status check |
| `scripts/omnivoice-enable.sh` | Conservative provider enable helper |
| `scripts/omnivoice-disable.sh` | Rollback helper |
| `scripts/omnivoice-qc-sample.sh` | Subjective QC sample generator |
| `scripts/test-omnivoice-tts.sh` | Local TTS smoke test |
| `scripts/test-omnivoice-remote.sh` | Remote TTS smoke test |
| `scripts/omnivoice-acceptance.py` | Static/live readiness summary |
| `scripts/validate-omnivoice-bridge.sh` | Full local validation |
| `scripts/check-omnivoice-artifacts.py` | Artifact and secret hygiene guard |
| `scripts/find-hermes-source.py` | Read-only Hermes source discovery |

## 📚 Docs

- 📦 [Feature and install path inventory](docs/features-install-paths.md)
- 🛠️ [Setup](docs/omnivoice-setup.md)
- 🎛️ [Operator runbook](docs/omnivoice-operator-runbook.md)
- 🖥️ [Remote MVP](docs/omnivoice-remote-mvp.md)
- 🎧 [Subjective QC](docs/omnivoice-qc.md)
- 🧪 [Acceptance checklist](docs/omnivoice-acceptance.md)
- 🎨 [Hermes custom voices](docs/tts-custom-voices.md)
- 🔌 [Studio bridge](docs/omnivoice-studio-bridge.md)
- 🧭 [Integration notes](docs/omnivoice-integration-notes.md)
- 📋 [MVP handoff](docs/omnivoice-mvp-handoff.md)
- 🗓️ [Weekend summary](docs/omnivoice-weekend-summary.md)

## 🧭 Recommendation

Use OmniVoice SSH-loopback for bounded manual evaluation when an operator wants
the Mac Studio voice. Keep `xtts-v2` as the unattended default until pacing
consistency, fallback behavior, and operational UX are fully addressed.
