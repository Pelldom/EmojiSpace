import hashlib
from typing import Iterable, List


_RISK_ADJECTIVES = {
    "low": ["quiet", "uneventful", "steady"],
    "medium": ["tense", "watchful", "pressured"],
    "high": ["volatile", "fraught", "severe"],
}

_REPUTATION_ADJECTIVES = {
    "low": ["wary", "dismissive", "cold"],
    "neutral": ["reserved", "measured", "even"],
    "high": ["welcoming", "warm", "approving"],
}

_GOVERNMENT_TONE_ADJECTIVES = {
    "authoritarian": ["formal", "strict", "severe"],
    "democratic": ["measured", "civil", "open"],
    "anarchic": ["rough", "blunt", "unfiltered"],
    "default": ["plain", "neutral", "unadorned"],
}

_ROLE_ADJECTIVES = {
    "bartender": ["chatty", "low key", "familiar"],
    "administrator": ["official", "formal", "procedural"],
    "trader": ["practical", "businesslike", "direct"],
    "pirate": ["taunting", "grim", "brazen"],
}


def generate_prose(
    *,
    risk_tier: str | None,
    reputation_band: str | None,
    government_tone: str | None,
    npc_role_tags: Iterable[str] | None,
) -> str:
    role_tags = list(npc_role_tags or [])
    adjectives: List[str] = []
    adjectives.append(_select_from_band(_RISK_ADJECTIVES, risk_tier, "low"))
    adjectives.append(_select_from_band(_REPUTATION_ADJECTIVES, reputation_band, "neutral"))
    adjectives.append(_select_from_band(_GOVERNMENT_TONE_ADJECTIVES, government_tone, "default"))
    if role_tags:
        role_tag = _select_role_tag(role_tags)
        adjectives.append(_select_from_band(_ROLE_ADJECTIVES, role_tag, "bartender"))
    else:
        adjectives.append("plain")
    return _render(adjectives)


def _render(adjectives: List[str]) -> str:
    cleaned = [word for word in adjectives if word]
    if not cleaned:
        return "A muted report settles into the channel."
    return f"A {', '.join(cleaned)} report settles into the channel."


def _select_from_band(options: dict, band: str | None, fallback: str) -> str:
    key = (band or fallback).lower()
    pool = options.get(key) or options.get(fallback) or ["plain"]
    index = _stable_index(f"{key}|{fallback}", len(pool))
    return pool[index]


def _select_role_tag(role_tags: List[str]) -> str:
    if not role_tags:
        return "bartender"
    role_tags = sorted(role_tags)
    index = _stable_index("|".join(role_tags), len(role_tags))
    return role_tags[index]


def _stable_index(seed_text: str, size: int) -> int:
    if size <= 1:
        return 0
    digest = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % size
