"""Test fixtures. Tests run without the OmniVoice SDK, torch, soundfile, or a
Hermes install — only PyYAML and the stdlib are required."""

from __future__ import annotations

import struct
import sys
import wave
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@pytest.fixture
def voices_dir(tmp_path: Path) -> Path:
    d = tmp_path / "voices"
    d.mkdir()
    return d


@pytest.fixture
def wav_factory(tmp_path: Path):
    def make(name: str = "ref.wav", frames: int = 8000) -> Path:
        p = tmp_path / name
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(struct.pack("<" + "h" * frames, *([0] * frames)))
        return p
    return make
