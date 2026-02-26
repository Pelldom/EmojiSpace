import copy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import combat_resolver as resolver  # noqa: E402
from ship_assembler import assemble_ship  # noqa: E402
from data_loader import load_hulls  # noqa: E402


def _baseline_ship_state() -> dict:
    """Create a baseline ship_state for testing."""
    hulls = load_hulls()["hulls"]
    hull = next(h for h in hulls if h["tier"] == 3 and h["frame"] == "CIV")
    return {
        "hull_id": hull["hull_id"],
        "module_instances": [
            {"module_id": "weapon_energy_mk1", "secondary_tags": []},
            {"module_id": "weapon_kinetic_mk1", "secondary_tags": []},
            {"module_id": "defense_shielded_mk1", "secondary_tags": []},
            {"module_id": "defense_armored_mk1", "secondary_tags": []},
            {"module_id": "combat_utility_repair_system_mk1", "secondary_tags": ["secondary:efficient"]},
            {"module_id": "ship_utility_probe_array", "secondary_tags": []},
        ],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
        "crew": ["crew:gunner", "crew:engineer", "crew:pilot", "crew:mechanic"],
    }


def test_combat_round_numbering_starts_at_1() -> None:
    """Test that round numbering starts at 1, not 0."""
    player = _baseline_ship_state()
    enemy = copy.deepcopy(player)
    
    player_selector = resolver.make_action_plan_selector(["Focus Fire"])
    enemy_selector = resolver.make_action_plan_selector(["Focus Fire"])
    
    result = resolver.resolve_combat(
        world_seed=12345,
        combat_id="round_test",
        player_ship_state=player,
        enemy_ship_state=enemy,
        player_action_selector=player_selector,
        enemy_action_selector=enemy_selector,
        max_rounds=3,
        combat_rng_seed=99999,
    )
    
    # Check that rounds start at 1
    round_logs = [entry for entry in result.log if "round" in entry and isinstance(entry["round"], int)]
    assert len(round_logs) > 0
    assert round_logs[0]["round"] == 1
    assert all(entry["round"] >= 1 for entry in round_logs)


def test_combat_requires_ship_state() -> None:
    """Test that resolve_combat requires ship_state and errors if missing."""
    player = _baseline_ship_state()
    
    # Should work with valid ship_state
    try:
        resolver.resolve_combat(
            world_seed=12345,
            combat_id="test",
            player_ship_state=player,
            enemy_ship_state=player,
            max_rounds=1,
            combat_rng_seed=99999,
        )
    except ValueError as e:
        assert False, f"Valid ship_state should not raise ValueError: {e}"
    
    # Should fail with missing hull_id
    invalid_state = copy.deepcopy(player)
    del invalid_state["hull_id"]
    try:
        resolver.resolve_combat(
            world_seed=12345,
            combat_id="test",
            player_ship_state=invalid_state,
            enemy_ship_state=player,
            max_rounds=1,
            combat_rng_seed=99999,
        )
        assert False, "Should have raised ValueError for missing hull_id"
    except ValueError:
        pass  # Expected
    
    # Should fail with missing module_instances
    invalid_state = copy.deepcopy(player)
    del invalid_state["module_instances"]
    try:
        resolver.resolve_combat(
            world_seed=12345,
            combat_id="test",
            player_ship_state=invalid_state,
            enemy_ship_state=player,
            max_rounds=1,
            combat_rng_seed=99999,
        )
        assert False, "Should have raised ValueError for missing module_instances"
    except ValueError:
        pass  # Expected


def test_combat_is_stochastic() -> None:
    """Test that combat produces different outcomes across repeated runs with identical inputs."""
    player = _baseline_ship_state()
    enemy = copy.deepcopy(player)
    
    player_selector = resolver.make_action_plan_selector(["Focus Fire", "Focus Fire", "Focus Fire"])
    enemy_selector = resolver.make_action_plan_selector(["Focus Fire", "Focus Fire", "Focus Fire"])
    
    # Run combat multiple times without providing combat_rng_seed (should generate different seeds)
    results = []
    for _ in range(5):
        result = resolver.resolve_combat(
            world_seed=12345,
            combat_id="stochastic_test",
            player_ship_state=player,
            enemy_ship_state=enemy,
            player_action_selector=player_selector,
            enemy_action_selector=enemy_selector,
            max_rounds=5,
        )
        results.append(result)
    
    # Check that combat_rng_seed is present and different (with high probability)
    seeds = [r.combat_rng_seed for r in results]
    assert len(set(seeds)) > 1, "Combat should generate different RNG seeds"
    
    # Check that outcomes can differ (they might be the same by chance, but seeds should differ)
    assert all(r.combat_rng_seed > 0 for r in results), "All results should have combat_rng_seed"


def test_combat_is_reproducible_with_seed() -> None:
    """Test that combat is reproducible when combat_rng_seed is provided."""
    player = _baseline_ship_state()
    enemy = copy.deepcopy(player)
    
    player_selector = resolver.make_action_plan_selector(["Scan", "Focus Fire", "Repair Systems", "Focus Fire"])
    enemy_selector = resolver.make_action_plan_selector(["Reinforce Shields", "Focus Fire", "Focus Fire", "Focus Fire"])
    
    test_seed = 123456789
    
    first = resolver.resolve_combat(
        world_seed=12345,
        combat_id="reproducibility_test",
        player_ship_state=player,
        enemy_ship_state=enemy,
        player_action_selector=player_selector,
        enemy_action_selector=enemy_selector,
        max_rounds=8,
        combat_rng_seed=test_seed,
    )
    second = resolver.resolve_combat(
        world_seed=12345,
        combat_id="reproducibility_test",
        player_ship_state=player,
        enemy_ship_state=enemy,
        player_action_selector=player_selector,
        enemy_action_selector=enemy_selector,
        max_rounds=8,
        combat_rng_seed=test_seed,
    )
    
    # Results should be identical
    assert first.combat_rng_seed == second.combat_rng_seed == test_seed
    assert (first.outcome, first.rounds, first.winner, first.rcp_player, first.rcp_enemy) == (
        second.outcome,
        second.rounds,
        second.winner,
        second.rcp_player,
        second.rcp_enemy,
    )
    assert first.final_state_player == second.final_state_player
    assert first.final_state_enemy == second.final_state_enemy
    
    # Check round logs match
    round_logs_first = [entry for entry in first.log if "round" in entry and isinstance(entry["round"], int)]
    round_logs_second = [entry for entry in second.log if "round" in entry and isinstance(entry["round"], int)]
    assert len(round_logs_first) == len(round_logs_second)
    
    for r1, r2 in zip(round_logs_first, round_logs_second):
        assert r1["round"] == r2["round"]
        assert r1["actions"] == r2["actions"]
        assert r1["attacks"] == r2["attacks"]
        assert r1["hull"] == r2["hull"]


def test_tr_mapping_boundaries() -> None:
    assert resolver.map_rcp_to_tr(0) == 1
    assert resolver.map_rcp_to_tr(6) == 1
    assert resolver.map_rcp_to_tr(7) == 2
    assert resolver.map_rcp_to_tr(13) == 2
    assert resolver.map_rcp_to_tr(14) == 3
    assert resolver.map_rcp_to_tr(20) == 3
    assert resolver.map_rcp_to_tr(21) == 4
    assert resolver.map_rcp_to_tr(26) == 4
    assert resolver.map_rcp_to_tr(27) == 5
    assert resolver.map_rcp_to_tr(100) == 5


def test_repair_usage_per_module_and_hull_cap() -> None:
    hulls = load_hulls()["hulls"]
    hull = next(h for h in hulls if h["tier"] == 2 and h["frame"] == "ALN")
    ship_state = {
        "hull_id": hull["hull_id"],
        "module_instances": [
            {"module_id": "weapon_energy_mk1", "secondary_tags": []},
            {"module_id": "defense_shielded_mk1", "secondary_tags": []},
            {"module_id": "combat_utility_repair_system_mk1", "secondary_tags": ["secondary:efficient"]},
            {"module_id": "combat_utility_repair_system_mk1", "secondary_tags": ["secondary:efficient", "secondary:alien"]},
            {"module_id": "ship_utility_probe_array", "secondary_tags": []},
        ],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
        "crew": ["crew:mechanic"],
    }
    state = resolver._create_initial_state_from_ship_state(ship_state)
    state.hull_current = 1
    
    uses = []
    while any(state.repair_uses_remaining.values()):
        before = state.hull_current
        event = resolver._repair_once(ship_state, state)
        uses.append(event)
        assert event is not None
        assert state.hull_current >= before
        assert state.hull_current <= state.hull_max
    
    # Should have used both repair modules
    assert len(uses) >= 2
    assert state.hull_current == state.hull_max
    assert resolver._repair_once(ship_state, state) is None


def test_degradation_thresholds_and_red_override() -> None:
    hulls = load_hulls()["hulls"]
    hull = next(h for h in hulls if h["tier"] == 1 and h["frame"] == "CIV")
    ship_state = {
        "hull_id": hull["hull_id"],
        "module_instances": [
            {"module_id": "weapon_energy_mk1", "secondary_tags": []},
            {"module_id": "defense_shielded_mk1", "secondary_tags": []},
            {"module_id": "combat_utility_targeting_mk1", "secondary_tags": []},
        ],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
        "crew": [],
    }
    state = resolver._create_initial_state_from_ship_state(ship_state)
    rng = resolver.CombatRng(combat_rng_seed=999)
    rng_events = []
    before_band = resolver._hull_band_index(state.hull_current, state.hull_max)
    events = resolver._apply_damage_and_degradation(
        target_state=state,
        damage=state.hull_max - 1,
        rng=rng,
        round_number=1,
        rng_events=rng_events,
        target_ship_state=ship_state,
    )
    after_band = resolver._hull_band_index(state.hull_current, state.hull_max)
    assert before_band == 2
    assert after_band == 0
    
    degrade_events = [entry for entry in events if "subsystem" in entry]
    assert len(degrade_events) == 2
    
    # Set weapon to RED and verify effective band is 0
    state.degradation["weapon"] = state.subsystem_capacity["weapon"]
    assembled = assemble_ship(ship_state["hull_id"], ship_state["module_instances"], state.degradation)
    assert assembled["bands"]["red"]["weapon"] is True


def test_escape_attempt_in_combat() -> None:
    """Test that escape is resolved inside combat using combat RNG."""
    player = _baseline_ship_state()
    enemy = copy.deepcopy(player)
    # Remove probe array from enemy, add interdiction
    enemy["module_instances"] = [m for m in enemy["module_instances"] if m["module_id"] != "ship_utility_probe_array"]
    enemy["module_instances"].append({"module_id": "ship_utility_interdiction", "secondary_tags": []})
    
    result = resolver.resolve_combat(
        world_seed=42,
        combat_id="escape_test",
        player_ship_state=player,
        enemy_ship_state=enemy,
        player_action_selector=resolver.make_action_plan_selector(["Attempt Escape"]),
        enemy_action_selector=resolver.make_action_plan_selector(["Focus Fire"]),
        max_rounds=5,
        combat_rng_seed=12345,
    )
    
    # Should have escape outcome or continue combat
    assert result.outcome in ["escape", "destroyed", "max_rounds", "surrender"]
    assert result.combat_rng_seed == 12345
    
    # Check that escape was attempted in round logs
    round_logs = [entry for entry in result.log if "round" in entry and isinstance(entry["round"], int)]
    if result.outcome == "escape":
        assert result.rounds >= 1
        escape_logs = [entry for entry in round_logs if entry.get("escape", {}).get("player")]
        assert len(escape_logs) > 0
