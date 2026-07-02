from __future__ import annotations

import pytest

from ov_core.backends import SynthError
from ov_core.provider import OmniVoiceProvider
from ov_core.registry import VoiceRegistry


@pytest.fixture
def provider_env(monkeypatch, tmp_path):
    home = tmp_path / "hermeshome"
    home.mkdir()
    vdir = tmp_path / "voices"
    vdir.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("HERMES_OMNIVOICE_VOICES_DIR", str(vdir))
    monkeypatch.setenv("HERMES_OMNIVOICE_BACKEND", "local")
    return vdir


def test_identity():
    p = OmniVoiceProvider()
    assert p.name == "omnivoice"
    assert p.display_name == "OmniVoice"
    assert p.voice_compatible is True


def test_setup_schema():
    schema = OmniVoiceProvider().get_setup_schema()
    assert schema["name"] == "OmniVoice"
    assert isinstance(schema["env_vars"], list)


def test_empty_registry(provider_env):
    p = OmniVoiceProvider()
    assert p.list_voices() == []
    assert p.default_voice() is None


def test_lists_and_defaults_created_voice(provider_env):
    VoiceRegistry(provider_env).create_design("narrator", "Narrator", "male voice")
    p = OmniVoiceProvider()
    voices = p.list_voices()
    assert len(voices) == 1 and voices[0]["id"] == "narrator"
    assert p.default_voice() == "narrator"


def test_synthesize_without_voice_raises(provider_env, tmp_path):
    p = OmniVoiceProvider()
    with pytest.raises(SynthError):
        p.synthesize("hello", str(tmp_path / "o.wav"))


def test_synthesize_local_without_sdk_raises(provider_env, tmp_path):
    # A voice exists but the local backend has no OmniVoice SDK installed here,
    # so synthesize must surface a SynthError (not crash).
    VoiceRegistry(provider_env).create_design("narrator", "Narrator", "male voice")
    p = OmniVoiceProvider()
    with pytest.raises(SynthError):
        p.synthesize("hello", str(tmp_path / "o.wav"), voice="narrator")
