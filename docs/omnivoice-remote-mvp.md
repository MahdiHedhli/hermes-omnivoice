# OmniVoice Remote MVP

This slice adds a command-provider path where Hermes calls a remote
OmniVoice FastAPI service over Tailscale. It does not add a native Hermes
provider and it does not change the default provider.

## Architecture

```text
Hermes Agent on hermes-01
  -> tts.providers.omnivoice-remote command provider
  -> scripts/hermes-omnivoice-remote.py
  -> HTTP(S) over Tailscale with bearer token
  -> Mac Studio OmniVoice FastAPI /v1/audio/speech
  -> audio bytes returned to Hermes wrapper
  -> wrapper validates and writes WAV output path
  -> Hermes existing conversion path returns final media
```

Keep `tts.provider: xtts-v2` until an operator intentionally starts a bounded
remote trial.

## Security Model

- The remote service must be reachable only over Tailscale.
- The remote service must require a bearer token for all endpoints.
- Do not rely on unauthenticated `/docs`, `/web`, `/health`, or TTS endpoints.
- Do not put credentials in URLs; `hermes-omnivoice-remote.py` rejects URL
  userinfo and redacts bearer tokens from errors.
- Do not expose OmniVoice-Studio or OmniVoice FastAPI broadly on the LAN.
- Store real tokens in host-local environment files or service environment,
  not in this repo.

The wrapper rejects public-looking base URLs by default. It allows loopback,
private IPs, Tailscale CGNAT IPs, `.ts.net`, `.local`, `.localhost`, and
single-label hostnames. Set `OMNIVOICE_REMOTE_ALLOW_PUBLIC=1` only after a
separate authentication and network review.

## Mac Studio Service Dependency

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
`diogod2r/OmniVoice-FastAPI` fork. It has a compatible endpoint shape but lacks
auth in the reviewed revision, so use a fork with auth middleware or an
authenticated reverse proxy.

## Environment

Copy the template locally and fill it outside git:

```bash
cp .env.example ~/.hermes/omnivoice-remote.env
chmod 600 ~/.hermes/omnivoice-remote.env
```

Example values:

```bash
export OMNIVOICE_REMOTE_BASE_URL=http://mac-studio.tailnet.ts.net:8880
export OMNIVOICE_REMOTE_API_TOKEN=<local-only-token>
```

On hermes-01, load these variables in the same environment that launches
Hermes or the command-provider subprocess. Do not commit the populated file.

## Hermes Config

Stage the provider while keeping the active default on `xtts-v2`:

```yaml
tts:
  provider: xtts-v2
  providers:
    omnivoice-remote:
      type: command
      command: "python /opt/hermes-local-tts/omnivoice-bridge/scripts/hermes-omnivoice-remote.py --voice {voice} --speed {speed} --text-file {input_path} --out {output_path} --max-chars 2000"
      voice: homelab_narrator
      speed: 1.0
      output_format: wav
      timeout: 600
      voice_compatible: true
      max_text_length: 2000
```

The same example lives in `examples/hermes-tts-omnivoice-remote.yaml`.

## Wrapper Usage

```bash
export OMNIVOICE_REMOTE_BASE_URL=http://mac-studio.tailnet.ts.net:8880
export OMNIVOICE_REMOTE_API_TOKEN=<local-only-token>

python scripts/hermes-omnivoice-remote.py \
  --text-file /tmp/hermes-input.txt \
  --out /tmp/hermes-remote-output.wav \
  --voice homelab_narrator \
  --speed 1.0 \
  --max-chars 2000
```

The wrapper fails closed on:

- missing or empty text,
- missing base URL,
- missing token,
- public-looking base URL without explicit override,
- HTTP timeout or connection refusal,
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
```

Remote smoke, only when the Mac Studio service is available:

```bash
source ~/.hermes/omnivoice-remote.env
scripts/test-omnivoice-remote.sh
```

The smoke script checks `/health` when available, synthesizes a short sentence,
validates the output is non-empty audio, and writes samples under
`~/.cache/hermes/omnivoice-remote-smoke/`.

## Operator Trial

1. Confirm active provider is `xtts-v2`.
2. Confirm `tts.providers.omnivoice-remote` exists.
3. Confirm `OMNIVOICE_REMOTE_BASE_URL` points to the Mac Studio Tailscale
   address or MagicDNS name.
4. Confirm `OMNIVOICE_REMOTE_API_TOKEN` is present in the Hermes runtime
   environment.
5. Run `scripts/test-omnivoice-remote.sh`.
6. Temporarily set `tts.provider` to `omnivoice-remote`.
7. Run Hermes' real `tools.tts_tool.text_to_speech_tool` path.
8. Roll back to `xtts-v2`.
9. Confirm `xtts-v2` still works.

Trial prompts:

- `Hermes OmniVoice remote trial one.`
- `This remote Mac Studio synthesis test checks pacing, clarity, and timeout behavior.`
- `Testing remote TTS numbers and abbreviations: 10 PM, API, VM, Tailscale, and Proxmox.`

## Latency Expectations

The local hermes-01 backend trial took roughly:

- short: 49.43 seconds,
- medium: 78.67 seconds,
- edge: 84.56 seconds.

The remote Mac Studio path is expected to improve model runtime if the Mac
Studio is substantially more capable, but first-token/model-load latency,
Tailscale transfer, and container cold-start can still dominate. Keep
`timeout: 600` until measured remote results justify lowering it.

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

## Local Vs Remote Recommendation

Use the local backend when hermes-01 is available, latency is acceptable, and
you want fewer network dependencies. Use the remote Mac Studio backend when
the operator needs faster synthesis or better hardware utilization and the
Tailscale/auth controls are verified.

Do not make `omnivoice-remote` the global default until subjective QC, remote
latency, and rollback have all passed.
