from __future__ import annotations

import os

import pytest

from ov_core.registry import RegistryError, VoiceRegistry


def test_design_create_list_and_active(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("narrator", "Narrator", "male, american accent")
    voices = reg.list_voices()
    assert len(voices) == 1
    assert voices[0].id == "narrator"
    assert voices[0].mode == "design"

    reg.set_active("narrator")
    assert reg.get_active() == "narrator"
    assert reg.default_voice() == "narrator"


def test_design_requires_instruct(voices_dir):
    reg = VoiceRegistry(voices_dir)
    with pytest.raises(RegistryError):
        reg.create_design("bad", "Bad", "")


def test_clone_roundtrip_and_consent_gate(voices_dir, wav_factory):
    reg = VoiceRegistry(voices_dir)
    ref = wav_factory()
    reg.create_clone("marvin", "Marvin", ref, "reference transcript here",
                     consent_source="user_uploaded")
    p = reg.get_voice("marvin")           # get_voice enforces consent + WAV validity
    assert p.mode == "clone"
    assert p.ref_audio_path.is_file()
    assert oct(p.ref_audio_path.stat().st_mode)[-3:] == "600"


def test_clone_requires_ref_text(voices_dir, wav_factory):
    reg = VoiceRegistry(voices_dir)
    with pytest.raises(RegistryError):
        reg.create_clone("x", "X", wav_factory(), "", consent_source="user_uploaded")


def test_clone_requires_consent_source(voices_dir, wav_factory):
    reg = VoiceRegistry(voices_dir)
    with pytest.raises(RegistryError):
        reg.create_clone("x", "X", wav_factory(), "text", consent_source="")


def test_clone_rejects_non_wav(voices_dir, tmp_path):
    reg = VoiceRegistry(voices_dir)
    junk = tmp_path / "notaudio.wav"
    junk.write_bytes(b"this is not a wav file")
    with pytest.raises(RegistryError):
        reg.create_clone("x", "X", junk, "text", consent_source="user_uploaded")


def test_clone_rejects_overlong_reference(voices_dir, wav_factory, monkeypatch):
    monkeypatch.delenv("HERMES_OMNIVOICE_MAX_REF_SECONDS", raising=False)
    reg = VoiceRegistry(voices_dir)
    long_ref = wav_factory("long.wav", frames=16000 * 50)  # 50s at 16 kHz > 45s cap
    with pytest.raises(RegistryError, match="short clean clip"):
        reg.create_clone("x", "X", long_ref, "text", consent_source="user_uploaded")


def test_clone_ref_cap_env_override_disables(voices_dir, wav_factory, monkeypatch):
    monkeypatch.setenv("HERMES_OMNIVOICE_MAX_REF_SECONDS", "0")  # 0 disables the cap
    reg = VoiceRegistry(voices_dir)
    long_ref = wav_factory("long2.wav", frames=16000 * 50)
    reg.create_clone("x", "X", long_ref, "text", consent_source="user_uploaded")
    assert reg.get_voice("x").mode == "clone"


def test_duplicate_id_rejected_unless_overwrite(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("dup", "Dup", "male")
    with pytest.raises(RegistryError):
        reg.create_design("dup", "Dup", "female")
    reg.create_design("dup", "Dup2", "female", overwrite=True)
    assert reg.get_voice("dup").name == "Dup2"


def test_invalid_id_rejected(voices_dir):
    reg = VoiceRegistry(voices_dir)
    with pytest.raises(RegistryError):
        reg.create_design("Bad Id!", "x", "voice")


def test_symlinked_voice_dir_is_skipped(voices_dir, tmp_path):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("real", "Real", "male")
    # A symlinked voice dir must not be listed or loaded.
    target = tmp_path / "elsewhere"
    target.mkdir()
    (target / "voice.yaml").write_text("id: evil\nname: Evil\nmode: design\ninstruct: x\n")
    link = voices_dir / "evil"
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unsupported here")
    ids = {v.id for v in reg.list_voices()}
    assert "evil" not in ids
    with pytest.raises(RegistryError):
        reg.get_voice("evil")


def test_design_rejects_unsupported_instruct(voices_dir):
    reg = VoiceRegistry(voices_dir)
    with pytest.raises(RegistryError, match="unsupported instruct"):
        reg.create_design("bad", "Bad", "female, energetic, moderate pitch")


def test_design_accepts_valid_instruct(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("ok", "Ok", "female, british accent, whisper")
    assert reg.get_voice("ok").instruct == "female, british accent, whisper"


def test_update_voice_design(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("nn", "NN", "male, moderate pitch")
    reg.update_voice("nn", name="Renamed", instruct="female, whisper", language="fr")
    p = reg.get_voice("nn")
    assert p.name == "Renamed" and p.instruct == "female, whisper" and p.language == "fr"


def test_update_voice_rejects_bad_instruct(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("nn", "NN", "male")
    with pytest.raises(RegistryError, match="unsupported instruct"):
        reg.update_voice("nn", instruct="male, sassy")


def test_update_voice_clone_ref_text(voices_dir, wav_factory):
    reg = VoiceRegistry(voices_dir)
    reg.create_clone("cl", "Cl", wav_factory(), "old text", consent_source="user_uploaded")
    reg.update_voice("cl", name="Cl2", ref_text="new transcript")
    p = reg.get_voice("cl")
    assert p.name == "Cl2" and p.ref_text == "new transcript" and p.mode == "clone"


def test_delete_clears_active(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("gone", "Gone", "male")
    reg.set_active("gone")
    reg.delete_voice("gone")
    assert reg.get_active() is None
    assert reg.list_voices() == []
