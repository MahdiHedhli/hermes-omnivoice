"""The OmniVoice gallery — a browsable library of ready-made designed voices.

Upstream (github.com/debpalash/omnivoice-gallery) publishes a ``manifest.json``
of community/team content over a CDN. Two item types exist there: ``preset``
(a *designed* voice — just a validated ``instruct`` string, no audio) and
``voice`` (a recorded reference clip for cloning, hosted as a release asset).

**We only take presets.** They are text-only, so browsing costs no downloads,
and they map exactly onto our existing design-voice path. Recorded clips would
mean fetching third-party audio of real people, which our clone path
deliberately gates behind explicit consent — out of scope for a browse tab.

**Local-first:** the plugin ships a vendored snapshot (``data/gallery.json``)
and makes *no* network call on its own. ``refresh()`` is the only outbound
request and it happens only when the user explicitly asks for it.

Every preset — vendored or freshly fetched — is run through
``validate_instruct`` before it is ever offered, so an upstream entry using a
word outside OmniVoice's fixed vocabulary can't be installed into a voice that
would then fail at synthesis (the failure mode that produced HTTP 502s here
before design-time validation existed).
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from . import paths
from .registry import RegistryError, validate_instruct

MANIFEST_URL = "https://cdn.jsdelivr.net/gh/debpalash/omnivoice-gallery@main/manifest.json"
_ALLOWED_HOSTS = {"cdn.jsdelivr.net"}
_MAX_MANIFEST_BYTES = 2 * 1024 * 1024  # 2 MiB — the real manifest is ~17 KiB
_KEEP_FIELDS = ("id", "name", "use_case", "instruct", "language",
                "sample_script", "author", "license", "icon")

# The gallery labels languages in prose ("English"); our registry and the SDK
# kwarg use short codes. Anything unrecognized falls back to English rather
# than writing a code the model would reject.
_LANG_CODES = {"english": "en", "en": "en", "chinese": "zh", "zh": "zh",
               "mandarin": "zh"}

_VENDORED = Path(__file__).resolve().parent.parent / "data" / "gallery.json"


def language_code(language: str) -> str:
    return _LANG_CODES.get((language or "").strip().lower(), "en")


def _usable_presets(raw_items: Any) -> List[Dict[str, Any]]:
    """Keep only presets whose instruct passes our validator."""
    items: List[Dict[str, Any]] = []
    if not isinstance(raw_items, list):
        return items
    for entry in raw_items:
        if not isinstance(entry, dict):
            continue
        # A vendored snapshot has already been filtered to presets and so
        # carries no "type"; a freshly fetched manifest still has it.
        if entry.get("type") not in (None, "preset"):
            continue
        try:
            validate_instruct(str(entry.get("instruct") or ""))
        except RegistryError:
            continue
        if not entry.get("id") or not entry.get("name"):
            continue
        items.append({k: entry[k] for k in _KEEP_FIELDS if k in entry})
    return items


def _read(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def load() -> Dict[str, Any]:
    """The presets to show: a user-refreshed cache when present, else the
    vendored snapshot. A corrupt cache silently falls back rather than
    breaking the tab."""
    for path, origin in ((paths.gallery_cache_path(), "refreshed"), (_VENDORED, "bundled")):
        try:
            if path.is_file():
                data = _read(path)
                items = _usable_presets(data.get("items"))
                if items:
                    return {
                        "items": items,
                        "origin": origin,
                        "updated_at": data.get("snapshot_updated_at") or data.get("updated_at") or "",
                        "source": data.get("source") or MANIFEST_URL,
                    }
        except (OSError, ValueError):
            continue
    return {"items": [], "origin": "unavailable", "updated_at": "", "source": MANIFEST_URL}


def refresh(timeout: int = 20) -> Tuple[int, str]:
    """Fetch the live manifest and cache the presets. Returns (count, updated_at).

    Only ever called from an explicit user action. Pinned to the CDN host over
    https, size-capped, and re-validated before anything is written.
    """
    parsed = urlparse(MANIFEST_URL)
    if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_HOSTS:
        raise RegistryError("gallery manifest URL is not an allowed https source")

    req = urllib.request.Request(MANIFEST_URL, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(_MAX_MANIFEST_BYTES + 1)
    except Exception as exc:
        raise RegistryError(f"could not reach the voice gallery: {exc}") from exc
    if len(raw) > _MAX_MANIFEST_BYTES:
        raise RegistryError("gallery manifest is unexpectedly large; refusing it")

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RegistryError(f"gallery manifest is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError("gallery manifest is not a JSON object")

    items = _usable_presets(data.get("items"))
    if not items:
        raise RegistryError("the gallery returned no presets this plugin can use")

    payload = {
        "schema_version": data.get("schema_version"),
        "source": "https://github.com/debpalash/omnivoice-gallery",
        "manifest_url": MANIFEST_URL,
        "snapshot_updated_at": data.get("updated_at") or "",
        "items": items,
    }
    out = paths.gallery_cache_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    tmp.replace(out)
    return len(items), str(payload["snapshot_updated_at"])


def get(preset_id: str) -> Dict[str, Any]:
    wanted = (preset_id or "").strip().lower()
    for item in load()["items"]:
        if str(item.get("id", "")).lower() == wanted:
            return item
    raise RegistryError(f"unknown gallery preset '{preset_id}'")
