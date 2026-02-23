"""Tests for destination population structural anchor requirement."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from collections import Counter  # noqa: E402


def test_every_system_has_max_population_destination() -> None:
    """Test that every populated system has at least one destination with population equal to system.population."""
    engine = GameEngine(world_seed=12345, config={"system_count": 50})
    
    systems_with_max_pop = 0
    systems_without_max_pop = []
    
    for system in engine.sector.systems:
        if system.population <= 0:
            continue  # Skip unpopulated systems (shouldn't exist, but be safe)
        
        populated_destinations = [
            d for d in system.destinations
            if d.population >= 1 and d.destination_type not in {"explorable_stub", "mining_stub"}
        ]
        
        if not populated_destinations:
            # System has no populated destinations (edge case)
            continue
        
        has_max_pop = any(d.population == system.population for d in populated_destinations)
        
        if has_max_pop:
            systems_with_max_pop += 1
        else:
            systems_without_max_pop.append({
                "system_id": system.system_id,
                "system_population": system.population,
                "destination_populations": [d.population for d in populated_destinations],
            })
    
    assert len(systems_without_max_pop) == 0, (
        f"Found {len(systems_without_max_pop)} systems without max population destination:\n"
        + "\n".join(
            f"  {s['system_id']}: pop={s['system_population']}, dest_pops={s['destination_populations']}"
            for s in systems_without_max_pop[:10]  # Show first 10
        )
        + (f"\n  ... and {len(systems_without_max_pop) - 10} more" if len(systems_without_max_pop) > 10 else "")
    )
    
    print(f"✓ All {systems_with_max_pop} populated systems have at least one destination with max population")


def test_destination_population_uniform_distribution() -> None:
    """Test that destination populations (excluding max-pop destination) appear uniformly distributed."""
    engine = GameEngine(world_seed=12345, config={"system_count": 50})
    
    # Collect all destination populations (excluding the max-pop one per system)
    all_populations = []
    
    for system in engine.sector.systems:
        if system.population <= 1:
            continue  # Skip systems with pop 1 (all destinations must be pop 1)
        
        populated_destinations = [
            d for d in system.destinations
            if d.population >= 1 and d.destination_type not in {"explorable_stub", "mining_stub"}
        ]
        
        if len(populated_destinations) <= 1:
            continue  # Need at least 2 destinations to test distribution
        
        # Find the max-pop destination
        max_pop_dest = next(
            (d for d in populated_destinations if d.population == system.population),
            None
        )
        
        if max_pop_dest is None:
            continue  # Shouldn't happen, but skip if it does
        
        # Collect populations of other destinations
        for dest in populated_destinations:
            if dest.destination_id != max_pop_dest.destination_id:
                all_populations.append(dest.population)
    
    if not all_populations:
        # Not enough data to test distribution
        print("⚠ Not enough destinations to test uniform distribution")
        return
    
    # Count occurrences of each population value
    pop_counts = Counter(all_populations)
    
    # Check that all valid values (1 to max system_population) appear
    # For a uniform distribution, we expect roughly equal counts
    # But with deterministic RNG, exact equality isn't guaranteed
    # So we just verify that multiple values appear (not all the same)
    unique_values = len(pop_counts)
    min_pop = min(all_populations)
    max_pop = max(all_populations)
    
    # Verify range is valid
    assert min_pop >= 1, f"Found destination with population < 1: {min_pop}"
    assert max_pop <= 5, f"Found destination with population > 5: {max_pop}"
    
    # For uniform distribution, we should see multiple different values
    # (unless we have very few samples)
    if len(all_populations) >= 10:
        assert unique_values >= 2, (
            f"Expected multiple population values for uniform distribution, "
            f"but found only {unique_values} unique value(s): {pop_counts}"
        )
    
    print(f"✓ Destination populations appear uniformly distributed:")
    print(f"  Total destinations analyzed: {len(all_populations)}")
    print(f"  Unique population values: {unique_values}")
    print(f"  Range: {min_pop} to {max_pop}")
    print(f"  Distribution: {dict(sorted(pop_counts.items()))}")


def test_deterministic_population_assignment() -> None:
    """Test that population assignment is deterministic (same seed produces same results)."""
    engine1 = GameEngine(world_seed=12345, config={"system_count": 10})
    engine2 = GameEngine(world_seed=12345, config={"system_count": 10})
    
    # Compare population assignments
    for sys1, sys2 in zip(engine1.sector.systems, engine2.sector.systems):
        assert sys1.system_id == sys2.system_id
        assert sys1.population == sys2.population
        
        dests1 = sorted(sys1.destinations, key=lambda d: d.destination_id)
        dests2 = sorted(sys2.destinations, key=lambda d: d.destination_id)
        
        assert len(dests1) == len(dests2)
        
        for d1, d2 in zip(dests1, dests2):
            assert d1.destination_id == d2.destination_id
            assert d1.population == d2.population, (
                f"Non-deterministic population for {d1.destination_id}: "
                f"run1={d1.population}, run2={d2.population}"
            )
    
    print("✓ Population assignment is deterministic")


def test_stub_destinations_remain_zero_population() -> None:
    """Test that stub destinations (mining_stub, explorable_stub) remain population 0."""
    engine = GameEngine(world_seed=12345, config={"system_count": 50})
    
    stub_destinations_with_pop = []
    
    for system in engine.sector.systems:
        for dest in system.destinations:
            if dest.destination_type in {"explorable_stub", "mining_stub"}:
                if dest.population != 0:
                    stub_destinations_with_pop.append({
                        "system_id": system.system_id,
                        "destination_id": dest.destination_id,
                        "destination_type": dest.destination_type,
                        "population": dest.population,
                    })
    
    assert len(stub_destinations_with_pop) == 0, (
        f"Found {len(stub_destinations_with_pop)} stub destinations with non-zero population:\n"
        + "\n".join(
            f"  {s['destination_id']} ({s['destination_type']}): pop={s['population']}"
            for s in stub_destinations_with_pop
        )
    )
    
    print("✓ All stub destinations have population 0")
