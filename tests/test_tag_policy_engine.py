import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from government_law_engine import GovernmentLawEngine  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
class _NullLogger:
    def log(self, **kwargs):  # noqa: ANN003
        return None


def test_tag_policy_interpretation_is_risk_only_for_law_engine() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_id = registry.government_ids()[0]
    government = registry.get_government(government_id)
    tags = {"weaponized", "stolen"}

    law_engine = GovernmentLawEngine(registry=registry, logger=_NullLogger(), seed=1)
    law_bias, law_risk, interpreted = law_engine._interpret_tags(government, tags)  # noqa: SLF001

    assert interpreted == tags
    assert law_bias == 0.0
    assert law_risk.value in {"None", "Low", "Medium", "High", "Severe"}

