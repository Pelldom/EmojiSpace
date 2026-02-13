import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import combat_resolver as resolver  # noqa: E402
from ship_assembler import assemble_ship  # noqa: E402


def _ship_state(hull_id: str, modules: list[str], degradation: dict | None = None) -> dict:
    return {
        "hull_id": hull_id,
        "module_instances": [{"module_id": module_id} for module_id in modules],
        "degradation_state": degradation or {"weapon": 0, "defense": 0, "engine": 0},
    }


def test_basic_combat_deterministic() -> None:
    player = _ship_state("civ_t1_midge", ["weapon_energy_mk1", "defense_shielded_mk1", "combat_utility_engine_boost_mk1"])
    enemy = _ship_state("frg_t1_ant", ["weapon_kinetic_mk1", "defense_armored_mk1", "combat_utility_targeting_mk1"])
    selector = resolver.make_action_plan_selector(["Focus Fire", "Focus Fire", "Focus Fire"])
    first = resolver.resolve_combat(
        world_seed=111,
        combat_id="asm_det",
        player_ship_state=player,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=5,
    )
    second = resolver.resolve_combat(
        world_seed=111,
        combat_id="asm_det",
        player_ship_state=player,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=5,
    )
    assert first.outcome == second.outcome
    assert first.rounds == second.rounds
    assert first.log == second.log


def test_degradation_reduces_bands() -> None:
    ship = _ship_state("civ_t1_midge", ["weapon_energy_mk1"])
    before = assemble_ship(ship["hull_id"], ship["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
    after = assemble_ship(ship["hull_id"], ship["module_instances"], {"weapon": 1, "defense": 0, "engine": 0})
    assert after["bands"]["effective"]["weapon"] <= before["bands"]["effective"]["weapon"]


def test_red_override_triggers() -> None:
    ship = _ship_state("civ_t1_midge", ["weapon_energy_mk1"])
    baseline = assemble_ship(ship["hull_id"], ship["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
    cap = baseline["degradation"]["capacity"]["weapon"]
    red = assemble_ship(ship["hull_id"], ship["module_instances"], {"weapon": cap, "defense": 0, "engine": 0})
    assert red["bands"]["red"]["weapon"] is True
    assert red["bands"]["effective"]["weapon"] == 0


def test_rps_still_applies() -> None:
    player = _ship_state("civ_t1_midge", ["weapon_energy_mk1"])
    enemy_shield = _ship_state("civ_t1_midge", ["defense_shielded_mk1"])
    enemy_armor = _ship_state("civ_t1_midge", ["defense_armored_mk1"])
    selector = resolver.make_action_plan_selector(["Focus Fire"])

    shield_result = resolver.resolve_combat(
        world_seed=1,
        combat_id="rps_shield",
        player_ship_state=player,
        enemy_ship_state=enemy_shield,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    armor_result = resolver.resolve_combat(
        world_seed=1,
        combat_id="rps_armor",
        player_ship_state=player,
        enemy_ship_state=enemy_armor,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    shield_delta = shield_result.log[0]["attacks"]["player_to_enemy"]["band_delta"]
    armor_delta = armor_result.log[0]["attacks"]["player_to_enemy"]["band_delta"]
    assert armor_delta >= shield_delta


def test_combat_does_not_recompute_bands_internally(monkeypatch) -> None:
    calls = []

    def fake_assemble_ship(hull_id, module_instances, degradation_state=None):
        calls.append((hull_id, tuple(sorted(degradation_state.items())) if degradation_state else ()))
        return {
            "bands": {
                "effective": {"weapon": 9, "defense": 1, "engine": 1},
                "red": {"weapon": False, "defense": False, "engine": False},
                "pre_degradation": {"weapon": 9, "defense": 1, "engine": 1},
            },
            "degradation": {"capacity": {"weapon": 1, "defense": 1, "engine": 1}},
        }

    monkeypatch.setattr(resolver, "assemble_ship", fake_assemble_ship)
    selector = resolver.make_action_plan_selector(["Focus Fire"])
    result = resolver.resolve_combat(
        world_seed=5,
        combat_id="fixed_bands",
        player_ship_state=_ship_state("civ_t1_midge", ["weapon_energy_mk1"]),
        enemy_ship_state=_ship_state("civ_t1_midge", ["defense_shielded_mk1"]),
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    assert calls
    assert result.log[0]["bands"]["player"]["weapon"] >= 9
