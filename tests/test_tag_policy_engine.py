import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from government_law_engine import GovernmentLawEngine  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
from market_pricing import _interpret_tags as pricing_interpret_tags  # noqa: E402


class _NullLogger:
    def log(self, **kwargs):  # noqa: ANN003
        return None


def test_tag_policy_interpretation_parity_between_law_and_pricing() -> None:
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    government_id = registry.government_ids()[0]
    government = registry.get_government(government_id)
    tags = {"weaponized", "stolen"}

    law_engine = GovernmentLawEngine(registry=registry, logger=_NullLogger(), seed=1)
    law_bias, law_risk, interpreted = law_engine._interpret_tags(government, tags)  # noqa: SLF001
    pricing_bias, pricing_risk = pricing_interpret_tags(government, sorted(tags))

    assert interpreted == tags
    assert law_bias == pricing_bias
    assert law_risk.value == pricing_risk.value

