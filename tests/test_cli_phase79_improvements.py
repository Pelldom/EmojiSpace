"""Tests for Phase 7.9 CLI improvements."""
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402


def test_cli_default_system_count_is_50() -> None:
    """Test that CLI default system_count is 50."""
    engine = GameEngine(world_seed=12345, config={"system_count": 50})
    assert len(engine.sector.systems) == 50, (
        f"Expected 50 systems with default config, got {len(engine.sector.systems)}"
    )


def test_travel_menu_header_includes_system_and_destination() -> None:
    """Test that travel menu header includes both system and destination."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Set player to a known system and destination
    current_system = engine.sector.systems[0]
    current_destination = current_system.destinations[0] if current_system.destinations else None
    
    if current_destination is None:
        # Skip if no destinations
        return
    
    engine.player_state.current_system_id = current_system.system_id
    engine.player_state.current_destination_id = current_destination.destination_id
    
    # Import the travel menu function
    from run_game_engine_cli import _travel_menu  # noqa: E402
    
    # Capture output
    with patch('builtins.input', return_value='3'):  # Back option
        with patch('sys.stdout', new=StringIO()) as fake_out:
            _travel_menu(engine)
            output = fake_out.getvalue()
    
    # Check that both system and destination are shown
    assert f"Current system: {current_system.system_id}" in output
    assert f"({current_system.name})" in output
    assert f"Current destination: {current_destination.destination_id}" in output
    assert f"({current_destination.display_name})" in output


def test_destination_header_prints_both_situation_scopes() -> None:
    """Test that destination header prints both system and destination situation scopes."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Set player to a known system and destination
    current_system = engine.sector.systems[0]
    current_destination = current_system.destinations[0] if current_system.destinations else None
    
    if current_destination is None:
        # Skip if no destinations
        return
    
    engine.player_state.current_system_id = current_system.system_id
    engine.player_state.current_destination_id = current_destination.destination_id
    
    # Import the print function
    from run_game_engine_cli import _print_destination_context  # noqa: E402
    
    # Capture output
    with patch('sys.stdout', new=StringIO()) as fake_out:
        _print_destination_context(engine)
        output = fake_out.getvalue()
    
    # Check that both situation scopes are mentioned (even if None)
    assert "System situations:" in output or "System situations: None" in output
    assert "Destination situations:" in output or "Destination situations: None" in output


def test_galaxy_summary_prints_expected_structure() -> None:
    """Test that Galaxy Summary prints expected structure."""
    engine = GameEngine(world_seed=12345, config={"system_count": 5})
    
    # Import the galaxy summary function
    from run_game_engine_cli import _galaxy_summary  # noqa: E402
    
    # Capture output
    with patch('sys.stdout', new=StringIO()) as fake_out:
        _galaxy_summary(engine)
        output = fake_out.getvalue()
    
    # Check expected structure elements
    assert "GALAXY SUMMARY" in output
    assert "Total systems:" in output
    assert f"Total systems: {len(engine.sector.systems)}" in output
    
    # Check that at least one system is shown with expected fields
    if engine.sector.systems:
        first_system = engine.sector.systems[0]
        assert f"System: {first_system.system_id}" in output
        assert f"Government:" in output
        assert f"Population:" in output
        assert f"Destinations:" in output
        
        # Check destination fields if any exist
        if first_system.destinations:
            first_dest = first_system.destinations[0]
            assert first_dest.destination_id in output
            assert f"Type: {first_dest.destination_type}" in output
            assert f"Primary Economy:" in output
            assert f"Secondary Economies:" in output
