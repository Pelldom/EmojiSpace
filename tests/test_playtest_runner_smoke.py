import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from playtest_runner import run_playtest  # noqa: E402


def test_playtest_runner_writes_transcript_and_events() -> None:
    summary = run_playtest(seed=12345, turns=5, bias="B", output_dir="tests/output")
    transcript_path = Path(summary["transcript_path"])
    events_path = Path(summary["events_path"])
    assert transcript_path.exists()
    assert events_path.exists()
    assert transcript_path.stat().st_size > 0
    assert events_path.stat().st_size > 0
