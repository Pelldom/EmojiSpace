"""
Player-facing CLI display. Single pipeline for all entity names.
ALL entity names displayed in the CLI must go through render_entity() or render_good().
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    # When running as a package where src is importable as a package
    from src.emoji_profile_builder import build_emoji_profile_parts  # type: ignore[import]
except ModuleNotFoundError:
    # When running via run_game_cli.py which already inserts src/ on sys.path
    from emoji_profile_builder import build_emoji_profile_parts


def normalize_entity(obj: Any) -> SimpleNamespace:
    """
    Normalize engine dict or object to SimpleNamespace with emoji_id, tier, tags, category.
    Missing values default to None or [] so the emoji builder always receives correct attributes.
    """
    if obj is None:
        return SimpleNamespace(emoji_id=None, tier=None, tags=[], category=None)
    if isinstance(obj, dict):
        return SimpleNamespace(
            emoji_id=obj.get("emoji_id"),
            tier=obj.get("tier"),
            tags=obj.get("tags") if isinstance(obj.get("tags"), (list, tuple)) else [],
            category=obj.get("category"),
        )
    if hasattr(obj, "emoji_id") or hasattr(obj, "tier") or hasattr(obj, "tags") or hasattr(obj, "category"):
        return SimpleNamespace(
            emoji_id=getattr(obj, "emoji_id", None),
            tier=getattr(obj, "tier", None),
            tags=list(getattr(obj, "tags", None) or []),
            category=getattr(obj, "category", None),
        )
    return SimpleNamespace(emoji_id=None, tier=None, tags=[], category=None)


def format_entity_name(entity: Any, name: str) -> str:
    """
    Standardized entity display:
      [primary] NAME [tier] [secondary] [secondary] ...

    All emoji parts are optional except NAME. Secondary emojis preserve
    order and duplicates and are never truncated.
    """
    # Always normalize so the builder sees emoji_id, tier, tags, category.
    normalized = normalize_entity(entity)
    try:
        primary, tier, secondary = build_emoji_profile_parts(normalized)
    except Exception:
        return name

    parts: list[str] = []
    if primary:
        parts.append(primary)
    parts.append(name)
    if tier:
        parts.append(tier)
    if isinstance(secondary, (list, tuple)):
        for glyph in secondary:
            if isinstance(glyph, str) and glyph:
                parts.append(glyph)
    return " ".join(parts).strip() or name


def render_entity(entity: Any, name: str, visible: bool = True) -> str:
    """
    Single display path for entities (systems, destinations, locations, ships, modules, NPCs, encounters, missions).
    If visible is False (fog of war), return name only. Otherwise route through format_entity_name().
    """
    if not visible:
        return name
    try:
        return format_entity_name(entity, name)
    except Exception:
        return name


def render_good(entity: Any, name: str, visible: bool = True) -> str:
    """
    Goods now use the same global format as all entities:
      [primary] NAME [tier] [secondary] [secondary] ...
    """
    if not visible or not name:
        return name or ""
    try:
        return format_entity_name(entity, name)
    except Exception:
        return name or ""


# ----- Destination display entity (emoji_id from destination or location_{destination_type}) -----

def destination_display_entity(destination: Any) -> Any:
    """Use destination as entity; when emoji_id is empty use location_{destination_type} from emoji.json."""
    if destination is None:
        return SimpleNamespace(emoji_id=None, tier=None, tags=[], category=None)
    if isinstance(destination, dict):
        eid = str((destination.get("emoji_id") or "")).strip()
    else:
        eid = str(getattr(destination, "emoji_id", None) or "").strip()
    if eid:
        return normalize_entity(destination)
    dtype = (getattr(destination, "destination_type", None) or "") if not isinstance(destination, dict) else (destination.get("destination_type") or "")
    if isinstance(destination, dict):
        dtype = str(dtype).strip()
    if not dtype:
        return normalize_entity(destination)
    return SimpleNamespace(
        emoji_id=f"location_{dtype}",
        tier=getattr(destination, "tier", None) if not isinstance(destination, dict) else destination.get("tier"),
        tags=getattr(destination, "tags", None) or [] if not isinstance(destination, dict) else (destination.get("tags") or []),
        category=None,
    )


# ----- Location display (location_type -> location_{type}) -----

def location_display_entity(location: Any) -> Any:
    """Entity for a location: emoji_id = location_{location_type}."""
    if location is None:
        return SimpleNamespace(emoji_id=None, tier=None, tags=[], category=None)
    loc_type = (getattr(location, "location_type", None) or "") if not isinstance(location, dict) else (location.get("location_type") or "")
    loc_type = str(loc_type).strip()
    return SimpleNamespace(
        emoji_id=f"location_{loc_type}" if loc_type else None,
        tier=None,
        tags=[],
        category=None,
    )


# ----- Encounter: map description/subtype to emoji_id -----

_encounter_emoji_map: dict[str, str] | None = None


def _load_encounter_emoji_map() -> dict[str, str]:
    global _encounter_emoji_map
    if _encounter_emoji_map is not None:
        return _encounter_emoji_map
    _encounter_emoji_map = {}
    try:
        root = Path(__file__).resolve().parents[1]
        path = root / "data" / "encounter_types.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        types_list = data.get("encounter_types") if isinstance(data, dict) else (data if isinstance(data, list) else [])
        for entry in types_list or []:
            if not isinstance(entry, dict):
                continue
            subtype = entry.get("subtype_id")
            emoji_key = entry.get("emoji")
            if subtype and emoji_key:
                _encounter_emoji_map[str(subtype)] = str(emoji_key)
    except Exception:
        pass
    # Fallback: known emoji.json ids for encounters
    fallback = {
        "pirate_raider": "encounter_pirate",
        "civilian_trader_ship": "encounter_trader",
        "customs_patrol": "encounter_authority",
        "bounty_hunter": "encounter_bounty_hunter",
    }
    for k, v in fallback.items():
        if k not in _encounter_emoji_map:
            _encounter_emoji_map[k] = v
    return _encounter_emoji_map


def encounter_display_entity(encounter_description: str, subtype_id: str | None = None) -> SimpleNamespace:
    """Build entity for encounter: use subtype_id or infer from description (e.g. 'Pirate Raider' -> pirate_raider)."""
    sid = subtype_id
    if not sid and encounter_description:
        sid = str(encounter_description).strip().lower().replace(" ", "_")
    emoji_id = None
    if sid:
        emoji_id = _load_encounter_emoji_map().get(sid)
        if not emoji_id and sid:
            emoji_id = f"encounter_{sid}"
    return SimpleNamespace(emoji_id=emoji_id, tier=None, tags=[], category=None)


def render_encounter(encounter_description: str, subtype_id: str | None = None, visible: bool = True) -> str:
    """Display encounter name with emoji profile when visible."""
    if not visible:
        return encounter_description or "Unknown"
    entity = encounter_display_entity(encounter_description, subtype_id)
    return render_entity(entity, encounter_description or "Unknown", visible=True)


# ----- Labels and headings (no entity) -----

def title_current_location(location_name: str) -> str:
    """Heading for current location (name only, no emoji)."""
    return location_name


def menu_option(number: int, label: str) -> str:
    """Format a menu line: '1 Travel'."""
    return f"{number} {label}"


def menu_back() -> str:
    """Standard back option."""
    return "0 Back"


def menu_exit() -> str:
    """Standard exit option."""
    return "0 Exit"


# ----- Ship: entity from hull_id (tier from hulls.json) -----

_ship_hull_cache: dict[str, dict[str, Any]] | None = None


def _load_hulls() -> dict[str, dict[str, Any]]:
    global _ship_hull_cache
    if _ship_hull_cache is not None:
        return _ship_hull_cache
    _ship_hull_cache = {}
    try:
        root = Path(__file__).resolve().parents[1]
        path = root / "data" / "hulls.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for hull in (data.get("hulls", []) if isinstance(data, dict) else []):
            if isinstance(hull, dict) and hull.get("hull_id"):
                _ship_hull_cache[str(hull["hull_id"])] = hull
    except Exception:
        pass
    return _ship_hull_cache


def ship_display_entity(ship_or_hull_id: Any) -> SimpleNamespace:
    """Build entity for ship: from ship dict with hull_id or raw hull_id. Sets tier from hulls.json."""
    hull_id = None
    if isinstance(ship_or_hull_id, dict):
        hull_id = ship_or_hull_id.get("hull_id") or ship_or_hull_id.get("model_id")
    elif isinstance(ship_or_hull_id, str):
        hull_id = ship_or_hull_id
    if not hull_id:
        return SimpleNamespace(emoji_id=None, tier=None, tags=[], category=None)
    hulls = _load_hulls()
    hull = hulls.get(str(hull_id))
    if not hull:
        return SimpleNamespace(emoji_id=None, tier=None, tags=[], category=None)
    return SimpleNamespace(
        emoji_id=hull.get("emoji_id"),
        tier=hull.get("tier"),
        tags=list(hull.get("traits") or []),
        category=None,
    )
