# OmniVoice Remote MVP

This lane keeps Hermes on the command-provider MVP and adds two remote
transports for a stronger OmniVoice host:

- `http`: direct HTTP(S) to an authenticated remote FastAPI base URL.
- `ssh-loopback`: SSH to the Mac Studio and call the loopback-only FastAPI
  service from inside that SSH session.

Direct HTTP remains supported, but it is not the proven Mac Studio path right
now. Direct HTTP to `100.78.163.62:8880` timed out from clients even though TCP
accepted connections. The current safe/proven path is SSH loopback:

```text
Hermes Agent on hermes-01
  -> tts.providers.omnivoice-remote-ssh-loopback command provider
  -> scripts/hermes-omnivoice-remote.py --transport ssh-loopback
  -> ssh hermes-ops@100.78.163.62
  -> remote helper calls http://127.0.0.1:8880/v1/audio/speech
  -> audio bytes stream back over SSH
  -> wrapper validates and atomically writes Hermes output path
```

Keep `tts.provider: xtts-v2` until an operator intentionally starts a bounded
remote trial.

## Security Model

- The Mac Studio OmniVoice service remains loopback-only on
  `127.0.0.1:8880`.
- Hermes reaches it through SSH to `hermes-ops@100.78.163.62`.
- Bearer auth is enforced by the service.
- Prefer `OMNIVOICE_REMOTE_TOKEN_FILE` over `OMNIVOICE_REMOTE_API_TOKEN`.
- Token files must be mode `600`; the wrapper rejects group/world-accessible
  token files.
- Do not put credentials in URLs; the wrapper rejects URL userinfo.
- In `ssh-loopback` mode, the token is sent to the remote helper on stdin, not
  as an `ssh` or `curl` argument.
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
export OMNIVOICE_REMOTE_TOKEN_FILE=/path/to/private/omnivoice-token
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
      command: "python /opt/hermes-local-tts/omnivoice-bridge/scripts/hermes-omnivoice-remote.py --transport ssh-loopback --remote-url http://127.0.0.1:8880 --voice {voice} --speed {speed} --text-file {input_path} --out {output_path} --max-chars 2000"
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
- missing token or unsafe token-file permissions,
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

Remote smoke, only when SSH and the token file are available:

```bash
source ~/.hermes/omnivoice-remote.env
scripts/test-omnivoice-remote.sh
```

The smoke script checks `/health` when available, synthesizes a short sentence,
validates non-empty audio, prints latency, and writes samples under
`~/.cache/hermes/omnivoice-remote-smoke/`. When samples are generated during
Codex work, post them in chat as local artifacts and keep them out of git.

## Operator Trial

1. Confirm active provider is `xtts-v2`.
2. Confirm `tts.providers.omnivoice-remote-ssh-loopback` exists.
3. Confirm `OMNIVOICE_REMOTE_SSH_HOST=hermes-ops@100.78.163.62`.
4. Confirm `OMNIVOICE_REMOTE_LOOPBACK_URL=http://127.0.0.1:8880`.
5. Confirm `OMNIVOICE_REMOTE_TOKEN_FILE` points to a mode `600` token file.
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

Use `ssh-loopback` for Mac Studio operator trials now. Keep direct `http` mode
for future diagnostics or for hosts where authenticated HTTP over Tailscale is
known to work. Do not make remote OmniVoice the global default until remote
Hermes tool-path smoke, subjective QC, and rollback all pass.
