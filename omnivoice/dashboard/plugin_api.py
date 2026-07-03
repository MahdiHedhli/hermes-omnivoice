"""Dashboard backend routes for the OmniVoice Voices tab.

Mounted at ``/api/plugins/omnivoice/`` by the dashboard. These routes run inside
the dashboard process; we add the plugin root to ``sys.path`` and import the
shared ``ov_core`` package by absolute name (the dashboard loads this file by
path, not as part of the ``omnivoice`` package, so a relative import would not
resolve).

SECURITY: plugin API routes bypass the dashboard session-auth gate, and the
dashboard binds loopback by default. Every route that mutates state or runs a
model (clone, design, preview, set-active, delete) refuses non-loopback callers
unless the operator opts in via ``HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE=1``. The
peer check uses the transport socket's client address, not a request header, so
it cannot be spoofed by ``X-Forwarded-For``. Keep the dashboard on loopback (or
a VPN/tailnet) — see the integration SPEC, Section 6.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.append(str(_PLUGIN_ROOT))

from fastapi import APIRouter, Body, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from ov_core import config, paths
from ov_core.backends import SynthError, synthesize
from ov_core.registry import INSTRUCT_VOCAB, RegistryError, VoiceRegistry

router = APIRouter()

_LOOPBACK = {"127.0.0.1", "::1", "localhost", None, ""}
_MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MiB cap on clone reference uploads
_PREVIEW_MAX_CHARS = 500
_PREVIEW_TEXT = (
    "The quick brown fox jumps over the lazy dog. This is a preview of the "
    "selected OmniVoice voice."
)


def _registry() -> VoiceRegistry:
    return VoiceRegistry(config.load().voices_dir)


def _require_local_or_optin(request: Request) -> None:
    """Refuse mutating/compute routes from a non-loopback peer unless opted in.

    ``request.client.host`` is the transport peer address (uvicorn sets it from
    the socket), not a client-supplied header, so it is not spoofable via
    ``X-Forwarded-For``.
    """
    host = request.client.host if request.client else None
    if host in _LOOPBACK:
        return
    if os.environ.get("HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE", "").strip() in ("1", "true", "yes"):
        return
    raise HTTPException(
        status_code=403,
        detail=("refused from a non-loopback client; set "
                "HERMES_OMNIVOICE_ALLOW_REMOTE_CLONE=1 on a trusted network to allow it"),
    )


def _split_uses(raw: str):
    return [u.strip() for u in (raw or "").split(",") if u.strip()] or None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/voices")
async def list_voices():
    reg = _registry()
    active = reg.get_active()
    return {
        "voices": [p.to_public() | {"active": p.id == active} for p in reg.list_voices()],
        "active": active,
        "backend": config.load().backend,
    }


@router.get("/instruct-vocab")
async def instruct_vocab():
    """The valid design-voice `instruct` attributes (single source of truth for
    the UI's term guide + validation)."""
    return {"vocab": INSTRUCT_VOCAB}


@router.patch("/voices/{voice_id}")
async def update_voice(voice_id: str, request: Request, body: dict = Body(...)):
    _require_local_or_optin(request)
    reg = _registry()
    try:
        profile = reg.update_voice(
            voice_id,
            name=body.get("name"),
            instruct=body.get("instruct"),
            ref_text=body.get("ref_text"),
            language=body.get("language"),
            speed=body.get("speed"),
        )
    except RegistryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "voice": profile.to_public()}


@router.post("/voices/design")
async def create_design(request: Request, body: dict = Body(...)):
    _require_local_or_optin(request)
    reg = _registry()
    try:
        profile = reg.create_design(
            voice_id=str(body.get("id", "")),
            name=str(body.get("name", "")),
            instruct=str(body.get("instruct", "")),
            consent_source=str(body.get("consent_source", "user_created")),
            allowed_uses=body.get("allowed_uses") or None,
            language=str(body.get("language", "en")),
            speed=float(body.get("speed", 1.0) or 1.0),
            overwrite=bool(body.get("overwrite", False)),
        )
    except RegistryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "voice": profile.to_public()}


@router.post("/voices/clone")
async def create_clone(
    request: Request,
    ref_audio: UploadFile = File(...),
    id: str = Form(...),
    name: str = Form(""),
    ref_text: str = Form(...),
    consent_source: str = Form("user_uploaded"),
    allowed_uses: str = Form(""),
    consent_confirmed: bool = Form(False),
    language: str = Form("en"),
    speed: float = Form(1.0),
    overwrite: bool = Form(False),
):
    _require_local_or_optin(request)
    if not consent_confirmed:
        raise HTTPException(status_code=400, detail="consent must be confirmed to create a clone")

    # Read with a hard cap so a hostile/oversized upload cannot exhaust memory.
    data = await ref_audio.read(_MAX_UPLOAD_BYTES + 1)
    if len(data) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"reference audio exceeds the {_MAX_UPLOAD_BYTES // (1024 * 1024)} MiB limit",
        )

    tmp = paths.audio_cache_dir() / f"upload-{uuid.uuid4().hex}.wav"
    try:
        tmp.write_bytes(data)
        reg = _registry()
        try:
            profile = reg.create_clone(
                voice_id=id, name=name, ref_audio_src=tmp, ref_text=ref_text,
                consent_source=consent_source, allowed_uses=_split_uses(allowed_uses),
                language=language, speed=speed, overwrite=overwrite,
            )
        except RegistryError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    finally:
        tmp.unlink(missing_ok=True)
    return {"ok": True, "voice": profile.to_public()}


def _render_preview(profile, text: str) -> bytes:
    """Synchronous synth used off the event loop (model inference can be slow)."""
    out = paths.audio_cache_dir() / f"preview-{profile.id}-{uuid.uuid4().hex}.wav"
    try:
        synthesize(text, str(out), voice=profile, cfg=config.load(), fmt="wav")
        return out.read_bytes()
    finally:
        out.unlink(missing_ok=True)


@router.post("/voices/{voice_id}/preview")
async def preview(voice_id: str, request: Request, body: dict = Body(default={})):
    _require_local_or_optin(request)
    reg = _registry()
    try:
        profile = reg.get_voice(voice_id)
    except RegistryError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    text = str((body or {}).get("text") or _PREVIEW_TEXT)[:_PREVIEW_MAX_CHARS]
    try:
        # Run the (synchronous, possibly GPU-bound) synth in a worker thread so
        # a preview does not block the dashboard's asyncio event loop.
        data = await run_in_threadpool(_render_preview, profile, text)
    except SynthError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return Response(content=data, media_type="audio/wav")


@router.put("/voices/{voice_id}/active")
async def set_active(voice_id: str, request: Request, body: dict = Body(default={})):
    _require_local_or_optin(request)
    reg = _registry()
    try:
        reg.set_active(voice_id)
    except RegistryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    set_provider = bool((body or {}).get("set_provider", False))
    provider_set = False
    if set_provider:
        provider_set = _set_tts_provider_omnivoice()
    return {"ok": True, "active": voice_id, "provider_set": provider_set}


@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str, request: Request):
    _require_local_or_optin(request)
    reg = _registry()
    try:
        reg.delete_voice(voice_id)
    except RegistryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True}


# ---------------------------------------------------------------------------
# config.yaml write (optional, gated behind set_provider)
# ---------------------------------------------------------------------------

def _set_tts_provider_omnivoice() -> bool:
    """Set ``tts.provider: omnivoice`` in config.yaml, preserving other keys."""
    try:
        import yaml
    except Exception:
        return False
    cfg_path = paths.hermes_home() / "config.yaml"
    try:
        data = {}
        if cfg_path.is_file():
            with cfg_path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            return False
        tts = data.get("tts")
        if not isinstance(tts, dict):
            tts = {}
        tts["provider"] = "omnivoice"
        data["tts"] = tts
        with cfg_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False)
        return True
    except Exception:
        return False
