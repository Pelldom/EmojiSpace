import copy
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import combat_resolver as resolver  # noqa: E402
from data_loader import load_hulls  # noqa: E402


def _baseline_ship_state() -> dict:
    """Create a baseline ship_state for escape ordering tests."""
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


def test_player_escape_prevents_damage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Player escape success should end combat before any damage is applied."""
    player_ship = _baseline_ship_state()
    enemy_ship = copy.deepcopy(player_ship)

    player_state = resolver._create_initial_state_from_ship_state(player_ship)
    enemy_state = resolver._create_initial_state_from_ship_state(enemy_ship)

    initial_player_hull = player_state.hull_current
    initial_enemy_hull = enemy_state.hull_current

    def fake_escape_in_combat(*args, **kwargs) -> dict:
        return {
            "escaped": True,
            "roll": 42,
            "threshold": 50,
            "engine_delta": 1,
            "escape_modifier": 0,
            "pursuer_modifier": 0,
            "final_delta": 1,
        }

    monkeypatch.setattr(resolver, "_escape_attempt_in_combat", fake_escape_in_combat)

    result = resolver.resolve_combat_round(
        combat_rng_seed=12345,
        round_number=1,
        player_state=player_state,
        enemy_state=enemy_state,
        player_action="Attempt Escape",
        enemy_action="Focus Fire",
        player_ship_state=player_ship,
        enemy_ship_state=enemy_ship,
        system_id="test-system",
    )

    assert result["combat_ended"] is True
    assert result["outcome"] == "escape"
    # No damage should have been applied
    assert player_state.hull_current == initial_player_hull
    assert enemy_state.hull_current == initial_enemy_hull


def test_mutual_escape_auto_success() -> None:
    """Mutual Attempt Escape should auto-disengage with no damage."""
    player_ship = _baseline_ship_state()
    enemy_ship = copy.deepcopy(player_ship)

    player_state = resolver._create_initial_state_from_ship_state(player_ship)
    enemy_state = resolver._create_initial_state_from_ship_state(enemy_ship)

    initial_player_hull = player_state.hull_current
    initial_enemy_hull = enemy_state.hull_current

    result = resolver.resolve_combat_round(
        combat_rng_seed=12345,
        round_number=1,
        player_state=player_state,
        enemy_state=enemy_state,
        player_action="Attempt Escape",
        enemy_action="Attempt Escape",
        player_ship_state=player_ship,
        enemy_ship_state=enemy_ship,
        system_id="test-system",
    )

    assert result["combat_ended"] is True
    assert result["outcome"] == "escape"
    summary = result["round_summary"]
    assert summary.get("escape") == "mutual"
    # No damage should have been applied
    assert player_state.hull_current == initial_player_hull
    assert enemy_state.hull_current == initial_enemy_hull


def test_failed_escape_still_allows_damage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Failed escape attempt should still allow normal damage resolution."""
    player_ship = _baseline_ship_state()
    enemy_ship = copy.deepcopy(player_ship)

    player_state = resolver._create_initial_state_from_ship_state(player_ship)
    enemy_state = resolver._create_initial_state_from_ship_state(enemy_ship)

    initial_player_hull = player_state.hull_current
    initial_enemy_hull = enemy_state.hull_current

    def fake_escape_fail(*args, **kwargs) -> dict:
        return {
            "escaped": False,
            "roll": 99,
            "threshold": 100,
            "engine_delta": 0,
            "escape_modifier": 0,
            "pursuer_modifier": 0,
            "final_delta": 0,
        }

    def fake_resolve_attack(
        attacker_side,
        defender_side,
        attacker_weapon,
        defender_defense,
        defender_action,
        rng,
        round_number,
        rng_events,
    ) -> dict:
        # Force a small, deterministic amount of damage
        return {
            "band_delta": 0,
            "damage_roll": 5,
            "mitigation_roll": 0,
            "damage": 5,
        }

    monkeypatch.setattr(resolver, "_escape_attempt_in_combat", fake_escape_fail)
    monkeypatch.setattr(resolver, "_resolve_attack", fake_resolve_attack)

    result = resolver.resolve_combat_round(
        combat_rng_seed=12345,
        round_number=1,
        player_state=player_state,
        enemy_state=enemy_state,
        player_action="Attempt Escape",
        enemy_action="Focus Fire",
        player_ship_state=player_ship,
        enemy_ship_state=enemy_ship,
        system_id="test-system",
    )

    assert result["combat_ended"] is False
    # At least one side should have taken damage
    assert (
        player_state.hull_current < initial_player_hull
        or enemy_state.hull_current < initial_enemy_hull
    )

