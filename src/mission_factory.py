import hashlib
import json
import math
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from mission_entity import MissionEntity, MissionPersistenceScope, MissionState
from world_generator import System, Destination, Galaxy


def create_mission(
    *,
    source_type: str,
    source_id: str,
    system_id: str,
    destination_id: str | None,
    mission_type: str,
    mission_tier: int,
    payout_policy: str,
    claim_scope: str,
    persistence_scope: str = "ephemeral",
    objectives: List[str] | None = None,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    _validate_inputs(source_type, source_id, system_id, mission_type, mission_tier)
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=system_id,
        destination_id=destination_id,
        mission_type=mission_type,
        mission_tier=mission_tier,
    )
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type=mission_type,
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope(persistence_scope),
        mission_state=MissionState.OFFERED,
        system_id=system_id,
        origin_location_id=destination_id,
        objectives=list(objectives or []),
        payout_policy=payout_policy,
        claim_scope=claim_scope,
        reward_status="ungranted",  # Phase 7.11.2a - Required
        reward_granted_turn=None,  # Phase 7.11.2a - Required
    )
    _log_creation(logger, turn, mission_id, source_type, source_id, system_id, destination_id)
    return mission


def _validate_inputs(
    source_type: str,
    source_id: str,
    system_id: str,
    mission_type: str,
    mission_tier: int,
) -> None:
    # Allowed source_type values: "bar", "administration", "datanet", "victory"
    ALLOWED_SOURCE_TYPES = {"bar", "administration", "datanet", "victory"}
    
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(
            f"source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}, got '{source_type}'. "
            f"'system' and other arbitrary values are not allowed."
        )
    if not source_id:
        raise ValueError("source_id is required.")
    if not system_id:
        raise ValueError("system_id is required.")
    if not mission_type:
        raise ValueError("mission_type is required.")
    if mission_tier < 1 or mission_tier > 5:
        raise ValueError("mission_tier must be 1-5.")


def _deterministic_mission_id(
    *,
    source_type: str,
    source_id: str,
    system_id: str,
    destination_id: str | None,
    mission_type: str,
    mission_tier: int,
) -> str:
    seed = f"{source_type}|{source_id}|{system_id}|{destination_id}|{mission_type}|{mission_tier}"
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return f"MIS-{digest[:10]}"


def _log_creation(
    logger,
    turn: int,
    mission_id: str,
    source_type: str,
    source_id: str,
    system_id: str,
    destination_id: str | None,
) -> None:
    if logger is None:
        return
    logger.log(
        turn=turn,
        action="mission_create",
        state_change=(
            f"mission_id={mission_id} source_type={source_type} source_id={source_id} "
            f"system_id={system_id} destination_id={destination_id}"
        ),
    )


# Registry of mission creators by type (Phase 7.11.4 - all types implemented).
# This is used by generation code to determine which mission types are
# actually creatable. If a mission type is present in the mission registry
# but missing from this mapping, it must be excluded from generation.
# Functions are defined below, so this dict is populated at module load time.
CREATOR_BY_TYPE: Dict[str, Any] = {}

# Cached reward distribution data
_REWARD_DISTRIBUTIONS_CACHE: Dict[str, Any] | None = None


def _load_reward_distributions() -> Dict[str, Any]:
    """Load mission reward distributions from JSON (cached)."""
    global _REWARD_DISTRIBUTIONS_CACHE
    if _REWARD_DISTRIBUTIONS_CACHE is not None:
        return _REWARD_DISTRIBUTIONS_CACHE
    
    # Find data directory relative to src
    src_dir = Path(__file__).parent
    data_dir = src_dir.parent / "data"
    dist_file = data_dir / "mission_reward_distributions.json"
    
    if not dist_file.exists():
        # Fallback: return empty structure
        _REWARD_DISTRIBUTIONS_CACHE = {"reward_matrices": []}
        return _REWARD_DISTRIBUTIONS_CACHE
    
    with dist_file.open("r", encoding="utf-8") as f:
        _REWARD_DISTRIBUTIONS_CACHE = json.load(f)
    return _REWARD_DISTRIBUTIONS_CACHE


def _select_reward_profile_id(
    *,
    mission_type_id: str,
    tier: int,
    source_type: str,
    rng: random.Random,
) -> str:
    """
    Select a reward_profile_id from mission_reward_distributions.json.
    
    Falls back to "mission_credits_500" if no match found.
    """
    distributions = _load_reward_distributions()
    matrices = distributions.get("reward_matrices", [])
    
    # Find matching matrix entry
    candidates = []
    for matrix in matrices:
        category = str(matrix.get("mission_category", "") or "")
        matrix_tier = int(matrix.get("tier", 0) or 0)
        allowed_sources = matrix.get("allowed_source_types", [])
        
        if category == mission_type_id and matrix_tier == tier:
            if source_type in allowed_sources:
                profile_ids = matrix.get("reward_profile_ids", [])
                if profile_ids:
                    candidates.extend(profile_ids)
    
    if not candidates:
        # Fallback to credits
        return "mission_credits_500"
    
    return rng.choice(candidates)


def create_delivery_mission(
    *,
    source_type: str,
    source_id: str,
    origin_system_id: str,
    origin_destination_id: str | None,
    origin_location_id: str | None,
    mission_tier: int,
    galaxy: Galaxy,
    catalog: Any,
    rng: random.Random,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    """
    Create a delivery mission with structured schema (Phase 7.11.1).
    
    Implements:
    - Deterministic target selection (80% inter-system, 20% same-system)
    - Distance calculation
    - Cargo payload generation
    - Structured objectives and target fields
    - Reward profile assignment
    
    Args:
        source_type: Must be "bar", "administration", "datanet", or "victory" (enforced)
    """
    # Enforce source_type - validation happens in _validate_inputs
    _validate_inputs(source_type, source_id, origin_system_id, "delivery", mission_tier)
    
    # Get origin system and destination
    origin_system = galaxy.get_system(origin_system_id)
    if origin_system is None:
        raise ValueError(f"Origin system not found: {origin_system_id}")
    
    origin_destination = None
    if origin_destination_id:
        for dest in origin_system.destinations:
            if dest.destination_id == origin_destination_id:
                origin_destination = dest
                break
    
    # A. Target Selection (Deterministic: 80% inter-system, 20% same-system)
    is_inter_system = rng.random() < 0.8
    
    target_system_id: str
    target_destination_id: str
    
    if is_inter_system:
        # Inter-system: select a reachable system
        target_system = _select_inter_system_target(origin_system, galaxy, rng)
        if target_system is None:
            # Fallback to same-system if no reachable systems
            is_inter_system = False
            target_system_id = origin_system_id
        else:
            target_system_id = target_system.system_id
            # Select a destination within target system
            target_destination = _select_destination_in_system(target_system, rng)
            target_destination_id = target_destination.destination_id
    else:
        # Same-system: choose a different destination
        target_system_id = origin_system_id
        alternative_destinations = [
            d for d in origin_system.destinations
            if d.destination_id != origin_destination_id
        ]
        if not alternative_destinations:
            # Fallback to inter-system if no alternative destination
            target_system = _select_inter_system_target(origin_system, galaxy, rng)
            if target_system is None:
                raise ValueError("No valid target destination available")
            target_system_id = target_system.system_id
            is_inter_system = True
            target_destination = _select_destination_in_system(target_system, rng)
            target_destination_id = target_destination.destination_id
        else:
            target_destination = rng.choice(alternative_destinations)
            target_destination_id = target_destination.destination_id
    
    # B. Distance Calculation
    target_system = galaxy.get_system(target_system_id)
    if target_system is None:
        raise ValueError(f"Target system not found: {target_system_id}")
    
    distance_ly = 0
    if is_inter_system:
        distance_ly = _calculate_distance_ly(origin_system, target_system)
    else:
        distance_ly = 0  # Same-system travel
    
    # C. Reward Profile (Phase 7.11.4 - select from distributions)
    reward_profile_id = _select_reward_profile_id(
        mission_type_id="delivery",
        tier=mission_tier,
        source_type=source_type,
        rng=rng,
    )
    
    # D. Cargo Payload (deterministic, tier-scaled)
    cargo_payload = _generate_cargo_payload(mission_tier, catalog, rng)
    
    # E. Structured Target Field
    target = {
        "target_type": "destination",
        "target_id": target_destination_id,
        "system_id": target_system_id,
    }
    
    # F. Structured Objectives (goods must be a list)
    objectives = [
        {
            "objective_id": "OBJ-1",
            "objective_type": "deliver_cargo",
            "status": "pending",
            "parameters": {
                "goods": [cargo_payload]  # Always a list
            }
        }
    ]
    
    # G. Source Field
    source = {
        "source_type": source_type,
        "source_id": source_id,
    }
    
    # Origin field (simple structure)
    origin = {
        "system_id": origin_system_id,
        "destination_id": origin_destination_id or "",
    }
    
    # Generate mission_id (deterministic)
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=origin_system_id,
        destination_id=target_destination_id,
        mission_type="delivery",
        mission_tier=mission_tier,
    )
    
    # Create mission entity
    # Default payout configuration for delivery missions (Phase 7.11.2)
    payout_policy = "auto"
    claim_scope = "none"
    
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type="delivery",
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope.EPHEMERAL,
        mission_state=MissionState.OFFERED,
        system_id=origin_system_id,
        origin_location_id=origin_location_id,
        destination_location_id=None,  # Will be set based on target
        objectives=objectives,
        source=source,
        origin=origin,
        target=target,
        distance_ly=int(math.ceil(distance_ly)),
        reward_profile_id=reward_profile_id,
        payout_policy=payout_policy,
        claim_scope=claim_scope,
        reward_status="ungranted",  # Phase 7.11.2a - Required
        reward_granted_turn=None,  # Phase 7.11.2a - Required
    )
    
    _log_creation(logger, turn, mission_id, source_type, source_id, origin_system_id, target_destination_id)
    return mission


def _select_inter_system_target(origin_system: System, galaxy: Galaxy, rng: random.Random) -> System | None:
    """Select a reachable system for inter-system delivery (deterministic)."""
    all_systems = [s for s in galaxy.systems if s.system_id != origin_system.system_id]
    if not all_systems:
        return None
    
    # Use existing deterministic selection logic (select from neighbors or all systems)
    # For now, use all systems as candidates (reachability check happens elsewhere)
    return rng.choice(all_systems)


def _select_destination_in_system(system: System, rng: random.Random) -> Destination:
    """Select a destination within a system (deterministic)."""
    if not system.destinations:
        raise ValueError(f"System {system.system_id} has no destinations")
    return rng.choice(system.destinations)


def _calculate_distance_ly(origin: System, target: System) -> float:
    """Calculate travel distance between two systems."""
    dx = float(target.x) - float(origin.x)
    dy = float(target.y) - float(origin.y)
    return math.sqrt((dx * dx) + (dy * dy))


def _generate_cargo_payload(tier: int, catalog: Any, rng: random.Random) -> Dict[str, Any]:
    """Generate deterministic cargo payload based on tier."""
    # Get all valid goods from catalog
    goods_list = []
    if catalog is not None:
        if hasattr(catalog, "goods"):
            goods_list = list(catalog.goods.keys()) if hasattr(catalog.goods, "keys") else []
        elif hasattr(catalog, "get_all_goods"):
            goods_list = catalog.get_all_goods()
    
    # Try to load from data_catalog if still empty
    if not goods_list:
        try:
            from data_catalog import load_data_catalog
            catalog = load_data_catalog()
            if hasattr(catalog, "goods"):
                goods_list = list(catalog.goods.keys())
        except:
            pass
    
    # Ultimate fallback to common goods
    if not goods_list:
        goods_list = ["basic_rations", "fresh_produce", "iron_ore", "steel_ingots", "energy_cells"]
    
    # Select a good deterministically
    good_id = rng.choice(goods_list)
    
    # Tier scaling for quantity
    if tier == 1:
        quantity = rng.randint(1, 2)
    elif tier == 2:
        quantity = rng.randint(2, 4)
    else:  # Tier 3+
        quantity = rng.randint(tier, tier * 2)
    
    return {
        "good_id": good_id,
        "quantity": quantity,
    }


def create_bounty_mission(
    *,
    source_type: str,
    source_id: str,
    origin_system_id: str,
    origin_destination_id: str | None,
    origin_location_id: str | None,
    mission_tier: int,
    galaxy: Galaxy,
    catalog: Any,
    rng: random.Random,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    """Create a bounty mission (Phase 7.11.4)."""
    _validate_inputs(source_type, source_id, origin_system_id, "bounty", mission_tier)
    
    # Select target system (similar to delivery)
    origin_system = galaxy.get_system(origin_system_id)
    if origin_system is None:
        raise ValueError(f"Origin system not found: {origin_system_id}")
    
    # Inter-system target selection
    target_system = _select_inter_system_target(origin_system, galaxy, rng)
    if target_system is None:
        target_system_id = origin_system_id
        target_destination = _select_destination_in_system(origin_system, rng)
    else:
        target_system_id = target_system.system_id
        target_destination = _select_destination_in_system(target_system, rng)
    
    target_destination_id = target_destination.destination_id
    distance_ly = _calculate_distance_ly(origin_system, galaxy.get_system(target_system_id))
    
    # Reward profile selection
    reward_profile_id = _select_reward_profile_id(
        mission_type_id="bounty",
        tier=mission_tier,
        source_type=source_type,
        rng=rng,
    )
    
    # Objectives: ship_destroyed
    objectives = [
        {
            "objective_id": "OBJ-1",
            "objective_type": "ship_destroyed",
            "status": "pending",
            "parameters": {}
        }
    ]
    
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=origin_system_id,
        destination_id=target_destination_id,
        mission_type="bounty",
        mission_tier=mission_tier,
    )
    
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type="bounty",
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope.EPHEMERAL,
        mission_state=MissionState.OFFERED,
        system_id=origin_system_id,
        origin_location_id=origin_location_id,
        destination_location_id=None,
        objectives=objectives,
        source={"source_type": source_type, "source_id": source_id},
        origin={"system_id": origin_system_id, "destination_id": origin_destination_id or ""},
        target={"target_type": "destination", "target_id": target_destination_id, "system_id": target_system_id},
        distance_ly=int(math.ceil(distance_ly)),
        reward_profile_id=reward_profile_id,
        payout_policy="auto",
        claim_scope="none",
        reward_status="ungranted",
        reward_granted_turn=None,
    )
    
    _log_creation(logger, turn, mission_id, source_type, source_id, origin_system_id, target_destination_id)
    return mission


def create_patrol_mission(
    *,
    source_type: str,
    source_id: str,
    origin_system_id: str,
    origin_destination_id: str | None,
    origin_location_id: str | None,
    mission_tier: int,
    galaxy: Galaxy,
    catalog: Any,
    rng: random.Random,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    """Create a patrol mission (Phase 7.11.4)."""
    _validate_inputs(source_type, source_id, origin_system_id, "patrol", mission_tier)
    
    origin_system = galaxy.get_system(origin_system_id)
    if origin_system is None:
        raise ValueError(f"Origin system not found: {origin_system_id}")
    
    # Same-system patrol
    target_system_id = origin_system_id
    alternative_destinations = [
        d for d in origin_system.destinations
        if d.destination_id != origin_destination_id
    ]
    if not alternative_destinations:
        target_destination = _select_destination_in_system(origin_system, rng)
    else:
        target_destination = rng.choice(alternative_destinations)
    
    target_destination_id = target_destination.destination_id
    distance_ly = 0
    
    reward_profile_id = _select_reward_profile_id(
        mission_type_id="patrol",
        tier=mission_tier,
        source_type=source_type,
        rng=rng,
    )
    
    objectives = [
        {
            "objective_id": "OBJ-1",
            "objective_type": "inspection_completed",
            "status": "pending",
            "parameters": {}
        }
    ]
    
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=origin_system_id,
        destination_id=target_destination_id,
        mission_type="patrol",
        mission_tier=mission_tier,
    )
    
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type="patrol",
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope.EPHEMERAL,
        mission_state=MissionState.OFFERED,
        system_id=origin_system_id,
        origin_location_id=origin_location_id,
        destination_location_id=None,
        objectives=objectives,
        source={"source_type": source_type, "source_id": source_id},
        origin={"system_id": origin_system_id, "destination_id": origin_destination_id or ""},
        target={"target_type": "destination", "target_id": target_destination_id, "system_id": target_system_id},
        distance_ly=distance_ly,
        reward_profile_id=reward_profile_id,
        payout_policy="auto",
        claim_scope="none",
        reward_status="ungranted",
        reward_granted_turn=None,
    )
    
    _log_creation(logger, turn, mission_id, source_type, source_id, origin_system_id, target_destination_id)
    return mission


def create_smuggling_mission(
    *,
    source_type: str,
    source_id: str,
    origin_system_id: str,
    origin_destination_id: str | None,
    origin_location_id: str | None,
    mission_tier: int,
    galaxy: Galaxy,
    catalog: Any,
    rng: random.Random,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    """Create a smuggling mission (Phase 7.11.4)."""
    _validate_inputs(source_type, source_id, origin_system_id, "smuggling", mission_tier)
    
    origin_system = galaxy.get_system(origin_system_id)
    if origin_system is None:
        raise ValueError(f"Origin system not found: {origin_system_id}")
    
    # Inter-system target (80% like delivery)
    is_inter_system = rng.random() < 0.8
    if is_inter_system:
        target_system = _select_inter_system_target(origin_system, galaxy, rng)
        if target_system is None:
            target_system_id = origin_system_id
        else:
            target_system_id = target_system.system_id
        target_destination = _select_destination_in_system(galaxy.get_system(target_system_id), rng)
    else:
        target_system_id = origin_system_id
        alternative_destinations = [
            d for d in origin_system.destinations
            if d.destination_id != origin_destination_id
        ]
        if not alternative_destinations:
            target_system = _select_inter_system_target(origin_system, galaxy, rng)
            if target_system is None:
                raise ValueError("No valid target destination available")
            target_system_id = target_system.system_id
            target_destination = _select_destination_in_system(target_system, rng)
        else:
            target_destination = rng.choice(alternative_destinations)
    
    target_destination_id = target_destination.destination_id
    distance_ly = _calculate_distance_ly(origin_system, galaxy.get_system(target_system_id)) if is_inter_system else 0
    
    reward_profile_id = _select_reward_profile_id(
        mission_type_id="smuggling",
        tier=mission_tier,
        source_type=source_type,
        rng=rng,
    )
    
    # Cargo payload for smuggling
    cargo_payload = _generate_cargo_payload(mission_tier, catalog, rng)
    
    objectives = [
        {
            "objective_id": "OBJ-1",
            "objective_type": "cargo_delivered",
            "status": "pending",
            "parameters": {
                "goods": [cargo_payload]
            }
        }
    ]
    
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=origin_system_id,
        destination_id=target_destination_id,
        mission_type="smuggling",
        mission_tier=mission_tier,
    )
    
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type="smuggling",
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope.EPHEMERAL,
        mission_state=MissionState.OFFERED,
        system_id=origin_system_id,
        origin_location_id=origin_location_id,
        destination_location_id=None,
        objectives=objectives,
        source={"source_type": source_type, "source_id": source_id},
        origin={"system_id": origin_system_id, "destination_id": origin_destination_id or ""},
        target={"target_type": "destination", "target_id": target_destination_id, "system_id": target_system_id},
        distance_ly=int(math.ceil(distance_ly)),
        reward_profile_id=reward_profile_id,
        payout_policy="auto",
        claim_scope="none",
        reward_status="ungranted",
        reward_granted_turn=None,
    )
    
    _log_creation(logger, turn, mission_id, source_type, source_id, origin_system_id, target_destination_id)
    return mission


def create_exploration_mission(
    *,
    source_type: str,
    source_id: str,
    origin_system_id: str,
    origin_destination_id: str | None,
    origin_location_id: str | None,
    mission_tier: int,
    galaxy: Galaxy,
    catalog: Any,
    rng: random.Random,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    """Create an exploration mission (Phase 7.11.4)."""
    _validate_inputs(source_type, source_id, origin_system_id, "exploration", mission_tier)
    
    origin_system = galaxy.get_system(origin_system_id)
    if origin_system is None:
        raise ValueError(f"Origin system not found: {origin_system_id}")
    
    # Inter-system exploration target
    target_system = _select_inter_system_target(origin_system, galaxy, rng)
    if target_system is None:
        target_system_id = origin_system_id
    else:
        target_system_id = target_system.system_id
    
    target_destination = _select_destination_in_system(galaxy.get_system(target_system_id), rng)
    target_destination_id = target_destination.destination_id
    distance_ly = _calculate_distance_ly(origin_system, galaxy.get_system(target_system_id))
    
    reward_profile_id = _select_reward_profile_id(
        mission_type_id="exploration",
        tier=mission_tier,
        source_type=source_type,
        rng=rng,
    )
    
    objectives = [
        {
            "objective_id": "OBJ-1",
            "objective_type": "destination_visited",
            "status": "pending",
            "parameters": {
                "destination_id": target_destination_id,
                "system_id": target_system_id
            }
        }
    ]
    
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=origin_system_id,
        destination_id=target_destination_id,
        mission_type="exploration",
        mission_tier=mission_tier,
    )
    
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type="exploration",
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope.EPHEMERAL,
        mission_state=MissionState.OFFERED,
        system_id=origin_system_id,
        origin_location_id=origin_location_id,
        destination_location_id=None,
        objectives=objectives,
        source={"source_type": source_type, "source_id": source_id},
        origin={"system_id": origin_system_id, "destination_id": origin_destination_id or ""},
        target={"target_type": "destination", "target_id": target_destination_id, "system_id": target_system_id},
        distance_ly=int(math.ceil(distance_ly)),
        reward_profile_id=reward_profile_id,
        payout_policy="auto",
        claim_scope="none",
        reward_status="ungranted",
        reward_granted_turn=None,
    )
    
    _log_creation(logger, turn, mission_id, source_type, source_id, origin_system_id, target_destination_id)
    return mission


def create_retrieval_mission(
    *,
    source_type: str,
    source_id: str,
    origin_system_id: str,
    origin_destination_id: str | None,
    origin_location_id: str | None,
    mission_tier: int,
    galaxy: Galaxy,
    catalog: Any,
    rng: random.Random,
    logger=None,
    turn: int = 0,
) -> MissionEntity:
    """Create a retrieval mission (Phase 7.11.4)."""
    _validate_inputs(source_type, source_id, origin_system_id, "retrieval", mission_tier)
    
    origin_system = galaxy.get_system(origin_system_id)
    if origin_system is None:
        raise ValueError(f"Origin system not found: {origin_system_id}")
    
    # Inter-system target
    target_system = _select_inter_system_target(origin_system, galaxy, rng)
    if target_system is None:
        target_system_id = origin_system_id
    else:
        target_system_id = target_system.system_id
    
    target_destination = _select_destination_in_system(galaxy.get_system(target_system_id), rng)
    target_destination_id = target_destination.destination_id
    distance_ly = _calculate_distance_ly(origin_system, galaxy.get_system(target_system_id))
    
    # Use delivery reward distribution for retrieval
    reward_profile_id = _select_reward_profile_id(
        mission_type_id="delivery",  # Retrieval uses delivery reward profiles
        tier=mission_tier,
        source_type=source_type,
        rng=rng,
    )
    
    # Cargo payload
    cargo_payload = _generate_cargo_payload(mission_tier, catalog, rng)
    
    objectives = [
        {
            "objective_id": "OBJ-1",
            "objective_type": "cargo_acquired",
            "status": "pending",
            "parameters": {
                "goods": [cargo_payload]
            }
        }
    ]
    
    mission_id = _deterministic_mission_id(
        source_type=source_type,
        source_id=source_id,
        system_id=origin_system_id,
        destination_id=target_destination_id,
        mission_type="retrieval",
        mission_tier=mission_tier,
    )
    
    mission = MissionEntity(
        mission_id=mission_id,
        mission_type="retrieval",
        mission_tier=mission_tier,
        persistence_scope=MissionPersistenceScope.EPHEMERAL,
        mission_state=MissionState.OFFERED,
        system_id=origin_system_id,
        origin_location_id=origin_location_id,
        destination_location_id=None,
        objectives=objectives,
        source={"source_type": source_type, "source_id": source_id},
        origin={"system_id": origin_system_id, "destination_id": origin_destination_id or ""},
        target={"target_type": "destination", "target_id": target_destination_id, "system_id": target_system_id},
        distance_ly=int(math.ceil(distance_ly)),
        reward_profile_id=reward_profile_id,
        payout_policy="auto",
        claim_scope="none",
        reward_status="ungranted",
        reward_granted_turn=None,
    )
    
    _log_creation(logger, turn, mission_id, source_type, source_id, origin_system_id, target_destination_id)
    return mission


# Register all creators after they're defined
CREATOR_BY_TYPE["delivery"] = create_delivery_mission
CREATOR_BY_TYPE["bounty"] = create_bounty_mission
CREATOR_BY_TYPE["patrol"] = create_patrol_mission
CREATOR_BY_TYPE["smuggling"] = create_smuggling_mission
CREATOR_BY_TYPE["exploration"] = create_exploration_mission
CREATOR_BY_TYPE["retrieval"] = create_retrieval_mission
