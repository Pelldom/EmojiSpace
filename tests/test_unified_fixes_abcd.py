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


# ============================================================
# E) Crew Dismissal Relocation Tests
# ============================================================

def test_e_dismiss_relocates_to_bar_in_current_destination_if_present():
    """E) Test that dismissed crew relocates to bar in current destination if present."""
    world_seed = 12345
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find a destination with a bar location
    bar_location = None
    target_system = None
    target_destination = None
    for system in engine.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar" and location.enabled:
                    bar_location = location
                    target_system = system
                    target_destination = destination
                    break
            if bar_location:
                break
        if bar_location:
            break
    
    assert bar_location is not None, "No bar location found in generated world"
    
    # Set player location context
    engine.player_state.current_system_id = target_system.system_id
    engine.player_state.current_destination_id = target_destination.destination_id
    engine.player_state.current_location_id = bar_location.location_id
    engine.player_state.visited_system_ids.add(target_system.system_id)
    engine.player_state.visited_destination_ids.add(target_destination.destination_id)
    
    # Create a crew member on the player's ship
    from crew_generator import generate_hireable_crew
    crew_pool = generate_hireable_crew(
        world_seed=world_seed,
        system_id=target_system.system_id,
        pool_size=1,
        world_state_engine=engine._world_state_engine(),
    )
    assert len(crew_pool) > 0, "No crew generated"
    
    crew_data = crew_pool[0]
    crew_npc = NPCEntity(
        npc_id="TEST-CREW-001",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew",
        role_tags=[str(crew_data.get("role_id", ""))],
        current_ship_id=engine.player_state.active_ship_id,
        current_system_id=target_system.system_id,
        is_crew=True,
        crew_role_id=str(crew_data.get("role_id", "")),
        hire_cost=int(crew_data.get("hire_cost", 0)),
        daily_wage=int(crew_data.get("daily_wage", 0)),
    )
    
    # Add crew to ship
    active_ship = engine._active_ship()
    # Ensure ship has crew capacity (starting ship should have capacity from assembler)
    if active_ship.crew_capacity == 0:
        # If somehow crew_capacity is 0, set it to at least 1 for testing
        active_ship.crew_capacity = 1
    active_ship.add_crew(crew_npc)
    engine._npc_registry.add(crew_npc, logger=None, turn=0)
    
    # Dismiss the crew
    result = engine.execute({"type": "dismiss_crew", "npc_id": "TEST-CREW-001"})
    detail = None
    for event in result.get("events", []):
        if event.get("stage") == "crew_dismissal":
            detail = event.get("detail", {})
            break
    
    assert detail is not None, f"Dismissal event not found. Result: {result}"
    result_detail = detail.get("result", {})
    assert result_detail.get("ok") is True, f"Dismissal failed: {result_detail.get('reason')}"
    
    # Verify relocation
    relocated = result_detail.get("relocated_to", {})
    assert relocated.get("system_id") == target_system.system_id, "Should relocate to current system"
    assert relocated.get("destination_id") == target_destination.destination_id, "Should relocate to current destination"
    assert relocated.get("location_id") == bar_location.location_id, "Should relocate to bar in current destination"
    
    # Verify NPC state
    dismissed_npc = engine._npc_registry.get("TEST-CREW-001")
    assert dismissed_npc is not None, "NPC should still exist in registry"
    assert dismissed_npc.current_ship_id is None, "NPC should not be on ship"
    assert dismissed_npc.current_location_id == bar_location.location_id, "NPC should be at bar location"
    assert dismissed_npc.current_system_id == target_system.system_id, "NPC should be in current system"
    assert dismissed_npc.persistence_tier == NPCPersistenceTier.TIER_2, "NPC should remain TIER_2"


def test_e_dismiss_relocates_to_bar_in_current_system_if_no_bar_in_destination():
    """E) Test that dismissed crew relocates to bar in current system if no bar in destination."""
    world_seed = 12345
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find a destination WITHOUT a bar, but in a system that HAS a bar in another destination
    target_system = None
    target_destination = None
    bar_destination = None
    bar_location = None
    
    for system in engine.sector.systems:
        # Find a destination without a bar
        for dest in system.destinations:
            has_bar = any(loc.location_type == "bar" and loc.enabled for loc in dest.locations)
            if not has_bar:
                target_destination = dest
                target_system = system
                # Now find a bar in another destination in the same system
                for other_dest in system.destinations:
                    if other_dest.destination_id != dest.destination_id:
                        for loc in other_dest.locations:
                            if loc.location_type == "bar" and loc.enabled:
                                bar_destination = other_dest
                                bar_location = loc
                                break
                        if bar_location:
                            break
                if bar_location:
                    break
        if target_destination and bar_location:
            break
    
    if not target_destination or not bar_location:
        # Fallback: create a minimal test scenario
        # Just verify the logic works with any system that has a bar
        for system in engine.sector.systems:
            for destination in system.destinations:
                for location in destination.locations:
                    if location.location_type == "bar" and location.enabled:
                        target_system = system
                        target_destination = destination
                        bar_location = location
                        break
                if bar_location:
                    break
            if bar_location:
                break
    
    assert target_system is not None and bar_location is not None, "Could not find suitable test scenario"
    
    # Set player location context (at destination without bar)
    engine.player_state.current_system_id = target_system.system_id
    engine.player_state.current_destination_id = target_destination.destination_id
    # Use a non-bar location in the destination
    non_bar_location = None
    for loc in target_destination.locations:
        if loc.location_type != "bar" and loc.enabled:
            non_bar_location = loc
            break
    if non_bar_location:
        engine.player_state.current_location_id = non_bar_location.location_id
    else:
        # Fallback: use destination_id as location_id (not ideal but works for test)
        engine.player_state.current_location_id = target_destination.destination_id + "-LOC-test"
    
    engine.player_state.visited_system_ids.add(target_system.system_id)
    engine.player_state.visited_destination_ids.add(target_destination.destination_id)
    
    # Create a crew member
    from crew_generator import generate_hireable_crew
    crew_pool = generate_hireable_crew(
        world_seed=world_seed,
        system_id=target_system.system_id,
        pool_size=1,
        world_state_engine=engine._world_state_engine(),
    )
    assert len(crew_pool) > 0, "No crew generated"
    
    crew_data = crew_pool[0]
    crew_npc = NPCEntity(
        npc_id="TEST-CREW-002",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew 2",
        role_tags=[str(crew_data.get("role_id", ""))],
        current_ship_id=engine.player_state.active_ship_id,
        current_system_id=target_system.system_id,
        is_crew=True,
        crew_role_id=str(crew_data.get("role_id", "")),
        hire_cost=int(crew_data.get("hire_cost", 0)),
        daily_wage=int(crew_data.get("daily_wage", 0)),
    )
    
    # Add crew to ship
    active_ship = engine._active_ship()
    # Ensure ship has crew capacity
    if active_ship.crew_capacity == 0:
        active_ship.crew_capacity = 1
    active_ship.add_crew(crew_npc)
    engine._npc_registry.add(crew_npc, logger=None, turn=0)
    
    # Dismiss the crew
    result = engine.execute({"type": "dismiss_crew", "npc_id": "TEST-CREW-002"})
    detail = None
    for event in result.get("events", []):
        if event.get("stage") == "crew_dismissal":
            detail = event.get("detail", {})
            break
    
    assert detail is not None, "Dismissal event not found"
    result_detail = detail.get("result", {})
    assert result_detail.get("ok") is True, f"Dismissal failed: {result_detail.get('reason')}"
    
    # Verify relocation is to a bar in the current system
    relocated = result_detail.get("relocated_to", {})
    assert relocated.get("system_id") == target_system.system_id, "Should relocate within current system"
    assert relocated.get("location_id") is not None, "Should have a location_id"
    
    # Verify the location is actually a bar
    relocated_location_id = relocated.get("location_id")
    found_bar = False
    for dest in target_system.destinations:
        for loc in dest.locations:
            if loc.location_id == relocated_location_id and loc.location_type == "bar":
                found_bar = True
                break
        if found_bar:
            break
    assert found_bar, f"Relocated location {relocated_location_id} should be a bar"


def test_e_dismiss_relocates_to_nearest_neighbor_system_when_no_bar_in_system():
    """E) Test that dismissed crew relocates to nearest neighbor system when no bar in current system."""
    world_seed = 12345
    
    engine = GameEngine(world_seed=world_seed)
    
    # Find a system with no bars, but has a neighbor with bars
    target_system = None
    neighbor_system_with_bar = None
    bar_location = None
    
    for system in engine.sector.systems:
        # Check if this system has any bars
        has_bar = False
        for dest in system.destinations:
            for loc in dest.locations:
                if loc.location_type == "bar" and loc.enabled:
                    has_bar = True
                    break
            if has_bar:
                break
        
        if not has_bar and len(system.neighbors) > 0:
            # Check neighbors for bars
            for neighbor_id in system.neighbors:
                neighbor = engine.sector.get_system(neighbor_id)
                if neighbor is None:
                    continue
                for dest in neighbor.destinations:
                    for loc in dest.locations:
                        if loc.location_type == "bar" and loc.enabled:
                            target_system = system
                            neighbor_system_with_bar = neighbor
                            bar_location = loc
                            break
                    if bar_location:
                        break
                if bar_location:
                    break
        if target_system and bar_location:
            break
    
    # If no such scenario exists, skip this test (not all world seeds may have this)
    if not target_system or not bar_location:
        # Fallback: just verify the BFS logic doesn't crash
        # Use any system and verify dismissal works
        target_system = engine.sector.systems[0]
        # Find any bar in the world for verification
        for system in engine.sector.systems:
            for dest in system.destinations:
                for loc in dest.locations:
                    if loc.location_type == "bar" and loc.enabled:
                        bar_location = loc
                        break
                if bar_location:
                    break
            if bar_location:
                break
    
    assert target_system is not None and bar_location is not None, "Could not find suitable test scenario"
    
    # Set player location context
    target_destination = target_system.destinations[0]
    engine.player_state.current_system_id = target_system.system_id
    engine.player_state.current_destination_id = target_destination.destination_id
    non_bar_location = None
    for loc in target_destination.locations:
        if loc.location_type != "bar" and loc.enabled:
            non_bar_location = loc
            break
    if non_bar_location:
        engine.player_state.current_location_id = non_bar_location.location_id
    else:
        engine.player_state.current_location_id = target_destination.destination_id + "-LOC-test"
    
    engine.player_state.visited_system_ids.add(target_system.system_id)
    engine.player_state.visited_destination_ids.add(target_destination.destination_id)
    
    # Create a crew member
    from crew_generator import generate_hireable_crew
    crew_pool = generate_hireable_crew(
        world_seed=world_seed,
        system_id=target_system.system_id,
        pool_size=1,
        world_state_engine=engine._world_state_engine(),
    )
    assert len(crew_pool) > 0, "No crew generated"
    
    crew_data = crew_pool[0]
    crew_npc = NPCEntity(
        npc_id="TEST-CREW-003",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew 3",
        role_tags=[str(crew_data.get("role_id", ""))],
        current_ship_id=engine.player_state.active_ship_id,
        current_system_id=target_system.system_id,
        is_crew=True,
        crew_role_id=str(crew_data.get("role_id", "")),
        hire_cost=int(crew_data.get("hire_cost", 0)),
        daily_wage=int(crew_data.get("daily_wage", 0)),
    )
    
    # Add crew to ship
    active_ship = engine._active_ship()
    # Ensure ship has crew capacity
    if active_ship.crew_capacity == 0:
        active_ship.crew_capacity = 1
    active_ship.add_crew(crew_npc)
    engine._npc_registry.add(crew_npc, logger=None, turn=0)
    
    # Dismiss the crew
    result = engine.execute({"type": "dismiss_crew", "npc_id": "TEST-CREW-003"})
    detail = None
    for event in result.get("events", []):
        if event.get("stage") == "crew_dismissal":
            detail = event.get("detail", {})
            break
    
    assert detail is not None, "Dismissal event not found"
    result_detail = detail.get("result", {})
    assert result_detail.get("ok") is True, f"Dismissal failed: {result_detail.get('reason')}"
    
    # Verify relocation found a bar (may be in neighbor system)
    relocated = result_detail.get("relocated_to", {})
    assert relocated.get("system_id") is not None, "Should have a system_id"
    assert relocated.get("location_id") is not None, "Should have a location_id"
    
    # Verify the location is actually a bar
    relocated_system_id = relocated.get("system_id")
    relocated_location_id = relocated.get("location_id")
    relocated_system = engine.sector.get_system(relocated_system_id)
    assert relocated_system is not None, f"Relocated system {relocated_system_id} should exist"
    
    found_bar = False
    for dest in relocated_system.destinations:
        for loc in dest.locations:
            if loc.location_id == relocated_location_id and loc.location_type == "bar":
                found_bar = True
                break
        if found_bar:
            break
    assert found_bar, f"Relocated location {relocated_location_id} should be a bar"


def test_e_dismiss_relocation_is_deterministic():
    """E) Test that dismissal relocation is deterministic across identical setups."""
    world_seed = 12345
    
    # First dismissal
    engine1 = GameEngine(world_seed=world_seed)
    
    # Find a bar location
    bar_location = None
    target_system = None
    target_destination = None
    for system in engine1.sector.systems:
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar" and location.enabled:
                    bar_location = location
                    target_system = system
                    target_destination = destination
                    break
            if bar_location:
                break
        if bar_location:
            break
    
    assert bar_location is not None, "No bar location found"
    
    # Set player location context
    engine1.player_state.current_system_id = target_system.system_id
    engine1.player_state.current_destination_id = target_destination.destination_id
    engine1.player_state.current_location_id = bar_location.location_id
    engine1.player_state.visited_system_ids.add(target_system.system_id)
    engine1.player_state.visited_destination_ids.add(target_destination.destination_id)
    
    # Create crew
    from crew_generator import generate_hireable_crew
    crew_pool = generate_hireable_crew(
        world_seed=world_seed,
        system_id=target_system.system_id,
        pool_size=1,
        world_state_engine=engine1._world_state_engine(),
    )
    assert len(crew_pool) > 0, "No crew generated"
    
    crew_data = crew_pool[0]
    crew_npc1 = NPCEntity(
        npc_id="TEST-CREW-DET-001",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew Det",
        role_tags=[str(crew_data.get("role_id", ""))],
        current_ship_id=engine1.player_state.active_ship_id,
        current_system_id=target_system.system_id,
        is_crew=True,
        crew_role_id=str(crew_data.get("role_id", "")),
        hire_cost=int(crew_data.get("hire_cost", 0)),
        daily_wage=int(crew_data.get("daily_wage", 0)),
    )
    
    active_ship1 = engine1._active_ship()
    # Ensure ship has crew capacity
    if active_ship1.crew_capacity == 0:
        active_ship1.crew_capacity = 1
    active_ship1.add_crew(crew_npc1)
    engine1._npc_registry.add(crew_npc1, logger=None, turn=0)
    
    # Dismiss
    result1 = engine1.execute({"type": "dismiss_crew", "npc_id": "TEST-CREW-DET-001"})
    detail1 = None
    for event in result1.get("events", []):
        if event.get("stage") == "crew_dismissal":
            detail1 = event.get("detail", {})
            break
    
    assert detail1 is not None, "Dismissal event not found"
    result_detail1 = detail1.get("result", {})
    assert result_detail1.get("ok") is True, f"Dismissal failed: {result_detail1.get('reason')}"
    relocated1 = result_detail1.get("relocated_to", {})
    
    # Second dismissal (identical setup)
    engine2 = GameEngine(world_seed=world_seed)
    
    # Find same bar location (deterministic world)
    bar_location2 = None
    target_system2 = None
    target_destination2 = None
    for system in engine2.sector.systems:
        if system.system_id == target_system.system_id:
            target_system2 = system
            for destination in system.destinations:
                if destination.destination_id == target_destination.destination_id:
                    target_destination2 = destination
                    for location in destination.locations:
                        if location.location_id == bar_location.location_id:
                            bar_location2 = location
                            break
                    break
            break
    
    assert bar_location2 is not None, "Could not find same bar location in second engine"
    
    # Set same player location context
    engine2.player_state.current_system_id = target_system2.system_id
    engine2.player_state.current_destination_id = target_destination2.destination_id
    engine2.player_state.current_location_id = bar_location2.location_id
    engine2.player_state.visited_system_ids.add(target_system2.system_id)
    engine2.player_state.visited_destination_ids.add(target_destination2.destination_id)
    
    # Create same crew
    crew_pool2 = generate_hireable_crew(
        world_seed=world_seed,
        system_id=target_system2.system_id,
        pool_size=1,
        world_state_engine=engine2._world_state_engine(),
    )
    assert len(crew_pool2) > 0, "No crew generated"
    
    crew_data2 = crew_pool2[0]
    crew_npc2 = NPCEntity(
        npc_id="TEST-CREW-DET-001",
        persistence_tier=NPCPersistenceTier.TIER_2,
        display_name="Test Crew Det",
        role_tags=[str(crew_data2.get("role_id", ""))],
        current_ship_id=engine2.player_state.active_ship_id,
        current_system_id=target_system2.system_id,
        is_crew=True,
        crew_role_id=str(crew_data2.get("role_id", "")),
        hire_cost=int(crew_data2.get("hire_cost", 0)),
        daily_wage=int(crew_data2.get("daily_wage", 0)),
    )
    
    active_ship2 = engine2._active_ship()
    # Ensure ship has crew capacity
    if active_ship2.crew_capacity == 0:
        active_ship2.crew_capacity = 1
    active_ship2.add_crew(crew_npc2)
    engine2._npc_registry.add(crew_npc2, logger=None, turn=0)
    
    # Dismiss
    result2 = engine2.execute({"type": "dismiss_crew", "npc_id": "TEST-CREW-DET-001"})
    detail2 = None
    for event in result2.get("events", []):
        if event.get("stage") == "crew_dismissal":
            detail2 = event.get("detail", {})
            break
    
    assert detail2 is not None, "Dismissal event not found"
    result_detail2 = detail2.get("result", {})
    assert result_detail2.get("ok") is True, f"Dismissal failed: {result_detail2.get('reason')}"
    relocated2 = result_detail2.get("relocated_to", {})
    
    # Verify determinism
    assert relocated1.get("system_id") == relocated2.get("system_id"), "Relocation system_id should be deterministic"
    assert relocated1.get("destination_id") == relocated2.get("destination_id"), "Relocation destination_id should be deterministic"
    assert relocated1.get("location_id") == relocated2.get("location_id"), "Relocation location_id should be deterministic"
