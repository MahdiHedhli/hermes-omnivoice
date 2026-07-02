"""OmniVoice Hermes plugin — agent/gateway entrypoint.

Hermes loads this package (``~/.hermes/plugins/omnivoice/``) and calls
``register(ctx)`` at startup. We register a single TTS provider; everything
else (voice registry, backends, dashboard routes) hangs off the shared
``ov_core`` package.

The shared package is deliberately named ``ov_core`` and **not** ``omnivoice``
so it can never shadow the real OmniVoice SDK, which imports as
``from omnivoice.models.omnivoice import OmniVoice``.

We add the plugin root to ``sys.path`` and import ``ov_core`` by absolute name
instead of using a relative import, so the exact same module resolves whether
this file is imported as a package (agent side) or the dashboard loads
``ov_core`` from ``dashboard/plugin_api.py`` by file path.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_PLUGIN_ROOT = Path(__file__).resolve().parent
if str(_PLUGIN_ROOT) not in sys.path:
    # Append (not insert-at-0) so ov_core is importable without letting generic
    # sibling names (tests/, dashboard/) shadow site-packages modules.
    sys.path.append(str(_PLUGIN_ROOT))


def register(ctx) -> None:
    """Register the OmniVoice TTS provider with Hermes.

    ``ctx.register_tts_provider`` is the documented hook
    (see ``agent/tts_provider.py``). Import is done inside ``register`` so a
    broken optional dependency surfaces as a load-time log line rather than
    preventing the whole plugin from importing.
    """
    try:
        from ov_core.provider import OmniVoiceProvider
    except Exception:  # pragma: no cover - defensive
        logger.exception("omnivoice: failed to import provider; TTS provider not registered")
        return

    ctx.register_tts_provider(OmniVoiceProvider())
    logger.info("omnivoice: registered TTS provider 'omnivoice'")
