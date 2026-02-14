import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from crew_modifiers import compute_crew_modifiers  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402


def _crew(
    npc_id: str,
    role: str,
    tags: list[str] | None = None,
    daily_wage: int = 0,
) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id=role,
        crew_tags=list(tags or []),
        daily_wage=daily_wage,
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def test_single_role_aggregation() -> None:
    ship = ShipEntity(crew=[_crew("NPC-1", role="pilot", daily_wage=5)])
    modifiers = compute_crew_modifiers(ship)
    assert modifiers.engine_band_bonus == 1
    assert modifiers.daily_wage_total == 5


def test_multiple_role_stacking() -> None:
    ship = ShipEntity(crew=[_crew("NPC-1", role="gunner"), _crew("NPC-2", role="gunner"), _crew("NPC-3", role="tactician")])
    modifiers = compute_crew_modifiers(ship)
    assert modifiers.attack_band_bonus == 2
    assert modifiers.defense_band_bonus == 1


def test_tag_stacking() -> None:
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", role="pilot", tags=["crew:steady_aim", "crew:evasive"]),
            _crew("NPC-2", role="pilot", tags=["crew:trigger_happy", "crew:slow_reactions"]),
        ]
    )
    modifiers = compute_crew_modifiers(ship)
    assert modifiers.focus_fire_bonus == 0
    assert modifiers.evasive_bonus == 0


def test_fuel_delta_stacking() -> None:
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", role="navigator", tags=["crew:fuel_efficient"]),
            _crew("NPC-2", role="navigator", tags=["crew:wasteful"]),
        ]
    )
    modifiers = compute_crew_modifiers(ship)
    assert modifiers.fuel_delta == -4


def test_cargo_stacking() -> None:
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", role="quartermaster", tags=["crew:organized"]),
            _crew("NPC-2", role="quartermaster", tags=["crew:cluttered"]),
        ]
    )
    modifiers = compute_crew_modifiers(ship)
    assert modifiers.cargo_delta == 6


def test_alien_stacking_amplifies_existing_numeric_modifiers_only() -> None:
    ship = ShipEntity(
        tags=["ship_trait_alien"],
        persistent_state={
            "modules": [
                {"primary_tag": "combat_weapon_alien", "secondary_tags": ["secondary_alien"]},
            ]
        },
        crew=[
            _crew("NPC-1", role="gunner", tags=["crew:alien", "crew:data_savvy"]),
        ],
    )
    modifiers = compute_crew_modifiers(ship)
    # aligned elements: ship tag (1) + module primary (1) + module secondary (1) = 3
    # gunner base attack +1 amplified by 3 -> +4, then combat cap to +3
    assert modifiers.attack_band_bonus == 3
    # data_savvy base +2 amplified by 3 -> +5
    assert modifiers.data_cargo_delta == 5
    # no created values for untouched fields
    assert modifiers.mission_slot_bonus == 0


def test_combat_band_cap_enforcement() -> None:
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", role="pilot"),
            _crew("NPC-2", role="pilot"),
            _crew("NPC-3", role="pilot"),
            _crew("NPC-4", role="pilot"),
            _crew("NPC-5", role="pilot"),
        ]
    )
    modifiers = compute_crew_modifiers(ship)
    assert modifiers.engine_band_bonus == 3


def test_multiplier_stacking() -> None:
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", role="broker", tags=["crew:haggler", "crew:bargain_hunter"]),
            _crew("NPC-2", role="broker", tags=["crew:awkward", "crew:blacklisted"]),
        ]
    )
    modifiers = compute_crew_modifiers(ship)
    assert round(modifiers.buy_multiplier, 6) == round(0.90 * 0.95 * 0.90 * 1.05, 6)
    assert round(modifiers.sell_multiplier, 6) == round(1.10 * 1.05 * 1.10 * 0.95, 6)


def test_no_crew_returns_defaults() -> None:
    modifiers = compute_crew_modifiers(ShipEntity())
    assert modifiers.attack_band_bonus == 0
    assert modifiers.defense_band_bonus == 0
    assert modifiers.engine_band_bonus == 0
    assert modifiers.buy_multiplier == 1.0
    assert modifiers.sell_multiplier == 1.0
    assert modifiers.daily_wage_total == 0
