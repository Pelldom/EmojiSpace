import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from government_type import GovernmentType


@dataclass(frozen=True)
class GovernmentRegistry:
    _governments: Dict[str, GovernmentType]
    _government_ids: List[str]

    @classmethod
    def from_file(cls, path: Path) -> "GovernmentRegistry":
        data = json.loads(path.read_text(encoding="utf-8"), strict=False)
        governments = data.get("governments", [])
        registry: Dict[str, GovernmentType] = {}
        government_ids: List[str] = []
        for entry in governments:
            government = GovernmentType(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                regulation_level=entry["regulation_level"],
                enforcement_strength=entry["enforcement_strength"],
                penalty_severity=entry["penalty_severity"],
                tolerance_bias=entry["tolerance_bias"],
                bribery_susceptibility=entry["bribery_susceptibility"],
                ideological_modifiers=entry["ideological_modifiers"],
                illegal_goods=entry["illegal_goods"],
            )
            if government.id in registry:
                raise ValueError(f"Duplicate government id: {government.id}")
            registry[government.id] = government
            government_ids.append(government.id)
        if not registry:
            raise ValueError("No governments loaded from JSON.")
        return cls(_governments=registry, _government_ids=government_ids)

    def get_government(self, government_id: str) -> GovernmentType:
        if government_id not in self._governments:
            raise KeyError(f"Unknown government id: {government_id}")
        return self._governments[government_id]

    def government_ids(self) -> List[str]:
        return list(self._government_ids)
