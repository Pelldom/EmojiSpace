"""
Reward service - unified reward preview and payout.

This module provides a unified interface for mission rewards using RewardBundle.
Uses the mission reward calculation system (_calculate_mission_reward) for mission rewards.
"""

from typing import Any, Dict, Optional
from mission_entity import MissionEntity
from mission_domain import RewardBundle, CargoGrant, ModuleGrant, HullVoucherGrant
from player_state import PlayerState


def preview(
    mission: MissionEntity,
    *,
    system_markets: Optional[list[Dict[str, Any]]] = None,
    world_seed: Optional[int | str] = None,
) -> RewardBundle:
    """
    Calculate reward preview for a mission.
    
    Uses the mission reward calculation system, not encounter rewards.
    
    Args:
        mission: MissionEntity to preview rewards for
        system_markets: Optional list of market data for cargo selection (not used for mission rewards)
        world_seed: Optional world seed for deterministic calculation
    
    Returns:
        RewardBundle with preview rewards
    """
    if not mission.reward_profile_id:
        return RewardBundle()
    
    try:
        from mission_manager import _calculate_mission_reward, _load_reward_profiles
        
        # Load reward profiles
        reward_profiles = _load_reward_profiles()
        
        # Load catalogs for reward calculation
        catalogs = {}
        try:
            from data_catalog import load_data_catalog
            catalogs["data_catalog"] = load_data_catalog()
        except Exception:
            pass
        
        # Calculate mission reward
        reward = _calculate_mission_reward(
            mission=mission,
            reward_profiles=reward_profiles,
            catalogs=catalogs,
            world_seed=world_seed,
        )
        
        # Convert to RewardBundle
        return RewardBundle.from_reward_calculation(reward)
        
    except (ValueError, KeyError, Exception):
        # If calculation fails, return empty bundle
        return RewardBundle()


def payout(
    mission: MissionEntity,
    player_state: PlayerState,
    *,
    system_markets: Optional[list[Dict[str, Any]]] = None,
    world_seed: Optional[int | str] = None,
    catalog: Optional[Any] = None,
    physical_cargo_capacity: Optional[int] = None,
    data_cargo_capacity: Optional[int] = None,
    enforce_capacity: bool = False,
    logger=None,
    turn: int = 0,
) -> RewardBundle:
    """
    Calculate and apply mission reward payout.
    
    Uses the mission reward calculation system, not encounter rewards.
    
    Args:
        mission: MissionEntity to payout rewards for
        player_state: PlayerState to apply rewards to
        system_markets: Optional list of market data (not used for mission rewards)
        world_seed: Optional world seed for deterministic calculation
        catalog: Optional DataCatalog for cargo type determination
        physical_cargo_capacity: Optional physical cargo capacity limit
        data_cargo_capacity: Optional data cargo capacity limit
        enforce_capacity: If True, check capacity and return error if overflow
        logger: Optional logger instance
        turn: Current turn number
    
    Returns:
        RewardBundle with applied rewards
    """
    if not mission.reward_profile_id:
        return RewardBundle()
    
    try:
        from mission_manager import _calculate_mission_reward, _load_reward_profiles, _check_cargo_capacity, _check_data_cargo_capacity
        from reward_applicator import _is_data_cargo
        
        # Load reward profiles
        reward_profiles = _load_reward_profiles()
        
        # Load catalogs for reward calculation
        catalogs = {}
        if catalog:
            catalogs["data_catalog"] = catalog
        else:
            try:
                from data_catalog import load_data_catalog
                catalogs["data_catalog"] = load_data_catalog()
            except Exception:
                pass
        
        # Calculate mission reward
        reward = _calculate_mission_reward(
            mission=mission,
            reward_profiles=reward_profiles,
            catalogs=catalogs,
            world_seed=world_seed,
        )
        
        reward_type = reward.get("type")
        bundle = RewardBundle()
        
        # Apply credits
        if reward_type == "credits":
            amount = reward.get("amount", 0)
            bundle.credits = int(amount)
            player_state.credits = max(0, int(player_state.credits) + bundle.credits)
            if logger:
                logger.log(
                    turn=turn,
                    action="reward_applied",
                    state_change=f"mission_id={mission.mission_id} credits={bundle.credits}",
                )
        
        # Apply goods/cargo
        elif reward_type == "goods":
            sku_id = reward.get("sku_id")
            quantity = reward.get("quantity", 0)
            
            if sku_id and quantity > 0:
                # Check capacity if enforcement enabled
                if enforce_capacity:
                    is_data = _is_data_cargo(sku_id, catalogs.get("data_catalog"))
                    if is_data:
                        if not _check_data_cargo_capacity(player_state, quantity):
                            # Capacity exceeded
                            if logger:
                                logger.log(
                                    turn=turn,
                                    action="reward_error",
                                    state_change=f"mission_id={mission.mission_id} error=insufficient_data_cargo_capacity",
                                )
                            return bundle
                    else:
                        if not _check_cargo_capacity(player_state, sku_id, quantity, catalogs.get("data_catalog")):
                            # Capacity exceeded
                            if logger:
                                logger.log(
                                    turn=turn,
                                    action="reward_error",
                                    state_change=f"mission_id={mission.mission_id} error=insufficient_cargo_capacity",
                                )
                            return bundle
                
                # Apply cargo
                player_state.cargo_by_ship.setdefault("active", {})
                current_qty = player_state.cargo_by_ship["active"].get(sku_id, 0)
                player_state.cargo_by_ship["active"][sku_id] = current_qty + quantity
                
                bundle.cargo_grants.append(
                    CargoGrant(
                        item_id=sku_id,
                        quantity=int(quantity),
                    )
                )
                
                if logger:
                    logger.log(
                        turn=turn,
                        action="reward_applied",
                        state_change=(
                            f"mission_id={mission.mission_id} "
                            f"cargo={sku_id} quantity={quantity}"
                        ),
                    )
        
        # Apply module
        elif reward_type == "module":
            module_id = reward.get("module_id")
            if module_id:
                if not hasattr(player_state, "salvage_modules"):
                    player_state.salvage_modules = []
                if not isinstance(player_state.salvage_modules, list):
                    player_state.salvage_modules = []
                
                module_dict = {"module_id": module_id, "secondary_tags": []}
                player_state.salvage_modules.append(module_dict)
                
                bundle.module_grants.append(
                    ModuleGrant(
                        module_id=module_id,
                        quantity=1,
                    )
                )
                
                if logger:
                    logger.log(
                        turn=turn,
                        action="reward_applied",
                        state_change=f"mission_id={mission.mission_id} module={module_id}",
                    )
        
        # Apply hull voucher
        elif reward_type == "hull_voucher":
            hull_id = reward.get("hull_id")
            if hull_id:
                voucher_sku = f"hull_voucher_{hull_id}"
                
                # Check data cargo capacity (vouchers are data cargo)
                if enforce_capacity:
                    if not _check_data_cargo_capacity(player_state, 1):
                        if logger:
                            logger.log(
                                turn=turn,
                                action="reward_error",
                                state_change=f"mission_id={mission.mission_id} error=insufficient_data_cargo_capacity",
                            )
                        return bundle
                
                # Apply voucher as data cargo
                player_state.cargo_by_ship.setdefault("active", {})
                current_qty = player_state.cargo_by_ship["active"].get(voucher_sku, 0)
                player_state.cargo_by_ship["active"][voucher_sku] = current_qty + 1
                
                bundle.hull_vouchers.append(
                    HullVoucherGrant(
                        hull_id=hull_id,
                        quantity=1,
                    )
                )
                
                if logger:
                    logger.log(
                        turn=turn,
                        action="reward_applied",
                        state_change=f"mission_id={mission.mission_id} hull_voucher={hull_id}",
                    )
        
        return bundle
        
    except (ValueError, KeyError, Exception) as e:
        # If calculation fails, log and return empty bundle
        if logger:
            logger.log(
                turn=turn,
                action="reward_error",
                state_change=f"mission_id={mission.mission_id} error={str(e)}",
            )
        return RewardBundle()
