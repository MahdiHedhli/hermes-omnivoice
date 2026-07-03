#!/usr/bin/env python3
"""ASR quality check — synth, then transcribe, and flag gibberish.

A valid WAV is not the same as intelligible speech. This synthesizes text with a
voice, runs Whisper ASR on the result, and reports whether the transcript
matches the input — catching the case where the model emits noise/garbage (e.g.
after an MPS out-of-memory event).

Examples:
  # verify a voice via the local in-process backend
  python tools/qc.py --voice heartbeat_narrator --text "Hello, testing one two three."
  # verify a voice via a running speech server
  python tools/qc.py --voice heartbeat_narrator --server http://127.0.0.1:8880

Deps: transformers (Whisper) for ASR; local mode also needs omnivoice+torch+soundfile.
Exit code 0 = intelligible, 2 = likely noise/garbage.
"""
from __future__ import annotations

import argparse
import difflib
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.request
import warnings
from pathlib import Path

_PLUGIN = Path(__file__).resolve().parent.parent / "omnivoice"
if _PLUGIN.is_dir():
    sys.path.insert(0, str(_PLUGIN))


def _words(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def _synth_local(text, voice_id, out, args):
    from ov_core import backends
    from ov_core.config import LocalConfig, OmniVoiceConfig
    from ov_core.registry import VoiceRegistry
    prof = VoiceRegistry(Path(args.voices_dir).expanduser()).get_voice(voice_id)
    cfg = OmniVoiceConfig(backend="local", voices_dir=Path(args.voices_dir).expanduser(),
                          local=LocalConfig(model=args.model, device=args.device, dtype=args.dtype))
    backends.synthesize(text, out, voice=prof, cfg=cfg, fmt="wav")


def _synth_server(text, voice_id, out, server, token):
    body = json.dumps({"model": "omnivoice", "input": text, "voice": voice_id,
                       "response_format": "wav"}).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(server.rstrip("/") + "/v1/audio/speech",
                                 data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            Path(out).write_bytes(r.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail).get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(f"server HTTP {exc.code}: {detail[:500]}") from exc


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="ASR quality check for OmniVoice output")
    p.add_argument("--voice", required=True)
    p.add_argument("--text", default="The quick brown fox jumps over the lazy dog.")
    p.add_argument("--server", default="", help="synth via this speech server instead of local")
    p.add_argument("--token", default=os.environ.get("HERMES_OMNIVOICE_SERVICE_TOKEN", ""))
    p.add_argument("--voices-dir", default=os.path.expanduser("~/.hermes/voices/omnivoice"))
    p.add_argument("--model", default="k2-fsa/OmniVoice")
    p.add_argument("--device", default="auto")
    p.add_argument("--dtype", default="float16")
    p.add_argument("--asr-model", default="openai/whisper-tiny.en")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--out", default="")
    args = p.parse_args(argv)

    out = args.out or f"/tmp/qc_{args.voice}.wav"
    try:
        if args.server:
            _synth_server(args.text, args.voice, out, args.server, args.token)
        else:
            _synth_local(args.text, args.voice, out, args)
    except Exception as exc:
        print(f"SYNTH FAILED: {exc}", file=sys.stderr)
        return 3

    warnings.filterwarnings("ignore")
    logging.disable(logging.WARNING)
    from transformers import pipeline
    heard = pipeline("automatic-speech-recognition", model=args.asr_model)(out)["text"].strip()
    ratio = difflib.SequenceMatcher(None, _words(args.text), _words(heard)).ratio()
    ok = ratio >= args.threshold

    print(f"voice:  {args.voice}  ({'server ' + args.server if args.server else 'local ' + args.device})")
    print(f"said:   {args.text!r}")
    print(f"heard:  {heard!r}")
    print(f"match:  {ratio:.2f}  ->  {'OK — intelligible speech' if ok else 'FAIL — likely noise/garbage'}")
    print(f"audio:  {out}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
