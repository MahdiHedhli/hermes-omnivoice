"""OmniVoice TTS provider.

Implements the Hermes ``agent.tts_provider.TTSProvider`` ABC. Selection
(``tts.provider: omnivoice``) routes every ``text_to_speech`` call, voice-mode
reply, Discord VC utterance, and messaging voice delivery through here.

The provider is a thin adapter: it resolves the requested voice against the
registry and hands synthesis to the configured backend. Registry + backend are
imported lazily so the provider imports cleanly even when the OmniVoice SDK or
a backend dependency is missing (``is_available`` reports that instead).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional

try:
    from agent.tts_provider import TTSProvider
except Exception:  # pragma: no cover - allows unit tests without hermes installed
    class TTSProvider:  # minimal shim mirroring the real ABC surface
        pass

logger = logging.getLogger(__name__)


class OmniVoiceProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "omnivoice"

    @property
    def display_name(self) -> str:
        return "OmniVoice"

    # -- registry / config accessors --------------------------------------

    def _cfg(self):
        from ov_core import config
        return config.load()

    def _registry(self):
        from ov_core.registry import VoiceRegistry
        return VoiceRegistry(self._cfg().voices_dir)

    # -- availability / catalog -------------------------------------------

    def is_available(self) -> bool:
        try:
            cfg = self._cfg()
            if cfg.backend == "local":
                try:
                    import omnivoice  # noqa: F401 - the real SDK
                    import torch  # noqa: F401
                    return True
                except Exception:
                    return False
            # studio/service: the model runs behind an HTTP server — ping it so
            # the picker reflects real readiness. (Explicit tts.provider=omnivoice
            # still routes here even if this returns False.)
            from ov_core import backends
            url = cfg.studio.url if cfg.backend == "studio" else cfg.service.url
            return backends.health_ok(url)
        except Exception:
            return False

    def list_voices(self) -> List[Dict[str, Any]]:
        try:
            return [p.to_voice_dict() for p in self._registry().list_voices()]
        except Exception:
            logger.exception("omnivoice: list_voices failed")
            return []

    def list_models(self) -> List[Dict[str, Any]]:
        try:
            cfg = self._cfg()
        except Exception:
            return []
        return [{
            "id": cfg.local.model,
            "display": "OmniVoice",
            "languages": ["en"],
            "max_text_length": 2000,
        }]

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "OmniVoice",
            "badge": "local / self-hosted",
            "tag": "ElevenLabs-tier quality, clone-capable, no per-token cost",
            "env_vars": [
                {"key": "HERMES_OMNIVOICE_SERVICE_URL",
                 "prompt": "OmniVoice service URL (leave blank for local/studio)",
                 "url": ""},
                {"key": "HERMES_OMNIVOICE_SERVICE_TOKEN",
                 "prompt": "OmniVoice service bearer token (service backend only)",
                 "url": ""},
            ],
        }

    def default_voice(self) -> Optional[str]:
        try:
            return self._registry().default_voice()
        except Exception:
            return None

    # -- synthesis ---------------------------------------------------------

    def _resolve_voice(self, voice_id: Optional[str]):
        registry = self._registry()
        vid = (voice_id or "").strip() or registry.default_voice()
        if not vid:
            from ov_core.backends import SynthError
            raise SynthError(
                "no OmniVoice voice selected and none available; create one via "
                "the dashboard Voices tab or create-voice helper"
            )
        return registry.get_voice(vid)

    def synthesize(self, text: str, output_path: str, *, voice: Optional[str] = None,
                   model: Optional[str] = None, speed: Optional[float] = None,
                   format: str = "mp3", **extra: Any) -> str:
        # `format` default mirrors the ABC (DEFAULT_OUTPUT_FORMAT); the actual
        # container is governed by output_path's extension in backends._finalize.
        from ov_core import backends
        cfg = self._cfg()
        profile = self._resolve_voice(voice)
        try:
            return backends.synthesize(text, output_path, voice=profile, cfg=cfg,
                                       speed=speed, fmt=format)
        except backends.SynthError:
            # TODO(phase5): degrade to cfg.fallback_provider (e.g. piper) instead
            # of raising, once a cross-provider fallback hook is available.
            raise

    def stream(self, text: str, *, voice: Optional[str] = None, model: Optional[str] = None,
               format: str = "opus", **extra: Any) -> Iterator[bytes]:
        from ov_core import backends
        cfg = self._cfg()
        profile = self._resolve_voice(voice)
        # Delegates to the (not-yet-wired) service streaming endpoint. Raises
        # NotImplementedError until wired, so Hermes falls back to synthesize().
        return backends.stream(text, voice=profile, cfg=cfg, speed=None, fmt=format)

    @property
    def voice_compatible(self) -> bool:
        # We emit WAV; Hermes' delivery pipeline converts to Opus for bubbles.
        return True
