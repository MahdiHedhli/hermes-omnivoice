# OmniVoice Remote MVP

This lane keeps Hermes on the command-provider MVP and adds two remote
transports for a stronger OmniVoice host:

- `http`: direct HTTP(S) to an authenticated remote FastAPI base URL.
- `ssh-loopback`: SSH to the Mac Studio and call the loopback-only FastAPI
  service from inside that SSH session. The proven Hermes path uses a
  Mac Studio-local helper that reads the bearer token from a protected file on
  the Mac Studio, so Hermes does not need a copied token.

Direct HTTP remains supported, but it is not the proven Mac Studio path right
now. Direct HTTP to `100.78.163.62:8880` timed out from clients even though TCP
accepted connections. The current safe/proven path is SSH loopback:

```text
Hermes Agent on hermes-01
  -> tts.providers.omnivoice-remote-ssh-loopback command provider
  -> scripts/hermes-omnivoice-remote.py --transport ssh-loopback
  -> ssh hermes-ops@100.78.163.62
  -> remote helper calls http://127.0.0.1:8880/v1/audio/speech
  -> wrapper copies back only the returned generated WAV artifact
  -> wrapper validates and atomically writes Hermes output path
```

Keep `tts.provider: xtts-v2` until an operator intentionally starts a bounded
remote trial.

## Security Model

- The Mac Studio OmniVoice service remains loopback-only on
  `127.0.0.1:8880`.
- Hermes reaches it through SSH to `hermes-ops@100.78.163.62`.
- Bearer auth is enforced by the service.
- For the proven helper path, the bearer token stays in a protected
  Mac Studio-local file read by
  `/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech`.
- For direct HTTP or direct SSH-loopback HTTP mode, prefer
  `OMNIVOICE_REMOTE_TOKEN_FILE` over `OMNIVOICE_REMOTE_API_TOKEN`.
- Token files copied to any client host must be mode `600`; the wrapper rejects
  group/world-accessible token files.
- Do not put credentials in URLs; the wrapper rejects URL userinfo.
- In helper mode, the token is not sent from Hermes at all. In direct
  `ssh-loopback` HTTP mode, the token is sent to the remote HTTP helper on
  stdin, not as an `ssh` or `curl` argument.
- Do not expose OmniVoice-Studio or OmniVoice FastAPI broadly on the LAN.
- Do not commit generated audio, voice samples, model files, caches, tokens,
  populated env files, or host-local configs.

The direct `http` transport rejects public-looking base URLs by default. It
allows loopback, private IPs, Tailscale CGNAT IPs, `.ts.net`, `.local`,
`.localhost`, and single-label hostnames. Set
`OMNIVOICE_REMOTE_ALLOW_PUBLIC=1` only after a separate authentication and
network review.

## FastAPI Service

The remote client expects an OpenAI-compatible endpoint:

```text
POST /v1/audio/speech
Authorization: Bearer <token>
Content-Type: application/json
Accept: audio/wav, audio/*
```

Payload:

```json
{
  "model": "omnivoice",
  "input": "Hermes OmniVoice remote test.",
  "voice": "homelab_narrator",
  "response_format": "wav",
  "speed": 1.0
}
```

`docs/omnivoice-fastapi-fork-review.md` documents the reviewed
`diogod2r/OmniVoice-FastAPI` fork. Its endpoint shape is compatible, but the
reviewed revision lacks auth and binds broadly by default, so use only the
hardened Mac Studio deployment or an authenticated fork/proxy.

## Environment

Copy the template locally and fill it outside git:

```bash
cp .env.example ~/.hermes/omnivoice-remote.env
chmod 600 ~/.hermes/omnivoice-remote.env
```

Current Mac Studio path:

```bash
export OMNIVOICE_REMOTE_TRANSPORT=ssh-loopback
export OMNIVOICE_REMOTE_SSH_HOST=hermes-ops@100.78.163.62
export OMNIVOICE_REMOTE_LOOPBACK_URL=http://127.0.0.1:8880
export OMNIVOICE_REMOTE_SSH_IDENTITY_FILE=/home/claude/.ssh/hermes_ops_macstudio_ed25519
export OMNIVOICE_REMOTE_HELPER=/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech
export OMNIVOICE_REMOTE_ARTIFACT_PREFIX=/Users/hermes-ops/Services/omnivoice/
export OMNIVOICE_REMOTE_VOICE=homelab_narrator
```

Direct HTTP mode remains available for a future network diagnostic lane:

```bash
export OMNIVOICE_REMOTE_TRANSPORT=http
export OMNIVOICE_REMOTE_BASE_URL=http://mac-studio.tailnet.ts.net:8880
export OMNIVOICE_REMOTE_TOKEN_FILE=/path/to/private/omnivoice-token
```

`OMNIVOICE_REMOTE_API_TOKEN` is a fallback for local tests. Prefer a protected
token file for Hermes operation.

## Hermes Config

Stage the SSH loopback provider while keeping the active default on `xtts-v2`:

```yaml
tts:
  provider: xtts-v2
  providers:
    omnivoice-remote-ssh-loopback:
      type: command
      command: "python3 /opt/hermes-local-tts/omnivoice-bridge/scripts/hermes-omnivoice-remote.py --transport ssh-loopback --ssh-host hermes-ops@100.78.163.62 --ssh-identity-file /home/claude/.ssh/hermes_ops_macstudio_ed25519 --remote-helper /Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech --remote-artifact-prefix /Users/hermes-ops/Services/omnivoice/ --voice {voice} --speed {speed} --text-file {input_path} --out {output_path} --max-chars 2000 --timeout 600"
      voice: homelab_narrator
      speed: 1.0
      output_format: wav
      timeout: 600
      voice_compatible: true
      max_text_length: 2000
```

The same example lives in
`examples/hermes-tts-omnivoice-remote-ssh-loopback.yaml`. Direct HTTP mode
remains in `examples/hermes-tts-omnivoice-remote.yaml`.

## Wrapper Usage

SSH loopback smoke:

```bash
source ~/.hermes/omnivoice-remote.env

python scripts/hermes-omnivoice-remote.py \
  --transport ssh-loopback \
  --ssh-host hermes-ops@100.78.163.62 \
  --ssh-identity-file /home/claude/.ssh/hermes_ops_macstudio_ed25519 \
  --remote-helper /Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech \
  --remote-artifact-prefix /Users/hermes-ops/Services/omnivoice/ \
  --text-file /tmp/hermes-input.txt \
  --out /tmp/hermes-remote-output.wav \
  --voice homelab_narrator \
  --speed 1.0 \
  --max-chars 2000
```

Direct HTTP smoke:

```bash
OMNIVOICE_REMOTE_TRANSPORT=http \
OMNIVOICE_REMOTE_BASE_URL=http://mac-studio.tailnet.ts.net:8880 \
OMNIVOICE_REMOTE_TOKEN_FILE=/path/to/private/omnivoice-token \
python scripts/hermes-omnivoice-remote.py \
  --text-file /tmp/hermes-input.txt \
  --out /tmp/hermes-remote-output.wav \
  --voice homelab_narrator
```

The wrapper fails closed on:

- missing or empty text,
- missing base URL in `http` mode,
- missing SSH host in `ssh-loopback` mode,
- missing token or unsafe token-file permissions in token-file modes,
- public-looking direct HTTP base URL without explicit override,
- SSH failure,
- loopback service timeout or connection refusal,
- HTTP 401 or 403,
- HTTP 500 or other non-2xx status,
- non-audio response,
- invalid WAV output,
- output write failure.

## Validation

Local validation:

```bash
python3 -m unittest discover -s tests -v
scripts/validate-omnivoice-bridge.sh
python3 scripts/omnivoice-acceptance.py --require-package-files
python3 scripts/check-omnivoice-artifacts.py
```

Remote smoke, only when SSH and either the helper workflow or a token-file workflow are available:

```bash
source ~/.hermes/omnivoice-remote.env
scripts/test-omnivoice-remote.sh
```

The smoke script checks `/health` when available, synthesizes a short sentence,
validates non-empty audio, prints latency, and writes samples under
`~/.cache/hermes/omnivoice-remote-smoke/`. When samples are generated during
Codex work, post them in chat as local artifacts and keep them out of git.

## Latest SSH Loopback Attempt

2026-06-02 SSH-loopback QC and soak lane:

- Preflight active provider: `xtts-v2`.
- Remote smoke from `hermes-01`: PASS through helper mode, 2.00s wrapper
  latency.
- Mac Studio helper path: confirmed executable at
  `/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech`.
- Mac Studio service listen address: confirmed `127.0.0.1:8880`; no network
  exposure changes were made.
- Subjective listening: completed by the operator on 2026-06-03. Manual
  operator use was approved with 4/5 intelligibility, pacing, pronunciation,
  naturalness, and operator acceptability. Voice consistency was not scored;
  different voices had different pace issues. No recurring artifact/noise issue
  was reported.

Direct SSH-helper soak:

| Metric | Result |
| --- | ---: |
| Prompt count | 20 |
| Success / failure / retry | 20 / 0 / 0 |
| Latency min / median / max | 1.714s / 2.122s / 2.597s |
| Output duration min / max | 2.160s / 6.760s |
| Artifact directory | `/home/claude/.cache/hermes/omnivoice-remote-soak/20260602T224637Z/` |

Live Hermes provider soak:

| Metric | Result |
| --- | ---: |
| Prompt count | 5 |
| Success / failure / retry | 5 / 0 / 0 |
| Latency min / median / max | 1.949s / 2.059s / 2.346s |
| Output duration min / max | 1.7565s / 4.0665s |
| Rollback smoke | PASS, 53.172s latency |
| Final provider | `xtts-v2` |
| Artifact directory | `/home/claude/.cache/hermes/omnivoice-remote-live-soak/20260602T224827Z/` |

Local review copies are under:

- `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-soak-20260602T224637Z/`
- `/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-soak-20260602T224827Z/`

Security review found no observed token values in command output, process args,
accessible Mac Studio logs, or git state. Local token-pattern hits were limited
to placeholder strings in docs/tests/code and ignored Python bytecode.

2026-06-02 live Hermes tool-path trial:

- Preflight active provider: `xtts-v2`.
- Config path: `/home/claude/.hermes/config.yaml`; backup created at
  `/home/claude/.hermes/config.yaml.pre-omnivoice-remote-20260602T220337Z.bak`.
- Staged provider: `tts.providers.omnivoice-remote-ssh-loopback`.
- First activation attempt found the command used `python`, which was not on
  Hermes' command-provider PATH. Hermes was rolled back to `xtts-v2`, rollback
  smoke passed, and the provider command was corrected to `python3`.
- Second activation attempt passed all live Hermes
  `tools.tts_tool.text_to_speech_tool` prompts through the remote Mac Studio
  helper, then rolled back to `xtts-v2`.
- Final active provider: `xtts-v2`.
- Subjective listening: not performed in this run; samples were copied locally
  for operator review.

| Case | Result | Latency | Duration | Size | Format | Artifact |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Short | PASS | 2.056s | 2.956500s | 24,046 bytes | Ogg Opus, mono, 24000 Hz | `/home/claude/.cache/hermes/omnivoice-remote-live-trial/20260602T220621Z/short.ogg` |
| Medium | PASS | 2.254s | 4.196500s | 34,082 bytes | Ogg Opus, mono, 24000 Hz | `/home/claude/.cache/hermes/omnivoice-remote-live-trial/20260602T220621Z/medium.ogg` |
| Edge | PASS | 2.579s | 5.386500s | 43,769 bytes | Ogg Opus, mono, 24000 Hz | `/home/claude/.cache/hermes/omnivoice-remote-live-trial/20260602T220621Z/edge.ogg` |
| Rollback `xtts-v2` | PASS | 54.308s | 4.871167s | 39,556 bytes | Ogg Opus, mono, 24000 Hz | `/home/claude/.cache/hermes/omnivoice-remote-live-trial/20260602T220621Z/rollback_xtts_v2.ogg` |

The same samples were copied to the local, out-of-repo review cache at
`/Users/mhedhli/.cache/hermes/omnivoice-chat-artifacts/remote-live-20260602T220621Z/`.

2026-06-02 admin helper smoke from ColPanicM2:

- The requested `/Volumes/mhedhli/.ssh/colpanicm2_macstudio_admin_ed25519`
  key path was not mounted in this Codex process, so the same-named local
  admin key at `/Users/mhedhli/.ssh/colpanicm2_macstudio_admin_ed25519` was
  used.
- Only `mhedhli@100.78.163.62` was used. No `hermes-ops` SSH, `sudo`, or
  token/env file reads were performed.
- `/Users/mhedhli/.local/bin/omnivoice-client-smoke health` returned
  `ok=true`, `provider=omnivoice`, `device=mps`, `model_id=k2-fsa/OmniVoice`,
  `sample_rate=24000`, and `voice_count=1`.
- `/Users/mhedhli/.local/bin/omnivoice-client-smoke voices` returned
  `homelab_narrator`, a consent-confirmed designed voice with no reference
  audio.
- Speech smoke with `ColPanicM2 OmniVoice integration smoke test.` returned
  HTTP 200, `ok=true`, 153,644 bytes, 3.200 seconds audio, 2.166 seconds
  reported latency, and RTF 0.6769.
- Only the returned WAV artifact was copied back locally for review. Token and
  env files stayed on the Mac Studio and were not inspected.

This proved the Mac Studio service, protected local token path, MPS backend,
and operator helper through the admin SSH route. The later live Hermes trial
above supersedes this as the command-provider proof.

2026-06-02 local workstation preflight:

- Repo branch and required wrapper/smoke/example files were present.
- Default SSH to `hermes-ops@100.78.163.62` failed with
  `Permission denied (publickey,password,keyboard-interactive)`.
- The local Mac Studio admin identity can SSH to `mhedhli@100.78.163.62`.
- Noninteractive `sudo -u hermes-ops` from that admin session requires a
  password, so it cannot be used for unattended smoke.
- Mac Studio loopback TCP on `127.0.0.1:8880` accepted connections from the
  admin SSH session.
- Unauthenticated `/health` over Mac Studio loopback returned HTTP 401,
  consistent with bearer auth enforcement.
- No local protected token file was available in the repo environment, and the
  `hermes-ops` service directory is not accessible from the admin account.
- Result: SSH loopback synthesis smoke, direct wrapper samples, and live Hermes
  tool-path trial were skipped. No sample artifacts were generated.

This was a historical blocked attempt. The later helper-based Hermes trial used
the host-local `claude` restricted key on `hermes-01` and did not require a
copied token file.

## Operator Trial

1. Confirm active provider is `xtts-v2`.
2. Confirm `tts.providers.omnivoice-remote-ssh-loopback` exists.
3. Confirm `OMNIVOICE_REMOTE_SSH_HOST=hermes-ops@100.78.163.62`.
4. Confirm `OMNIVOICE_REMOTE_SSH_IDENTITY_FILE` points to the mode `600`
   Hermes-host key `/home/claude/.ssh/hermes_ops_macstudio_ed25519`.
5. Confirm `OMNIVOICE_REMOTE_HELPER` is
   `/Users/hermes-ops/Services/omnivoice/bin/omnivoice-remote-speech`.
6. Run `scripts/test-omnivoice-remote.sh`.
7. Temporarily set `tts.provider` to `omnivoice-remote-ssh-loopback`.
8. Run Hermes' real `tools.tts_tool.text_to_speech_tool` path.
9. Roll back to `xtts-v2`.
10. Confirm `xtts-v2` still works.

Trial prompts:

- `Hermes OmniVoice SSH loopback trial one.`
- `This Mac Studio synthesis test checks pacing, clarity, and timeout behavior.`
- `Testing remote TTS numbers and abbreviations: 10 PM, API, VM, Tailscale, and Proxmox.`

## Latency Expectations

Measured Mac Studio results:

- Mac Studio local smoke: 0.897 seconds latency, 1.910 seconds audio,
  RTF 0.4694.
- Hermes-initiated SSH smoke: 0.967 seconds latency, 2.950 seconds audio,
  RTF 0.3279.
- Live Hermes remote tool path: 2.056-2.579 seconds latency for the tested
  prompts, producing 2.956500-5.386500 seconds of Opus audio.
- Post-rollback `xtts-v2` smoke remained much slower on `hermes-01` CPU:
  54.308 seconds latency for 4.871167 seconds of Opus audio.

The older local hermes-01 backend trial took roughly 49-85 seconds for similar
short and medium prompts. Keep `timeout: 600` until repeated remote Hermes
tool-path measurements justify lowering it.

## Fallback And Rollback

No automatic fallback was observed for a failing OmniVoice command provider.
Treat remote OmniVoice failures as hard TTS failures and roll back explicitly:

```python
from hermes_cli.config import load_config, save_config

cfg = load_config()
cfg.setdefault("tts", {})["provider"] = "xtts-v2"
save_config(cfg)
```

Run one Hermes TTS smoke after rollback.

## Direct HTTP Follow-Up

Direct HTTP over the Mac Studio Tailscale IP remains a separate network
diagnostic follow-up. Do not apply firewall, Tailscale ACL, UniFi, VLAN, or
network policy changes in this lane.

## Recommendation

Use `ssh-loopback` helper mode for bounded manual Mac Studio operator requests
now. Reliability and human listening QC passed for manual use, and the reviewer
preferred OmniVoice over the rollback `xtts-v2` sample. Keep `xtts-v2` as the
active default for unattended routine use until pacing consistency and fallback
behavior are addressed. Keep direct `http` mode for future diagnostics or for
hosts where authenticated HTTP over Tailscale is known to work.
