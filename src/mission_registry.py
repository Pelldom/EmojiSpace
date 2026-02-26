from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class MissionTypeDefinition:
    """Data-driven mission type definition (Phase 7.11.2 registry).

    This registry is the single source of truth for which mission types
    are *eligible* for generation. Only types defined here can be offered.
    """

    mission_type_id: str
    base_weight: float
    allowed_source_types: List[str]
    mission_tags: List[str]


# Mission type registry (Option B - code-based for now).
#
# For Phase 7.11.2, ONLY delivery missions are implemented as structured
# missions. Additional types (e.g., bounty) can be added here later once
# their creators exist in mission_factory.CREATOR_BY_TYPE.
_MISSION_TYPES: List[MissionTypeDefinition] = [
    MissionTypeDefinition(
        mission_type_id="delivery",
        base_weight=1.0,
        allowed_source_types=["bar", "administration", "datanet"],
        mission_tags=["delivery", "cargo"],
    ),
    # Example future extension (disabled until creator exists):
    # MissionTypeDefinition(
    #     mission_type_id="bounty",
    #     base_weight=1.0,
    #     allowed_source_types=["administration", "datanet"],
    #     mission_tags=["combat", "bounty"],
    # ),
]


def mission_type_candidates_for_source(source_type: str) -> List[Dict[str, Any]]:
    """Return mission type candidate rows for a given source_type.

    Returned rows are compatible with mission_generator.select_weighted_mission_type:
      - mission_type_id: str
      - base_weight: float
      - mission_tags: list[str]

    Filtering is deterministic and based solely on allowed_source_types.
    """
    source_type = str(source_type or "").strip()
    rows: List[Dict[str, Any]] = []
    for entry in _MISSION_TYPES:
        if source_type and source_type not in entry.allowed_source_types:
            continue
        rows.append(
            {
                "mission_type_id": entry.mission_type_id,
                "base_weight": float(entry.base_weight),
                "mission_tags": list(entry.mission_tags or []),
            }
        )
    return rows

