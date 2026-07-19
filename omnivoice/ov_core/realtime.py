"""Real-time analysis for spoken replies.

Whether a voice feels *live* is not "is synthesis fast" — it's two questions:

1. **Time to first audio (TTFA).** How long after the user stops talking before
   they hear anything. This is what reads as responsiveness.
2. **Does it keep up?** Once speech starts, each following chunk has to be
   synthesized before the previous one finishes playing. If it isn't, playback
   stalls mid-sentence, which sounds far worse than a slightly longer wait.

The Talk tab speaks a reply sentence-by-sentence, synthesizing the next chunk
while the current one plays, so both questions are answerable from per-chunk
timings. This module is the pure timing model behind that — no audio, no
network, no model — so it can be unit-tested offline and reused by the
benchmark CLI (``tools/bench_live.py``).

The headline number is the **real-time factor (RTF)**: synthesis seconds per
second of audio produced. RTF < 1.0 means the engine generates speech faster
than it is spoken, so it can sustain a reply of any length. RTF > 1.0 means it
falls behind and only finite replies work — the gap is covered by whatever
audio is already buffered.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Mirrors forSpeech() in the dashboard bundle: the benchmark must measure the
# same chunking the UI actually performs, or the numbers describe nothing.
_SPEECH_MAX_CHARS = 360
_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+(?:\s|$)|[^.!?]+$")


def trim_for_speech(text: str, max_chars: int = _SPEECH_MAX_CHARS) -> str:
    """Strip stray markdown and cap length, as the Talk tab does before speaking."""
    t = re.sub(r"```.*?```", " ", text or "", flags=re.S)
    t = re.sub(r"[*_#`>|~]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) <= max_chars:
        return t
    cut = t[:max_chars]
    stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return (cut[:stop + 1] if stop > 120 else cut).strip()


def split_for_speech(text: str, max_chars: int = _SPEECH_MAX_CHARS) -> List[str]:
    """The chunks the UI would synthesize and play, in order."""
    trimmed = trim_for_speech(text, max_chars)
    if not trimmed:
        return []
    return [c.strip() for c in _SENTENCE_RE.findall(trimmed) if c.strip()] or [trimmed]


@dataclass
class Chunk:
    """One synthesized piece: how long it took, and how long it plays for."""
    text: str
    synth_s: float
    audio_s: float


@dataclass
class StreamResult:
    ttfa_s: float = 0.0           # silence before the first word is heard
    speech_s: float = 0.0         # audio produced
    synth_s: float = 0.0          # compute spent
    wall_s: float = 0.0           # request -> last word finishes playing
    rtf: float = 0.0              # synth_s / speech_s  (<1 sustains indefinitely)
    stalls: int = 0               # times playback ran dry waiting on synthesis
    stall_s: float = 0.0          # total silence mid-reply
    chunks: int = 0
    gaps: List[float] = field(default_factory=list)

    @property
    def sustainable(self) -> bool:
        """True when synthesis outpaces speech, so reply length doesn't matter."""
        return self.rtf < 1.0 and self.stalls == 0


def simulate_stream(chunks: List[Chunk]) -> StreamResult:
    """Play chunks back the way the Talk tab does and report what the user hears.

    Synthesis is modelled as serial — one model behind a lock, so chunk *i+1*
    is being produced while chunk *i* plays, but never two at once. Playback of
    a chunk starts when it is both ready and its predecessor has finished.
    """
    res = StreamResult(chunks=len(chunks))
    if not chunks:
        return res

    ready = 0.0        # when chunk i has finished synthesizing
    play_end = 0.0     # when the previous chunk finishes playing
    for idx, c in enumerate(chunks):
        ready += max(0.0, c.synth_s)
        if idx == 0:
            res.ttfa_s = ready
            start = ready
        else:
            start = max(ready, play_end)
            gap = max(0.0, ready - play_end)   # playback ran dry this long
            res.gaps.append(gap)
            if gap > 0:
                res.stalls += 1
                res.stall_s += gap
        play_end = start + max(0.0, c.audio_s)
        res.speech_s += max(0.0, c.audio_s)
        res.synth_s += max(0.0, c.synth_s)

    res.wall_s = play_end
    res.rtf = (res.synth_s / res.speech_s) if res.speech_s > 0 else float("inf")
    return res


# --- verdicts ---------------------------------------------------------------

# What "feels live" means for a spoken assistant. TTFA dominates the sense of
# responsiveness; RTF 1.0 is the hard line between "sustains any reply" and
# "only finite replies work".
DEFAULT_BUDGETS: Dict[str, float] = {"ttfa_s": 2.5, "rtf": 1.0, "stall_s": 0.0}


def evaluate(result: StreamResult, budgets: Optional[Dict[str, float]] = None) -> Dict[str, object]:
    """Check a run against live-conversation budgets."""
    b = dict(DEFAULT_BUDGETS)
    if budgets:
        b.update({k: v for k, v in budgets.items() if v is not None})
    checks = {
        "ttfa_s": (result.ttfa_s, b["ttfa_s"]),
        "rtf": (result.rtf, b["rtf"]),
        "stall_s": (result.stall_s, b["stall_s"]),
    }
    failures = [k for k, (got, limit) in checks.items() if got > limit]
    return {"ok": not failures, "failures": failures,
            "checks": {k: {"got": got, "budget": limit} for k, (got, limit) in checks.items()}}


def compare_baseline(result: StreamResult, baseline: Dict[str, float],
                     tolerance: float = 0.15) -> Dict[str, object]:
    """Regression gate: flag metrics that got meaningfully worse than a recorded run.

    Absolute budgets answer "is this fast enough"; this answers "did we make it
    slower", which is the one that belongs in a dev loop — it stays useful on
    hardware that never met the absolute target in the first place.
    """
    regressions = []
    for key in ("ttfa_s", "rtf", "wall_s"):
        was = baseline.get(key)
        now = getattr(result, key, None)
        if not isinstance(was, (int, float)) or was <= 0 or now is None:
            continue
        if now > was * (1.0 + tolerance):
            regressions.append({"metric": key, "baseline": was, "now": now,
                                "pct": (now / was - 1.0) * 100.0})
    return {"ok": not regressions, "regressions": regressions, "tolerance": tolerance}
