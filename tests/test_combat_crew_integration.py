import copy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import combat_resolver as resolver  # noqa: E402


def _ship_state(
    *,
    hull_id: str = "civ_t1_midge",
    modules: list[dict] | None = None,
    crew: list[dict] | None = None,
    tags: list[str] | None = None,
) -> dict:
    return {
        "hull_id": hull_id,
        "module_instances": modules
        if modules is not None
        else [
            {"module_id": "weapon_energy_mk1"},
            {"module_id": "defense_shielded_mk1"},
            {"module_id": "combat_utility_engine_boost_mk1"},
        ],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
        "crew": list(crew or []),
        "tags": list(tags or []),
    }


def _crew(role: str, crew_tags: list[str] | None = None) -> dict:
    return {
        "crew_role_id": role,
        "crew_tags": list(crew_tags or []),
        "daily_wage": 0,
    }


def test_no_crew_combat_unchanged_baseline() -> None:
    player = _ship_state()
    enemy = _ship_state(hull_id="frg_t1_ant")
    selector = resolver.make_action_plan_selector(["Focus Fire"])
    first = resolver.resolve_combat(
        world_seed=1001,
        combat_id="crew_none_a",
        player_ship_state=copy.deepcopy(player),
        enemy_ship_state=copy.deepcopy(enemy),
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    second = resolver.resolve_combat(
        world_seed=1001,
        combat_id="crew_none_a",
        player_ship_state=copy.deepcopy(player),
        enemy_ship_state=copy.deepcopy(enemy),
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    assert first.log == second.log


def test_tactician_increases_defense_band_and_reduces_damage() -> None:
    base_player = _ship_state()
    crew_player = _ship_state(crew=[_crew("tactician")])
    enemy = _ship_state(hull_id="frg_t1_ant")
    selector = resolver.make_action_plan_selector(["Focus Fire"])

    baseline = resolver.resolve_combat(
        world_seed=1002,
        combat_id="tactician_base",
        player_ship_state=base_player,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    buffed = resolver.resolve_combat(
        world_seed=1002,
        combat_id="tactician_buff",
        player_ship_state=crew_player,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    base_def = baseline.log[0]["bands"]["player"]["defense"]
    buff_def = buffed.log[0]["bands"]["player"]["defense"]
    base_taken = baseline.log[0]["attacks"]["enemy_to_player"]["damage"]
    buff_taken = buffed.log[0]["attacks"]["enemy_to_player"]["damage"]
    assert buff_def >= base_def
    assert buff_taken <= base_taken


def test_pilot_increases_engine_band() -> None:
    base_player = _ship_state()
    pilot_player = _ship_state(crew=[_crew("pilot")])
    enemy = _ship_state(hull_id="frg_t1_ant")
    selector = resolver.make_action_plan_selector(["Focus Fire"])

    baseline = resolver.resolve_combat(
        world_seed=1003,
        combat_id="pilot_base",
        player_ship_state=base_player,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    buffed = resolver.resolve_combat(
        world_seed=1003,
        combat_id="pilot_buff",
        player_ship_state=pilot_player,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    assert buffed.log[0]["bands"]["player"]["engine"] >= baseline.log[0]["bands"]["player"]["engine"]


def test_mechanic_increases_repair_amount_per_use() -> None:
    ship_state = _ship_state(
        modules=[
            {"module_id": "weapon_energy_mk1"},
            {"module_id": "defense_shielded_mk1"},
            {"module_id": "combat_utility_repair_system_mk1"},
        ],
        crew=[_crew("mechanic")],
    )
    state = resolver._create_initial_state_from_ship_state(ship_state)
    state.hull_current = 1
    repair_event = resolver._repair_once(ship_state, state)
    assert repair_event is not None
    assert repair_event["repair_amount"] == 3


def test_engineer_increases_repair_uses_per_combat() -> None:
    ship_state = _ship_state(
        modules=[
            {"module_id": "weapon_energy_mk1"},
            {"module_id": "defense_shielded_mk1"},
            {"module_id": "combat_utility_repair_system_mk1"},
        ],
        crew=[_crew("engineer")],
    )
    state = resolver._create_initial_state_from_ship_state(ship_state)
    # Base is 2 uses per repair module; engineer adds +1.
    assert sum(state.repair_uses_remaining.values()) == 3


def test_focus_tag_modifies_only_selected_focus_action() -> None:
    enemy = _ship_state(hull_id="frg_t1_ant")
    no_crew = _ship_state()
    trigger_happy = _ship_state(crew=[_crew("pilot", ["crew:trigger_happy"])])

    reinforce = resolver.make_action_plan_selector(["Reinforce Shields"])
    focus_fire = resolver.make_action_plan_selector(["Focus Fire"])

    no_tag_reinforce = resolver.resolve_combat(
        world_seed=1004,
        combat_id="focus_none_reinforce",
        player_ship_state=copy.deepcopy(no_crew),
        enemy_ship_state=copy.deepcopy(enemy),
        player_action_selector=reinforce,
        enemy_action_selector=reinforce,
        max_rounds=1,
    )
    tag_reinforce = resolver.resolve_combat(
        world_seed=1004,
        combat_id="focus_tag_reinforce",
        player_ship_state=copy.deepcopy(trigger_happy),
        enemy_ship_state=copy.deepcopy(enemy),
        player_action_selector=reinforce,
        enemy_action_selector=reinforce,
        max_rounds=1,
    )
    assert tag_reinforce.log[0]["bands"]["player"]["weapon"] == no_tag_reinforce.log[0]["bands"]["player"]["weapon"]

    no_tag_focus = resolver.resolve_combat(
        world_seed=1005,
        combat_id="focus_none_focusfire",
        player_ship_state=copy.deepcopy(no_crew),
        enemy_ship_state=copy.deepcopy(enemy),
        player_action_selector=focus_fire,
        enemy_action_selector=focus_fire,
        max_rounds=1,
    )
    tag_focus = resolver.resolve_combat(
        world_seed=1005,
        combat_id="focus_tag_focusfire",
        player_ship_state=copy.deepcopy(trigger_happy),
        enemy_ship_state=copy.deepcopy(enemy),
        player_action_selector=focus_fire,
        enemy_action_selector=focus_fire,
        max_rounds=1,
    )
    assert tag_focus.log[0]["bands"]["player"]["weapon"] == max(
        0, no_tag_focus.log[0]["bands"]["player"]["weapon"] - 1
    )


def test_crew_combat_cap_respected() -> None:
    enemy = _ship_state(hull_id="frg_t1_ant")
    baseline = _ship_state()
    heavy_gunner = _ship_state(crew=[_crew("gunner") for _ in range(10)])
    selector = resolver.make_action_plan_selector(["Focus Fire"])

    base_result = resolver.resolve_combat(
        world_seed=1006,
        combat_id="cap_base",
        player_ship_state=baseline,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    capped_result = resolver.resolve_combat(
        world_seed=1006,
        combat_id="cap_heavy",
        player_ship_state=heavy_gunner,
        enemy_ship_state=enemy,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    delta = capped_result.log[0]["bands"]["player"]["weapon"] - base_result.log[0]["bands"]["player"]["weapon"]
    assert delta <= 3


def test_npc_ship_with_crew_receives_same_effects_as_player() -> None:
    player = _ship_state()
    enemy_base = _ship_state(hull_id="frg_t1_ant")
    enemy_crew = _ship_state(hull_id="frg_t1_ant", crew=[_crew("tactician")])
    selector = resolver.make_action_plan_selector(["Focus Fire"])

    base = resolver.resolve_combat(
        world_seed=1007,
        combat_id="npc_base",
        player_ship_state=player,
        enemy_ship_state=enemy_base,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    buffed = resolver.resolve_combat(
        world_seed=1007,
        combat_id="npc_buff",
        player_ship_state=player,
        enemy_ship_state=enemy_crew,
        player_action_selector=selector,
        enemy_action_selector=selector,
        max_rounds=1,
    )
    base_enemy_def = base.log[0]["bands"]["enemy"]["defense"]
    buff_enemy_def = buffed.log[0]["bands"]["enemy"]["defense"]
    base_delta = base.log[0]["attacks"]["player_to_enemy"]["band_delta"]
    buff_delta = buffed.log[0]["attacks"]["player_to_enemy"]["band_delta"]
    assert buff_enemy_def >= base_enemy_def
    assert buff_delta <= base_delta
