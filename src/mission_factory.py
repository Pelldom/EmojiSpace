import hashlib
from typing import Any, Dict, List

from mission_entity import MissionEntity, MissionPersistenceScope, MissionState


def create_mission(
    *,
    source_type: str,
    source_id: str,
    system_id: str,
    destination_id: str | None,
    mission_type: str,
    mission_tier: int,
    persistence_scope: str = "ephemeral",
    objectives: List[str] | None = None,
    rewards: List[Dict[str, Any]] | None = None,
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
        rewards=list(rewards or []),
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
    if source_type not in {"npc", "datanet", "system"}:
        raise ValueError("source_type must be npc, datanet, or system.")
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
