"""Plugin configuration.

Reads the ``tts.omnivoice`` block from ``~/.hermes/config.yaml`` and applies
environment overrides. We read the YAML directly rather than depending on a
specific ``hermes_cli.config`` import path, so the same code works from the
agent process and the dashboard process. Only simple scalar keys are read, so
a direct load is sufficient and robust.

Config shape (see ``config.example.yaml``)::

    tts:
      provider: omnivoice
      omnivoice:
        backend: local            # local | studio | service
        voices_dir: ""            # default: <HERMES_HOME>/voices/omnivoice
        speed: 1.0
        fallback_provider: piper  # provider to fall back to on backend failure
        local:
          model: k2-fsa/OmniVoice
          device: auto            # auto | cpu | cuda | mps
          dtype: float16
          sample_rate: 24000
          num_step: 16             # diffusion denoising steps; speed/quality tradeoff (see LocalConfig)
        studio:
          url: http://127.0.0.1:3900
          speech_path: /v1/audio/speech
          model: omnivoice
          auth_token_env: HERMES_OMNIVOICE_STUDIO_TOKEN
          timeout: 180
        service:
          url: ""                 # http(s)://host:port
          speech_path: /v1/audio/speech
          model: omnivoice
          auth_token_env: HERMES_OMNIVOICE_SERVICE_TOKEN
          timeout: 180
          max_concurrency: 2
          stream: false

The ``studio``/``service`` backends speak the OpenAI-compatible
``POST {url}{speech_path}`` audio-speech contract (JSON body ``{model, input,
voice, response_format, speed, language_id}``, bearer auth). This matches the
proven OmniVoice-Studio FastAPI surface; it is NOT a bespoke ``/generate``
endpoint. See ``backends.py`` for the wire shape.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from . import paths

_ENV = os.environ

_DEFAULT_SPEECH_PATH = "/v1/audio/speech"
_DEFAULT_HTTP_MODEL = "omnivoice"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        import yaml  # PyYAML ships with Hermes (config.yaml is YAML)
    except Exception:  # pragma: no cover
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data if isinstance(data, dict) else {}
    except Exception:  # pragma: no cover - malformed config never crashes us
        return {}


def _section() -> Dict[str, Any]:
    cfg = _load_yaml(paths.hermes_home() / "config.yaml")
    tts = cfg.get("tts") if isinstance(cfg.get("tts"), dict) else {}
    ov = tts.get("omnivoice") if isinstance(tts.get("omnivoice"), dict) else {}
    return ov or {}


def _sub(section: Dict[str, Any], key: str) -> Dict[str, Any]:
    v = section.get(key)
    return v if isinstance(v, dict) else {}


@dataclass
class LocalConfig:
    model: str = "k2-fsa/OmniVoice"
    device: str = "auto"
    dtype: str = "float16"
    sample_rate: int = 24000
    # OmniVoice is a diffusion-LM TTS model: `num_step` is the denoising step
    # count and scales synthesis time roughly linearly (measured on Apple
    # Silicon/MPS: 32->36.6s, 16->19.4s, 8->11.4s, 4->6.3s for the same phrase).
    # ASR-verified: 16 produces the identical transcript as the 32 default; 8
    # starts dropping words; 4 is broken. 16 is the default here as the best
    # verified speed/quality tradeoff — override via HERMES_OMNIVOICE_NUM_STEP.
    num_step: int = 16


@dataclass
class StudioConfig:
    url: str = "http://127.0.0.1:3900"
    speech_path: str = _DEFAULT_SPEECH_PATH
    model: str = _DEFAULT_HTTP_MODEL
    auth_token_env: str = "HERMES_OMNIVOICE_STUDIO_TOKEN"
    timeout: int = 180

    @property
    def auth_token(self) -> str:
        return _ENV.get(self.auth_token_env, "").strip()


@dataclass
class ServiceConfig:
    url: str = ""
    speech_path: str = _DEFAULT_SPEECH_PATH
    model: str = _DEFAULT_HTTP_MODEL
    auth_token_env: str = "HERMES_OMNIVOICE_SERVICE_TOKEN"
    timeout: int = 180
    max_concurrency: int = 2
    stream: bool = False
    # transport: "http" (direct) or "ssh-loopback" (tunnel the request through
    # SSH so the remote host calls its own loopback-only OmniVoice service —
    # the proven Mac Studio path, ported from the archived spike). In
    # ssh-loopback mode, `url` is the REMOTE-side loopback URL (e.g.
    # http://127.0.0.1:8880) and `ssh_host` is how to reach that host.
    transport: str = "http"
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_identity_file: str = ""

    @property
    def auth_token(self) -> str:
        return _ENV.get(self.auth_token_env, "").strip()


@dataclass
class OmniVoiceConfig:
    backend: str = "local"
    voices_dir: Path = field(default_factory=paths.default_voices_dir)
    speed: float = 1.0
    fallback_provider: str = "piper"
    local: LocalConfig = field(default_factory=LocalConfig)
    studio: StudioConfig = field(default_factory=StudioConfig)
    service: ServiceConfig = field(default_factory=ServiceConfig)


def load() -> OmniVoiceConfig:
    """Load the effective config (config.yaml overlaid with env vars)."""
    s = _section()
    local_s = _sub(s, "local")
    studio_s = _sub(s, "studio")
    service_s = _sub(s, "service")

    voices_dir_raw = _ENV.get("HERMES_OMNIVOICE_VOICES_DIR") or str(s.get("voices_dir") or "").strip()
    voices_dir = Path(voices_dir_raw).expanduser() if voices_dir_raw else paths.default_voices_dir()

    return OmniVoiceConfig(
        backend=(_ENV.get("HERMES_OMNIVOICE_BACKEND") or s.get("backend") or "local").strip(),
        voices_dir=voices_dir,
        speed=float(s.get("speed", 1.0) or 1.0),
        fallback_provider=str(s.get("fallback_provider", "piper") or "piper").strip(),
        local=LocalConfig(
            model=(_ENV.get("HERMES_OMNIVOICE_MODEL") or local_s.get("model") or "k2-fsa/OmniVoice").strip(),
            device=(_ENV.get("HERMES_OMNIVOICE_DEVICE") or local_s.get("device") or "auto").strip(),
            dtype=(_ENV.get("HERMES_OMNIVOICE_DTYPE") or local_s.get("dtype") or "float16").strip(),
            sample_rate=int(local_s.get("sample_rate", 24000) or 24000),
            num_step=int(_ENV.get("HERMES_OMNIVOICE_NUM_STEP") or local_s.get("num_step", 16) or 16),
        ),
        studio=StudioConfig(
            url=(_ENV.get("HERMES_OMNIVOICE_STUDIO_URL") or studio_s.get("url") or "http://127.0.0.1:3900").strip(),
            speech_path=(studio_s.get("speech_path") or _DEFAULT_SPEECH_PATH).strip(),
            model=(_ENV.get("HERMES_OMNIVOICE_STUDIO_MODEL") or studio_s.get("model") or _DEFAULT_HTTP_MODEL).strip(),
            auth_token_env=str(studio_s.get("auth_token_env", "HERMES_OMNIVOICE_STUDIO_TOKEN")
                               or "HERMES_OMNIVOICE_STUDIO_TOKEN").strip(),
            timeout=int(studio_s.get("timeout", 180) or 180),
        ),
        service=ServiceConfig(
            url=(_ENV.get("HERMES_OMNIVOICE_SERVICE_URL") or service_s.get("url") or "").strip(),
            speech_path=(service_s.get("speech_path") or _DEFAULT_SPEECH_PATH).strip(),
            model=(_ENV.get("HERMES_OMNIVOICE_SERVICE_MODEL") or service_s.get("model") or _DEFAULT_HTTP_MODEL).strip(),
            auth_token_env=str(service_s.get("auth_token_env", "HERMES_OMNIVOICE_SERVICE_TOKEN")
                               or "HERMES_OMNIVOICE_SERVICE_TOKEN").strip(),
            timeout=int(service_s.get("timeout", 180) or 180),
            max_concurrency=int(service_s.get("max_concurrency", 2) or 2),
            stream=bool(service_s.get("stream", False)),
            transport=(_ENV.get("HERMES_OMNIVOICE_SERVICE_TRANSPORT") or service_s.get("transport") or "http").strip(),
            ssh_host=(_ENV.get("HERMES_OMNIVOICE_SERVICE_SSH_HOST") or service_s.get("ssh_host") or "").strip(),
            ssh_port=int(_ENV.get("HERMES_OMNIVOICE_SERVICE_SSH_PORT") or service_s.get("ssh_port", 22) or 22),
            ssh_identity_file=(_ENV.get("HERMES_OMNIVOICE_SERVICE_SSH_IDENTITY_FILE")
                               or service_s.get("ssh_identity_file") or "").strip(),
        ),
    )
