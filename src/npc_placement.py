import hashlib
from typing import List

from npc_entity import NPCEntity, NPCPersistenceTier
from npc_registry import NPCRegistry


def resolve_npcs_for_location(
    *,
    location_id: str,
    location_type: str,
    system_id: str,
    registry: NPCRegistry,
    logger=None,
    turn: int = 0,
) -> List[NPCEntity]:
    if location_type not in {"bar", "administration"}:
        return []
    role = "bartender" if location_type == "bar" else "administrator"
    npc_id = _deterministic_npc_id(location_id, role)
    npc = registry.get(npc_id)
    if npc is None:
        npc = NPCEntity(
            npc_id=npc_id,
            persistence_tier=NPCPersistenceTier.TIER_3,
            display_name=role.replace("_", " ").title(),
            role_tags=[role],
            current_location_id=location_id,
            current_system_id=system_id,
        )
        registry.add(npc, logger=logger, turn=turn)
        _log_placement(logger, turn, location_id, npc_id, "created")
    else:
        _log_placement(logger, turn, location_id, npc_id, "resolved")
    return [npc]


def _deterministic_npc_id(location_id: str, role: str) -> str:
    digest = hashlib.md5(f"{location_id}:{role}".encode("utf-8")).hexdigest()
    return f"NPC-{digest[:8]}"


def _log_placement(logger, turn: int, location_id: str, npc_id: str, action: str) -> None:
    if logger is None:
        return
    logger.log(
        turn=turn,
        action="npc_placement",
        state_change=f"{action} location_id={location_id} npc_id={npc_id}",
    )
