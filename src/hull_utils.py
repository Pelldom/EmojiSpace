"""
Utility functions for hull data access and filtering.
"""

from functools import lru_cache
from typing import Any

try:
    from data_loader import load_hulls
except ModuleNotFoundError:
    from src.data_loader import load_hulls


@lru_cache(maxsize=1)
def _hulls_by_id() -> dict[str, dict[str, Any]]:
    """Cache hull data by hull_id."""
    payload = load_hulls()
    return {hull["hull_id"]: hull for hull in payload.get("hulls", [])}


def get_hull_display_name(hull_id: str) -> str:
    """
    Get the display name for a hull by its hull_id.
    
    Args:
        hull_id: The hull identifier (e.g., "civ_t1_midge")
        
    Returns:
        The display name (e.g., "Midge") or hull_id if not found.
    """
    if not isinstance(hull_id, str) or not hull_id:
        return str(hull_id) if hull_id else ""
    
    hulls = _hulls_by_id()
    hull_data = hulls.get(hull_id)
    if hull_data is None:
        return hull_id
    
    display_name = hull_data.get("name", "")
    if isinstance(display_name, str) and display_name:
        return display_name
    
    return hull_id


def is_shipdock_sellable_hull(hull_id: str, hull_data: dict[str, Any] | None = None) -> bool:
    """
    Determine if a hull can be sold at shipdock.
    
    Restrictions:
    - ALN frames (hull_id prefix "aln_") are never sold
    - X-Class frames (hull_id prefixes "xa_", "xb_", "xc_") are never sold
    
    Args:
        hull_id: The hull identifier
        hull_data: Optional hull data dict (if not provided, will be looked up)
        
    Returns:
        True if the hull can be sold at shipdock, False otherwise.
    """
    if not isinstance(hull_id, str) or not hull_id:
        return False
    
    # Hard rule: exclude ALN frames
    if hull_id.startswith("aln_"):
        return False
    
    # Hard rule: exclude X-Class frames (XA, XB, XC)
    if hull_id.startswith("xa_") or hull_id.startswith("xb_") or hull_id.startswith("xc_"):
        return False
    
    # If hull_data is provided, also check availability_flags for defense in depth
    if hull_data is not None:
        flags = set(hull_data.get("availability_flags", []))
        if "experimental" in flags or "alien" in flags:
            return False
    
    return True
