"""Shared OmniVoice integration core.

Imported by both the agent-side provider (``omnivoice/__init__.py``) and the
dashboard backend routes (``omnivoice/dashboard/plugin_api.py``). Named
``ov_core`` to avoid shadowing the real OmniVoice SDK package (``omnivoice``).
"""

__all__ = ["config", "paths", "registry", "backends", "provider"]
