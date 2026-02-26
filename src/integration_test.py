import traceback
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from data_catalog import load_data_catalog
from datanet_entry import DataNetEntry
from datanet_feed import assemble_datanet_feed
from mission_entity import MissionEntity
from mission_factory import create_mission
from mission_manager import MissionManager
from end_game_evaluator import evaluate_end_game
from npc_entity import NPCEntity, NPCPersistenceTier
from npc_placement import resolve_npcs_for_location
from npc_registry import NPCRegistry
from player_state import PlayerState
from prose_generator import generate_prose
from ship_entity import ShipEntity
from time_engine import (
    _reset_time_state_for_test,
    _set_player_action_context,
    advance_time,
    get_current_date,
    get_current_turn,
)
from warehouse_entity import WarehouseEntity
from world_generator import WorldGenerator
from government_registry import GovernmentRegistry


class ResultCollector:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0

    def record(self, status: str) -> None:
        self.total += 1
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "SKIPPED":
            self.skipped += 1


def _print_group(title: str) -> None:
    print("")
    print(f"== {title} ==")


def _print_result(label: str, status: str, detail: str | None = None) -> None:
    if detail:
        print(f"{status}: {label} -> {detail}")
    else:
        print(f"{status}: {label}")


def _run_test(label: str, fn, collector: ResultCollector) -> None:
    try:
        fn()
        _print_result(label, "PASS")
        collector.record("PASS")
    except SkipTest as exc:
        _print_result(label, "SKIPPED", str(exc))
        collector.record("SKIPPED")
    except Exception as exc:  # noqa: BLE001
        summary = f"{type(exc).__name__}: {exc}"
        _print_result(label, "FAIL", summary)
        print("  Trace:", traceback.format_exc().splitlines()[-1])
        collector.record("FAIL")


class SkipTest(Exception):
    pass


def _serialize_world(galaxy) -> Dict[str, Any]:
    systems: List[Dict[str, Any]] = []
    for system in galaxy.systems:
        destinations: List[Dict[str, Any]] = []
        for destination in system.destinations:
            destinations.append(
                {
                    "destination_id": destination.destination_id,
                    "destination_type": destination.destination_type,
                    "population": destination.population,
                    "primary_economy_id": destination.primary_economy_id,
                    "secondary_economy_ids": list(destination.secondary_economy_ids),
                    "locations": [loc.location_type for loc in destination.locations],
                }
            )
        systems.append(
            {
                "system_id": system.system_id,
                "population": system.population,
                "government_id": system.government_id,
                "destinations": destinations,
            }
        )
    return {"systems": systems}


def world_generation_tests(collector: ResultCollector) -> None:
    _print_group("WORLD GENERATION TESTS")

    def test_world_determinism() -> None:
        catalog = load_data_catalog()
        registry = GovernmentRegistry.from_file(Path(__file__).resolve().parents[1] / "data" / "governments.json")
        generator = WorldGenerator(
            seed=12345,
            system_count=5,
            government_ids=registry.government_ids(),
            catalog=catalog,
            logger=None,
        )
        galaxy_a = generator.generate()
        galaxy_b = generator.generate()
        assert galaxy_a.systems
        assert _serialize_world(galaxy_a) == _serialize_world(galaxy_b)

    def test_system_fields_present() -> None:
        catalog = load_data_catalog()
        registry = GovernmentRegistry.from_file(Path(__file__).resolve().parents[1] / "data" / "governments.json")
        generator = WorldGenerator(
            seed=12345,
            system_count=5,
            government_ids=registry.government_ids(),
            catalog=catalog,
            logger=None,
        )
        galaxy = generator.generate()
        for system in galaxy.systems:
            assert system.system_id
            assert system.population >= 1
            assert system.government_id

    _run_test("deterministic world generation", test_world_determinism, collector)
    _run_test("system fields present", test_system_fields_present, collector)


def destination_generation_tests(collector: ResultCollector) -> None:
    _print_group("DESTINATION GENERATION TESTS")

    def test_destination_fields() -> None:
        catalog = load_data_catalog()
        registry = GovernmentRegistry.from_file(Path(__file__).resolve().parents[1] / "data" / "governments.json")
        generator = WorldGenerator(
            seed=12345,
            system_count=5,
            government_ids=registry.government_ids(),
            catalog=catalog,
            logger=None,
        )
        galaxy = generator.generate()
        for system in galaxy.systems:
            for destination in system.destinations:
                assert destination.destination_id
                assert destination.system_id == system.system_id
                assert destination.destination_type in {"planet", "station", "asteroid_field", "contact"}

    def test_destination_determinism() -> None:
        catalog = load_data_catalog()
        registry = GovernmentRegistry.from_file(Path(__file__).resolve().parents[1] / "data" / "governments.json")
        generator = WorldGenerator(
            seed=12345,
            system_count=5,
            government_ids=registry.government_ids(),
            catalog=catalog,
            logger=None,
        )
        galaxy_a = generator.generate()
        galaxy_b = generator.generate()
        assert _serialize_world(galaxy_a) == _serialize_world(galaxy_b)

    _run_test("destination fields present", test_destination_fields, collector)
    _run_test("destination determinism", test_destination_determinism, collector)


def location_availability_tests(collector: ResultCollector) -> None:
    _print_group("LOCATION AVAILABILITY TESTS")

    def test_location_placement_and_types() -> None:
        catalog = load_data_catalog()
        registry = GovernmentRegistry.from_file(Path(__file__).resolve().parents[1] / "data" / "governments.json")
        generator = WorldGenerator(
            seed=12345,
            system_count=5,
            government_ids=registry.government_ids(),
            catalog=catalog,
            logger=None,
        )
        galaxy = generator.generate()
        availability_path = Path(__file__).resolve().parents[1] / "data" / "location_availability.json"
        availability = __import__("json").loads(availability_path.read_text(encoding="utf-8"))
        allowed_types = set(availability.keys()) | {"datanet"}
        seen_ids = set()
        for system in galaxy.systems:
            for destination in system.destinations:
                for location in destination.locations:
                    assert location.location_type in allowed_types
                    assert location.location_id not in seen_ids
                    seen_ids.add(location.location_id)
        if not seen_ids:
            raise AssertionError("No locations were generated.")

    _run_test("location types and unique ids", test_location_placement_and_types, collector)


def time_engine_tests(collector: ResultCollector) -> None:
    _print_group("TIME ENGINE TESTS")

    def test_time_progression() -> None:
        _reset_time_state_for_test()
        assert get_current_turn() == 0
        assert get_current_date() == "2200.0.0"
        _set_player_action_context(True)
        try:
            result = advance_time(2, "test")
        finally:
            _set_player_action_context(False)
        assert result.current_turn == 2

    _run_test("deterministic time progression", test_time_progression, collector)


def core_entity_tests(collector: ResultCollector) -> None:
    _print_group("CORE ENTITY TESTS")

    def test_player_serialization() -> None:
        player = PlayerState(current_system_id="SYS-1")
        payload = player.to_dict()
        restored = PlayerState.from_dict(payload)
        assert payload == restored.to_dict()

    def test_ship_serialization() -> None:
        ship = ShipEntity()
        payload = ship.to_dict()
        restored = ShipEntity.from_dict(payload)
        assert payload == restored.to_dict()

    def test_warehouse_serialization() -> None:
        warehouse = WarehouseEntity()
        warehouse.add_goods("sku", 2)
        payload = warehouse.to_dict()
        restored = WarehouseEntity.from_dict(payload)
        assert payload == restored.to_dict()

    _run_test("player entity serialize/deserialize", test_player_serialization, collector)
    _run_test("ship entity serialize/deserialize", test_ship_serialization, collector)
    _run_test("warehouse entity serialize/deserialize", test_warehouse_serialization, collector)


def npc_system_tests(collector: ResultCollector) -> None:
    _print_group("NPC SYSTEM TESTS")

    def test_npc_serialization() -> None:
        npc = NPCEntity(npc_id="NPC-1", persistence_tier=NPCPersistenceTier.TIER_2, display_name="Test")
        payload = npc.to_dict()
        restored = NPCEntity.from_dict(payload)
        assert payload == restored.to_dict()

    def test_registry_add_remove() -> None:
        registry = NPCRegistry()
        npc = NPCEntity(npc_id="NPC-2", persistence_tier=NPCPersistenceTier.TIER_2, current_location_id="LOC-1")
        registry.add(npc)
        assert registry.get("NPC-2") is not None
        assert registry.list_by_location("LOC-1")
        registry.remove("NPC-2")
        assert registry.get("NPC-2") is None

    def test_placement_required_npcs() -> None:
        registry = NPCRegistry()
        bar_npcs = resolve_npcs_for_location(
            location_id="LOC-BAR", location_type="bar", system_id="SYS-1", registry=registry
        )
        admin_npcs = resolve_npcs_for_location(
            location_id="LOC-ADMIN", location_type="administration", system_id="SYS-1", registry=registry
        )
        assert len(bar_npcs) == 1
        assert len(admin_npcs) == 1

    _run_test("npc serialization", test_npc_serialization, collector)
    _run_test("npc registry add/remove", test_registry_add_remove, collector)
    _run_test("npc placement required", test_placement_required_npcs, collector)


def datanet_prose_tests(collector: ResultCollector) -> None:
    _print_group("DATANET & PROSE TESTS")

    def test_prose_determinism() -> None:
        text_a = generate_prose(
            risk_tier="low", reputation_band="neutral", government_tone="democratic", npc_role_tags=["bartender"]
        )
        text_b = generate_prose(
            risk_tier="low", reputation_band="neutral", government_tone="democratic", npc_role_tags=["bartender"]
        )
        assert text_a == text_b

    def test_datanet_serialization() -> None:
        entry = DataNetEntry(datanet_id="DN-1", prose_text="Calm report.", related_ids=["SYS-1"])
        payload = entry.to_dict()
        restored = DataNetEntry.from_dict(payload)
        assert payload == restored.to_dict()

    def test_feed_assembly() -> None:
        entries = [
            DataNetEntry(
                datanet_id="DN-1",
                scope="system",
                truth_band="accurate",
                censorship_level="none",
                related_ids=["SYS-1"],
                prose_text="Calm report.",
                is_red_herring=False,
            ),
            DataNetEntry(
                datanet_id="DN-2",
                scope="system",
                truth_band="false",
                censorship_level="heavy",
                related_ids=["SYS-1"],
                prose_text="False report.",
                is_red_herring=True,
            ),
        ]
        feed = assemble_datanet_feed(entries=entries, context_id="SYS-1", scope="system")
        assert len(feed) == 1

    _run_test("prose determinism", test_prose_determinism, collector)
    _run_test("datanet entry serialization", test_datanet_serialization, collector)
    _run_test("datanet feed assembly", test_feed_assembly, collector)


def mission_system_tests(collector: ResultCollector) -> None:
    _print_group("MISSION SYSTEM TESTS")

    def test_mission_serialization() -> None:
        mission = MissionEntity(
            mission_id="MIS-1",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
        )
        payload = mission.to_dict()
        restored = MissionEntity.from_dict(payload)
        assert payload == restored.to_dict()

    def test_mission_factory_determinism() -> None:
        mission_a = create_mission(
            source_type="bar",
            source_id="NPC-1",
            system_id="SYS-1",
            destination_id="DST-1",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
        )
        mission_b = create_mission(
            source_type="bar",
            source_id="NPC-1",
            system_id="SYS-1",
            destination_id="DST-1",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
        )
        assert mission_a.mission_id == mission_b.mission_id

    def test_mission_manager_flow() -> None:
        player = PlayerState(current_system_id="SYS-1")
        player.mission_slots = 1
        manager = MissionManager()
        mission = create_mission(
            source_type="bar",
            source_id="SYS-1",
            system_id="SYS-1",
            destination_id=None,
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            rewards=[{"field": "credits", "delta": 5}],
        )
        manager.offer(mission)
        accepted, _ = manager.accept(mission.mission_id, player)
        assert accepted
        manager.complete(mission.mission_id, player)
        assert mission.mission_id in player.completed_missions
        assert player.credits == 5

    def test_delivery_mission_completion_on_arrival() -> None:
        """Test that delivery missions complete when player arrives at destination."""
        from game_engine import GameEngine
        from mission_entity import MissionState, MissionOutcome
        
        engine = GameEngine(world_seed=12345, config={"system_count": 5})
        
        # Get current destination and location
        system = engine.sector.get_system(engine.player_state.current_system_id)
        destination = system.destinations[0] if system.destinations else None
        assert destination is not None
        
        # Create a delivery mission with destination matching current location
        destination_location_id = f"{destination.destination_id}-LOC-delivery"
        mission = create_mission(
            source_type="bar",
            source_id="TEST",
            system_id=engine.player_state.current_system_id,
            destination_id=destination.destination_id,
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            rewards=[{"field": "credits", "delta": 100}],
        )
        mission.destination_location_id = destination_location_id
        mission.mission_state = MissionState.ACTIVE
        
        # Add mission to manager and active missions
        engine._mission_manager.missions[mission.mission_id] = mission
        engine.player_state.active_missions.append(mission.mission_id)
        
        # Set player location to match destination
        engine.player_state.current_location_id = destination_location_id
        
        # Evaluate active missions
        engine._evaluate_active_missions(
            logger=engine._logger if engine._logging_enabled else None,
            turn=0,
        )
        
        # Assert mission is completed
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in engine.player_state.completed_missions
        assert mission.mission_id not in engine.player_state.active_missions

    def test_bounty_mission_completion_on_target_destroyed() -> None:
        """Test that bounty missions complete when target ship is destroyed."""
        from game_engine import GameEngine
        from mission_entity import MissionState, MissionOutcome
        
        engine = GameEngine(world_seed=12345, config={"system_count": 5})
        
        # Create a mock target ship and add it to fleet
        from ship_entity import ShipEntity
        target_ship_id = "SHIP-TARGET-1"
        target_ship = ShipEntity(
            ship_id=target_ship_id,
            model_id="hull_small",
            current_system_id=engine.player_state.current_system_id,
        )
        engine.fleet_by_id[target_ship_id] = target_ship
        
        # Create a bounty mission targeting the ship
        mission = create_mission(
            source_type="bar",
            source_id="TEST",
            system_id=engine.player_state.current_system_id,
            destination_id=None,
            mission_type="bounty",
            mission_tier=2,
            payout_policy="claim_required",
            claim_scope="source_entity",
        )
        mission.target_ship_id = target_ship_id
        mission.mission_state = MissionState.ACTIVE
        
        # Add mission to manager and active missions
        engine._mission_manager.missions[mission.mission_id] = mission
        engine.player_state.active_missions.append(mission.mission_id)
        
        # Initially, target exists - mission should not complete
        engine._evaluate_active_missions(
            logger=engine._logger if engine._logging_enabled else None,
            turn=0,
        )
        assert mission.mission_state == MissionState.ACTIVE
        
        # Remove target ship (simulating destruction)
        del engine.fleet_by_id[target_ship_id]
        
        # Evaluate active missions again
        engine._evaluate_active_missions(
            logger=engine._logger if engine._logging_enabled else None,
            turn=1,
        )
        
        # Assert mission is completed
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in engine.player_state.completed_missions
        assert mission.mission_id not in engine.player_state.active_missions

    _run_test("mission serialization", test_mission_serialization, collector)
    _run_test("mission factory determinism", test_mission_factory_determinism, collector)
    _run_test("mission manager flow", test_mission_manager_flow, collector)
    _run_test("delivery mission completion on arrival", test_delivery_mission_completion_on_arrival, collector)
    _run_test("bounty mission completion on target destroyed", test_bounty_mission_completion_on_target_destroyed, collector)


def end_game_goal_tests(collector: ResultCollector) -> None:
    _print_group("END GAME GOALS TESTS")

    def test_end_goal_eval_win_loss() -> None:
        player = PlayerState(current_system_id="SYS-1")
        player.progression_tracks["trust"] = 100
        player.progression_tracks["notoriety"] = 0
        player.credits = 1
        from mission_entity import MissionState, MissionOutcome
        mission = MissionEntity(
            mission_id="MIS-VICTORY",
            mission_type="victory:charter_of_authority",
            mission_tier=5,
            mission_state=MissionState.RESOLVED,
            outcome=MissionOutcome.COMPLETED,
            persistent_state={"victory_id": "charter_of_authority"},
            payout_policy="claim_required",
            claim_scope="any_source_type",
        )
        result = evaluate_end_game(player=player, missions=[mission])
        assert result.status == "win"
        assert result.victory == "charter_of_authority"

        player.arrest_state = "detained_tier_2"
        result = evaluate_end_game(player=player, missions=[mission])
        assert result.status == "lose"
        assert "tier2_arrest" in result.failure_reasons

    _run_test("end goals evaluation", test_end_goal_eval_win_loss, collector)


def placeholder_tests(collector: ResultCollector) -> None:
    _print_group("PLACEHOLDER TESTS (SKIPPED)")

    def skip(label: str) -> None:
        raise SkipTest(label)

    _run_test("Travel & Encounters", lambda: skip("Not implemented."), collector)
    _run_test("Situations & World State", lambda: skip("Not implemented."), collector)
    _run_test("Mission Prose", lambda: skip("Not implemented."), collector)
    _run_test("UI / Visualization", lambda: skip("Not implemented."), collector)


def main() -> None:
    collector = ResultCollector()
    world_generation_tests(collector)
    destination_generation_tests(collector)
    location_availability_tests(collector)
    time_engine_tests(collector)
    core_entity_tests(collector)
    npc_system_tests(collector)
    datanet_prose_tests(collector)
    mission_system_tests(collector)
    end_game_goal_tests(collector)
    placeholder_tests(collector)

    print("")
    print("== SUMMARY ==")
    print(f"Total: {collector.total}")
    print(f"Passed: {collector.passed}")
    print(f"Failed: {collector.failed}")
    print(f"Skipped: {collector.skipped}")
    if collector.failed == 0:
        print("Overall: ALL SYSTEMS HEALTHY")
    else:
        print("Overall: FAILURES DETECTED")


if __name__ == "__main__":
    print("Deprecated harness entry point. Use src/cli_run.py.")
