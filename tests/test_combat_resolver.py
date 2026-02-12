import copy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import combat_resolver as resolver  # noqa: E402


def _baseline_loadout() -> resolver.ShipLoadout:
    return resolver.ShipLoadout(
        name="Baseline",
        tier=3,
        frame="CIV",
        weapon_slots=2,
        defense_slots=2,
        utility_slots=2,
        untyped_slots=0,
        modules=[
            resolver.ModuleDef("w1", "weapon", {"combat:weapon_energy"}),
            resolver.ModuleDef("w2", "weapon", {"combat:weapon_kinetic"}),
            resolver.ModuleDef("d1", "defense", {"combat:defense_shielded"}),
            resolver.ModuleDef("d2", "defense", {"combat:defense_armored"}),
            resolver.ModuleDef("u1", "utility", {"combat:utility_repair_system"}, secondary="secondary:efficient"),
            resolver.ModuleDef("u2", "utility", {"ship:utility_probe_array"}),
        ],
        crew=["crew:gunner", "crew:engineer", "crew:pilot", "crew:mechanic"],
        seed_salt="baseline",
    )


def test_combat_determinism_identical_inputs_identical_result() -> None:
    player = _baseline_loadout()
    enemy = copy.deepcopy(player)
    enemy.name = "Enemy"
    enemy.seed_salt = "enemy"

    player_selector = resolver.make_action_plan_selector(["Scan", "Focus Fire", "Repair Systems", "Focus Fire"])
    enemy_selector = resolver.make_action_plan_selector(["Reinforce Shields", "Focus Fire", "Focus Fire", "Focus Fire"])

    first = resolver.resolve_combat(
        world_seed=12345,
        combat_id="determinism_case",
        player_loadout=player,
        enemy_loadout=enemy,
        player_action_selector=player_selector,
        enemy_action_selector=enemy_selector,
        max_rounds=8,
    )
    second = resolver.resolve_combat(
        world_seed=12345,
        combat_id="determinism_case",
        player_loadout=player,
        enemy_loadout=enemy,
        player_action_selector=player_selector,
        enemy_action_selector=enemy_selector,
        max_rounds=8,
    )

    assert (first.outcome, first.rounds, first.winner, first.rcp_player, first.rcp_enemy) == (
        second.outcome,
        second.rounds,
        second.winner,
        second.rcp_player,
        second.rcp_enemy,
    )
    assert first.final_state_player == second.final_state_player
    assert first.final_state_enemy == second.final_state_enemy
    key_fields_first = [
        {
            "round": entry["round"],
            "actions": entry["actions"],
            "attacks": entry["attacks"],
            "hull": entry["hull"],
            "escape": entry["escape"],
            "scan": entry["scan"],
            "rng_events": entry["rng_events"],
        }
        for entry in first.log
    ]
    key_fields_second = [
        {
            "round": entry["round"],
            "actions": entry["actions"],
            "attacks": entry["attacks"],
            "hull": entry["hull"],
            "escape": entry["escape"],
            "scan": entry["scan"],
            "rng_events": entry["rng_events"],
        }
        for entry in second.log
    ]
    assert key_fields_first == key_fields_second


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
    loadout = resolver.ShipLoadout(
        name="Repair Tester",
        tier=2,
        frame="ALN",
        weapon_slots=1,
        defense_slots=1,
        utility_slots=3,
        untyped_slots=0,
        modules=[
            resolver.ModuleDef("w1", "weapon", {"combat:weapon_energy"}),
            resolver.ModuleDef("d1", "defense", {"combat:defense_shielded"}),
            resolver.ModuleDef("r1", "utility", {"combat:utility_repair_system"}, secondary={"secondary:efficient"}),
            resolver.ModuleDef(
                "r2",
                "utility",
                {"combat:utility_repair_system"},
                secondary={"secondary:efficient", "secondary:alien"},
            ),
            resolver.ModuleDef("u1", "utility", {"combat:utility_cloak"}),
        ],
        crew=["crew:mechanic"],
    )
    state = resolver.create_initial_state(loadout)
    state.hull_current = 1

    uses = []
    while any(state.repair_uses_remaining.values()):
        before = state.hull_current
        event = resolver._repair_once(loadout, state)
        uses.append(event)
        assert event is not None
        assert state.hull_current >= before
        assert state.hull_current <= state.hull_max

    assert sum(1 for entry in uses if entry["module_id"] == "r1") == 2
    assert sum(1 for entry in uses if entry["module_id"] == "r2") == 2
    assert state.hull_current == state.hull_max
    assert resolver._repair_once(loadout, state) is None


def test_degradation_thresholds_and_red_override() -> None:
    loadout = resolver.ShipLoadout(
        name="Red Override",
        tier=1,
        frame="CIV",
        weapon_slots=1,
        defense_slots=1,
        utility_slots=1,
        untyped_slots=0,
        modules=[
            resolver.ModuleDef("w1", "weapon", {"combat:weapon_energy"}),
            resolver.ModuleDef("d1", "defense", {"combat:defense_shielded"}),
            resolver.ModuleDef("u1", "utility", {"combat:utility_targeting"}),
        ],
        crew=[],
    )
    state = resolver.create_initial_state(loadout)
    rng = resolver.CombatRng(world_seed=999, salt="degrade_case")
    rng_events = []
    before_band = resolver._hull_band_index(state.hull_current, state.hull_max)
    events = resolver._apply_damage_and_degradation(state, damage=state.hull_max - 1, rng=rng, round_number=1, rng_events=rng_events)
    after_band = resolver._hull_band_index(state.hull_current, state.hull_max)
    assert before_band == 2
    assert after_band == 0

    degrade_events = [entry for entry in events if "subsystem" in entry]
    assert len(degrade_events) == 2

    state.degradation["weapon"] = state.subsystem_capacity["weapon"]
    effective_weapon, _ = resolver._effective_band(
        loadout=loadout,
        state=state,
        subsystem="weapon",
        action="Focus Fire",
        opponent_loadout=loadout,
        for_attack=True,
    )
    assert effective_weapon == 0


def test_escape_attempt_uses_pursuit_resolver_and_ends_combat(monkeypatch) -> None:
    calls = []

    class FakePursuit:
        def __init__(self) -> None:
            self.escaped = True
            self.roll = 0.01
            self.threshold = 0.99
            self.log = {"seed": "fake"}

    def fake_resolve_pursuit(encounter_id, world_seed, pursuer_ship, pursued_ship):
        calls.append(
            {
                "encounter_id": encounter_id,
                "world_seed": world_seed,
                "pursuer_ship": pursuer_ship,
                "pursued_ship": pursued_ship,
            }
        )
        return FakePursuit()

    monkeypatch.setattr(resolver, "resolve_pursuit", fake_resolve_pursuit)

    player = _baseline_loadout()
    enemy = _baseline_loadout()
    enemy.name = "Enemy"
    enemy.modules = [entry for entry in enemy.modules if "ship:utility_probe_array" not in entry.tags]
    enemy.modules.append(resolver.ModuleDef("u99", "utility", {"ship:utility_interdiction"}))
    result = resolver.resolve_combat(
        world_seed=42,
        combat_id="escape_case",
        player_loadout=player,
        enemy_loadout=enemy,
        player_action_selector=resolver.make_action_plan_selector(["Attempt Escape"]),
        enemy_action_selector=resolver.make_action_plan_selector(["Focus Fire"]),
        max_rounds=5,
    )

    assert result.outcome == "escape"
    assert result.rounds == 1
    assert calls
    assert calls[0]["world_seed"] == "42"
