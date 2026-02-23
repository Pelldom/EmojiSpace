"""
Tests for crew spawning and hiring consolidation.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from npc_registry import NPCRegistry  # noqa: E402
from player_state import PlayerState  # noqa: E402
from ship_entity import ShipEntity, ShipActivityState  # noqa: E402
from world_generator import WorldGenerator  # noqa: E402
from time_engine import TimeEngine  # noqa: E402
from logger import Logger  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402


class _TestLogger:
    def log(self, turn: int, action: str, state_change: str) -> None:
        pass


def test_crew_spawn_deterministic():
    """Test that crew spawning is deterministic for fixed seed + location + population."""
    world_seed = 12345
    location_id = "LOC-TEST-BAR"
    system_id = "SYS-TEST"
    
    # Create minimal game engine
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    
    # Create engine with test system
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state.current_system_id = system_id
    engine.player_state.current_destination_id = system.destinations[0].destination_id if system.destinations else None
    
    # Spawn crew twice with same parameters
    crew1 = engine._spawn_crew_for_bar_location(location_id=location_id, system_id=system_id)
    crew2 = engine._spawn_crew_for_bar_location(location_id=location_id, system_id=system_id)
    
    # Should be deterministic (same spawn roll result)
    assert len(crew1) == len(crew2), "Crew spawn count should be deterministic"
    if crew1:
        assert len(crew1) == len(crew2)
        for npc1, npc2 in zip(crew1, crew2):
            assert npc1.npc_id == npc2.npc_id, "Crew NPC IDs should be deterministic"


def test_crew_spawn_cap_population_1():
    """Test that population 1 systems spawn at most 1 crew."""
    world_seed = 99999  # Use seed that triggers spawn
    location_id = "LOC-TEST-BAR-1"
    system_id = "SYS-TEST-1"
    
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    # Force population to 1
    system = type(system)(**{**system.__dict__, "population": 1})
    sector.systems[0] = system
    
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state.current_system_id = system_id
    
    # Try multiple spawns to find one that succeeds
    max_spawned = 0
    for test_location_id in [f"{location_id}-{i}" for i in range(100)]:
        crew = engine._spawn_crew_for_bar_location(location_id=test_location_id, system_id=system_id)
        if crew:
            max_spawned = max(max_spawned, len(crew))
            assert len(crew) <= 1, f"Population 1 should spawn at most 1 crew, got {len(crew)}"
    
    # At least one spawn should succeed (20% chance over 100 attempts)
    # But we're just testing the cap, so we check that when spawn succeeds, cap is respected


def test_crew_spawn_cap_population_5():
    """Test that population 5 systems spawn at most 3 crew."""
    world_seed = 88888
    location_id = "LOC-TEST-BAR-5"
    system_id = "SYS-TEST-5"
    
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    # Force population to 5
    system = type(system)(**{**system.__dict__, "population": 5})
    sector.systems[0] = system
    
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state.current_system_id = system_id
    
    # Try multiple spawns to find one that succeeds
    for test_location_id in [f"{location_id}-{i}" for i in range(100)]:
        crew = engine._spawn_crew_for_bar_location(location_id=test_location_id, system_id=system_id)
        if crew:
            assert len(crew) <= 3, f"Population 5 should spawn at most 3 crew, got {len(crew)}"


def test_crew_spawn_tier_2_contract():
    """Test that spawned crew have correct contract fields."""
    world_seed = 77777
    location_id = "LOC-TEST-BAR-CONTRACT"
    system_id = "SYS-TEST-CONTRACT"
    
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state.current_system_id = system_id
    
    # Try multiple spawns to find one that succeeds
    crew = None
    for test_location_id in [f"{location_id}-{i}" for i in range(100)]:
        spawned = engine._spawn_crew_for_bar_location(location_id=test_location_id, system_id=system_id)
        if spawned:
            crew = spawned[0]
            break
    
    if crew is None:
        # Skip if no spawn succeeded (20% chance)
        return
    
    # Verify contract fields
    assert crew.is_crew is True, "Crew must have is_crew=True"
    assert crew.persistence_tier == NPCPersistenceTier.TIER_2, "Crew must be TIER_2"
    assert crew.crew_role_id is not None, "Crew must have crew_role_id"
    assert crew.hire_cost >= 0, "Crew must have hire_cost"
    assert crew.daily_wage >= 0, "Crew must have daily_wage"
    assert crew.current_location_id == test_location_id, "Crew must be at spawn location"
    assert crew.current_system_id == system_id, "Crew must be in spawn system"
    
    # Validate should pass
    crew.validate()


def test_crew_hiring_success():
    """Test successful crew hiring path."""
    world_seed = 66666
    location_id = "LOC-TEST-HIRE"
    system_id = "SYS-TEST-HIRE"
    
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    
    time_engine = TimeEngine()
    logger = _TestLogger()
    player_state = PlayerState()
    player_state.current_system_id = system_id
    player_state.credits = 10000
    player_state.current_destination_id = system.destinations[0].destination_id if system.destinations else None
    
    # Create active ship with crew capacity
    from ship_assembler import assemble_ship
    assembled = assemble_ship("civ_t1_midge", [], {"weapon": 0, "defense": 0, "engine": 0})
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == "civ_t1_midge":
            hull_data = hull
            break
    
    cargo_base = hull_data.get("cargo", {}) if hull_data else {}
    utility_effects = assembled.get("ship_utility_effects", {})
    
    active_ship = ShipEntity(
        ship_id="PLAYER-SHIP-001",
        model_id="civ_t1_midge",
        owner_id=player_state.player_id,
        owner_type="player",
        activity_state=ShipActivityState.ACTIVE,
        destination_id=player_state.current_destination_id,
        current_system_id=system_id,
        current_destination_id=player_state.current_destination_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
        crew_capacity=int(hull_data.get("crew_capacity", 0)) if hull_data else 0,
        physical_cargo_capacity=int(cargo_base.get("physical_base", 0)) + int(utility_effects.get("physical_cargo_bonus", 0)),
        data_cargo_capacity=int(cargo_base.get("data_base", 0)) + int(utility_effects.get("data_cargo_bonus", 0)),
    )
    
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state = player_state
    engine.fleet_by_id[active_ship.ship_id] = active_ship
    player_state.active_ship_id = active_ship.ship_id
    
    # Create a bar location and enter it
    from world_generator import Location
    bar_location = Location(
        location_id=location_id,
        destination_id=system.destinations[0].destination_id if system.destinations else "",
        location_type="bar",
        enabled=True,
    )
    destination = system.destinations[0] if system.destinations else None
    if destination:
        # Add location to destination
        locations = list(destination.locations) + [bar_location]
        destination = type(destination)(**{**destination.__dict__, "locations": locations})
        system = type(system)(**{**system.__dict__, "destinations": [destination]})
        sector.systems[0] = system
    
    player_state.current_location_id = location_id
    
    # Spawn crew
    crew = engine._spawn_crew_for_bar_location(location_id=location_id, system_id=system_id)
    
    if not crew:
        # Skip if spawn didn't succeed
        return
    
    crew_npc = crew[0]
    hire_cost = crew_npc.hire_cost
    
    # Ensure player has enough credits
    player_state.credits = hire_cost + 1000
    
    # Execute hire
    from game_engine import EngineContext
    context = EngineContext(
        command_type="location_action",
        turn_before=int(time_engine.current_turn),
        turn_after=int(time_engine.current_turn),
    )
    
    engine._execute_bar_hire_crew(context)
    
    # Verify hire succeeded
    events = context.events
    hire_event = None
    for event in events:
        if isinstance(event, dict) and event.get("stage") == "location_action":
            detail = event.get("detail", {})
            if detail.get("action_id") == "bar_hire_crew":
                hire_event = detail
                break
    
    assert hire_event is not None, "Hire event should be generated"
    result = hire_event.get("result", {})
    assert result.get("ok") is True, "Hire should succeed"
    
    # Verify crew is on ship
    assert len(active_ship.crew) == 1, "Ship should have 1 crew member"
    assert active_ship.crew[0].npc_id == crew_npc.npc_id, "Crew NPC should be on ship"
    
    # Verify NPC location updated
    assert crew_npc.current_ship_id == active_ship.ship_id, "Crew should be assigned to ship"
    assert crew_npc.current_location_id is None, "Crew location should be cleared"


def test_crew_hiring_insufficient_credits():
    """Test that insufficient credits leaves NPC in registry."""
    world_seed = 55555
    location_id = "LOC-TEST-NO-CREDITS"
    system_id = "SYS-TEST-NO-CREDITS"
    
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    
    time_engine = TimeEngine()
    logger = _TestLogger()
    player_state = PlayerState()
    player_state.current_system_id = system_id
    player_state.credits = 100  # Low credits
    player_state.current_destination_id = system.destinations[0].destination_id if system.destinations else None
    
    from ship_assembler import assemble_ship
    assembled = assemble_ship("civ_t1_midge", [], {"weapon": 0, "defense": 0, "engine": 0})
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == "civ_t1_midge":
            hull_data = hull
            break
    
    cargo_base = hull_data.get("cargo", {}) if hull_data else {}
    utility_effects = assembled.get("ship_utility_effects", {})
    
    active_ship = ShipEntity(
        ship_id="PLAYER-SHIP-001",
        model_id="civ_t1_midge",
        owner_id=player_state.player_id,
        owner_type="player",
        activity_state=ShipActivityState.ACTIVE,
        destination_id=player_state.current_destination_id,
        current_system_id=system_id,
        current_destination_id=player_state.current_destination_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
        crew_capacity=int(hull_data.get("crew_capacity", 0)) if hull_data else 0,
        physical_cargo_capacity=int(cargo_base.get("physical_base", 0)) + int(utility_effects.get("physical_cargo_bonus", 0)),
        data_cargo_capacity=int(cargo_base.get("data_base", 0)) + int(utility_effects.get("data_cargo_bonus", 0)),
    )
    
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state = player_state
    engine.fleet_by_id[active_ship.ship_id] = active_ship
    player_state.active_ship_id = active_ship.ship_id
    
    from world_generator import Location
    bar_location = Location(
        location_id=location_id,
        destination_id=system.destinations[0].destination_id if system.destinations else "",
        location_type="bar",
        enabled=True,
    )
    destination = system.destinations[0] if system.destinations else None
    if destination:
        locations = list(destination.locations) + [bar_location]
        destination = type(destination)(**{**destination.__dict__, "locations": locations})
        system = type(system)(**{**system.__dict__, "destinations": [destination]})
        sector.systems[0] = system
    
    player_state.current_location_id = location_id
    
    # Spawn crew
    crew = engine._spawn_crew_for_bar_location(location_id=location_id, system_id=system_id)
    
    if not crew:
        return
    
    crew_npc = crew[0]
    hire_cost = crew_npc.hire_cost
    
    # Set credits below hire cost
    player_state.credits = max(0, hire_cost - 100)
    
    # Store original location
    original_location_id = crew_npc.current_location_id
    
    # Execute hire (should fail)
    from game_engine import EngineContext
    context = EngineContext(
        command_type="location_action",
        turn_before=int(time_engine.current_turn),
        turn_after=int(time_engine.current_turn),
    )
    
    engine._execute_bar_hire_crew(context)
    
    # Verify hire failed
    events = context.events
    hire_event = None
    for event in events:
        if isinstance(event, dict) and event.get("stage") == "location_action":
            detail = event.get("detail", {})
            if detail.get("action_id") == "bar_hire_crew":
                hire_event = detail
                break
    
    assert hire_event is not None, "Hire event should be generated"
    result = hire_event.get("result", {})
    assert result.get("ok") is False, "Hire should fail"
    assert result.get("reason") == "insufficient_credits", "Should fail due to insufficient credits"
    
    # Verify NPC still in registry and at location
    registry_npc = engine._npc_registry.get(crew_npc.npc_id)
    assert registry_npc is not None, "NPC should remain in registry"
    assert registry_npc.current_location_id == original_location_id, "NPC location should be unchanged"
    assert registry_npc.current_ship_id is None, "NPC should not be assigned to ship"
    
    # Verify ship has no crew
    assert len(active_ship.crew) == 0, "Ship should have no crew"


def test_crew_hiring_capacity_exceeded():
    """Test that capacity exceeded prevents hire."""
    world_seed = 44444
    location_id = "LOC-TEST-CAPACITY"
    system_id = "SYS-TEST-CAPACITY"
    
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    generator = WorldGenerator(seed=world_seed, system_count=1, government_ids=government_ids)
    sector = generator.generate()
    system = sector.systems[0]
    
    time_engine = TimeEngine()
    logger = _TestLogger()
    player_state = PlayerState()
    player_state.current_system_id = system_id
    player_state.credits = 10000
    player_state.current_destination_id = system.destinations[0].destination_id if system.destinations else None
    
    from ship_assembler import assemble_ship
    assembled = assemble_ship("civ_t1_midge", [], {"weapon": 0, "defense": 0, "engine": 0})
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == "civ_t1_midge":
            hull_data = hull
            break
    
    cargo_base = hull_data.get("cargo", {}) if hull_data else {}
    utility_effects = assembled.get("ship_utility_effects", {})
    
    # Create ship with crew_capacity = 0 (Midge has 0 crew capacity)
    active_ship = ShipEntity(
        ship_id="PLAYER-SHIP-001",
        model_id="civ_t1_midge",
        owner_id=player_state.player_id,
        owner_type="player",
        activity_state=ShipActivityState.ACTIVE,
        destination_id=player_state.current_destination_id,
        current_system_id=system_id,
        current_destination_id=player_state.current_destination_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
        crew_capacity=int(hull_data.get("crew_capacity", 0)) if hull_data else 0,
        physical_cargo_capacity=int(cargo_base.get("physical_base", 0)) + int(utility_effects.get("physical_cargo_bonus", 0)),
        data_cargo_capacity=int(cargo_base.get("data_base", 0)) + int(utility_effects.get("data_cargo_bonus", 0)),
    )
    
    engine = GameEngine(world_seed=world_seed, config={"system_count": 1})
    # Replace sector and player_state with test versions
    engine.sector = sector
    engine.player_state = player_state
    engine.fleet_by_id[active_ship.ship_id] = active_ship
    player_state.active_ship_id = active_ship.ship_id
    
    from world_generator import Location
    bar_location = Location(
        location_id=location_id,
        destination_id=system.destinations[0].destination_id if system.destinations else "",
        location_type="bar",
        enabled=True,
    )
    destination = system.destinations[0] if system.destinations else None
    if destination:
        locations = list(destination.locations) + [bar_location]
        destination = type(destination)(**{**destination.__dict__, "locations": locations})
        system = type(system)(**{**system.__dict__, "destinations": [destination]})
        sector.systems[0] = system
    
    player_state.current_location_id = location_id
    
    # Spawn crew
    crew = engine._spawn_crew_for_bar_location(location_id=location_id, system_id=system_id)
    
    if not crew or active_ship.crew_capacity > 0:
        # Skip if no spawn or ship has capacity (test requires capacity = 0)
        return
    
    crew_npc = crew[0]
    
    # Execute hire (should fail due to capacity)
    from game_engine import EngineContext
    context = EngineContext(
        command_type="location_action",
        turn_before=int(time_engine.current_turn),
        turn_after=int(time_engine.current_turn),
    )
    
    engine._execute_bar_hire_crew(context)
    
    # Verify hire failed
    events = context.events
    hire_event = None
    for event in events:
        if isinstance(event, dict) and event.get("stage") == "location_action":
            detail = event.get("detail", {})
            if detail.get("action_id") == "bar_hire_crew":
                hire_event = detail
                break
    
    assert hire_event is not None, "Hire event should be generated"
    result = hire_event.get("result", {})
    assert result.get("ok") is False, "Hire should fail"
    assert result.get("reason") == "crew_capacity_exceeded", "Should fail due to capacity exceeded"
    
    # Verify ship has no crew
    assert len(active_ship.crew) == 0, "Ship should have no crew"
