"""Filesystem paths for the OmniVoice integration."""

from __future__ import annotations

import os
from pathlib import Path


def hermes_home() -> Path:
    """Return the Hermes home directory (``$HERMES_HOME`` or ``~/.hermes``)."""
    raw = os.environ.get("HERMES_HOME", "~/.hermes")
    return Path(raw).expanduser()


def default_voices_dir() -> Path:
    """Default voice-registry root: ``<HERMES_HOME>/voices/omnivoice``."""
    return hermes_home() / "voices" / "omnivoice"


def audio_cache_dir() -> Path:
    """Scratch dir for previews and temp synthesis output."""
    d = hermes_home() / "audio_cache" / "omnivoice"
    d.mkdir(parents=True, exist_ok=True)
    return d
