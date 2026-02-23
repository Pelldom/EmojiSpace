"""Tests for names.json validation and worldgen name usage."""

import json
import re
from pathlib import Path

import pytest

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from world_generator import WorldGenerator, _load_names
from data_catalog import load_data_catalog
from government_registry import GovernmentRegistry


def test_names_json_exists() -> None:
    """Test that names.json exists."""
    path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    assert path.exists(), f"names.json must exist at {path}"


def test_names_json_structure() -> None:
    """Test that names.json has correct structure."""
    # Load directly to avoid validation errors
    path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    
    assert "systems" in data
    assert "planets" in data
    assert "stations" in data
    
    assert isinstance(data["systems"], list)
    assert isinstance(data["planets"], list)
    assert isinstance(data["stations"], list)


def test_names_json_minimum_counts() -> None:
    """Test that names.json meets minimum count requirements."""
    names_data = _load_names()
    
    assert len(names_data["systems"]) >= 200, (
        f"names.json 'systems' must have at least 200 names, got {len(names_data['systems'])}"
    )
    assert len(names_data["planets"]) >= 250, (
        f"names.json 'planets' must have at least 250 names, got {len(names_data['planets'])}"
    )
    assert len(names_data["stations"]) >= 240, (
        f"names.json 'stations' must have at least 240 names, got {len(names_data['stations'])}"
    )


def test_names_json_no_duplicates() -> None:
    """Test that names.json lists contain no duplicates."""
    # Load directly to avoid validation errors
    path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    
    systems = data["systems"]
    planets = data["planets"]
    stations = data["stations"]
    
    assert len(systems) == len(set(systems)), (
        f"names.json 'systems' contains duplicates: "
        f"{[name for name in systems if systems.count(name) > 1]}"
    )
    assert len(planets) == len(set(planets)), (
        f"names.json 'planets' contains duplicates: "
        f"{[name for name in planets if planets.count(name) > 1]}"
    )
    assert len(stations) == len(set(stations)), (
        f"names.json 'stations' contains duplicates: "
        f"{[name for name in stations if stations.count(name) > 1]}"
    )


def test_names_json_ascii_only() -> None:
    """Test that all names in names.json are ASCII-only."""
    # Load directly to avoid validation errors
    path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    
    for list_name, name_list in [
        ("systems", data["systems"]),
        ("planets", data["planets"]),
        ("stations", data["stations"]),
    ]:
        for name in name_list:
            assert isinstance(name, str), (
                f"names.json '{list_name}' contains non-string value: {name!r}"
            )
            assert all(ord(c) < 128 for c in name), (
                f"names.json '{list_name}' contains non-ASCII name: {name!r}. "
                "All names must be ASCII-only (ord(c) < 128)."
            )


def test_load_names_missing_file() -> None:
    """Test that _load_names() raises FileNotFoundError if file is missing."""
    import tempfile
    import shutil
    
    # Save original path
    original_path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    temp_backup = original_path.with_suffix(".json.backup")
    
    try:
        # Move file temporarily
        if original_path.exists():
            shutil.move(str(original_path), str(temp_backup))
        
        # Try to load - should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="names.json not found"):
            _load_names()
    finally:
        # Restore file
        if temp_backup.exists():
            shutil.move(str(temp_backup), str(original_path))


def test_load_names_malformed_json() -> None:
    """Test that _load_names() raises ValueError if JSON is malformed."""
    import tempfile
    import shutil
    
    original_path = Path(__file__).resolve().parents[1] / "data" / "names.json"
    temp_backup = original_path.with_suffix(".json.backup")
    
    try:
        # Backup original
        if original_path.exists():
            shutil.copy2(str(original_path), str(temp_backup))
        
        # Write malformed JSON
        original_path.write_text("{ invalid json }", encoding="utf-8")
        
        # Try to load - should raise ValueError
        with pytest.raises(ValueError, match="names.json is malformed JSON"):
            _load_names()
    finally:
        # Restore file
        if temp_backup.exists():
            shutil.move(str(temp_backup), str(original_path))


def test_worldgen_no_fallback_names() -> None:
    """Test that worldgen does not use fallback names."""
    catalog = load_data_catalog()
    registry = GovernmentRegistry.from_file(
        Path(__file__).resolve().parents[1] / "data" / "governments.json"
    )
    government_ids = registry.government_ids()
    
    generator = WorldGenerator(
        seed=12345,
        system_count=100,
        government_ids=government_ids,
        catalog=catalog,
    )
    
    galaxy = generator.generate()
    
    # Check system names - no fallback names like "System123"
    fallback_system_pattern = re.compile(r"^System[0-9]+$", re.IGNORECASE)
    for system in galaxy.systems:
        assert not fallback_system_pattern.match(system.name), (
            f"System {system.system_id} has fallback name: {system.name}"
        )
        assert not system.name.startswith("System"), (
            f"System {system.system_id} has name starting with 'System': {system.name}"
        )
    
    # Check planet names - no fallback names like "Planet123"
    planet_pattern = re.compile(r"^Planet[0-9]+$", re.IGNORECASE)
    for system in galaxy.systems:
        for destination in system.destinations:
            if destination.destination_type == "planet":
                assert not planet_pattern.match(destination.display_name), (
                    f"Planet {destination.destination_id} has fallback name: {destination.display_name}"
                )
    
    # Check station names - no fallback names like "Station123"
    station_pattern = re.compile(r"^Station[0-9]+$", re.IGNORECASE)
    for system in galaxy.systems:
        for destination in system.destinations:
            if destination.destination_type == "station":
                assert not station_pattern.match(destination.display_name), (
                    f"Station {destination.destination_id} has fallback name: {destination.display_name}"
                )


def test_worldgen_deterministic_naming() -> None:
    """Test that worldgen produces deterministic names for same seed."""
    catalog = load_data_catalog()
    registry = GovernmentRegistry.from_file(
        Path(__file__).resolve().parents[1] / "data" / "governments.json"
    )
    government_ids = registry.government_ids()
    
    # Generate twice with same seed
    generator1 = WorldGenerator(
        seed=12345,
        system_count=50,
        government_ids=government_ids,
        catalog=catalog,
    )
    galaxy1 = generator1.generate()
    
    generator2 = WorldGenerator(
        seed=12345,
        system_count=50,
        government_ids=government_ids,
        catalog=catalog,
    )
    galaxy2 = generator2.generate()
    
    # Verify all system names match
    assert len(galaxy1.systems) == len(galaxy2.systems)
    for sys1, sys2 in zip(galaxy1.systems, galaxy2.systems):
        assert sys1.name == sys2.name, (
            f"System {sys1.system_id} name mismatch: {sys1.name} != {sys2.name}"
        )
        
        # Verify destination names match
        assert len(sys1.destinations) == len(sys2.destinations)
        for dest1, dest2 in zip(sys1.destinations, sys2.destinations):
            if dest1.destination_type in {"planet", "station"}:
                assert dest1.display_name == dest2.display_name, (
                    f"Destination {dest1.destination_id} name mismatch: "
                    f"{dest1.display_name} != {dest2.display_name}"
                )
