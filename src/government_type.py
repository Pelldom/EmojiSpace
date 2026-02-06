from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GovernmentType:
    id: str
    name: str
    description: str
    regulation_level: int
    enforcement_strength: int
    penalty_severity: int
    tolerance_bias: int
    bribery_susceptibility: int
    ideological_modifiers: Dict[str, List[str]]
    illegal_goods: List[str]

    def __post_init__(self) -> None:
        numeric_fields = [
            ("regulation_level", self.regulation_level),
            ("enforcement_strength", self.enforcement_strength),
            ("penalty_severity", self.penalty_severity),
            ("tolerance_bias", self.tolerance_bias),
            ("bribery_susceptibility", self.bribery_susceptibility),
        ]
        for field_name, value in numeric_fields:
            if not 0 <= value <= 100:
                raise ValueError(f"{field_name} must be within 0-100: {value}")
