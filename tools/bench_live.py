#!/usr/bin/env python3
"""Live-voice benchmark — can this voice hold a real-time conversation?

Synthesizes replies the way the Talk tab does (sentence by sentence, next chunk
produced while the current one plays) and reports what the user would actually
experience:

  TTFA   time to first audio — silence before the first word is heard
  RTF    real-time factor: synthesis seconds per second of speech.
         < 1.0 means speech is produced faster than it is spoken, so a reply of
         any length streams without falling behind.
  stalls playback running dry mid-reply while waiting on the next chunk

Examples:
  # against the running speech server (the real path the dashboard uses)
  python tools/bench_live.py --voice arnold --server http://127.0.0.1:8880

  # sweep the diffusion step count to find the real-time knee on this hardware
  python tools/bench_live.py --voice arnold --server http://127.0.0.1:8880 --sweep 32,16,8,4

  # record a baseline, then gate later runs against it in the dev loop
  python tools/bench_live.py --voice arnold --server ... --save-baseline bench.json
  python tools/bench_live.py --voice arnold --server ... --baseline bench.json

Exit codes: 0 pass, 1 over budget (or regressed vs --baseline), 2 could not run.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import List, Optional

_PLUGIN = Path(__file__).resolve().parent.parent / "omnivoice"
if _PLUGIN.is_dir():
    sys.path.insert(0, str(_PLUGIN))

from ov_core.realtime import (  # noqa: E402
    Chunk, compare_baseline, evaluate, simulate_stream, split_for_speech,
)

# Representative of what an assistant actually says: a terse acknowledgement, a
# normal answer, and a long one that only streams cleanly if RTF < 1.
UTTERANCES = {
    "short": "Done — that's finished.",
    "reply": "I've restarted the server and it's healthy again. Want me to tail the logs?",
    "long": (
        "I found three things worth flagging. The cache was never invalidated after a "
        "write, so stale reads were possible under load. The retry loop had no ceiling, "
        "which is what produced the runaway traffic last night. And the health check was "
        "reporting success before the model had finished loading, so traffic arrived early."
    ),
}


# A timing run on a loaded machine measures the machine, not the change. Record
# load so results are comparable later, and say so loudly when it's high.
BUSY_LOAD_PER_CPU = 0.7


def _load_snapshot() -> dict:
    try:
        one, five, _ = os.getloadavg()
    except (OSError, AttributeError):
        return {}
    cpus = os.cpu_count() or 1
    return {"load1": round(one, 2), "load5": round(five, 2), "cpus": cpus,
            "busy": one > cpus * BUSY_LOAD_PER_CPU}


def _wav_seconds(data: bytes) -> float:
    with wave.open(io.BytesIO(data), "rb") as w:
        return w.getnframes() / float(w.getframerate() or 1)


def _synth_server(text: str, *, url: str, voice: str, token: str, timeout: int) -> bytes:
    payload = {"model": "omnivoice", "input": text, "voice": voice,
               "response_format": "wav", "speed": 1.0}
    headers = {"Content-Type": "application/json", "Accept": "audio/wav"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url.rstrip("/") + "/v1/audio/speech",
                                 data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _synth_local(text: str, *, voice: str, voices_dir: str, num_step: Optional[int],
                 device: str, dtype: str) -> bytes:
    from ov_core import backends
    from ov_core.config import LocalConfig, OmniVoiceConfig
    from ov_core.registry import VoiceRegistry

    root = Path(voices_dir).expanduser()
    profile = VoiceRegistry(root).get_voice(voice)
    local = LocalConfig(device=device, dtype=dtype)
    if num_step:
        local.num_step = num_step
    cfg = OmniVoiceConfig(backend="local", voices_dir=root, local=local)
    out = Path(os.environ.get("TMPDIR", "/tmp")) / f"bench_live_{os.getpid()}.wav"
    backends.synthesize(text, str(out), voice=profile, cfg=cfg, fmt="wav")
    data = out.read_bytes()
    out.unlink(missing_ok=True)
    return data


def _measure(text: str, synth, warm: bool) -> List[Chunk]:
    """Time each chunk exactly as the UI would split and speak it."""
    chunks: List[Chunk] = []
    for piece in split_for_speech(text):
        t0 = time.perf_counter()
        audio = synth(piece)
        elapsed = time.perf_counter() - t0
        chunks.append(Chunk(text=piece, synth_s=elapsed, audio_s=_wav_seconds(audio)))
    return chunks


def _run_case(name: str, text: str, synth, repeat: int):
    """Best-of-N: the fastest run is the least polluted by background load."""
    best = None
    for _ in range(max(1, repeat)):
        res = simulate_stream(_measure(text, synth, warm=True))
        if best is None or res.ttfa_s < best.ttfa_s:
            best = res
    return best


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--voice", required=True)
    p.add_argument("--server", default="", help="benchmark via a speech server (recommended)")
    p.add_argument("--token", default=os.environ.get("HERMES_OMNIVOICE_SERVICE_TOKEN", ""))
    p.add_argument("--voices-dir", default=os.path.expanduser("~/.hermes/voices/omnivoice"))
    p.add_argument("--device", default="auto")
    p.add_argument("--dtype", default="float16")
    p.add_argument("--num-step", type=int, default=None, help="local backend only")
    p.add_argument("--sweep", default="", help="compare num_step values, e.g. 32,16,8,4 (local only)")
    p.add_argument("--case", default="", help="only this case: " + ",".join(UTTERANCES))
    p.add_argument("--repeat", type=int, default=1, help="best-of-N per case")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--budget-ttfa", type=float, default=None)
    p.add_argument("--budget-rtf", type=float, default=None)
    p.add_argument("--baseline", default="", help="fail if slower than this recorded run")
    p.add_argument("--tolerance", type=float, default=0.15)
    p.add_argument("--save-baseline", default="")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if not args.server and args.sweep:
        pass  # sweep needs the local backend, which is the default when no server
    if args.sweep and args.server:
        print("--sweep varies num_step in-process; it needs the local backend "
              "(drop --server, or restart the server with --num-step).", file=sys.stderr)
        return 2

    cases = {args.case: UTTERANCES[args.case]} if args.case else UTTERANCES
    if args.case and args.case not in UTTERANCES:
        print(f"unknown case '{args.case}'; choose from {', '.join(UTTERANCES)}", file=sys.stderr)
        return 2

    steps = [int(s) for s in args.sweep.split(",") if s.strip()] if args.sweep else [args.num_step]
    report = {"voice": args.voice, "backend": "server" if args.server else "local",
              "load_before": _load_snapshot(), "runs": []}

    for step in steps:
        if args.server:
            def synth(t, _s=step):
                return _synth_server(t, url=args.server, voice=args.voice,
                                     token=args.token, timeout=args.timeout)
        else:
            def synth(t, _s=step):
                return _synth_local(t, voice=args.voice, voices_dir=args.voices_dir,
                                    num_step=_s, device=args.device, dtype=args.dtype)

        try:
            synth("Warm up.")  # never time a cold model
        except urllib.error.URLError as exc:
            print(f"could not reach the speech server: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 - report, don't traceback
            print(f"synthesis unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2

        for name, text in cases.items():
            res = _run_case(name, text, synth, args.repeat)
            report["runs"].append({
                "case": name, "num_step": step, "chunks": res.chunks,
                "ttfa_s": round(res.ttfa_s, 2), "speech_s": round(res.speech_s, 2),
                "synth_s": round(res.synth_s, 2), "wall_s": round(res.wall_s, 2),
                "rtf": round(res.rtf, 2), "stalls": res.stalls,
                "stall_s": round(res.stall_s, 2), "sustainable": res.sustainable,
            })

    report["load_after"] = _load_snapshot()
    budgets = {"ttfa_s": args.budget_ttfa, "rtf": args.budget_rtf}
    worst = max(report["runs"], key=lambda r: r["rtf"]) if report["runs"] else None
    verdict = {"ok": True}
    if worst:
        merged = simulate_stream([Chunk("", worst["synth_s"], worst["speech_s"])])
        merged.ttfa_s, merged.rtf = worst["ttfa_s"], worst["rtf"]
        merged.stall_s = worst["stall_s"]
        verdict = evaluate(merged, budgets)
    report["verdict"] = verdict

    exit_code = 0 if verdict["ok"] else 1

    if args.baseline:
        try:
            base = json.loads(Path(args.baseline).read_text())
        except (OSError, ValueError) as exc:
            print(f"could not read baseline: {exc}", file=sys.stderr)
            return 2
        by_key = {(r["case"], r.get("num_step")): r for r in base.get("runs", [])}
        regressions = []
        for run in report["runs"]:
            prev = by_key.get((run["case"], run.get("num_step")))
            if not prev:
                continue
            res = simulate_stream([])
            res.ttfa_s, res.rtf, res.wall_s = run["ttfa_s"], run["rtf"], run["wall_s"]
            cmp = compare_baseline(res, prev, args.tolerance)
            for reg in cmp["regressions"]:
                reg["case"] = run["case"]
                regressions.append(reg)
        report["regressions"] = regressions
        if regressions:
            exit_code = 1

    if args.save_baseline:
        Path(args.save_baseline).write_text(json.dumps(report, indent=2))

    if args.json:
        print(json.dumps(report, indent=2))
        return exit_code

    load = report.get("load_before") or {}
    load_note = (f" · load {load.get('load1')}/{load.get('cpus')} cpu"
                 if load else "")
    print(f"\nlive-voice benchmark · voice={args.voice} · backend={report['backend']}{load_note}\n")
    if load.get("busy"):
        print("  ! machine is busy — these timings measure contention as much as the\n"
              "    engine. Re-run on an idle machine before trusting or recording them.\n")
    hdr = f"{'case':7} {'step':>5} {'chunks':>7} {'TTFA':>7} {'speech':>7} {'synth':>7} {'RTF':>6} {'stalls':>7}"
    print(hdr); print("-" * len(hdr))
    for r in report["runs"]:
        print(f"{r['case']:7} {str(r['num_step'] or '-'):>5} {r['chunks']:>7} "
              f"{r['ttfa_s']:>6.2f}s {r['speech_s']:>6.2f}s {r['synth_s']:>6.2f}s "
              f"{r['rtf']:>6.2f} {r['stalls']:>7}")
    print()
    for key, c in verdict.get("checks", {}).items():
        mark = "ok " if c["got"] <= c["budget"] else "OVER"
        print(f"  [{mark}] {key:8} {c['got']:.2f} (budget {c['budget']:.2f})")
    sustained = [r for r in report["runs"] if r["sustainable"]]
    print(f"\n  RTF < 1.0 means speech is generated faster than it is spoken — "
          f"{len(sustained)}/{len(report['runs'])} runs sustain a reply of any length.")
    for reg in report.get("regressions", []):
        print(f"  [REGRESSED] {reg['case']}/{reg['metric']}: "
              f"{reg['baseline']:.2f} -> {reg['now']:.2f} (+{reg['pct']:.0f}%)")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
