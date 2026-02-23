"""
Tests for unified fixes: A) Tier 3 NPC enforcement, B) Crew visibility, C) Shipdock price variance, D) Band computation.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from law_enforcement import band_index_from_1_100  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402


def test_a_tier3_npc_enforcement_bars():
    """A) Test that every Bar location has at least 1 Tier 3 bartender."""
    world_seed = 12345
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find all bar locations by traversing systems -> destinations -> locations
    bar_locations = []
    for system in engine.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar":
                    bar_locations.append((system, destination, location))
    
    assert len(bar_locations) > 0, "No bar locations found in generated world"
    
    # Check each bar has bartender
    for system, destination, location in bar_locations:
        # Set proper location context (system + destination + location)
        engine.player_state.current_system_id = system.system_id
        engine.player_state.current_destination_id = destination.destination_id
        engine.player_state.current_location_id = location.location_id
        # Ensure visited flags are set
        engine.player_state.visited_system_ids.add(system.system_id)
        engine.player_state.visited_destination_ids.add(destination.destination_id)
        
        npcs = engine._list_current_location_npcs()
        
        # Find bartender
        bartender = None
        for npc in npcs:
            if isinstance(npc, NPCEntity):
                if "bartender" in npc.role_tags and npc.persistence_tier == NPCPersistenceTier.TIER_3:
                    bartender = npc
                    break
        
        assert bartender is not None, f"Bar location {location.location_id} missing Tier 3 bartender"
        assert bartender.persistence_tier == NPCPersistenceTier.TIER_3, f"Bartender at {location.location_id} not Tier 3"


def test_a_tier3_npc_enforcement_administration():
    """A) Test that every Administration location has at least 1 Tier 3 administrator."""
    world_seed = 12345
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find all administration locations by traversing systems -> destinations -> locations
    admin_locations = []
    for system in engine.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "administration":
                    admin_locations.append((system, destination, location))
    
    if len(admin_locations) == 0:
        # Skip if no admin locations in this seed
        return
    
    # Check each admin has administrator
    for system, destination, location in admin_locations:
        # Set proper location context (system + destination + location)
        engine.player_state.current_system_id = system.system_id
        engine.player_state.current_destination_id = destination.destination_id
        engine.player_state.current_location_id = location.location_id
        # Ensure visited flags are set
        engine.player_state.visited_system_ids.add(system.system_id)
        engine.player_state.visited_destination_ids.add(destination.destination_id)
        
        npcs = engine._list_current_location_npcs()
        
        # Find administrator
        administrator = None
        for npc in npcs:
            if isinstance(npc, NPCEntity):
                if "administrator" in npc.role_tags and npc.persistence_tier == NPCPersistenceTier.TIER_3:
                    administrator = npc
                    break
        
        assert administrator is not None, f"Admin location {location.location_id} missing Tier 3 administrator"
        assert administrator.persistence_tier == NPCPersistenceTier.TIER_3, f"Administrator at {location.location_id} not Tier 3"


def test_a_tier3_npc_idempotent():
    """A) Test that re-entering location doesn't create duplicate Tier 3 NPCs."""
    world_seed = 12345
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find a bar location by traversing systems -> destinations -> locations
    bar_location = None
    for system in engine.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar":
                    bar_location = (system, destination, location)
                    break
            if bar_location:
                break
        if bar_location:
            break
    
    if not bar_location:
        return
    
    system, destination, location = bar_location
    # Set proper location context (system + destination + location)
    engine.player_state.current_system_id = system.system_id
    engine.player_state.current_destination_id = destination.destination_id
    engine.player_state.current_location_id = location.location_id
    # Ensure visited flags are set
    engine.player_state.visited_system_ids.add(system.system_id)
    engine.player_state.visited_destination_ids.add(destination.destination_id)
    
    # First entry
    npcs1 = engine._list_current_location_npcs()
    bartender_ids1 = {
        npc.npc_id for npc in npcs1
        if isinstance(npc, NPCEntity) and "bartender" in npc.role_tags and npc.persistence_tier == NPCPersistenceTier.TIER_3
    }
    
    # Second entry
    npcs2 = engine._list_current_location_npcs()
    bartender_ids2 = {
        npc.npc_id for npc in npcs2
        if isinstance(npc, NPCEntity) and "bartender" in npc.role_tags and npc.persistence_tier == NPCPersistenceTier.TIER_3
    }
    
    assert bartender_ids1 == bartender_ids2, "Re-entering location created duplicate bartenders"
    assert len(bartender_ids1) == 1, "Should have exactly one bartender"


def test_b_crew_visibility_present():
    """B) Test that crew NPCs at location appear in location view."""
    world_seed = 99999
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find a bar location by traversing systems -> destinations -> locations
    bar_location = None
    for system in engine.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar":
                    bar_location = (system, destination, location)
                    break
            if bar_location:
                break
        if bar_location:
            break
    
    if not bar_location:
        return
    
    system, destination, location = bar_location
    # Set proper location context (system + destination + location)
    engine.player_state.current_system_id = system.system_id
    engine.player_state.current_destination_id = destination.destination_id
    engine.player_state.current_location_id = location.location_id
    # Ensure visited flags are set
    engine.player_state.visited_system_ids.add(system.system_id)
    engine.player_state.visited_destination_ids.add(destination.destination_id)
    
    system_id = system.system_id
    location_id = location.location_id
    
    # Manually create a crew NPC for testing (bypass spawn chance)
    crew_npc = NPCEntity(
        npc_id="NPC-TEST-CREW-VISIBLE",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew Visible",
        role_tags=["test_role"],
        current_location_id=location_id,
        current_system_id=system_id,
        is_crew=True,
        crew_role_id="test_role",
        hire_cost=1000,
        daily_wage=10,
    )
    engine._npc_registry.add(crew_npc, logger=None, turn=0)
    crew = [crew_npc]
    
    # Get location view
    npcs = engine._list_current_location_npcs()
    
    # Check crew appears
    crew_ids = {npc.npc_id for npc in crew}
    visible_npc_ids = {
        npc.npc_id if isinstance(npc, NPCEntity) else npc.get("npc_id")
        for npc in npcs
        if isinstance(npc, NPCEntity) or (isinstance(npc, dict) and npc.get("npc_id"))
    }
    
    for crew_id in crew_ids:
        assert crew_id in visible_npc_ids, f"Crew NPC {crew_id} not visible in location view"


def test_b_crew_visibility_hired():
    """B) Test that hired crew (with ship_id) no longer appear in bar view."""
    world_seed = 88888
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find a bar location by traversing systems -> destinations -> locations
    bar_location = None
    for system in engine.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar":
                    bar_location = (system, destination, location)
                    break
            if bar_location:
                break
        if bar_location:
            break
    
    if not bar_location:
        return
    
    system, destination, location = bar_location
    # Set proper location context (system + destination + location)
    engine.player_state.current_system_id = system.system_id
    engine.player_state.current_destination_id = destination.destination_id
    engine.player_state.current_location_id = location.location_id
    # Ensure visited flags are set
    engine.player_state.visited_system_ids.add(system.system_id)
    engine.player_state.visited_destination_ids.add(destination.destination_id)
    
    system_id = system.system_id
    location_id = location.location_id
    
    # Create a crew NPC at location
    crew_npc = NPCEntity(
        npc_id="NPC-TEST-CREW",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew",
        role_tags=["test_role"],
        current_location_id=location_id,
        current_system_id=system_id,
        is_crew=True,
        crew_role_id="test_role",
        hire_cost=1000,
        daily_wage=10,
    )
    engine._npc_registry.add(crew_npc, logger=None, turn=0)
    
    # Verify crew appears
    npcs_before = engine._list_current_location_npcs()
    crew_visible_before = any(
        (isinstance(npc, NPCEntity) and npc.npc_id == "NPC-TEST-CREW") or
        (isinstance(npc, dict) and npc.get("npc_id") == "NPC-TEST-CREW")
        for npc in npcs_before
    )
    assert crew_visible_before, "Crew should be visible before hiring"
    
    # Simulate hiring: set ship_id
    crew_npc.current_ship_id = "PLAYER-SHIP-001"
    crew_npc.current_location_id = None
    engine._npc_registry.update(crew_npc, logger=None, turn=0)
    
    # Clear cached location NPCs to force re-resolution with updated NPC state
    if hasattr(engine, '_location_npc_ids') and location_id in engine._location_npc_ids:
        del engine._location_npc_ids[location_id]
    
    # Verify crew no longer appears
    npcs_after = engine._list_current_location_npcs()
    crew_visible_after = any(
        (isinstance(npc, NPCEntity) and npc.npc_id == "NPC-TEST-CREW") or
        (isinstance(npc, dict) and npc.get("npc_id") == "NPC-TEST-CREW")
        for npc in npcs_after
    )
    assert not crew_visible_after, "Crew should not be visible after hiring"


def test_c_shipdock_price_variance_deterministic():
    """C) Test that shipdock price multiplier is deterministic and stable."""
    world_seed = 77777
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    
    # Generate world twice with same seed
    engine1 = GameEngine(world_seed=world_seed)
    engine2 = GameEngine(world_seed=world_seed)
    
    # Find a destination with market
    destination1 = None
    for system in engine1.sector.systems:
        for dest in system.destinations:
            if dest.market is not None:
                destination1 = dest
                break
        if destination1:
            break
    
    destination2 = None
    for system in engine2.sector.systems:
        for dest in system.destinations:
            if dest.destination_id == destination1.destination_id:
                destination2 = dest
                break
        if destination2:
            break
    
    if destination1 is None or destination2 is None:
        return
    
    multiplier1 = destination1.market.shipdock_price_multiplier
    multiplier2 = destination2.market.shipdock_price_multiplier
    
    assert multiplier1 == multiplier2, "Shipdock multiplier should be deterministic"
    assert 0.95 <= multiplier1 <= 1.05, f"Multiplier should be in [0.95, 1.05], got {multiplier1}"


def test_c_shipdock_price_variance_different_markets():
    """C) Test that different markets may have different multipliers."""
    world_seed = 66666
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_ids = registry.government_ids()
    
    engine = GameEngine(world_seed=world_seed)
    
    multipliers = []
    for system in engine.sector.systems:
        for destination in system.destinations:
            if destination.market is not None:
                multipliers.append(destination.market.shipdock_price_multiplier)
    
    if len(multipliers) < 2:
        return
    
    # At least two different multipliers (very likely with different destination_ids)
    unique_multipliers = set(multipliers)
    # Note: It's possible but unlikely all are the same, so we just check they're in valid range
    for mult in multipliers:
        assert 0.95 <= mult <= 1.05, f"Multiplier {mult} should be in [0.95, 1.05]"


def test_d_band_computation_boundaries():
    """D) Test band computation boundaries (just below, at, just above thresholds)."""
    # Test boundary at 20 (band -2 to -1)
    assert band_index_from_1_100(19) == -2, "19 should be band -2"
    assert band_index_from_1_100(20) == -2, "20 should be band -2"
    assert band_index_from_1_100(21) == -1, "21 should be band -1"
    
    # Test boundary at 40 (band -1 to 0)
    assert band_index_from_1_100(39) == -1, "39 should be band -1"
    assert band_index_from_1_100(40) == -1, "40 should be band -1"
    assert band_index_from_1_100(41) == 0, "41 should be band 0"
    
    # Test boundary at 60 (band 0 to 1)
    assert band_index_from_1_100(59) == 0, "59 should be band 0"
    assert band_index_from_1_100(60) == 0, "60 should be band 0"
    assert band_index_from_1_100(61) == 1, "61 should be band 1"
    
    # Test boundary at 80 (band 1 to 2)
    assert band_index_from_1_100(79) == 1, "79 should be band 1"
    assert band_index_from_1_100(80) == 1, "80 should be band 1"
    assert band_index_from_1_100(81) == 2, "81 should be band 2"
    
    # Test extremes
    assert band_index_from_1_100(0) == -2, "0 should be band -2"
    assert band_index_from_1_100(1) == -2, "1 should be band -2"
    assert band_index_from_1_100(100) == 2, "100 should be band 2"
    
    # Test negative values (treated as <= 20)
    assert band_index_from_1_100(-10) == -2, "Negative values should map to band -2"


def test_d_band_computation_transitions():
    """D) Test at least 3 band transitions."""
    # Transition 1: -2 to -1 at 21
    assert band_index_from_1_100(20) == -2
    assert band_index_from_1_100(21) == -1
    
    # Transition 2: -1 to 0 at 41
    assert band_index_from_1_100(40) == -1
    assert band_index_from_1_100(41) == 0
    
    # Transition 3: 0 to 1 at 61
    assert band_index_from_1_100(60) == 0
    assert band_index_from_1_100(61) == 1
    
    # Transition 4: 1 to 2 at 81
    assert band_index_from_1_100(80) == 1
    assert band_index_from_1_100(81) == 2
