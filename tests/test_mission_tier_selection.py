"""Tests for deterministic weighted mission tier selection."""
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from logger import Logger  # noqa: E402
from player_state import PlayerState  # noqa: E402


def test_tier_selection_deterministic() -> None:
    """Test that tier selection is deterministic with fixed seed."""
    # Create minimal engine setup
    seed = 12345
    engine = GameEngine(world_seed=seed)
    
    # Test each source_type multiple times with same seed
    source_types = ["bar", "administration", "datanet"]
    
    for source_type in source_types:
        # Generate two sequences with same seed
        rng1 = random.Random(seed)
        rng2 = random.Random(seed)
        
        tiers1 = []
        tiers2 = []
        for _ in range(100):
            tier1 = engine._select_mission_tier(source_type, rng1)
            tier2 = engine._select_mission_tier(source_type, rng2)
            tiers1.append(tier1)
            tiers2.append(tier2)
        
        # Sequences must be identical
        assert tiers1 == tiers2, f"Tier selection not deterministic for {source_type}"


def test_tier_distribution_bar() -> None:
    """Test bar tier distribution: T1 > T2 > T3, T4+T5 < 10%."""
    engine = GameEngine(world_seed=42)
    rng = random.Random(42)
    
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    n = 5000
    
    for _ in range(n):
        tier = engine._select_mission_tier("bar", rng)
        counts[tier] = counts.get(tier, 0) + 1
    
    # T1 should be most common
    assert counts[1] > counts[2], f"T1 ({counts[1]}) should be > T2 ({counts[2]})"
    # T2 should be > T3
    assert counts[2] > counts[3], f"T2 ({counts[2]}) should be > T3 ({counts[3]})"
    # T4 + T5 should be < 10%
    high_tier_pct = (counts[4] + counts[5]) / n * 100
    assert high_tier_pct < 10.0, f"T4+T5 ({high_tier_pct:.1f}%) should be < 10%"


def test_tier_distribution_administration() -> None:
    """Test administration tier distribution: T1+T2+T3 > 80%."""
    engine = GameEngine(world_seed=42)
    rng = random.Random(42)
    
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    n = 5000
    
    for _ in range(n):
        tier = engine._select_mission_tier("administration", rng)
        counts[tier] = counts.get(tier, 0) + 1
    
    # T1+T2+T3 should dominate (> 80%)
    low_tier_pct = (counts[1] + counts[2] + counts[3]) / n * 100
    assert low_tier_pct > 80.0, f"T1+T2+T3 ({low_tier_pct:.1f}%) should be > 80%"


def test_tier_distribution_datanet() -> None:
    """Test datanet tier distribution: only T4 and T5 appear."""
    engine = GameEngine(world_seed=42)
    rng = random.Random(42)
    
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    n = 5000
    
    for _ in range(n):
        tier = engine._select_mission_tier("datanet", rng)
        counts[tier] = counts.get(tier, 0) + 1
    
    # Only T4 and T5 should appear
    assert counts[1] == 0, "Datanet should never produce T1"
    assert counts[2] == 0, "Datanet should never produce T2"
    assert counts[3] == 0, "Datanet should never produce T3"
    assert counts[4] > 0, "Datanet should produce T4"
    assert counts[5] > 0, "Datanet should produce T5"
    # T4 should be more common than T5 (80 vs 20 weight)
    assert counts[4] > counts[5], f"T4 ({counts[4]}) should be > T5 ({counts[5]})"
