from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class EntityType(str, Enum):
    PERSON = "person"
    PLACE = "place"
    OBJECT = "object"


@dataclass(frozen=True)
class Entity:
    entity_id: str
    entity_type: EntityType
    name: str
    emoji: str
    system_id: str
    location_id: str | None
    roles: List[str]
    tags: List[str]
    affiliations: List[str]
    connections: List[str]
    interaction_types: List[str]
    persistent_state: Dict[str, Any]
    memory_flags: Dict[str, Any]


def create_location_entity(
    *,
    entity_id: str,
    name: str,
    system_id: str,
    location_type: str,
    emoji: str = "",
) -> Entity:
    return Entity(
        entity_id=entity_id,
        entity_type=EntityType.PLACE,
        name=name,
        emoji=emoji,
        system_id=system_id,
        location_id=None,
        roles=[location_type],
        tags=[f"location_type:{location_type}"],
        affiliations=[],
        connections=[],
        interaction_types=[],
        persistent_state=_location_metadata(location_type),
        memory_flags={},
    )


def _location_metadata(location_type: str) -> Dict[str, Any]:
    if location_type != "datanet_terminal":
        return {}
    return {
        "interaction_registry": {
            "emergency_transport_to_nearest_shipdock": {
                "type": "placeholder",
                "notes": "metadata only; no execution logic",
            }
        }
    }
