"""Dashboard route tests (FastAPI TestClient).

Skipped cleanly when fastapi/httpx are absent, so the stdlib+PyYAML baseline
still runs. TestClient's peer host is ``testclient`` (non-loopback), which lets
us exercise the loopback gate in both directions.
"""

from __future__ import annotations

import importlib.util
import io
import wave
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import FastAPI
from fastapi.testclient import TestClient

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_API_FILE = _PLUGIN_ROOT / "dashboard" / "plugin_api.py"
BASE = "/api/plugins/omnivoice"


def _load_api():
    spec = importlib.util.spec_from_file_location("ov_dashboard_api", _API_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wav_bytes(frames: int = 8000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x00\x00" * frames)
    return buf.getvalue()


@pytest.fixture
def api(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    vdir = tmp_path / "voices"
    vdir.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("HERMES_OMNIVOICE_VOICES_DIR", str(vdir))
    monkeypatch.setenv("HERMES_OMNIVOICE_BACKEND", "studio")

    mod = _load_api()

    def fake_synth(text, out, *, voice, cfg, fmt="wav"):
        Path(out).write_bytes(_wav_bytes(10))
        return out

    monkeypatch.setattr(mod, "synthesize", fake_synth)
    app = FastAPI()
    app.include_router(mod.router, prefix=BASE)
    return TestClient(app), monkeypatch


def _optin(monkeypatch):
    monkeypatch.setenv("HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE", "1")


def test_list_empty(api):
    client, _ = api
    r = client.get(BASE + "/voices")
    assert r.status_code == 200
    body = r.json()
    assert body["voices"] == [] and body["active"] is None


def test_non_loopback_refused_without_optin(api):
    client, monkeypatch = api
    monkeypatch.delenv("HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE", raising=False)
    r = client.post(BASE + "/voices/design", json={"id": "x", "name": "X", "instruct": "male"})
    assert r.status_code == 403


def test_design_create_and_list(api):
    client, monkeypatch = api
    _optin(monkeypatch)
    r = client.post(BASE + "/voices/design",
                    json={"id": "narrator", "name": "Narrator", "instruct": "male, moderate pitch"})
    assert r.status_code == 200, r.text
    ids = [v["id"] for v in client.get(BASE + "/voices").json()["voices"]]
    assert "narrator" in ids


def test_clone_requires_consent(api):
    client, monkeypatch = api
    _optin(monkeypatch)
    files = {"ref_audio": ("ref.wav", _wav_bytes(), "audio/wav")}
    data = {"id": "cl", "ref_text": "hello", "consent_confirmed": "false"}
    r = client.post(BASE + "/voices/clone", files=files, data=data)
    assert r.status_code == 400


def test_clone_rejects_non_wav(api):
    client, monkeypatch = api
    _optin(monkeypatch)
    files = {"ref_audio": ("ref.wav", b"not a wav file", "audio/wav")}
    data = {"id": "cl", "ref_text": "hello", "consent_confirmed": "true"}
    r = client.post(BASE + "/voices/clone", files=files, data=data)
    assert r.status_code == 400


def test_instruct_vocab(api):
    client, _ = api
    r = client.get(BASE + "/instruct-vocab")
    assert r.status_code == 200
    vocab = r.json()["vocab"]
    assert "gender" in vocab and "male" in vocab["gender"]


def test_patch_updates_and_rejects_bad_instruct(api):
    client, monkeypatch = api
    _optin(monkeypatch)
    assert client.post(BASE + "/voices/design",
                       json={"id": "n", "name": "N", "instruct": "male, moderate pitch"}).status_code == 200
    r = client.patch(BASE + "/voices/n", json={"name": "N2", "instruct": "female, whisper"})
    assert r.status_code == 200 and r.json()["voice"]["name"] == "N2"
    assert client.patch(BASE + "/voices/n", json={"instruct": "female, energetic"}).status_code == 400


class _FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_talk_returns_reply_and_session(api):
    import subprocess

    client, monkeypatch = api
    _optin(monkeypatch)
    captured = {}

    def fake_run(cmd, capture_output, text, timeout):
        captured["cmd"] = cmd
        # Mirror the real CLI: reply on stdout, `session_id:` line on stderr.
        return _FakeProc(stdout="Hello there, friend.",
                         stderr="\nsession_id: 20260101_000000_abcdef")

    # plugin_api does `import subprocess`, so patching the shared module's `run`
    # attribute reaches the route without needing a handle on the loaded module.
    monkeypatch.setattr(subprocess, "run", fake_run)

    r = client.post(BASE + "/talk", json={"text": "hi"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["reply"] == "Hello there, friend."
    assert body["session_id"] == "20260101_000000_abcdef"
    # continuity: a provided session id becomes --resume <id>
    r2 = client.post(BASE + "/talk", json={"text": "again", "session_id": "sess42"})
    assert r2.status_code == 200
    assert "--resume" in captured["cmd"] and "sess42" in captured["cmd"]


def test_talk_requires_text(api):
    client, monkeypatch = api
    _optin(monkeypatch)
    assert client.post(BASE + "/talk", json={"text": "  "}).status_code == 400


def test_talk_non_loopback_refused_without_optin(api):
    client, monkeypatch = api
    monkeypatch.delenv("HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE", raising=False)
    assert client.post(BASE + "/talk", json={"text": "hi"}).status_code == 403


def test_set_provider_is_surgical_and_preserves_comments(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / "config.yaml"
    cfg.write_text(
        "# top comment\n"
        "model:\n  provider: openai\n"
        "tts:\n"
        "  provider: edge   # inline comment\n"
        "  edge:\n    voice: en-US-AriaNeural\n"
        "stt:\n  provider: local\n"
        "# trailing comment block\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_HOME", str(home))
    mod = _load_api()
    assert mod._set_tts_provider_omnivoice() is True
    out = cfg.read_text(encoding="utf-8")
    assert "provider: omnivoice" in out
    # only the tts provider changed; other providers + all comments intact
    assert "  provider: openai\n" in out           # model.provider untouched
    assert "stt:\n  provider: local\n" in out       # stt.provider untouched
    assert "# top comment" in out and "# trailing comment block" in out
    assert "voice: en-US-AriaNeural" in out
    # idempotent
    assert mod._set_tts_provider_omnivoice() is True
    assert out.count("provider: omnivoice") == 1


def test_provider_reported_in_list(api):
    client, _ = api
    r = client.get(BASE + "/voices")
    assert r.status_code == 200 and "provider" in r.json()


def test_talk_agent_error_is_502(api):
    import subprocess

    client, monkeypatch = api
    _optin(monkeypatch)
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _FakeProc(returncode=1, stderr="model not configured"))
    r = client.post(BASE + "/talk", json={"text": "hi"})
    assert r.status_code == 502 and "model not configured" in r.json()["detail"]


def test_clone_preview_activate_delete(api):
    client, monkeypatch = api
    _optin(monkeypatch)
    files = {"ref_audio": ("ref.wav", _wav_bytes(), "audio/wav")}
    data = {"id": "cl", "name": "Cl", "ref_text": "hello world", "consent_confirmed": "true"}
    assert client.post(BASE + "/voices/clone", files=files, data=data).status_code == 200

    rp = client.post(BASE + "/voices/cl/preview", json={})
    assert rp.status_code == 200 and rp.headers["content-type"].startswith("audio/wav")

    ra = client.put(BASE + "/voices/cl/active", json={"set_provider": False})
    assert ra.status_code == 200 and ra.json()["active"] == "cl"

    assert client.delete(BASE + "/voices/cl").status_code == 200
    assert client.get(BASE + "/voices").json()["voices"] == []
