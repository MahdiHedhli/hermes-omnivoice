"""Timing model behind the live-voice benchmark.

Pure arithmetic — no audio, no model — so the thing that decides "is this
real-time" is itself covered by the offline suite.
"""

from __future__ import annotations

from ov_core.realtime import (
    Chunk, compare_baseline, evaluate, simulate_stream, split_for_speech, trim_for_speech,
)


def test_ttfa_is_only_the_first_chunk():
    """Responsiveness is the first sentence, not the whole reply — that is the
    entire point of speaking chunk-by-chunk."""
    res = simulate_stream([Chunk("a", 2.0, 3.0), Chunk("b", 2.0, 3.0), Chunk("c", 2.0, 3.0)])
    assert res.ttfa_s == 2.0
    assert res.synth_s == 6.0          # total compute is still all three
    assert res.speech_s == 9.0


def test_faster_than_realtime_never_stalls():
    """RTF < 1: each chunk is produced well inside the previous chunk's playback."""
    res = simulate_stream([Chunk("a", 1.0, 4.0), Chunk("b", 1.0, 4.0), Chunk("c", 1.0, 4.0)])
    assert res.rtf < 1.0
    assert res.stalls == 0 and res.stall_s == 0.0
    assert res.sustainable is True
    # playback is continuous: first word at 1.0, then 12s of speech
    assert res.wall_s == 13.0


def test_slower_than_realtime_stalls_between_chunks():
    """RTF > 1: synthesis falls behind, so playback runs dry mid-reply."""
    res = simulate_stream([Chunk("a", 5.0, 2.0), Chunk("b", 5.0, 2.0), Chunk("c", 5.0, 2.0)])
    assert res.rtf > 1.0
    assert res.stalls == 2                 # a->b and b->c
    assert res.stall_s == 6.0              # 3s of silence each time
    assert res.sustainable is False


def test_buffer_absorbs_one_slow_chunk():
    """A long first chunk buys time: a single slow follower can still land
    before playback catches up, so it must NOT be reported as a stall."""
    res = simulate_stream([Chunk("a", 2.0, 10.0), Chunk("b", 6.0, 2.0)])
    assert res.stalls == 0
    assert res.rtf < 1.0


def test_empty_and_single_chunk():
    empty = simulate_stream([])
    assert empty.chunks == 0 and empty.ttfa_s == 0.0
    one = simulate_stream([Chunk("a", 3.0, 6.0)])
    assert one.ttfa_s == 3.0 and one.wall_s == 9.0 and one.stalls == 0


def test_split_matches_the_ui_chunking():
    """The benchmark must measure the same pieces the Talk tab speaks."""
    assert split_for_speech("One. Two! Three?") == ["One.", "Two!", "Three?"]
    assert split_for_speech("No terminator here") == ["No terminator here"]
    assert split_for_speech("   ") == []


def test_trim_strips_markdown_and_caps_length():
    assert "**" not in trim_for_speech("**bold** text")
    assert trim_for_speech("```py\ncode\n```  spoken") == "spoken"
    long = "This sentence is here to pad the reply. " * 40
    assert len(trim_for_speech(long)) <= 360


def test_evaluate_flags_each_budget():
    good = simulate_stream([Chunk("a", 1.0, 4.0)])
    assert evaluate(good)["ok"] is True

    slow = simulate_stream([Chunk("a", 9.0, 3.0)])
    verdict = evaluate(slow)
    assert verdict["ok"] is False
    assert "ttfa_s" in verdict["failures"] and "rtf" in verdict["failures"]

    # budgets are overridable for hardware that will never hit the ideal
    assert evaluate(slow, {"ttfa_s": 20.0, "rtf": 5.0})["ok"] is True


def test_baseline_catches_a_regression_but_tolerates_noise():
    res = simulate_stream([Chunk("a", 1.0, 4.0)])
    res.ttfa_s, res.rtf, res.wall_s = 2.0, 0.5, 10.0

    assert compare_baseline(res, {"ttfa_s": 1.95, "rtf": 0.49, "wall_s": 9.9})["ok"] is True

    worse = compare_baseline(res, {"ttfa_s": 1.0, "rtf": 0.5, "wall_s": 10.0})
    assert worse["ok"] is False
    assert [r["metric"] for r in worse["regressions"]] == ["ttfa_s"]
    assert worse["regressions"][0]["pct"] == 100.0


def test_baseline_ignores_missing_or_zero_metrics():
    res = simulate_stream([Chunk("a", 1.0, 4.0)])
    assert compare_baseline(res, {})["ok"] is True
    assert compare_baseline(res, {"ttfa_s": 0})["ok"] is True
