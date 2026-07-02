"""OmniVoice voice registry.

One source of truth for both the CLI picker (via
``OmniVoiceProvider.list_voices``) and the dashboard tab (via the plugin API
routes). Each voice is a directory under the registry root:

    <voices_dir>/<id>/voice.yaml      # profile
    <voices_dir>/<id>/ref.wav         # clone reference audio (clone mode only)
    <voices_dir>/.active              # id of the active voice (plain text)

Security hardening (carried over from the donor spike, applied where
user-supplied audio enters the system):

- Reject symlinked registry root, voice dirs, ``voice.yaml``, and ``ref.wav``.
- Validate reference audio is a readable WAV before copy; reject symlinked
  ``--ref-audio`` input.
- Write registry files ``0600`` and voice directories private.
- Consent gate on clone load: ``status == "confirmed"``, non-empty ``source``,
  at least one non-empty ``allowed_uses`` entry.
"""

from __future__ import annotations

import os
import shutil
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_ALLOWED_USES = ["personal_assistant", "local_generation"]
_ID_ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789-_")


class RegistryError(RuntimeError):
    """Raised for any registry validation or IO failure."""


# ---------------------------------------------------------------------------
# Hardening helpers
# ---------------------------------------------------------------------------

def _reject_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise RegistryError(f"refusing symlinked {label}: {path}")


def _safe_child(parent: Path, child: str) -> Path:
    """Resolve ``parent/child`` and refuse traversal outside ``parent``."""
    if not child or child in (".", "..") or "/" in child or "\\" in child:
        raise RegistryError(f"invalid path component: {child!r}")
    candidate = (parent / child).resolve()
    parent_resolved = parent.resolve()
    if parent_resolved != candidate and parent_resolved not in candidate.parents:
        raise RegistryError(f"path escapes registry root: {candidate}")
    return candidate


def _validate_wav(path: Path) -> None:
    """Confirm ``path`` is a readable WAV with at least one frame."""
    _reject_symlink(path, "reference audio")
    if not path.is_file():
        raise RegistryError(f"reference audio not found: {path}")
    try:
        with wave.open(str(path), "rb") as wf:
            if wf.getnframes() <= 0:
                raise RegistryError(f"reference audio has no frames: {path}")
    except wave.Error as exc:
        raise RegistryError(f"reference audio is not valid WAV: {path} ({exc})") from exc


def _validate_id(voice_id: str) -> str:
    voice_id = (voice_id or "").strip().lower()
    if not voice_id:
        raise RegistryError("voice id must not be empty")
    if any(ch not in _ID_ALLOWED for ch in voice_id):
        raise RegistryError("voice id may only contain [a-z0-9-_]")
    return voice_id


def _write_private_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
    finally:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def _copy_private(src: Path, dst: Path) -> None:
    _reject_symlink(src, "reference audio source")
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(dst), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with src.open("rb") as s, os.fdopen(fd, "wb") as d:
            shutil.copyfileobj(s, d)
    finally:
        try:
            os.chmod(dst, 0o600)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Consent
# ---------------------------------------------------------------------------

def validate_consent(source: str, allowed_uses: Optional[List[str]]) -> Dict[str, Any]:
    source = (source or "").strip()
    if not source:
        raise RegistryError("consent source cannot be empty")
    uses = [u.strip() for u in (allowed_uses or DEFAULT_ALLOWED_USES) if u and u.strip()]
    if not uses:
        raise RegistryError("consent requires at least one allowed use")
    return {"status": "confirmed", "source": source, "allowed_uses": uses}


def _assert_consented(consent: Dict[str, Any], voice_id: str) -> None:
    if consent.get("status") != "confirmed":
        raise RegistryError(f"voice '{voice_id}' consent is not confirmed")
    if not str(consent.get("source", "")).strip():
        raise RegistryError(f"voice '{voice_id}' consent source is empty")
    uses = [u for u in (consent.get("allowed_uses") or []) if str(u).strip()]
    if not uses:
        raise RegistryError(f"voice '{voice_id}' has no allowed uses")


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@dataclass
class VoiceProfile:
    id: str
    name: str
    mode: str  # "clone" | "design"
    voice_dir: Path
    engine: str = "omnivoice"
    ref_audio: str = ""      # filename, clone only
    ref_text: str = ""       # clone only
    instruct: str = ""       # design only
    language: str = "en"
    speed: float = 1.0
    consent: Dict[str, Any] = field(default_factory=dict)

    @property
    def ref_audio_path(self) -> Optional[Path]:
        return (self.voice_dir / self.ref_audio) if self.ref_audio else None

    def to_public(self) -> Dict[str, Any]:
        """Serializable view for the dashboard (no absolute paths)."""
        return {
            "id": self.id,
            "name": self.name,
            "mode": self.mode,
            "engine": self.engine,
            "language": self.language,
            "speed": self.speed,
            "has_ref_audio": bool(self.ref_audio),
            "instruct": self.instruct,
            "consent": self.consent,
        }

    def to_voice_dict(self) -> Dict[str, Any]:
        """List-voices entry consumed by the Hermes picker."""
        return {
            "id": self.id,
            "display": f"{self.name} ({self.mode})",
            "language": self.language,
        }


class VoiceRegistry:
    def __init__(self, voices_dir: Path):
        self.root = Path(voices_dir).expanduser()

    # -- listing / reading -------------------------------------------------

    def _load_profile(self, voice_dir: Path) -> VoiceProfile:
        import yaml

        _reject_symlink(voice_dir, "voice directory")
        yaml_path = voice_dir / "voice.yaml"
        _reject_symlink(yaml_path, "voice.yaml")
        if not yaml_path.is_file():
            raise RegistryError(f"missing voice.yaml in {voice_dir}")
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise RegistryError(f"malformed voice.yaml in {voice_dir}")

        profile = VoiceProfile(
            id=str(data.get("id", voice_dir.name)),
            name=str(data.get("name", voice_dir.name)),
            mode=str(data.get("mode", "design")),
            voice_dir=voice_dir,
            engine=str(data.get("engine", "omnivoice")),
            ref_audio=str(data.get("ref_audio", "") or ""),
            ref_text=str(data.get("ref_text", "") or ""),
            instruct=str(data.get("instruct", "") or ""),
            language=str(data.get("language", "en") or "en"),
            speed=float(data.get("speed", 1.0) or 1.0),
            consent=data.get("consent") if isinstance(data.get("consent"), dict) else {},
        )
        return profile

    def list_voices(self) -> List[VoiceProfile]:
        if not self.root.is_dir():
            return []
        _reject_symlink(self.root, "voices root")
        out: List[VoiceProfile] = []
        for child in sorted(self.root.iterdir()):
            if child.name.startswith(".") or not child.is_dir():
                continue
            try:
                out.append(self._load_profile(child))
            except RegistryError:
                # Skip malformed/hostile entries rather than failing the whole list.
                continue
        return out

    def get_voice(self, voice_id: str) -> VoiceProfile:
        voice_id = _validate_id(voice_id)
        voice_dir = _safe_child(self.root, voice_id)
        profile = self._load_profile(voice_dir)
        # Clone voices must pass the consent gate before they can be used.
        if profile.mode == "clone":
            _assert_consented(profile.consent, voice_id)
            if profile.ref_audio_path is not None:
                _validate_wav(profile.ref_audio_path)
        return profile

    # -- writing -----------------------------------------------------------

    def _write_profile(self, profile: VoiceProfile) -> None:
        import yaml

        payload: Dict[str, Any] = {
            "id": profile.id,
            "name": profile.name,
            "engine": profile.engine,
            "mode": profile.mode,
            "language": profile.language,
            "speed": profile.speed,
            "consent": profile.consent,
        }
        if profile.mode == "clone":
            payload["ref_audio"] = profile.ref_audio
            payload["ref_text"] = profile.ref_text
        else:
            payload["instruct"] = profile.instruct
        _write_private_text(profile.voice_dir / "voice.yaml", yaml.safe_dump(payload, sort_keys=False))

    def create_clone(
        self,
        voice_id: str,
        name: str,
        ref_audio_src: Path,
        ref_text: str,
        *,
        consent_source: str,
        allowed_uses: Optional[List[str]] = None,
        language: str = "en",
        speed: float = 1.0,
        overwrite: bool = False,
    ) -> VoiceProfile:
        voice_id = _validate_id(voice_id)
        if not (ref_text or "").strip():
            raise RegistryError("ref_text is required for a clone voice")
        consent = validate_consent(consent_source, allowed_uses)

        ref_audio_src = Path(ref_audio_src).expanduser()
        _validate_wav(ref_audio_src)

        voice_dir = _safe_child(self.root, voice_id)
        _reject_symlink(voice_dir, "voice directory")
        if voice_dir.exists() and not overwrite:
            raise RegistryError(f"voice '{voice_id}' already exists")
        voice_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(voice_dir, 0o700)
        except OSError:
            pass

        _copy_private(ref_audio_src, voice_dir / "ref.wav")

        profile = VoiceProfile(
            id=voice_id, name=(name or voice_id).strip(), mode="clone", voice_dir=voice_dir,
            ref_audio="ref.wav", ref_text=ref_text.strip(), language=language.strip() or "en",
            speed=float(speed or 1.0), consent=consent,
        )
        self._write_profile(profile)
        return profile

    def create_design(
        self,
        voice_id: str,
        name: str,
        instruct: str,
        *,
        consent_source: str = "user_created",
        allowed_uses: Optional[List[str]] = None,
        language: str = "en",
        speed: float = 1.0,
        overwrite: bool = False,
    ) -> VoiceProfile:
        voice_id = _validate_id(voice_id)
        if not (instruct or "").strip():
            raise RegistryError("instruct is required for a design voice")
        consent = validate_consent(consent_source, allowed_uses)

        voice_dir = _safe_child(self.root, voice_id)
        _reject_symlink(voice_dir, "voice directory")
        if voice_dir.exists() and not overwrite:
            raise RegistryError(f"voice '{voice_id}' already exists")
        voice_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(voice_dir, 0o700)
        except OSError:
            pass

        profile = VoiceProfile(
            id=voice_id, name=(name or voice_id).strip(), mode="design", voice_dir=voice_dir,
            instruct=instruct.strip(), language=language.strip() or "en",
            speed=float(speed or 1.0), consent=consent,
        )
        self._write_profile(profile)
        return profile

    def delete_voice(self, voice_id: str) -> None:
        voice_id = _validate_id(voice_id)
        voice_dir = _safe_child(self.root, voice_id)
        _reject_symlink(voice_dir, "voice directory")
        if not voice_dir.is_dir():
            raise RegistryError(f"voice '{voice_id}' not found")
        shutil.rmtree(voice_dir)
        if self.get_active() == voice_id:
            self._active_path().unlink(missing_ok=True)

    # -- active selection --------------------------------------------------

    def _active_path(self) -> Path:
        return self.root / ".active"

    def get_active(self) -> Optional[str]:
        p = self._active_path()
        if p.is_symlink() or not p.is_file():
            return None
        try:
            return p.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None

    def set_active(self, voice_id: str) -> None:
        voice_id = _validate_id(voice_id)
        # Confirm the voice exists and (for clones) is usable before activating.
        self.get_voice(voice_id)
        self.root.mkdir(parents=True, exist_ok=True)
        _write_private_text(self._active_path(), voice_id)

    def default_voice(self) -> Optional[str]:
        active = self.get_active()
        if active:
            try:
                self.get_voice(active)
                return active
            except RegistryError:
                pass
        for profile in self.list_voices():
            try:
                self.get_voice(profile.id)
                return profile.id
            except RegistryError:
                continue
        return None
