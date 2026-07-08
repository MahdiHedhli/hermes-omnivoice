#!/usr/bin/env python3
"""Reference OmniVoice speech server — OpenAI-compatible ``/v1/audio/speech``.

This is the server the plugin's ``studio`` (loopback) and ``service`` (LAN)
backends talk to. The OmniVoice SDK ships a gradio demo + inference CLIs but no
HTTP server, so this fills that gap with a tiny FastAPI wrapper.

It reuses the plugin's own ``ov_core`` package: a request names a ``voice`` id,
the server resolves it against the shared Hermes voice registry
(``~/.hermes/voices/omnivoice``) — consent gate, WAV validation and all — and
runs the exact same local synth path the ``local`` backend uses. So a voice you
clone/design in the dashboard is immediately synthesizable here.

Same artifact for single-host and fleet:
  * loopback:  python server/serve.py --host 127.0.0.1 --port 8880
  * LAN/fleet: python server/serve.py --host 0.0.0.0 --port 8880 --require-auth
               (set HERMES_OMNIVOICE_SERVICE_TOKEN; put it on a VPN/tailnet)

Point the plugin at it:
  tts:
    omnivoice:
      backend: studio                     # or `service` for the LAN case
      studio: { url: http://127.0.0.1:8880 }

Deps: pip install -r server/requirements.txt  (omnivoice torch soundfile fastapi uvicorn)
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import uuid
from pathlib import Path

# Make the plugin's ov_core importable. NOTE: sys.path[0] for a script is this
# file's directory (server/), NOT the repo root — so `import omnivoice` still
# resolves to the real SDK, never the sibling plugin package dir.
_PLUGIN_DIR = Path(__file__).resolve().parent.parent / "omnivoice"
if _PLUGIN_DIR.is_dir():
    sys.path.insert(0, str(_PLUGIN_DIR))

from fastapi import Body, FastAPI, Header, HTTPException, Response

from ov_core import backends
from ov_core.config import LocalConfig, OmniVoiceConfig
from ov_core.registry import RegistryError, VoiceProfile, VoiceRegistry

app = FastAPI(title="OmniVoice speech server")

# populated by main() before uvicorn starts
CFG: OmniVoiceConfig
AUTH_TOKEN: str = ""
_synth_lock = threading.Lock()  # the model is single-instance; serialize synths


def _check_auth(authorization: str | None) -> None:
    if not AUTH_TOKEN:
        return
    if authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    try:
        voices = [v.id for v in VoiceRegistry(CFG.voices_dir).list_voices()]
    except Exception:
        voices = []
    return {
        "ok": True,
        "model": CFG.local.model,
        "device": CFG.local.device,
        "voices": voices,
    }


@app.post("/v1/audio/speech")
def speech(body: dict = Body(...), authorization: str | None = Header(default=None)):
    _check_auth(authorization)
    voice_id = str(body.get("voice") or "").strip()
    text = str(body.get("input") or "")
    if not voice_id:
        raise HTTPException(status_code=400, detail="'voice' (a registry voice id) is required")
    if not text.strip():
        raise HTTPException(status_code=400, detail="'input' text is required")
    try:
        speed = float(body.get("speed", 1.0) or 1.0)
    except (TypeError, ValueError):
        speed = 1.0

    try:
        profile = VoiceRegistry(CFG.voices_dir).get_voice(voice_id)
    except RegistryError as exc:
        raise HTTPException(status_code=404, detail=f"voice '{voice_id}': {exc}")

    out = backends.paths.audio_cache_dir() / f"serve-{uuid.uuid4().hex}.wav"
    try:
        with _synth_lock:  # one synth at a time; concurrent requests queue here
            backends.synthesize(text, str(out), voice=profile, cfg=CFG, speed=speed, fmt="wav")
            data = out.read_bytes()
    except backends.SynthError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    finally:
        out.unlink(missing_ok=True)
    return Response(content=data, media_type="audio/wav")


def _warmup() -> None:
    """Load the model and run one throwaway synth so the first *real* request is
    warm and reliable — a cold first inference can fail or glitch."""
    prof = VoiceProfile(id="__warmup__", name="warmup", mode="design",
                        voice_dir=Path("/tmp"),
                        instruct="male, american accent, moderate pitch", language="en")
    out = backends.paths.audio_cache_dir() / f"warmup-{uuid.uuid4().hex}.wav"
    print("warming up model (first load can take a moment)…", flush=True)
    try:
        backends.synthesize("OmniVoice warm up. One, two, three.", str(out),
                            voice=prof, cfg=CFG, fmt="wav")
        print("warmup OK — model ready", flush=True)
    except Exception as exc:  # non-fatal: still serve, just log it
        print(f"warmup failed (continuing anyway): {exc}", flush=True)
    finally:
        out.unlink(missing_ok=True)


def main(argv=None) -> int:
    global CFG, AUTH_TOKEN
    default_voices = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser() / "voices" / "omnivoice"
    p = argparse.ArgumentParser(description="OmniVoice OpenAI-compatible speech server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8880)
    p.add_argument("--model", default=os.environ.get("HERMES_OMNIVOICE_MODEL", "k2-fsa/OmniVoice"))
    p.add_argument("--device", default=os.environ.get("HERMES_OMNIVOICE_DEVICE", "auto"),
                   help="auto | cpu | cuda | mps")
    p.add_argument("--dtype", default=os.environ.get("HERMES_OMNIVOICE_DTYPE", "float16"))
    p.add_argument("--num-step", type=int, default=int(os.environ.get("HERMES_OMNIVOICE_NUM_STEP", 16)),
                   help="diffusion denoising steps — lower is faster (measured on MPS: 32->36.6s, "
                        "16->19.4s, 8->11.4s, 4->6.3s for the same phrase). 16 is ASR-verified as "
                        "identical output to the SDK's 32 default; 8 starts dropping words")
    p.add_argument("--voices-dir", default=str(default_voices))
    p.add_argument("--auth-token", default=os.environ.get("HERMES_OMNIVOICE_SERVICE_TOKEN", ""))
    p.add_argument("--require-auth", action="store_true",
                   help="refuse to start without a token (use for any non-loopback bind)")
    p.add_argument("--no-warmup", action="store_true",
                   help="skip the startup warmup synth (warmup makes the first request reliable)")
    args = p.parse_args(argv)

    AUTH_TOKEN = (args.auth_token or "").strip()
    is_loopback = args.host in {"127.0.0.1", "::1", "localhost"}
    if (args.require_auth or not is_loopback) and not AUTH_TOKEN:
        p.error("a non-loopback bind requires --auth-token (or HERMES_OMNIVOICE_SERVICE_TOKEN)")

    CFG = OmniVoiceConfig(
        backend="local",
        voices_dir=Path(args.voices_dir).expanduser(),
        local=LocalConfig(model=args.model, device=args.device, dtype=args.dtype, num_step=args.num_step),
    )

    print(f"OmniVoice speech server → http://{args.host}:{args.port}  "
          f"(model={args.model}, device={args.device}, dtype={args.dtype}, num_step={args.num_step}, "
          f"voices={CFG.voices_dir}, auth={'on' if AUTH_TOKEN else 'off'})", flush=True)
    if not args.no_warmup:
        _warmup()
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
