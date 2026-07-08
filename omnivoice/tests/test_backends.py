from __future__ import annotations

import wave

import pytest

from ov_core import backends
from ov_core.backends import SynthError
from ov_core.config import OmniVoiceConfig, ServiceConfig, StudioConfig
from ov_core.registry import VoiceRegistry


def _design_profile(voices_dir):
    reg = VoiceRegistry(voices_dir)
    reg.create_design("narrator", "Narrator", "male, moderate pitch")
    return reg.get_voice("narrator")


def test_validate_url_loopback_ok():
    assert backends._validate_url("http://127.0.0.1:3900", require_loopback=True) == "http://127.0.0.1:3900"


def test_validate_url_rejects_non_loopback_when_required():
    with pytest.raises(SynthError):
        backends._validate_url("http://10.0.0.5:3900", require_loopback=True)


def test_validate_url_rejects_bad_scheme_and_userinfo():
    with pytest.raises(SynthError):
        backends._validate_url("ftp://127.0.0.1", require_loopback=False)
    with pytest.raises(SynthError):
        backends._validate_url("http://user:pw@127.0.0.1", require_loopback=False)


def test_health_ok_unreachable_is_false():
    assert backends.health_ok("") is False
    assert backends.health_ok("http://127.0.0.1:59999", timeout=0.5) is False


def test_join_normalizes_slashes():
    assert backends._join("http://h:1", "/v1/audio/speech") == "http://h:1/v1/audio/speech"
    assert backends._join("http://h:1/", "v1/audio/speech") == "http://h:1/v1/audio/speech"


def test_http_payload_design_uses_openai_shape(voices_dir):
    design = _design_profile(voices_dir)
    payload = backends._http_payload("hi there", design, 1.1, model="omnivoice")
    assert payload == {
        "model": "omnivoice",
        "input": "hi there",
        "voice": "narrator",          # server-side voice id
        "response_format": "wav",
        "speed": 1.1,
        "language_id": "en",
    }


def test_http_payload_clone_selects_server_voice_by_id(voices_dir, wav_factory):
    reg = VoiceRegistry(voices_dir)
    reg.create_clone("cl", "Cl", wav_factory(), "ref text", consent_source="user_uploaded")
    clone = reg.get_voice("cl")
    payload = backends._http_payload("hi", clone, 1.0, model="omnivoice")
    # Over the OpenAI wire, a clone is selected by id — no local ref audio bytes.
    assert payload["voice"] == "cl"
    assert "ref_audio" not in payload and "ref_text" not in payload


def test_finalize_wav_moves(tmp_path):
    src = tmp_path / "t.wav"
    with wave.open(str(src), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\x00\x00" * 100)
    out = tmp_path / "out.wav"
    result = backends._finalize(src, out, "wav")
    assert result == str(out)
    assert out.is_file() and not src.exists()


def test_synthesize_unknown_backend(voices_dir):
    cfg = OmniVoiceConfig(backend="nope")
    with pytest.raises(SynthError):
        backends.synthesize("hi", "/tmp/x.wav", voice=_design_profile(voices_dir), cfg=cfg)


def test_synthesize_empty_text(voices_dir):
    cfg = OmniVoiceConfig(backend="studio")
    with pytest.raises(SynthError):
        backends.synthesize("   ", "/tmp/x.wav", voice=_design_profile(voices_dir), cfg=cfg)


def test_studio_backend_rejects_non_loopback(voices_dir, tmp_path):
    cfg = OmniVoiceConfig(backend="studio", studio=StudioConfig(url="http://10.1.1.9:3900"))
    with pytest.raises(SynthError):
        backends.synthesize("hello", str(tmp_path / "o.wav"),
                            voice=_design_profile(voices_dir), cfg=cfg)


def test_service_backend_requires_url(voices_dir, tmp_path):
    cfg = OmniVoiceConfig(backend="service", service=ServiceConfig(url=""))
    with pytest.raises(SynthError):
        backends.synthesize("hello", str(tmp_path / "o.wav"),
                            voice=_design_profile(voices_dir), cfg=cfg)


def test_service_non_loopback_requires_auth(voices_dir, tmp_path, monkeypatch):
    monkeypatch.delenv("HERMES_OMNIVOICE_SERVICE_TOKEN", raising=False)
    cfg = OmniVoiceConfig(backend="service", service=ServiceConfig(url="http://10.0.0.9:8880"))
    with pytest.raises(SynthError, match="requires an auth token"):
        backends.synthesize("hello", str(tmp_path / "o.wav"),
                            voice=_design_profile(voices_dir), cfg=cfg)


def test_synth_studio_posts_openai_json(voices_dir, tmp_path, monkeypatch):
    captured = {}

    def fake_post(url, payload, *, timeout, auth_token=""):
        captured["url"] = url
        captured["payload"] = payload
        captured["auth"] = auth_token
        return b"RIFF....WAVEfake-audio-bytes"

    monkeypatch.setattr(backends, "_post_json", fake_post)
    cfg = OmniVoiceConfig(backend="studio", studio=StudioConfig(url="http://127.0.0.1:8880"))
    out = tmp_path / "o.wav"
    result = backends.synthesize("hello world", str(out),
                                 voice=_design_profile(voices_dir), cfg=cfg)
    assert result == str(out) and out.is_file()
    assert captured["url"] == "http://127.0.0.1:8880/v1/audio/speech"
    assert captured["payload"]["input"] == "hello world"
    assert captured["payload"]["voice"] == "narrator"


def test_synth_service_sends_bearer(voices_dir, tmp_path, monkeypatch):
    captured = {}

    def fake_post(url, payload, *, timeout, auth_token=""):
        captured["auth"] = auth_token
        return b"RIFF....WAVEfake"

    monkeypatch.setenv("HERMES_OMNIVOICE_SERVICE_TOKEN", "sekret")
    monkeypatch.setattr(backends, "_post_json", fake_post)
    # Loopback service URL is allowed to carry a token without the non-loopback guard.
    cfg = OmniVoiceConfig(backend="service", service=ServiceConfig(url="http://127.0.0.1:8880"))
    backends.synthesize("hi", str(tmp_path / "o.wav"),
                        voice=_design_profile(voices_dir), cfg=cfg)
    assert captured["auth"] == "sekret"


def test_synth_local_sends_language_kwarg(voices_dir, tmp_path, monkeypatch):
    """Regression: the omnivoice 0.1.5 SDK kwarg is `language` (not `language_id`,
    which is the OpenAI HTTP wire field used by the studio/service backends)."""
    import sys
    import types

    from ov_core.config import LocalConfig

    torch = types.ModuleType("torch")
    torch.float32 = "float32-dtype"
    torch.float16 = "float16-dtype"
    torch.bfloat16 = "bfloat16-dtype"
    torch.cuda = types.SimpleNamespace(is_available=lambda: False)
    torch.backends = types.SimpleNamespace(mps=types.SimpleNamespace(is_available=lambda: False))

    captured = {}

    class FakeModel:
        sampling_rate = 24000

        def generate(self, **kw):
            captured.update(kw)
            return [[0.0, 0.0, 0.0]]

    class FakeOmni:
        @staticmethod
        def from_pretrained(model, device_map=None, dtype=None):
            captured["_from_pretrained"] = (model, device_map, dtype)
            return FakeModel()

    omni = types.ModuleType("omnivoice")
    omni.OmniVoice = FakeOmni
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "omnivoice", omni)
    monkeypatch.setattr(backends, "_write_samples", lambda samples, sr, out, fmt: str(out))
    backends._model_cache.clear()

    cfg = OmniVoiceConfig(backend="local", local=LocalConfig(device="cpu", dtype="float32"))
    backends.synthesize("hello", str(tmp_path / "o.wav"),
                        voice=_design_profile(voices_dir), cfg=cfg)

    assert captured.get("language") == "en"
    assert "language_id" not in captured
    assert captured.get("instruct") == "male, moderate pitch"
    assert captured["_from_pretrained"] == ("k2-fsa/OmniVoice", "cpu", "float32-dtype")


def test_synth_local_passes_configured_num_step(voices_dir, tmp_path, monkeypatch):
    """OmniVoice is a diffusion-LM TTS model: num_step is the denoising step
    count and is the main speed/quality knob (measured on MPS: 16 steps is
    ASR-identical to the 32 default at ~1.9x the speed). Regression: the
    configured value must actually reach generate()'s generation_config."""
    import sys
    import types

    from ov_core.config import LocalConfig

    torch = types.ModuleType("torch")
    torch.float32 = "float32-dtype"
    torch.backends = types.SimpleNamespace(mps=types.SimpleNamespace(is_available=lambda: False))
    torch.cuda = types.SimpleNamespace(is_available=lambda: False)

    captured = {}

    class FakeModel:
        sampling_rate = 24000

        def generate(self, **kw):
            captured.update(kw)
            return [[0.0, 0.0, 0.0]]

    class FakeOmni:
        @staticmethod
        def from_pretrained(model, device_map=None, dtype=None):
            return FakeModel()

    class FakeGenerationConfig:
        def __init__(self, num_step):
            self.num_step = num_step

    omni = types.ModuleType("omnivoice")
    omni.OmniVoice = FakeOmni
    omni_models = types.ModuleType("omnivoice.models")
    omni_models_ov = types.ModuleType("omnivoice.models.omnivoice")
    omni_models_ov.OmniVoiceGenerationConfig = FakeGenerationConfig
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "omnivoice", omni)
    monkeypatch.setitem(sys.modules, "omnivoice.models", omni_models)
    monkeypatch.setitem(sys.modules, "omnivoice.models.omnivoice", omni_models_ov)
    monkeypatch.setattr(backends, "_write_samples", lambda samples, sr, out, fmt: str(out))
    backends._model_cache.clear()

    cfg = OmniVoiceConfig(backend="local", local=LocalConfig(device="cpu", dtype="float32", num_step=8))
    backends.synthesize("hello", str(tmp_path / "o.wav"),
                        voice=_design_profile(voices_dir), cfg=cfg)

    gen_cfg = captured.get("generation_config")
    assert isinstance(gen_cfg, FakeGenerationConfig)
    assert gen_cfg.num_step == 8


# --- ssh-loopback service transport ----------------------------------------

def _svc(**kw):
    return OmniVoiceConfig(backend="service", service=ServiceConfig(**kw))


def test_service_unknown_transport_raises(voices_dir, tmp_path):
    cfg = _svc(url="http://127.0.0.1:8880", transport="carrier-pigeon")
    with pytest.raises(SynthError, match="unknown service transport"):
        backends.synthesize("hi", str(tmp_path / "o.wav"),
                            voice=_design_profile(voices_dir), cfg=cfg)


def test_service_ssh_loopback_requires_ssh_host(voices_dir, tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_OMNIVOICE_SERVICE_TOKEN", "tok")
    cfg = _svc(url="http://127.0.0.1:8880", transport="ssh-loopback", ssh_host="")
    with pytest.raises(SynthError, match="requires service.ssh_host"):
        backends.synthesize("hi", str(tmp_path / "o.wav"),
                            voice=_design_profile(voices_dir), cfg=cfg)


def test_service_ssh_loopback_requires_token(voices_dir, tmp_path, monkeypatch):
    monkeypatch.delenv("HERMES_OMNIVOICE_SERVICE_TOKEN", raising=False)
    cfg = _svc(url="http://127.0.0.1:8880", transport="ssh-loopback", ssh_host="h@1.2.3.4")
    with pytest.raises(SynthError, match="requires an auth token"):
        backends.synthesize("hi", str(tmp_path / "o.wav"),
                            voice=_design_profile(voices_dir), cfg=cfg)


def test_synth_service_ssh_loopback_routes(voices_dir, tmp_path, monkeypatch):
    captured = {}

    def fake_ssh(url, payload, *, timeout, auth_token, ssh_host, ssh_port=22, ssh_identity_file=""):
        captured.update(url=url, auth=auth_token, host=ssh_host, port=ssh_port)
        return b"RIFF....WAVEfake"

    monkeypatch.setenv("HERMES_OMNIVOICE_SERVICE_TOKEN", "tok")
    monkeypatch.setattr(backends, "_post_json_ssh_loopback", fake_ssh)
    cfg = _svc(url="http://127.0.0.1:8880", transport="ssh-loopback",
               ssh_host="hermes-ops@100.78.163.62", ssh_port=2222)
    backends.synthesize("hi", str(tmp_path / "o.wav"),
                        voice=_design_profile(voices_dir), cfg=cfg)
    assert captured["url"] == "http://127.0.0.1:8880/v1/audio/speech"
    assert captured["auth"] == "tok"
    assert captured["host"] == "hermes-ops@100.78.163.62" and captured["port"] == 2222


def test_post_json_ssh_loopback_parses_framed_response(monkeypatch):
    import json as _json
    import struct as _struct
    import types

    meta = _json.dumps({"status": 200, "content_type": "audio/wav"}).encode()
    body = b"RIFF....WAVE-real-audio"
    stdout = _struct.pack(">I", len(meta)) + meta + body

    def fake_run(cmd, **kw):
        assert "ssh" in cmd[0]
        return types.SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")

    monkeypatch.setattr(backends.subprocess, "run", fake_run)
    out = backends._post_json_ssh_loopback(
        "http://127.0.0.1:8880/v1/audio/speech", {"input": "hi"},
        timeout=30, auth_token="tok", ssh_host="h@1.2.3.4",
    )
    assert out == body


def test_post_json_ssh_loopback_non_200_raises(monkeypatch):
    import json as _json
    import struct as _struct
    import types

    meta = _json.dumps({"status": 403, "content_type": "application/json"}).encode()
    stdout = _struct.pack(">I", len(meta)) + meta + b'{"detail":"nope"}'
    monkeypatch.setattr(backends.subprocess, "run",
                        lambda cmd, **kw: types.SimpleNamespace(returncode=0, stdout=stdout, stderr=b""))
    with pytest.raises(SynthError, match="HTTP 403"):
        backends._post_json_ssh_loopback("http://127.0.0.1:8880/v1/audio/speech", {"input": "hi"},
                                         timeout=30, auth_token="tok", ssh_host="h@1.2.3.4")
