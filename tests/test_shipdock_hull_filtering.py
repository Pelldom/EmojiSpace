"""
Tests for shipdock hull inventory filtering.
"""

import pytest

try:
    from shipdock_inventory import generate_shipdock_inventory, _eligible_hulls
    from hull_utils import is_shipdock_sellable_hull
except ImportError:
    from src.shipdock_inventory import generate_shipdock_inventory, _eligible_hulls
    from src.hull_utils import is_shipdock_sellable_hull


def test_eligible_hulls_excludes_aln():
    """Test that _eligible_hulls() excludes ALN frames."""
    eligible = _eligible_hulls()
    
    # Verify no ALN hulls are in the eligible list
    aln_hulls = [hull for hull in eligible if hull.get("hull_id", "").startswith("aln_")]
    assert len(aln_hulls) == 0, f"Found {len(aln_hulls)} ALN hulls in eligible list: {[h.get('hull_id') for h in aln_hulls]}"


def test_eligible_hulls_excludes_xclass():
    """Test that _eligible_hulls() excludes X-Class frames (XA, XB, XC)."""
    eligible = _eligible_hulls()
    
    # Verify no X-Class hulls are in the eligible list
    xclass_hulls = [
        hull for hull in eligible
        if hull.get("hull_id", "").startswith(("xa_", "xb_", "xc_"))
    ]
    assert len(xclass_hulls) == 0, f"Found {len(xclass_hulls)} X-Class hulls in eligible list: {[h.get('hull_id') for h in xclass_hulls]}"


def test_eligible_hulls_includes_normal_hulls():
    """Test that _eligible_hulls() includes normal civilian and military hulls."""
    eligible = _eligible_hulls()
    
    # Verify some normal hulls are present
    normal_hulls = [
        hull for hull in eligible
        if hull.get("hull_id", "").startswith(("civ_", "mil_", "frg_"))
    ]
    assert len(normal_hulls) > 0, "No normal hulls found in eligible list"


def test_shipdock_inventory_excludes_restricted_hulls():
    """Test that generate_shipdock_inventory() excludes ALN and X-Class hulls."""
    # Generate inventory with a fixed seed for determinism
    inventory = generate_shipdock_inventory(
        world_seed=12345,
        system_id="SYS-TEST",
        system_population=5,  # High population to maximize hull selection
        world_state_engine=None,
    )
    
    hull_inventory = inventory.get("hulls", [])
    
    # Check that no ALN hulls appear
    aln_hull_ids = [h.get("hull_id", "") for h in hull_inventory if h.get("hull_id", "").startswith("aln_")]
    assert len(aln_hull_ids) == 0, f"Found ALN hulls in inventory: {aln_hull_ids}"
    
    # Check that no X-Class hulls appear
    xclass_hull_ids = [
        h.get("hull_id", "")
        for h in hull_inventory
        if h.get("hull_id", "").startswith(("xa_", "xb_", "xc_"))
    ]
    assert len(xclass_hull_ids) == 0, f"Found X-Class hulls in inventory: {xclass_hull_ids}"


def test_shipdock_inventory_deterministic():
    """Test that shipdock inventory generation is deterministic."""
    inventory1 = generate_shipdock_inventory(
        world_seed=99999,
        system_id="SYS-TEST",
        system_population=3,
        world_state_engine=None,
    )
    
    inventory2 = generate_shipdock_inventory(
        world_seed=99999,
        system_id="SYS-TEST",
        system_population=3,
        world_state_engine=None,
    )
    
    # Same seed should produce same inventory
    hull_ids1 = sorted([h.get("hull_id", "") for h in inventory1.get("hulls", [])])
    hull_ids2 = sorted([h.get("hull_id", "") for h in inventory2.get("hulls", [])])
    assert hull_ids1 == hull_ids2, "Inventory generation is not deterministic"


def test_all_eligible_hulls_pass_filter():
    """Test that all hulls in _eligible_hulls() pass the shipdock filter."""
    eligible = _eligible_hulls()
    
    for hull in eligible:
        hull_id = hull.get("hull_id", "")
        assert is_shipdock_sellable_hull(hull_id, hull_data=hull), (
            f"Hull {hull_id} is in eligible list but fails shipdock filter"
        )
