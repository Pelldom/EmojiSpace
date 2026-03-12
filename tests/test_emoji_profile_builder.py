"""Phase 7.14 - Emoji Profile Builder: optional primary, category-derived primary, no fallback."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from emoji_profile_builder import build_emoji_profile, build_emoji_profile_parts  # noqa: E402


def _entity(
    emoji_id: str | None = None,
    tier: int | None = None,
    tags: list[str] | None = None,
    category: str | None = None,
) -> object:
    """Simple entity-like object with optional .emoji_id, .tier, .tags, .category."""
    class Entity:
        def __init__(self) -> None:
            self.emoji_id = emoji_id
            self.tier = tier
            self.tags = tags or []
            self.category = category

    return Entity()


def test_primary_tier_secondary() -> None:
    """Primary + tier + secondary all present."""
    entity = _entity("ship_trait_freighter", tier=2, tags=["combat:weapon_energy", "ship:utility_probe_array"])
    profile = build_emoji_profile(entity)
    assert "📦" in profile
    assert "Ⅱ" in profile
    assert "⚡" in profile
    assert "🛰" in profile
    parts = profile.split()
    assert parts[0] == "📦"
    assert parts[1] == "Ⅱ"
    assert len(parts) == 4


def test_category_derived_primary_for_goods() -> None:
    """Goods: category FOOD -> goods_category_food primary, tags as secondary."""
    entity = _entity(emoji_id=None, tier=None, tags=["essential", "agricultural"], category="FOOD")
    profile = build_emoji_profile(entity)
    # category FOOD -> goods_category_food 🍞; tags -> goods_essential, goods_agricultural
    assert "🍞" in profile
    parts = profile.split()
    assert parts[0] == "🍞"
    assert len(parts) >= 2


def test_no_primary_but_secondary_renders() -> None:
    """No primary (no emoji_id, no category) but tags -> secondary only, no fallback ?."""
    entity = _entity(emoji_id=None, tier=None, tags=["combat:weapon_energy", "combat:defense_shielded"])
    profile = build_emoji_profile(entity)
    assert "⚡" in profile
    assert "🛡" in profile
    assert "❓" not in profile
    parts = profile.split()
    assert len(parts) == 2
    assert set(parts) == {"⚡", "🛡"}


def test_no_fallback_question_mark() -> None:
    """Missing primary must not produce ?; tier-only or empty is ok."""
    entity = _entity("nonexistent_emoji_id", tier=1, tags=[])
    profile = build_emoji_profile(entity)
    assert "❓" not in profile
    # Only tier resolves
    assert profile.strip() == "Ⅰ"


def test_overflow_indicator_after_five_secondaries() -> None:
    """More than 5 secondaries -> first 5 glyphs then +N."""
    ten_tags = [
        "combat:weapon_energy",
        "combat:weapon_kinetic",
        "combat:defense_shielded",
        "combat:defense_armored",
        "ship:utility_probe_array",
        "ship:utility_data_array",
        "ship:utility_extra_cargo",
        "secondary:compact",
        "secondary:efficient",
        "crew:wanted",
    ]
    entity = _entity("ship_trait_military", tier=4, tags=ten_tags)
    profile = build_emoji_profile(entity)
    assert "🛡" in profile
    assert "Ⅳ" in profile
    assert profile.endswith("+5") or " +5" in profile
    parts = profile.split()
    assert parts[-1] == "+5"
    assert len(parts) == 8


def test_deterministic_secondary_sorting() -> None:
    """Secondary emojis ordered by emoji_id alphabetically."""
    entity = _entity(None, None, tags=["crew:wanted", "combat:weapon_energy", "ship:utility_probe_array"])
    profile = build_emoji_profile(entity)
    # Order by emoji_id: combat_weapon_energy, crew_wanted, ship_utility_probe_array -> ⚡ 🚨 🛰
    parts = profile.split()
    assert len(parts) == 3
    assert parts[0] == "⚡"
    assert parts[1] == "🚨"
    assert parts[2] == "🛰"


def test_empty_profile_returns_empty_string() -> None:
    """Entity with nothing that resolves -> empty string."""
    entity = _entity(None, None, tags=[], category=None)
    profile = build_emoji_profile(entity)
    assert profile == ""

    class Empty:
        pass

    profile = build_emoji_profile(Empty())
    assert profile == ""


def test_primary_only() -> None:
    """Primary only, no tier or tags."""
    entity = _entity("encounter_derelict_ship", tier=None, tags=[])
    profile = build_emoji_profile(entity)
    assert "🛰" in profile or "🛰️" in profile
    parts = profile.split()
    assert len(parts) == 1


def test_build_emoji_profile_parts() -> None:
    """Parts: (primary, tier, secondary list)."""
    entity = _entity("cargo_crate", tier=1, tags=["luxury"])
    primary, tier, secondary = build_emoji_profile_parts(entity)
    assert primary == "📦"
    assert tier == "Ⅰ"
    assert len(secondary) == 1
    assert secondary[0] == "💎"
