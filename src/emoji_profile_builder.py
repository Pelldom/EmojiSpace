"""
Emoji Profile Builder — composite profiles for game entities.

Builds deterministic emoji identity for presentation only from real entity
shapes: destinations, systems, goods, ships/hulls. Resolves via data/emoji.json,
data/tags.json, data/categories.json. Must not affect gameplay.

Profile formats:
- Destination: [type] NAME [population tier] [economy] [economy] [situation] ...
- System: [type] NAME [population tier] [government] [situation] ...
- Goods: [category] NAME [tag] [tag] ...
- Ship: [frame/trait] NAME [tier] [tag] [tag] ...

Order and duplicates in secondaries are preserved; no sorting or truncation.
"""

import json
from pathlib import Path
from types import SimpleNamespace

# Tier 1–10 → roman_i through roman_x (ids map to keycap glyphs in emoji.json).
_TIER_EMOJI_IDS = [
    "roman_i", "roman_ii", "roman_iii", "roman_iv", "roman_v",
    "roman_vi", "roman_vii", "roman_viii", "roman_ix", "roman_x",
]

# Default system/star primary when no star type is present.
_DEFAULT_SYSTEM_EMOJI_ID = "star_yellow"

# Module-level caches (loaded once).
EMOJI_REGISTRY: dict[str, str] = {}
TAG_MAP: dict[str, str] = {}
CATEGORY_MAP: dict[str, str] = {}


def _load_emoji_registry() -> dict[str, str]:
    """Load emoji.json into emoji_id → glyph. Never raises."""
    global EMOJI_REGISTRY
    if EMOJI_REGISTRY:
        return EMOJI_REGISTRY
    try:
        path = Path(__file__).resolve().parent.parent / "data" / "emoji.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    eid = entry.get("emoji_id")
                    glyph = entry.get("glyph")
                    if eid and glyph is not None:
                        EMOJI_REGISTRY[str(eid)] = str(glyph)
    except Exception:
        pass
    return EMOJI_REGISTRY


def _load_tag_map() -> dict[str, str]:
    """Load tags.json into tag_id → emoji_id. Never raises."""
    global TAG_MAP
    if TAG_MAP:
        return TAG_MAP
    try:
        path = Path(__file__).resolve().parent.parent / "data" / "tags.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    tid = entry.get("tag_id")
                    eid = entry.get("emoji_id")
                    if tid and eid:
                        TAG_MAP[str(tid)] = str(eid)
    except Exception:
        pass
    return TAG_MAP


def _load_category_map() -> dict[str, str]:
    """Load categories.json into category_id → emoji_id. Never raises."""
    global CATEGORY_MAP
    if CATEGORY_MAP:
        return CATEGORY_MAP
    try:
        path = Path(__file__).resolve().parent.parent / "data" / "categories.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        categories = data.get("categories") if isinstance(data, dict) else None
        if isinstance(categories, dict):
            for cid, details in categories.items():
                if isinstance(details, dict):
                    eid = details.get("emoji_id")
                    if cid and eid:
                        CATEGORY_MAP[str(cid)] = str(eid)
    except Exception:
        pass
    return CATEGORY_MAP


def _safe_get(entity: object, *keys: str):
    """Safe field access: try getattr then dict.get for each key. Return first non-None."""
    if entity is None:
        return None
    for k in keys:
        v = getattr(entity, k, None)
        if v is not None:
            return v
        if isinstance(entity, dict):
            v = entity.get(k)
        if v is not None:
            return v
    return None


def _safe_list(entity: object, *keys: str) -> list:
    """Return list from first key that yields a sequence. Empty list if missing or not sequence."""
    val = _safe_get(entity, *keys)
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        return list(val)
    return []


def _normalize_destination(entity: object) -> tuple[str | None, int | None, list[str]]:
    """Derive (primary_emoji_id, tier_1_10, secondary_emoji_ids) for a destination."""
    dest_type = _safe_get(entity, "destination_type", "destinationType")
    primary = None
    if dest_type:
        raw = str(dest_type).strip().lower().replace(" ", "_")
        if raw in ("planet", "station"):
            primary = f"location_{raw}"
        else:
            primary = f"location_{raw}"
    if not primary:
        primary = "location_planet"
    pop = _safe_get(entity, "population")
    tier = None
    if pop is not None:
        try:
            t = int(pop)
            tier = max(1, min(10, t))
        except (TypeError, ValueError):
            pass
    secondaries: list[str] = []
    prim_eco = _safe_get(entity, "primary_economy_id", "primary_economy")
    if prim_eco and str(prim_eco).strip():
        secondaries.append(f"economy_{str(prim_eco).strip().lower().replace(' ', '_')}")
    for e in _safe_list(entity, "secondary_economy_ids", "secondary_economies"):
        if e and str(e).strip():
            secondaries.append(f"economy_{str(e).strip().lower().replace(' ', '_')}")
    for s in _safe_list(entity, "active_destination_situations", "situations", "destination_situations"):
        if s and str(s).strip():
            secondaries.append(f"situation_{str(s).strip().lower().replace(' ', '_')}")
    return (primary, tier, secondaries)


def _normalize_system(entity: object) -> tuple[str | None, int | None, list[str]]:
    """Derive (primary_emoji_id, tier_1_10, secondary_emoji_ids) for a system."""
    star_type = _safe_get(entity, "star_type", "star_type_id")
    primary = None
    if star_type and str(star_type).strip():
        raw = str(star_type).strip().lower().replace(" ", "_")
        primary = f"star_{raw}"
    if not primary:
        primary = _DEFAULT_SYSTEM_EMOJI_ID
    pop = _safe_get(entity, "population")
    tier = None
    if pop is not None:
        try:
            t = int(pop)
            tier = max(1, min(10, t))
        except (TypeError, ValueError):
            pass
    secondaries: list[str] = []
    gov = _safe_get(entity, "government_id", "government")
    if gov and str(gov).strip():
        secondaries.append(f"government_{str(gov).strip().lower().replace(' ', '_')}")
    for s in _safe_list(entity, "active_system_situations", "situations", "system_situations"):
        if s and str(s).strip():
            secondaries.append(f"situation_{str(s).strip().lower().replace(' ', '_')}")
    return (primary, tier, secondaries)


def _normalize_goods(entity: object) -> tuple[str | None, int | None, list[str]]:
    """Derive (primary_emoji_id, tier, secondary_emoji_ids) for goods. Category → primary; tags → secondaries via tag_map."""
    primary = None
    category = _safe_get(entity, "category")
    if category and str(category).strip():
        primary = str(category).strip()
    tier = None
    t = _safe_get(entity, "tier")
    if t is not None:
        try:
            idx = int(t)
            if 1 <= idx <= 10:
                tier = idx
        except (TypeError, ValueError):
            pass
    secondaries = []
    for tag in _safe_list(entity, "tags"):
        if tag is not None and str(tag).strip():
            secondaries.append(str(tag).strip())
    return (primary, tier, secondaries)


def _normalize_ship_or_generic(entity: object) -> tuple[str | None, int | None, list[str]]:
    """Derive (primary_emoji_id, tier, secondary_emoji_ids) for ships/hulls or generic. emoji_id/tier/tags."""
    primary = _safe_get(entity, "emoji_id")
    if primary and str(primary).strip():
        primary = str(primary).strip()
    else:
        primary = None
    tier = None
    t = _safe_get(entity, "tier")
    if t is not None:
        try:
            idx = int(t)
            if 1 <= idx <= 10:
                tier = idx
        except (TypeError, ValueError):
            pass
    secondaries = []
    for tag in _safe_list(entity, "tags"):
        if tag is not None and str(tag).strip():
            secondaries.append(str(tag).strip())
    return (primary, tier, secondaries)


def _normalize_entity(entity: object) -> tuple[str | None, int | None, list[str]]:
    """
    Recognize entity shape and return (primary_emoji_id, tier_1_10_or_None, secondary_emoji_ids).
    secondary_emoji_ids for goods/ships are tag_ids (resolved later via tag_map); for dest/system are emoji_ids.
    Order and duplicates preserved; no sort, no cap.
    """
    if entity is None:
        return (None, None, [])
    dest_type = _safe_get(entity, "destination_type", "destinationType")
    if dest_type is not None:
        return _normalize_destination(entity)
    gov = _safe_get(entity, "government_id", "government")
    sys_id = _safe_get(entity, "system_id")
    if gov is not None or sys_id is not None:
        return _normalize_system(entity)
    if isinstance(entity, dict) and "government" in entity:
        return _normalize_system(entity)
    category = _safe_get(entity, "category")
    if category is not None:
        return _normalize_goods(entity)
    return _normalize_ship_or_generic(entity)


def _resolve_primary(
    registry: dict[str, str],
    category_map: dict[str, str],
    entity: object,
    normalized: tuple[str | None, int | None, list[str]],
) -> str | None:
    """Resolve primary glyph from normalized primary (emoji_id or category_id), or entity.emoji_id / entity.category."""
    primary_eid, _, _ = normalized
    if primary_eid and str(primary_eid).strip():
        key = str(primary_eid).strip()
        if key in registry:
            return registry[key]
        eid = category_map.get(key)
        if eid and eid in registry:
            return registry[eid]
    eid = getattr(entity, "emoji_id", None)
    if eid and str(eid).strip():
        glyph = registry.get(str(eid).strip())
        if glyph:
            return glyph
    category = getattr(entity, "category", None) or (entity.get("category") if isinstance(entity, dict) else None)
    if category and str(category).strip():
        eid = category_map.get(str(category).strip())
        if eid and eid in registry:
            return registry[eid]
    return None


def _resolve_tier(
    registry: dict[str, str],
    entity: object,
    normalized: tuple[str | None, int | None, list[str]],
) -> str | None:
    """Resolve tier glyph from normalized tier (1–10) or entity.tier. Uses roman_i..roman_x → keycap glyphs."""
    _, tier_int, _ = normalized
    if tier_int is not None and 1 <= tier_int <= len(_TIER_EMOJI_IDS):
        eid = _TIER_EMOJI_IDS[tier_int - 1]
        return registry.get(eid)
    tier = getattr(entity, "tier", None)
    if tier is None and isinstance(entity, dict):
        tier = entity.get("tier")
    if tier is None:
        return None
    try:
        idx = int(tier)
        if 1 <= idx <= len(_TIER_EMOJI_IDS):
            eid = _TIER_EMOJI_IDS[idx - 1]
            return registry.get(eid)
    except (TypeError, ValueError):
        pass
    return None


def _resolve_secondary(
    registry: dict[str, str],
    tag_map: dict[str, str],
    normalized: tuple[str | None, int | None, list[str]],
    entity: object,
) -> list[str]:
    """
    Resolve secondary glyphs from normalized secondary list.
    Each item is either an emoji_id (resolve via registry) or a tag_id (resolve via tag_map then registry).
    Preserves order and duplicates; no sort, no cap.
    """
    _, _, secondary_ids = normalized
    out: list[str] = []
    for sid in secondary_ids:
        if not sid or not str(sid).strip():
            continue
        sid = str(sid).strip()
        eid = tag_map.get(sid) or sid
        if eid and eid in registry:
            out.append(registry[eid])
    tags = getattr(entity, "tags", None)
    if isinstance(tags, (list, tuple)) and not secondary_ids:
        for tag in tags:
            tid = str(tag).strip() if tag is not None else ""
            if not tid:
                continue
            eid = tag_map.get(tid)
            if eid and eid in registry:
                out.append(registry[eid])
    return out


def build_emoji_profile(entity: object) -> str:
    """
    Build deterministic emoji profile string: Primary Tier Secondary... (emojis only).
    Primary, tier, and secondaries are optional. Order preserved; no truncation.
    """
    try:
        registry = _load_emoji_registry()
        tag_map = _load_tag_map()
        category_map = _load_category_map()
    except Exception:
        return ""

    norm = _normalize_entity(entity)
    parts: list[str] = []

    primary_glyph = _resolve_primary(registry, category_map, entity, norm)
    if primary_glyph:
        parts.append(primary_glyph)

    tier_glyph = _resolve_tier(registry, entity, norm)
    if tier_glyph:
        parts.append(tier_glyph)

    secondary = _resolve_secondary(registry, tag_map, norm, entity)
    parts.extend(secondary)

    return " ".join(parts)


def build_emoji_profile_parts(entity: object) -> tuple[str | None, str | None, list[str]]:
    """
    Return (primary_glyph, tier_glyph, secondary_glyphs) for flexible display.
    CLI uses this to format e.g. [primary] NAME [tier] [secondary]...
    Order and duplicates in secondary_glyphs preserved; no cap.
    """
    try:
        registry = _load_emoji_registry()
        tag_map = _load_tag_map()
        category_map = _load_category_map()
    except Exception:
        return (None, None, [])

    norm = _normalize_entity(entity)
    primary = _resolve_primary(registry, category_map, entity, norm)
    tier = _resolve_tier(registry, entity, norm)
    secondary = _resolve_secondary(registry, tag_map, norm, entity)
    return (primary, tier, secondary)
