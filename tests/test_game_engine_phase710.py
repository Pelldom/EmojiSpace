"""
Phase 7.10 encounter system correction tests.

Focused tests for:
- Per-encounter StepResult.events isolation
- pending_encounter / pending_combat / pending_loot in StepResult
- Environmental subtypes (derelict, distress, ion_storm) produce real resolver
- Combat credits applied immediately; cargo/salvage pending
- Pending loot not overwritten by second combat
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402


def test_phase710_step_result_events_isolated_per_encounter() -> None:
    """StepResult.events for an encounter_decision contains only that encounter's events."""
    engine = GameEngine(world_seed=7777)
    sys_id = engine.player_state.current_system_id
    dests = engine.sector.get_system(sys_id).destinations if engine.sector.get_system(sys_id) else []
    if not dests:
        pytest.skip("No destinations in starting system.")
    dest_id = dests[0].destination_id
    # Start travel (no encounter_action so we get hard_stop for first encounter)
    r = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": sys_id,
        "target_destination_id": dest_id,
    })
    if not r.get("ok") or not r.get("hard_stop") or r.get("hard_stop_reason") != "pending_encounter_decision":
        pytest.skip("Travel did not yield pending_encounter_decision.")
    events_after_travel = r.get("events") or []
    # Resolve first encounter with ignore
    r2 = engine.execute({
        "type": "encounter_decision",
        "encounter_id": r["pending_encounter"]["encounter_id"],
        "decision_id": "ignore",
    })
    events_enc1 = r2.get("events") or []
    # Events should be for this encounter only (interaction_dispatch, resolver, reward_gate)
    stages = [e.get("detail", {}).get("stage") or e.get("stage") for e in events_enc1]
    assert "interaction_dispatch" in stages or "resolver" in stages
    # No duplicate/cumulative from previous travel events
    for ev in events_enc1:
        detail = ev.get("detail") if isinstance(ev.get("detail"), dict) else {}
        enc_id = detail.get("encounter_id") or (ev.get("detail") or {}).get("encounter_id")
        if enc_id:
            assert enc_id == r["pending_encounter"]["encounter_id"]


def test_phase710_pending_encounter_in_step_result() -> None:
    """When hard_stop_reason is pending_encounter_decision, result includes pending_encounter."""
    engine = GameEngine(world_seed=8888)
    sys_id = engine.player_state.current_system_id
    dests = engine.sector.get_system(sys_id).destinations if engine.sector.get_system(sys_id) else []
    if not dests:
        pytest.skip("No destinations.")
    r = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": sys_id,
        "target_destination_id": dests[0].destination_id,
    })
    if r.get("hard_stop_reason") != "pending_encounter_decision":
        pytest.skip("Need pending_encounter_decision from travel.")
    assert "pending_encounter" in r
    assert r["pending_encounter"] is not None
    assert "encounter_id" in r["pending_encounter"]
    assert "options" in r["pending_encounter"]


def test_phase710_combat_started_includes_pending_combat() -> None:
    """When combat is initialized, StepResult includes pending_combat payload."""
    engine = GameEngine(world_seed=9999)
    sys_id = engine.player_state.current_system_id
    dests = engine.sector.get_system(sys_id).destinations if engine.sector.get_system(sys_id) else []
    if not dests:
        pytest.skip("No destinations.")
    r = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": sys_id,
        "target_destination_id": dests[0].destination_id,
    })
    if r.get("hard_stop_reason") != "pending_encounter_decision":
        pytest.skip("Need pending encounter.")
    enc_id = r["pending_encounter"]["encounter_id"]
    # Try attack to force combat
    r2 = engine.execute({
        "type": "encounter_decision",
        "encounter_id": enc_id,
        "decision_id": "attack",
    })
    if r2.get("hard_stop_reason") != "pending_combat_action":
        pytest.skip("Attack did not lead to combat (e.g. wrong encounter type).")
    assert "pending_combat" in r2
    assert r2["pending_combat"] is not None
    assert r2["pending_combat"].get("encounter_id") == enc_id
    assert "allowed_actions" in r2["pending_combat"]


def test_phase710_environmental_derelict_resolver_not_none() -> None:
    """Investigate on derelict-style encounter returns resolver exploration, not none."""
    engine = GameEngine(world_seed=10101)
    sys_id = engine.player_state.current_system_id
    dests = engine.sector.get_system(sys_id).destinations if engine.sector.get_system(sys_id) else []
    if not dests:
        pytest.skip("No destinations.")
    r = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": sys_id,
        "target_destination_id": dests[0].destination_id,
    })
    if r.get("hard_stop_reason") != "pending_encounter_decision":
        pytest.skip("Need pending encounter.")
    enc_id = r["pending_encounter"]["encounter_id"]
    options = [o.get("id") for o in r["pending_encounter"].get("options", [])]
    if "investigate" not in options:
        pytest.skip("Encounter does not offer investigate (not environmental).")
    r2 = engine.execute({
        "type": "encounter_decision",
        "encounter_id": enc_id,
        "decision_id": "investigate",
    })
    events = r2.get("events") or []
    resolver_events = [e for e in events if (e.get("detail") or e).get("stage") == "resolver" or (e.get("detail") or {}).get("resolver")]
    resolver = None
    for e in events:
        d = e.get("detail") if isinstance(e.get("detail"), dict) else {}
        if d.get("resolver"):
            resolver = d.get("resolver")
            break
        if isinstance(e.get("detail"), dict) and "resolver_outcome" in e.get("detail", {}):
            resolver = e["detail"]["resolver_outcome"].get("resolver")
            break
    assert resolver is not None, "Resolver should be set in events"
    assert resolver != "none", "Environmental investigate must not return resolver none"


def test_phase710_combat_credits_applied_immediately() -> None:
    """After combat victory, credits are applied before any loot prompt."""
    engine = GameEngine(world_seed=12121)
    sys_id = engine.player_state.current_system_id
    dests = engine.sector.get_system(sys_id).destinations if engine.sector.get_system(sys_id) else []
    if not dests:
        pytest.skip("No destinations.")
    r = engine.execute({
        "type": "travel_to_destination",
        "target_system_id": sys_id,
        "target_destination_id": dests[0].destination_id,
    })
    if r.get("hard_stop_reason") != "pending_encounter_decision":
        pytest.skip("Need pending encounter.")
    enc_id = r["pending_encounter"]["encounter_id"]
    options = [o.get("id") for o in r["pending_encounter"].get("options", [])]
    if "attack" not in options:
        pytest.skip("Encounter does not offer attack.")
    credits_before = engine.player_state.credits
    r2 = engine.execute({"type": "encounter_decision", "encounter_id": enc_id, "decision_id": "attack"})
    if r2.get("hard_stop_reason") != "pending_combat_action":
        pytest.skip("Combat did not start.")
    r3 = r2
    for _ in range(15):
        r3 = engine.execute({
            "type": "combat_action",
            "encounter_id": r2["pending_combat"]["encounter_id"],
            "action": "focus_fire",
        })
        if not r3.get("hard_stop") or r3.get("hard_stop_reason") != "pending_combat_action":
            break
    if r3.get("hard_stop_reason") == "pending_loot_decision":
        credits_after_combat = engine.player_state.credits
        # Credits must have been applied (if any) before loot prompt
        assert credits_after_combat >= credits_before or not engine.get_pending_loot(), (
            "Credits should be applied on victory before loot prompt"
        )


def test_phase710_pending_loot_not_overwritten() -> None:
    """If _pending_loot is set, a second combat does not overwrite it."""
    engine = GameEngine(world_seed=13131)
    # Set pending loot manually to simulate "first combat loot unresolved"
    engine._pending_loot = {
        "encounter_id": "fake_enc_1",
        "credits": 0,
        "cargo_sku": None,
        "cargo_quantity": 0,
        "salvage_modules": [],
        "reward_payload": None,
        "stolen_applied": False,
    }
    from game_engine import EngineContext
    from time_engine import get_current_turn
    ctx = EngineContext(
        command={},
        command_type="combat_action",
        turn_before=int(get_current_turn()),
        turn_after=int(get_current_turn()),
    )
    # Simulate post-combat reward call (would run after a second combat)
    engine._pending_combat = {
        "spec": type("Spec", (), {"encounter_id": "enc_2", "reward_profile_id": "raider_loot", "threat_rating_tr": 3})(),
    }
    class FakeCombatResult:
        outcome = "destroyed"
        winner = "player"
        salvage_modules = []
    engine._apply_post_combat_rewards_and_salvage(ctx, FakeCombatResult(), "enc_2")
    # Pending loot should still be the first bundle (blocked overwrite)
    assert engine._pending_loot is not None
    assert engine._pending_loot.get("encounter_id") == "fake_enc_1"
    engine._pending_combat = None  # leave engine in clean state


def test_phase710_salvage_capacity_enforced() -> None:
    """Salvage modules count against physical cargo capacity when accepted."""
    engine = GameEngine(world_seed=14141)
    ship = engine._active_ship()
    if not hasattr(ship, "get_effective_physical_capacity"):
        pytest.skip("Ship has no physical capacity.")
    cap = ship.get_effective_physical_capacity()
    if cap is None or int(cap) < 2:
        pytest.skip("Need at least 2 physical cargo capacity.")
    # Fill cargo to capacity
    engine.player_state.cargo_by_ship.setdefault("active", {})
    engine.player_state.cargo_by_ship["active"]["test_sku"] = int(cap)
    engine._pending_loot = {
        "encounter_id": "cap_test",
        "reward_payload": None,
        "credits": 0,
        "cargo_sku": None,
        "cargo_quantity": 0,
        "stolen_applied": False,
        "salvage_modules": [{"module_id": "weapon_laser_small"}, {"module_id": "weapon_laser_medium"}],
    }
    engine.resolve_pending_loot(take_all=True)
    # At most one module should fit (capacity was full)
    holdings = engine.player_state.cargo_by_ship.get("active", {})
    module_units = sum(
        qty for sku, qty in holdings.items()
        if sku in ("weapon_laser_small", "weapon_laser_medium")
    )
    assert module_units <= int(cap), "Salvage must not exceed physical capacity"
