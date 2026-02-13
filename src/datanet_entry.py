from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DataNetEntry:
    datanet_id: str = ""
    datanet_type: str = "news"
    source_type: str = "system"
    scope: str = "system"
    truth_band: str = "accurate"
    censorship_level: str = "none"
    related_ids: List[str] = field(default_factory=list)
    prose_text: str = ""
    persistence: str = "ephemeral"
    is_red_herring: bool = False

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DataNetEntry":
        state = cls()
        for key, value in payload.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "datanet_id": self.datanet_id,
            "datanet_type": self.datanet_type,
            "source_type": self.source_type,
            "scope": self.scope,
            "truth_band": self.truth_band,
            "censorship_level": self.censorship_level,
            "related_ids": list(self.related_ids),
            "prose_text": self.prose_text,
            "persistence": self.persistence,
            "is_red_herring": self.is_red_herring,
        }
