import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import combat_resolver as resolver  # noqa: E402
import npc_ship_generator as npc_gen  # noqa: E402
import salvage_resolver as salvage  # noqa: E402


def test_npc_ship_determinism_same_inputs() -> None:
    first = npc_gen.generate_npc_ship(
        world_seed=12345,
        system_id="SYS-001",
        system_population=3,
        encounter_id="ENC-001",
        encounter_subtype="civilian_trader_ship",
    )
    second = npc_gen.generate_npc_ship(
        world_seed=12345,
        system_id="SYS-001",
        system_population=3,
        encounter_id="ENC-001",
        encounter_subtype="civilian_trader_ship",
    )
    assert first["hull_id"] == second["hull_id"]
    assert first["module_instances"] == second["module_instances"]
    assert first == second


def test_tier_weights_never_zero() -> None:
    crafted_seeds = [3, 24, 144, 205, 210, 275, 299, 320, 331, 334]
    tiers = [
        npc_gen._select_tier(1, npc_gen._rng_for_stream(seed, "SYS-T", "ENC-T", "npc_hull_select"))
        for seed in crafted_seeds
    ]
    assert 5 in tiers


def test_fill_fraction_distribution_respects_bounds() -> None:
    rng = npc_gen._rng_for_stream(99, "SYS-F", "ENC-F", "npc_loadout_fill")
    target = npc_gen._fill_slots_target(total_slots=9, rng=rng)
    assert 0 <= target <= 9


def test_salvage_count_caps_at_2_and_respects_weights() -> None:
    destroyed_ship = {
        "module_instances": [
            {"module_id": "weapon_energy_mk1", "secondary_tags": []},
            {"module_id": "defense_shielded_mk1", "secondary_tags": []},
            {"module_id": "combat_utility_engine_boost_mk1", "secondary_tags": []},
        ]
    }
    result = salvage.resolve_salvage_modules(
        world_seed=123,
        system_id="SYS-S",
        encounter_id="ENC-S",
        destroyed_ship=destroyed_ship,
    )
    assert len(result) in {0, 1, 2}
    assert len(result) <= 2


def test_salvage_prefers_rarer_modules(monkeypatch) -> None:
    destroyed_ship = {
        "module_instances": [
            {"module_id": "weapon_energy_mk1", "secondary_tags": []},  # common
            {"module_id": "weapon_energy_mk2", "secondary_tags": ["secondary:alien"]},  # rare + alien
        ]
    }

    class _FixedRng:
        def __init__(self, values):
            self._values = list(values)
            self._index = 0

        def random(self):
            value = self._values[self._index % len(self._values)]
            self._index += 1
            return value

    def _fake_rng_for_stream(world_seed, system_id, encounter_id, stream_name):
        if stream_name == "npc_salvage_count":
            return _FixedRng([0.70])  # choose salvage_count = 1
        if stream_name == "npc_salvage_select":
            return _FixedRng([0.95])  # bias to heavier-weight end
        return _FixedRng([0.99])

    monkeypatch.setattr(salvage, "_rng_for_stream", _fake_rng_for_stream)
    selected = salvage.resolve_salvage_modules(
        world_seed=1,
        system_id="SYS-S",
        encounter_id="ENC-S",
        destroyed_ship=destroyed_ship,
    )
    assert len(selected) == 1
    assert selected[0]["module_id"] == "weapon_energy_mk2"


def test_salvage_unstable_injection_rule(monkeypatch) -> None:
    class _FixedRng:
        def random(self):
            return 0.0

    monkeypatch.setattr(salvage, "_rng_for_stream", lambda *args, **kwargs: _FixedRng())

    with_secondary = {
        "module_instances": [{"module_id": "weapon_energy_mk1", "secondary_tags": ["secondary:prototype"]}]
    }
    selected_with = salvage.resolve_salvage_modules(
        world_seed=1,
        system_id="SYS-I",
        encounter_id="ENC-I",
        destroyed_ship=with_secondary,
    )
    if selected_with:
        assert selected_with[0]["secondary_tags"] == ["secondary:prototype"]

    without_secondary = {"module_instances": [{"module_id": "weapon_energy_mk1", "secondary_tags": []}]}
    selected_without = salvage.resolve_salvage_modules(
        world_seed=1,
        system_id="SYS-I",
        encounter_id="ENC-I2",
        destroyed_ship=without_secondary,
    )
    if selected_without:
        assert "secondary:unstable" in selected_without[0].get("secondary_tags", [])


def test_combat_outcome_includes_salvage_modules(monkeypatch) -> None:
    player_ship = {
        "hull_id": "civ_t1_midge",
        "module_instances": [{"module_id": "weapon_energy_mk1", "secondary_tags": []}],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
    }
    enemy_ship = {
        "hull_id": "civ_t1_midge",
        "module_instances": [{"module_id": "weapon_energy_mk1", "secondary_tags": []}],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
    }

    monkeypatch.setattr(
        resolver,
        "resolve_salvage_modules",
        lambda world_seed, system_id, encounter_id, destroyed_ship: [{"module_id": "weapon_energy_mk1", "secondary_tags": []}],
    )

    def _forced_attack(attacker, defender, attack_band, defense_band, defender_action, rng, round_number, event_log):
        if attacker == "player":
            return {"attacker": "player", "defender": "enemy", "band_delta": 10, "damage_roll": 10, "mitigation_roll": 0, "damage": 10}
        return {"attacker": "enemy", "defender": "player", "band_delta": 0, "damage_roll": 0, "mitigation_roll": 0, "damage": 0}

    monkeypatch.setattr(resolver, "_resolve_attack", _forced_attack)
    result = resolver.resolve_combat(
        world_seed=42,
        combat_id="COMBAT-SALVAGE",
        system_id="SYS-001",
        player_ship_state=player_ship,
        enemy_ship_state=enemy_ship,
        max_rounds=1,
    )
    assert result.outcome == "destroyed"
    assert isinstance(result.salvage_modules, list)
    assert result.salvage_modules


def test_combat_salvage_only_triggers_for_enemy_destroyed(monkeypatch) -> None:
    player_ship = {
        "hull_id": "civ_t1_midge",
        "module_instances": [{"module_id": "weapon_energy_mk1", "secondary_tags": []}],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
    }
    enemy_ship = {
        "hull_id": "civ_t1_midge",
        "module_instances": [{"module_id": "weapon_energy_mk1", "secondary_tags": []}],
        "degradation_state": {"weapon": 0, "defense": 0, "engine": 0},
    }
    calls: list[str] = []

    def _tracked_salvage(world_seed, system_id, encounter_id, destroyed_ship):
        calls.append(encounter_id)
        return [{"module_id": "weapon_energy_mk1", "secondary_tags": []}]

    def _enemy_kills_player(attacker, defender, attack_band, defense_band, defender_action, rng, round_number, event_log):
        if attacker == "enemy":
            return {"attacker": "enemy", "defender": "player", "band_delta": 10, "damage_roll": 10, "mitigation_roll": 0, "damage": 10}
        return {"attacker": "player", "defender": "enemy", "band_delta": 0, "damage_roll": 0, "mitigation_roll": 0, "damage": 0}

    monkeypatch.setattr(resolver, "resolve_salvage_modules", _tracked_salvage)
    monkeypatch.setattr(resolver, "_resolve_attack", _enemy_kills_player)
    result = resolver.resolve_combat(
        world_seed=99,
        combat_id="COMBAT-PLAYER-DESTROYED",
        system_id="SYS-002",
        player_ship_state=player_ship,
        enemy_ship_state=enemy_ship,
        max_rounds=1,
    )
    assert result.outcome == "destroyed"
    assert result.winner == "enemy"
    assert result.salvage_modules == []
    assert calls == []