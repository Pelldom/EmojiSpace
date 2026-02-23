import sys
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from run_game_engine_cli import _show_system_info  # noqa: E402


def test_starting_location_marked_visited_on_init() -> None:
    engine = GameEngine(world_seed=12345)
    assert engine.player_state.current_system_id in engine.player_state.visited_system_ids
    assert engine.player_state.current_destination_id in engine.player_state.visited_destination_ids


def test_initialization_marker_is_not_injected_into_command_events() -> None:
    engine = GameEngine(world_seed=12345)
    first = engine.execute({"type": "get_system_profile"})
    second = engine.execute({"type": "get_system_profile"})

    first_stages = [event.get("stage") for event in first.get("events", []) if isinstance(event, dict)]
    second_stages = [event.get("stage") for event in second.get("events", []) if isinstance(event, dict)]

    assert "initialization" not in first_stages
    assert "initialization" not in second_stages


def test_system_info_no_unknown_for_starting_system() -> None:
    engine = GameEngine(world_seed=12345)
    stream = StringIO()
    with redirect_stdout(stream):
        _show_system_info(engine)
    text = stream.getvalue()
    assert "Government: Unknown" not in text
    assert "Population: Unknown" not in text
    assert "Active situations: Unknown" not in text
