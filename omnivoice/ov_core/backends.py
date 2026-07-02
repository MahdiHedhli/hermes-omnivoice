"""Synthesis backends.

One contract, three implementations, chosen by ``tts.omnivoice.backend``:

- ``local``   — in-process OmniVoice Python SDK (donor: python adapter).
- ``studio``  — OmniVoice-Studio over HTTP, loopback only (OpenAI-compatible
  ``/v1/audio/speech``).
- ``service`` — networked shared voice service: same OpenAI-compatible wire
  shape as ``studio`` + bearer auth + a client-side concurrency guard.

The backend is fully decoupled from the provider and the registry: it takes a
resolved :class:`ov_core.registry.VoiceProfile` and writes audio to a path.

Wire contract (studio/service), verified against the proven OmniVoice-Studio
FastAPI client (``scripts/hermes-omnivoice-remote.py`` in the archived spike)::

    POST {url}{speech_path}          # speech_path defaults to /v1/audio/speech
    Authorization: Bearer <token>    # required for service; optional for studio
    Content-Type: application/json
    { "model": ..., "input": <text>, "voice": <voice-id>,
      "response_format": "wav", "speed": <float>, "language_id": <lang?> }
    -> audio/wav bytes

Because the OpenAI-compatible surface selects a **server-side** ``voice`` by id,
per-request local clone reference audio cannot be sent over HTTP: clone-by-
reference-audio is a ``local``-backend capability. The ``studio``/``service``
backends send ``voice = profile.id`` and rely on the server holding a voice of
that name.

Local SDK contract (verified against k2-fsa/OmniVoice, PyPI ``omnivoice``)::

    from omnivoice import OmniVoice
    OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=..., dtype=...)
        .generate(text=, speed=, language_id=, ref_audio=, ref_text=, instruct=)
    # -> list[np.ndarray] shape (T,) @ 24 kHz
"""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple
from urllib.parse import urlparse

from . import paths
from .config import OmniVoiceConfig
from .registry import VoiceProfile

_WAV = "wav"
_service_semaphores: Dict[Tuple[str, int], threading.Semaphore] = {}
_sem_lock = threading.Lock()


class SynthError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Audio output helpers
# ---------------------------------------------------------------------------

def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _ffmpeg_convert(src: Path, dst: Path) -> bool:
    """Convert ``src`` to ``dst`` (extension decides format). Returns success."""
    if not _ffmpeg_available():
        return False
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), str(dst)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        return dst.is_file()
    except (subprocess.CalledProcessError, OSError):
        return False


def _finalize(tmp_wav: Path, output_path: Path, fmt: str) -> str:
    """Move/convert a temp WAV to the requested output path/format."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    target_ext = out.suffix.lower().lstrip(".") or fmt or _WAV
    if target_ext == _WAV:
        shutil.move(str(tmp_wav), str(out))
        return str(out)
    if _ffmpeg_convert(tmp_wav, out):
        tmp_wav.unlink(missing_ok=True)
        return str(out)
    # No ffmpeg: deliver the WAV bytes at the requested path. Hermes' delivery
    # pipeline also runs ffmpeg conversion for voice bubbles, so this stays
    # playable even if the extension disagrees.
    shutil.move(str(tmp_wav), str(out))
    return str(out)


def _write_samples(samples, sample_rate: int, output_path: Path, fmt: str) -> str:
    import soundfile as sf  # local dep, only needed for the local backend

    tmp = paths.audio_cache_dir() / f"synth-{uuid.uuid4().hex}.wav"
    sf.write(str(tmp), samples, int(sample_rate))
    return _finalize(tmp, output_path, fmt)


def _write_bytes(data: bytes, output_path: Path, fmt: str) -> str:
    if not data:
        raise SynthError("backend returned no audio bytes")
    tmp = paths.audio_cache_dir() / f"synth-{uuid.uuid4().hex}.wav"
    tmp.write_bytes(data)
    return _finalize(tmp, output_path, fmt)


# ---------------------------------------------------------------------------
# local backend (OmniVoice Python SDK) — donor: hermes-omnivoice-python-adapter
# ---------------------------------------------------------------------------

def _best_device(torch_mod) -> str:
    if torch_mod.cuda.is_available():
        return "cuda"
    if getattr(torch_mod.backends, "mps", None) and torch_mod.backends.mps.is_available():
        return "mps"
    return "cpu"


def _resolve_dtype(torch_mod, name: str):
    table = {
        "float16": getattr(torch_mod, "float16", None), "fp16": getattr(torch_mod, "float16", None),
        "bfloat16": getattr(torch_mod, "bfloat16", None), "bf16": getattr(torch_mod, "bfloat16", None),
        "float32": getattr(torch_mod, "float32", None), "fp32": getattr(torch_mod, "float32", None),
    }
    dt = table.get((name or "float16").strip().lower())
    if dt is None:
        raise SynthError(f"unsupported dtype: {name}")
    return dt


# cache the loaded model per (model, device, dtype) so we don't reload per call
_model_cache: Dict[Tuple[str, str, str], object] = {}
_model_lock = threading.Lock()


def _import_omnivoice():
    """Import the real OmniVoice SDK class (NOT the ov_core package).

    Prefers the documented public import ``from omnivoice import OmniVoice``;
    falls back to the internal module path for older SDK layouts.
    """
    try:
        from omnivoice import OmniVoice  # documented public path
        return OmniVoice
    except ImportError:
        from omnivoice.models.omnivoice import OmniVoice  # older internal path
        return OmniVoice


def _load_local_model(cfg: OmniVoiceConfig):
    try:
        import torch  # noqa: F401
        OmniVoice = _import_omnivoice()
    except ImportError as exc:
        raise SynthError(
            "OmniVoice Python SDK not installed; install omnivoice in this "
            "environment, or use the studio/service backend"
        ) from exc

    import torch
    device = cfg.local.device
    if device == "auto":
        device = _best_device(torch)
    dtype = _resolve_dtype(torch, cfg.local.dtype)
    key = (cfg.local.model, device, cfg.local.dtype)
    with _model_lock:
        model = _model_cache.get(key)
        if model is None:
            model = OmniVoice.from_pretrained(cfg.local.model, device_map=device, dtype=dtype)
            _model_cache[key] = model
    return model


def _synth_local(text: str, output_path: Path, *, voice: VoiceProfile,
                 cfg: OmniVoiceConfig, speed: float, fmt: str) -> str:
    model = _load_local_model(cfg)
    kwargs: Dict[str, object] = {"text": text, "speed": speed}
    if voice.language:
        kwargs["language_id"] = voice.language  # SDK kwarg is language_id, not language
    if voice.mode == "clone":
        ref = voice.ref_audio_path
        if ref is None:
            raise SynthError(f"clone voice '{voice.id}' has no reference audio")
        kwargs["ref_audio"] = str(ref)
        kwargs["ref_text"] = voice.ref_text
    else:
        kwargs["instruct"] = voice.instruct

    audios = model.generate(**kwargs)
    if not audios:
        raise SynthError("OmniVoice returned no audio")
    sample_rate = int(getattr(model, "sampling_rate", cfg.local.sample_rate) or cfg.local.sample_rate)
    return _write_samples(audios[0], sample_rate, output_path, fmt)


# ---------------------------------------------------------------------------
# HTTP backends (studio / service) — OpenAI-compatible /v1/audio/speech
# ---------------------------------------------------------------------------

_LOOPBACK = {"localhost", "127.0.0.1", "::1"}


def _validate_url(url: str, *, require_loopback: bool) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SynthError(f"backend URL must be an absolute http(s) URL: {url!r}")
    if "@" in parsed.netloc:
        raise SynthError("backend URL must not include userinfo")
    if require_loopback and (parsed.hostname or "") not in _LOOPBACK:
        raise SynthError(
            f"refusing non-loopback OmniVoice-Studio URL {url!r}; use the "
            "'service' backend (with auth) for cross-machine synthesis"
        )
    return url.rstrip("/")


def _is_loopback_url(url: str) -> bool:
    return (urlparse(url).hostname or "") in _LOOPBACK


def _join(base: str, path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{base.rstrip('/')}{path}"


def _http_payload(text: str, voice: VoiceProfile, speed: float, *, model: str) -> Dict[str, object]:
    """OpenAI-compatible audio-speech JSON body.

    ``voice`` is a server-side voice id (``profile.id``). We always request WAV
    so the temp file is genuinely WAV for ``_finalize`` to convert.
    """
    payload: Dict[str, object] = {
        "model": model,
        "input": text,
        "voice": voice.id,
        "response_format": _WAV,
        "speed": speed,
    }
    if voice.language:
        payload["language_id"] = voice.language
    return payload


def _post_json(url: str, payload: Dict[str, object], *, timeout: int,
               auth_token: str = "") -> bytes:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "audio/wav, audio/*"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise SynthError(f"OmniVoice backend HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SynthError(f"OmniVoice backend unreachable: {exc}") from exc
    if "application/json" in ctype.lower():
        raise SynthError(f"OmniVoice backend returned JSON, not audio: {data[:300]!r}")
    return data


def _synth_studio(text: str, output_path: Path, *, voice: VoiceProfile,
                  cfg: OmniVoiceConfig, speed: float, fmt: str) -> str:
    base = _validate_url(cfg.studio.url, require_loopback=True)
    payload = _http_payload(text, voice, speed, model=cfg.studio.model)
    data = _post_json(_join(base, cfg.studio.speech_path), payload,
                      timeout=cfg.studio.timeout, auth_token=cfg.studio.auth_token)
    return _write_bytes(data, output_path, fmt)


def _service_semaphore(cfg: OmniVoiceConfig) -> threading.Semaphore:
    key = (cfg.service.url, cfg.service.max_concurrency)
    with _sem_lock:
        sem = _service_semaphores.get(key)
        if sem is None:
            sem = threading.Semaphore(max(1, cfg.service.max_concurrency))
            _service_semaphores[key] = sem
    return sem


def _synth_service(text: str, output_path: Path, *, voice: VoiceProfile,
                   cfg: OmniVoiceConfig, speed: float, fmt: str) -> str:
    if not cfg.service.url:
        raise SynthError("service backend selected but tts.omnivoice.service.url is empty")
    base = _validate_url(cfg.service.url, require_loopback=False)
    # A cross-machine (non-loopback) service must carry auth — never trust the
    # network. Loopback service URLs (rare) may omit the token.
    if not _is_loopback_url(base) and not cfg.service.auth_token:
        raise SynthError(
            "service backend at a non-loopback URL requires an auth token; set "
            f"the env named by service.auth_token_env ({cfg.service.auth_token_env})"
        )
    payload = _http_payload(text, voice, speed, model=cfg.service.model)
    sem = _service_semaphore(cfg)
    with sem:  # client-side concurrency guard so we don't overrun the node
        data = _post_json(_join(base, cfg.service.speech_path), payload,
                          timeout=cfg.service.timeout, auth_token=cfg.service.auth_token)
    return _write_bytes(data, output_path, fmt)


# ---------------------------------------------------------------------------
# Public contract
# ---------------------------------------------------------------------------

_DISPATCH = {"local": _synth_local, "studio": _synth_studio, "service": _synth_service}


def synthesize(text: str, output_path: str, *, voice: VoiceProfile,
               cfg: OmniVoiceConfig, speed: Optional[float] = None,
               fmt: str = _WAV) -> str:
    """Synthesize ``text`` for ``voice`` and write audio to ``output_path``."""
    if not (text or "").strip():
        raise SynthError("text must not be empty")
    fn = _DISPATCH.get(cfg.backend)
    if fn is None:
        raise SynthError(f"unknown backend: {cfg.backend!r} (expected local|studio|service)")
    resolved_speed = float(speed if speed is not None else voice.speed or cfg.speed or 1.0)
    return fn(text, Path(output_path), voice=voice, cfg=cfg, speed=resolved_speed, fmt=fmt)


def stream(text: str, *, voice: VoiceProfile, cfg: OmniVoiceConfig,
           speed: Optional[float] = None, fmt: str = "opus") -> Iterator[bytes]:
    """Stream audio bytes (service backend only, when the server supports it).

    VERIFY: wire this to the service's chunked endpoint once its streaming
    contract is confirmed. Until then this raises so the provider falls back to
    synthesize()+read-whole-file.
    """
    raise NotImplementedError(
        "streaming not yet wired to a service endpoint; see backends.stream()"
    )
