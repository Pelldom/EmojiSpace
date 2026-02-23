"""
Tests for hull utility functions.
"""

import pytest

try:
    from hull_utils import get_hull_display_name, is_shipdock_sellable_hull
except ImportError:
    from src.hull_utils import get_hull_display_name, is_shipdock_sellable_hull


def test_get_hull_display_name_known_hull():
    """Test that get_hull_display_name returns the correct display name for a known hull."""
    # Test with Midge
    display_name = get_hull_display_name("civ_t1_midge")
    assert display_name == "Midge", f"Expected 'Midge', got '{display_name}'"
    assert isinstance(display_name, str)
    assert len(display_name) > 0


def test_get_hull_display_name_unknown_hull():
    """Test that get_hull_display_name falls back to hull_id for unknown hulls."""
    unknown_id = "unknown_hull_xyz"
    display_name = get_hull_display_name(unknown_id)
    assert display_name == unknown_id, f"Expected '{unknown_id}', got '{display_name}'"


def test_get_hull_display_name_empty():
    """Test that get_hull_display_name handles empty strings."""
    result = get_hull_display_name("")
    assert result == ""


def test_is_shipdock_sellable_hull_civilian():
    """Test that civilian hulls are sellable."""
    assert is_shipdock_sellable_hull("civ_t1_midge") is True
    assert is_shipdock_sellable_hull("civ_t2_gnat") is True


def test_is_shipdock_sellable_hull_military():
    """Test that military hulls are sellable."""
    assert is_shipdock_sellable_hull("mil_t1_paper_wasp") is True


def test_is_shipdock_sellable_hull_aln_excluded():
    """Test that ALN hulls are excluded from shipdock."""
    assert is_shipdock_sellable_hull("aln_t1_trilobite") is False
    assert is_shipdock_sellable_hull("aln_t2_tardigrade") is False
    # Test with any aln_ prefix
    assert is_shipdock_sellable_hull("aln_anything") is False


def test_is_shipdock_sellable_hull_xclass_excluded():
    """Test that X-Class hulls (XA, XB, XC) are excluded from shipdock."""
    # XA frames
    assert is_shipdock_sellable_hull("xa_t1_nova") is False
    assert is_shipdock_sellable_hull("xa_t5_quasar") is False
    
    # XB frames
    assert is_shipdock_sellable_hull("xb_t1_flare") is False
    assert is_shipdock_sellable_hull("xb_t5_cataclysm") is False
    
    # XC frames
    assert is_shipdock_sellable_hull("xc_t1_aegis") is False
    assert is_shipdock_sellable_hull("xc_t5_sentinel") is False


def test_is_shipdock_sellable_hull_with_hull_data():
    """Test that is_shipdock_sellable_hull respects hull_data availability_flags."""
    # Test with experimental flag
    hull_data_experimental = {"availability_flags": ["experimental"]}
    assert is_shipdock_sellable_hull("civ_t1_midge", hull_data=hull_data_experimental) is False
    
    # Test with alien flag
    hull_data_alien = {"availability_flags": ["alien"]}
    assert is_shipdock_sellable_hull("civ_t1_midge", hull_data=hull_data_alien) is False
    
    # Test with normal flags
    hull_data_normal = {"availability_flags": []}
    assert is_shipdock_sellable_hull("civ_t1_midge", hull_data=hull_data_normal) is True


def test_is_shipdock_sellable_hull_empty_string():
    """Test that empty hull_id returns False."""
    assert is_shipdock_sellable_hull("") is False
    assert is_shipdock_sellable_hull(None) is False
