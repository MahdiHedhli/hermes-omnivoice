# OmniVoice speech server

A small OpenAI-compatible `/v1/audio/speech` server for OmniVoice. The SDK ships
a gradio demo and inference CLIs but no HTTP server, so this is the piece the
plugin's `studio` (loopback) and `service` (LAN) backends talk to.

It reuses the plugin's `ov_core` package: a request names a `voice` id, the
server resolves it against the shared Hermes registry (`~/.hermes/voices/omnivoice`)
— consent gate, WAV validation and all — and runs the same local synth path the
in-process `local` backend uses. So a voice you clone/design in the dashboard is
immediately synthesizable here.

**Same artifact, single host → fleet.** Run it on loopback for one machine, or
bind a LAN/tailnet address + a token to serve a fleet of thin agents (Mode B).

## Run

```bash
pip install -r server/requirements.txt   # omnivoice torch soundfile fastapi uvicorn

# single host (pair with backend: studio, url http://127.0.0.1:8880)
python server/serve.py --host 127.0.0.1 --port 8880

# shared node (pair with backend: service); a non-loopback bind REQUIRES a token
export HERMES_OMNIVOICE_SERVICE_TOKEN=$(openssl rand -hex 24)
python server/serve.py --host 0.0.0.0 --port 8880 --require-auth
```

Options: `--model` (default `k2-fsa/OmniVoice`), `--device auto|cpu|cuda|mps`,
`--dtype float16` (default; less memory than float32), `--num-step` (diffusion
denoising steps, default `16` — see below), `--voices-dir`, `--auth-token`,
`--no-warmup`. The server **warms the model at startup** so the first real
request is reliable.

### Speed: `--num-step`

OmniVoice is a **diffusion-LM** TTS model — synthesis runs `num_step` denoising
passes per generation, and time scales roughly linearly with it. Measured on
Apple Silicon (MPS/float16, a ~13s phrase against a real clone reference):

| `num_step` | synth time | ASR-checked output |
|---|---|---|
| 32 (SDK default) | 36.6s | reference transcript |
| **16 (this server's default)** | **19.4s** | **identical transcript** |
| 8 | 11.4s | starts dropping words |
| 4 | 6.3s | broken/garbled |

16 is the verified sweet spot — same output as the SDK default at ~1.9x the
speed. Pass `--num-step 32` for max quality or `--num-step 8` to trade a little
accuracy for more speed; below 8 the output degrades noticeably. There is no
MLX build of OmniVoice (it's pure PyTorch/`transformers`), so on Apple Silicon
this diffusion-step count — not device choice — is the main lever you control;
device/dtype (`mps`/`float16`) already get you the ~3.3x speedup over CPU.

## Endpoints

- `GET /health` → `{ok, model, device, voices:[…]}`
- `POST /v1/audio/speech` → JSON `{model, input, voice, response_format, speed}`,
  bearer auth when a token is set, returns `audio/wav`.

## Verify it actually speaks

A valid WAV is not the same as intelligible speech (e.g. after an MPS OOM the
model can emit noise). Check with ASR:

```bash
python tools/qc.py --voice <id> --server http://127.0.0.1:8880
```

## Keep it running

For a persistent server, wrap the run command in a `launchd` plist (macOS) or a
`systemd` unit (Linux). The plugin's `setup-omnivoice.py --mode install` prints
the commands to create a dedicated venv and launch it.
