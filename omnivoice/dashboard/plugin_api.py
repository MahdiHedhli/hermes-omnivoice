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
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.append(str(_PLUGIN_ROOT))

from fastapi import APIRouter, Body, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from ov_core import config, gallery, paths
from ov_core.backends import SynthError, synthesize
from ov_core.registry import INSTRUCT_VOCAB, RegistryError, VoiceRegistry

router = APIRouter()

_LOOPBACK = {"127.0.0.1", "::1", "localhost", None, ""}
_MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MiB cap on clone reference uploads
_HERMES_BIN = shutil.which("hermes") or "hermes"  # for the Talk tab agent bridge
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

def _current_tts_provider() -> str:
    """The global ``tts.provider`` from config.yaml — the UI shows whether
    OmniVoice is what Hermes actually speaks with everywhere (not just the
    plugin's Talk tab, which calls OmniVoice directly)."""
    try:
        import yaml
        cfg_path = paths.hermes_home() / "config.yaml"
        if cfg_path.is_file():
            data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            return str(((data.get("tts") or {}).get("provider")) or "")
    except Exception:
        pass
    return ""


@router.get("/voices")
async def list_voices():
    reg = _registry()
    active = reg.get_active()
    return {
        "voices": [p.to_public() | {"active": p.id == active} for p in reg.list_voices()],
        "active": active,
        "backend": config.load().backend,
        "provider": _current_tts_provider(),
    }


@router.get("/instruct-vocab")
async def instruct_vocab():
    """The valid design-voice `instruct` attributes (single source of truth for
    the UI's term guide + validation)."""
    return {"vocab": INSTRUCT_VOCAB}


# ---------------------------------------------------------------------------
# Voice gallery — browse ready-made designed voices, install into the registry
# ---------------------------------------------------------------------------

@router.get("/gallery")
async def list_gallery():
    """Ready-made presets plus which ones are already in the registry.

    Reads a local file only — the bundled snapshot, or the user's refreshed
    cache. No network call happens here.
    """
    data = gallery.load()
    have = {p.id for p in _registry().list_voices()}
    items = [dict(item, installed=str(item.get("id", "")).lower() in have)
             for item in data["items"]]
    return {**data, "items": items}


@router.post("/gallery/refresh")
async def refresh_gallery(request: Request):
    """Explicitly re-fetch the published manifest (the only outbound call the
    plugin ever makes, and only when the user asks for it)."""
    _require_local_or_optin(request)
    try:
        count, updated_at = await run_in_threadpool(gallery.refresh)
    except RegistryError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"ok": True, "count": count, "updated_at": updated_at}


@router.post("/gallery/{preset_id}/install")
async def install_gallery_preset(preset_id: str, request: Request, body: dict = Body(default={})):
    """Create a design voice from a gallery preset.

    Goes through the same create_design() path as the Design tab, so id rules,
    instruct validation and the consent record are identical — a preset is just
    a pre-filled design, not a privileged import.
    """
    _require_local_or_optin(request)
    try:
        preset = gallery.get(preset_id)
    except RegistryError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    voice_id = str((body or {}).get("voice_id") or preset["id"]).strip()
    try:
        profile = _registry().create_design(
            voice_id,
            str((body or {}).get("name") or preset.get("name") or voice_id),
            str(preset.get("instruct") or ""),
            consent_source="omnivoice_gallery",
            language=gallery.language_code(str(preset.get("language") or "")),
            overwrite=bool((body or {}).get("overwrite", False)),
        )
    except RegistryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "voice": profile.to_public()}


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


_TALK_MAX_CHARS = 4000

# Synthesis time scales with reply length (~1s/word on Apple-Silicon MPS), so a
# spoken assistant must answer briefly. Prepended to the query (never shown in the
# transcript, which keeps the user's own words) to steer replies short.
_VOICE_PREAMBLE = (
    "You are in a spoken voice conversation and your reply is read aloud by a "
    "slow text-to-speech voice, so brevity matters. Reply with AT MOST two short "
    "sentences (about 25 words total). Be direct and conversational — no preamble, "
    "markdown, lists, headings, emojis, or code. If more detail is truly needed, "
    "offer to go deeper instead of dumping it. Here is what I said:\n\n"
)


def _run_agent(text: str, session_id: str, max_turns: int, timeout: int):
    """Bridge to the Hermes agent via its stable single-query CLI contract.

    `hermes chat -q <text> -Q` runs one non-interactive turn and prints only the
    final response plus a `session_id:` line (see `hermes chat --help`). Passing
    `--resume <id>` continues an existing conversation, which is how the Talk tab
    keeps context across turns. We deliberately drive the CLI rather than the
    dashboard's `/api/pty` chat, which is a raw terminal (xterm/Ink) stream with
    no machine-readable reply to hand to TTS.
    """
    cmd = [_HERMES_BIN, "chat", "-q", text, "-Q", "--max-turns", str(max_turns)]
    if session_id:
        cmd += ["--resume", session_id]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


@router.post("/talk")
async def talk(request: Request, body: dict = Body(...)):
    """One voice-chat turn: transcribed text in, agent reply + session id out.

    The browser Talk tab records the mic, sends it to the native
    `/api/audio/transcribe`, posts the transcript here, then speaks the reply
    back through the plugin's own OmniVoice synth (`/voices/{id}/preview`) so the
    agent always answers in the selected voice regardless of `tts.provider`.
    """
    _require_local_or_optin(request)
    text = str((body or {}).get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    if len(text) > _TALK_MAX_CHARS:
        raise HTTPException(status_code=400, detail="text too long")
    session_id = str((body or {}).get("session_id") or "").strip()
    concise = bool((body or {}).get("concise", True))
    try:
        max_turns = max(1, min(int((body or {}).get("max_turns") or 8), 40))
    except (TypeError, ValueError):
        max_turns = 8
    try:
        timeout = max(10, min(int((body or {}).get("timeout") or 300), 600))
    except (TypeError, ValueError):
        timeout = 300

    query = (_VOICE_PREAMBLE + text) if concise else text
    try:
        proc = await run_in_threadpool(_run_agent, query, session_id, max_turns, timeout)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="the agent took too long to respond")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="the `hermes` CLI was not found on PATH")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "agent failed").strip()
        raise HTTPException(status_code=502, detail=f"agent error: {detail[:400]}")

    # `hermes chat -Q` prints the reply on stdout and a `session_id:` line on
    # stderr. We scan both streams for the id (order-independent, version-proof)
    # and take the reply from stdout with any stray id line removed.
    sid = session_id
    for stream in ((proc.stderr or ""), (proc.stdout or "")):
        for line in stream.splitlines():
            if line.startswith("session_id:"):
                sid = line.split(":", 1)[1].strip()
                break
    reply = "\n".join(
        ln for ln in (proc.stdout or "").splitlines() if not ln.startswith("session_id:")
    ).strip()
    if not reply:
        raise HTTPException(status_code=502, detail="the agent returned an empty reply")
    return {"reply": reply, "session_id": sid}


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
    """Set ``tts.provider: omnivoice`` in config.yaml via a surgical, in-place line
    edit — only the one line changes, so the file's comments and formatting are
    preserved (a YAML round-trip would strip every comment)."""
    cfg_path = paths.hermes_home() / "config.yaml"
    try:
        if not cfg_path.is_file():
            return False
        lines = cfg_path.read_text(encoding="utf-8").splitlines(keepends=True)
        in_tts = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            # a top-level key (no indent, not a comment/blank) ends the tts block
            if line[:1] not in (" ", "\t", "\n", "#", "") and stripped and not stripped.startswith("#"):
                if in_tts:
                    break
                in_tts = stripped.split(":", 1)[0] == "tts"
                continue
            if in_tts:
                m = re.match(r"^(\s+)provider:\s*(.*?)\s*$", line)
                if m:
                    if m.group(2) == "omnivoice":
                        return True  # already set
                    lines[i] = f"{m.group(1)}provider: omnivoice\n"
                    cfg_path.write_text("".join(lines), encoding="utf-8")
                    return True
        return False
    except Exception:
        return False
