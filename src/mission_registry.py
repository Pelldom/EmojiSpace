import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

# Cached alien mission definitions
_ALIEN_MISSIONS_CACHE: List[Dict[str, Any]] | None = None


def _load_alien_mission_definitions() -> List[Dict[str, Any]]:
    """Load alien mission definitions from JSON (cached)."""
    global _ALIEN_MISSIONS_CACHE
    if _ALIEN_MISSIONS_CACHE is not None:
        return _ALIEN_MISSIONS_CACHE
    
    src_dir = Path(__file__).parent
    data_dir = src_dir.parent / "data"
    def_file = data_dir / "mission_definitions.json"
    
    if not def_file.exists():
        _ALIEN_MISSIONS_CACHE = []
        return _ALIEN_MISSIONS_CACHE
    
    with def_file.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    
    missions = payload.get("missions", [])
    _ALIEN_MISSIONS_CACHE = missions if isinstance(missions, list) else []
    return _ALIEN_MISSIONS_CACHE


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
# Phase 7.11.4: All mission types registered and wired.
_MISSION_TYPES: List[MissionTypeDefinition] = [
    MissionTypeDefinition(
        mission_type_id="delivery",
        base_weight=1.0,
        allowed_source_types=["bar", "administration", "datanet"],
        mission_tags=[],
    ),
    MissionTypeDefinition(
        mission_type_id="bounty",
        base_weight=1.0,
        allowed_source_types=["administration"],
        mission_tags=[],
    ),
    MissionTypeDefinition(
        mission_type_id="patrol",
        base_weight=1.0,
        allowed_source_types=["administration"],
        mission_tags=[],
    ),
    MissionTypeDefinition(
        mission_type_id="smuggling",
        base_weight=1.0,
        allowed_source_types=["bar"],
        mission_tags=[],
    ),
    MissionTypeDefinition(
        mission_type_id="exploration",
        base_weight=1.0,
        allowed_source_types=["bar", "administration", "datanet"],
        mission_tags=[],
    ),
    MissionTypeDefinition(
        mission_type_id="retrieval",
        base_weight=1.0,
        allowed_source_types=["bar", "administration"],
        mission_tags=[],
    ),
]


def mission_type_candidates_for_source(
    source_type: str,
    progression_context: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Return mission type candidate rows for a given source_type.

    Returned rows are compatible with mission_generator.select_weighted_mission_type:
      - mission_type_id: str
      - base_weight: float
      - mission_tags: list[str]
      - progression_gate: dict (optional, for alien missions)

    Filtering is deterministic and based solely on allowed_source_types.
    Phase 7.11.4: Also includes eligible alien missions from mission_definitions.json.
    """
    source_type = str(source_type or "").strip()
    rows: List[Dict[str, Any]] = []
    
    # Add standard mission types
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
    
    # Phase 7.11.4: Add eligible alien missions
    alien_defs = _load_alien_mission_definitions()
    for alien_mission in alien_defs:
        allowed_sources = alien_mission.get("allowed_source_types", [])
        if source_type not in allowed_sources:
            continue
        
        # Check progression gate if present
        gate = alien_mission.get("progression_gate")
        if gate and progression_context:
            # Inline progression gate check to avoid circular import
            requires_tag = str(gate.get("requires_tag", "") or "").strip()
            if requires_tag:
                try:
                    min_completed = int(gate.get("min_completed_with_tag", 0) or 0)
                except (TypeError, ValueError):
                    min_completed = 0
                
                completed_by_tag = progression_context.get("completed_missions_by_tag", {}) or {}
                try:
                    completed_count = int(completed_by_tag.get(requires_tag, 0) or 0)
                except (TypeError, ValueError):
                    completed_count = 0
                
                if completed_count < min_completed:
                    continue
        
        # Convert alien mission to candidate format
        mission_type = str(alien_mission.get("mission_type", "delivery") or "delivery")
        # Handle "delivery_or_retrieval" by choosing delivery for now
        if mission_type == "delivery_or_retrieval":
            mission_type = "delivery"
        
        candidate = {
            "mission_type_id": alien_mission.get("mission_id", ""),  # Use mission_id as identifier
            "base_weight": 1.0,  # Default weight
            "mission_tags": list(alien_mission.get("tags", [])),
            "is_alien_mission": True,  # Flag to identify alien missions
            "alien_definition": alien_mission,  # Store full definition
        }
        
        # Include progression_gate if present
        if gate:
            candidate["progression_gate"] = gate
        
        rows.append(candidate)
    
    return rows

