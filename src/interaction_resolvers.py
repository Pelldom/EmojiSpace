from __future__ import annotations

try:
    from data_loader import load_hulls, load_modules
    from ship_assembler import assemble_ship, compute_hull_max_from_ship_state
    from ship_entity import ShipEntity
    from market_pricing import price_hull_transaction, price_module_transaction
except ModuleNotFoundError:
    from src.data_loader import load_hulls, load_modules
    from src.ship_assembler import assemble_ship, compute_hull_max_from_ship_state
    from src.ship_entity import ShipEntity
    from src.market_pricing import price_hull_transaction, price_module_transaction


FUEL_PRICE_PER_UNIT = 5
HULL_REPAIR_UNIT = 10
SUBSYSTEM_REPAIR_UNIT = 25
REPAIR_POPULATION_MODIFIER = {1: 1.20, 2: 1.10, 3: 1.00, 4: 0.90, 5: 0.80}


def destination_has_datanet_service(destination) -> bool:
    locations = []
    if isinstance(destination, dict):
        locations = destination.get("locations", [])
    elif hasattr(destination, "locations"):
        locations = list(destination.locations)
    for location in locations:
        if isinstance(location, str) and location == "datanet":
            return True
        if isinstance(location, dict) and location.get("location_type") == "datanet":
            return True
        if hasattr(location, "location_type") and getattr(location, "location_type") == "datanet":
            return True
    return False


def destination_has_shipdock_service(destination) -> bool:
    locations = []
    if isinstance(destination, dict):
        locations = destination.get("locations", [])
    elif hasattr(destination, "locations"):
        locations = list(destination.locations)
    for location in locations:
        if isinstance(location, str) and location == "shipdock":
            return True
        if isinstance(location, dict) and location.get("location_type") == "shipdock":
            return True
        if hasattr(location, "location_type") and getattr(location, "location_type") == "shipdock":
            return True
    return False


def destination_actions(destination, base_actions=None):
    actions = list(base_actions or [])
    if destination_has_tag(destination, "destroyed"):
        # Destroyed destinations remain travel-reachable but expose no normal local actions.
        return sorted(actions, key=lambda value: value)
    if destination_has_datanet_service(destination) and "refuel" not in actions:
        actions.append("refuel")
    if destination_has_shipdock_service(destination):
        for action in (
            "buy_hull",
            "sell_hull",
            "buy_module",
            "sell_module",
            "repair_ship",
        ):
            if action not in actions:
                actions.append(action)
    return sorted(actions, key=lambda value: value)


def destination_has_tag(destination, tag: str) -> bool:
    tags = []
    if isinstance(destination, dict):
        tags = destination.get("tags", [])
    elif hasattr(destination, "tags"):
        tags = list(getattr(destination, "tags", []))
    return isinstance(tags, list) and tag in tags


def execute_refuel(*, ship, player_credits: int, requested_units: int | None = None, player=None) -> dict:
    if requested_units is not None and requested_units < 0:
        return {"ok": False, "reason": "invalid_request", "units_purchased": 0, "total_cost": 0, "credits": player_credits}

    missing = max(0, int(ship.fuel_capacity) - int(ship.current_fuel))
    units_target = missing if requested_units is None else min(requested_units, missing)
    total_cost = units_target * FUEL_PRICE_PER_UNIT
    if player_credits < total_cost:
        return {"ok": False, "reason": "insufficient_credits", "units_purchased": 0, "total_cost": 0, "credits": player_credits}

    ship.current_fuel = int(ship.current_fuel) + units_target
    updated_credits = player_credits - total_cost
    if player is not None:
        player.credits = max(0, int(updated_credits))
    return {
        "ok": True,
        "reason": "ok",
        "units_purchased": units_target,
        "total_cost": total_cost,
        "credits": updated_credits,
        "current_fuel": int(ship.current_fuel),
    }


def _destination_id(destination) -> str | None:
    if isinstance(destination, dict):
        return destination.get("destination_id")
    return getattr(destination, "destination_id", None)


def _module_instances(ship) -> list[dict]:
    return list(getattr(ship, "persistent_state", {}).get("module_instances", []))


def _set_module_instances(ship, module_instances: list[dict]) -> None:
    ship.persistent_state.setdefault("module_instances", [])
    ship.persistent_state["module_instances"] = list(module_instances)


def _degradation_state(ship) -> dict[str, int]:
    state = getattr(ship, "persistent_state", {}).get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})
    return {
        "weapon": int(state.get("weapon", 0)),
        "defense": int(state.get("defense", 0)),
        "engine": int(state.get("engine", 0)),
    }


def _set_degradation_state(ship, degradation_state: dict[str, int]) -> None:
    ship.persistent_state["degradation_state"] = {
        "weapon": int(degradation_state.get("weapon", 0)),
        "defense": int(degradation_state.get("defense", 0)),
        "engine": int(degradation_state.get("engine", 0)),
    }


def _is_ship_active(ship, player) -> bool:
    if getattr(ship, "activity_state", "inactive") == "active":
        return True
    if getattr(player, "active_ship_id", None) == getattr(ship, "ship_id", None):
        return True
    return bool(getattr(ship, "persistent_state", {}).get("active_flag", False))


def _set_ship_active(ship, value: bool) -> None:
    ship.activity_state = "active" if value else "inactive"
    ship.persistent_state["active_flag"] = bool(value)


def _ship_present_at_destination(ship, player, destination_id: str | None = None) -> bool:
    """
    Check if ship is present at destination.
    
    Presence is determined by:
    - ship.destination_id == player.current_destination_id
    
    Ships exist at DESTINATION level, not LOCATION level.
    Do NOT check system_id. Destination match only.
    """
    ship_destination_id = getattr(ship, "destination_id", None)
    player_destination_id = getattr(player, "current_destination_id", None)
    return ship_destination_id == player_destination_id


def _hull_by_id() -> dict[str, dict]:
    return {entry["hull_id"]: entry for entry in load_hulls()["hulls"]}


def _module_by_id() -> dict[str, dict]:
    return {entry["module_id"]: entry for entry in load_modules()["modules"]}


def _inventory_hull_price(inventory: dict, hull_id: str) -> int | None:
    for hull in inventory.get("hulls", []):
        if hull.get("hull_id") == hull_id:
            return int(hull.get("base_price_credits", 0))
    return None


def _inventory_module_price(inventory: dict, module_id: str) -> int | None:
    for module in inventory.get("modules", []):
        if module.get("module_id") == module_id:
            return int(module.get("base_price_credits", 0))
    return None


def execute_buy_hull(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    inventory: dict,
    hull_id: str,
    ship_id: str,
    system_id: str | None = None,
    world_state_engine=None,
    logger=None,
    turn: int = 0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    base_price = _inventory_hull_price(inventory, hull_id)
    if base_price is None:
        return {"ok": False, "reason": "hull_not_in_inventory"}
    
    # Use pricing contract for buy transaction
    if system_id is None:
        # Fallback: try to get system_id from destination
        system_id = getattr(destination, "system_id", None) if hasattr(destination, "system_id") else None
        if system_id is None:
            system_id = ""
    
    pricing = price_hull_transaction(
        base_price_credits=base_price,
        hull_id=hull_id,
        system_id=system_id,
        transaction_type="buy",
        world_state_engine=world_state_engine,
        logger=logger,
        turn=turn,
    )
    # C) Apply shipdock price variance multiplier (locked per market)
    # C) Apply shipdock price variance multiplier (locked per market)
    final_price = pricing.final_price
    if hasattr(destination, "market") and destination.market is not None:
        final_price = final_price * destination.market.shipdock_price_multiplier
        final_price = max(1.0, round(final_price))
    price = int(final_price)
    
    if int(player.credits) < price:
        return {"ok": False, "reason": "insufficient_credits"}
    if ship_id in fleet_by_id:
        return {"ok": False, "reason": "ship_id_exists"}

    # Use assembler to derive all ship stats
    module_instances = []
    degradation_state = {"weapon": 0, "defense": 0, "engine": 0}
    assembled = assemble_ship(hull_id, module_instances, degradation_state)
    
    # Extract hull data for crew_capacity and cargo base
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == hull_id:
            hull_data = hull
            break
    
    if hull_data is None:
        return {"ok": False, "reason": "hull_data_not_found"}
    
    # Extract cargo capacities: base from hull + module bonuses from assembler
    cargo_base = hull_data.get("cargo", {})
    physical_cargo_base = int(cargo_base.get("physical_base", 0))
    data_cargo_base = int(cargo_base.get("data_base", 0))
    utility_effects = assembled.get("ship_utility_effects", {})
    physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
    data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
    
    # Extract crew capacity from hull data
    crew_capacity = int(hull_data.get("crew_capacity", 0))
    
    # Extract subsystem bands from assembler
    bands = assembled.get("bands", {})
    effective_bands = bands.get("effective", {})
    
    ship = ShipEntity(
        ship_id=ship_id,
        model_id=hull_id,
        owner_id=getattr(player, "player_id", "player"),
        owner_type="player",
        activity_state="inactive",
        destination_id=destination_id,
        current_system_id=getattr(player, "current_system_id", ""),
        current_destination_id=destination_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
        crew_capacity=crew_capacity,
        physical_cargo_capacity=physical_cargo_capacity,
        data_cargo_capacity=data_cargo_capacity,
    )
    ship.persistent_state["module_instances"] = list(module_instances)
    ship.persistent_state["degradation_state"] = dict(degradation_state)
    ship.persistent_state["max_hull_integrity"] = int(assembled.get("hull_max", 0))
    ship.persistent_state["current_hull_integrity"] = int(assembled.get("hull_max", 0))
    ship.persistent_state["assembled"] = assembled
    ship.persistent_state["subsystem_bands"] = {
        "weapon": int(effective_bands.get("weapon", 0)),
        "defense": int(effective_bands.get("defense", 0)),
        "engine": int(effective_bands.get("engine", 0)),
    }
    ship.persistent_state["active_flag"] = False
    fleet_by_id[ship_id] = ship
    if ship_id not in player.owned_ship_ids:
        player.owned_ship_ids.append(ship_id)
    player.credits = max(0, int(player.credits) - price)
    return {"ok": True, "reason": "ok", "ship_id": ship_id, "credits": int(player.credits)}


def execute_sell_hull(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    ship_id: str | None = None,
    price_modifier_multiplier: float = 1.0,
    system_id: str | None = None,
    world_state_engine=None,
    logger=None,
    turn: int = 0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    
    # Default to player's active ship if ship_id not provided
    if ship_id is None:
        ship_id = getattr(player, "active_ship_id", None)
        if ship_id is None:
            return {"ok": False, "reason": "no_active_ship"}
    
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    
    # Check presence: ship.destination_id must match player.current_destination_id
    player_destination_id = getattr(player, "current_destination_id", None)
    ship_destination_id = getattr(ship, "destination_id", None)
    if ship_destination_id != player_destination_id:
        if logger is not None:
            logger.log(
                turn=turn,
                action="shipdock_presence_check",
                state_change=(
                    f"ship_not_present ship_id={ship_id} "
                    f"player_destination_id={player_destination_id} "
                    f"ship_destination_id={ship_destination_id}"
                ),
            )
        return {"ok": False, "reason": "ship_not_present"}

    is_active = _is_ship_active(ship, player)
    if is_active:
        others = sorted(
            [
                other_id
                for other_id, other_ship in fleet_by_id.items()
                if other_id != ship_id and _ship_present_at_destination(other_ship, player)
            ]
        )
        if not others:
            return {"ok": False, "reason": "no_replacement_active_ship"}
        replacement_id = others[0]
        _set_ship_active(fleet_by_id[replacement_id], True)
        player.active_ship_id = replacement_id

    hull_id = ship.model_id
    hull = _hull_by_id().get(hull_id)
    if hull is None:
        return {"ok": False, "reason": "unknown_hull"}
    
    # Use pricing contract for sell transaction
    if system_id is None:
        system_id = getattr(destination, "system_id", None) if hasattr(destination, "system_id") else None
        if system_id is None:
            system_id = ""
    
    pricing = price_hull_transaction(
        base_price_credits=int(hull["base_price_credits"]),
        hull_id=hull_id,
        system_id=system_id,
        transaction_type="sell",
        world_state_engine=world_state_engine,
        logger=logger,
        turn=turn,
    )
    # C) Apply shipdock price variance multiplier (locked per market)
    final_price = pricing.final_price * float(price_modifier_multiplier)
    if hasattr(destination, "market") and destination.market is not None:
        final_price = final_price * destination.market.shipdock_price_multiplier
    final_price = max(1.0, round(final_price))
    final_price = int(final_price)
    player.credits = max(0, int(player.credits) + final_price)
    fleet_by_id.pop(ship_id, None)
    player.owned_ship_ids = [owned for owned in player.owned_ship_ids if owned != ship_id]
    if player.active_ship_id == ship_id:
        player.active_ship_id = None
    return {"ok": True, "reason": "ok", "credits": int(player.credits), "final_price": final_price}


def execute_buy_module(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    inventory: dict,
    ship_id: str,
    module_id: str,
    system_id: str | None = None,
    world_state_engine=None,
    logger=None,
    turn: int = 0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    base_price = _inventory_module_price(inventory, module_id)
    if base_price is None:
        return {"ok": False, "reason": "module_not_in_inventory"}
    
    # Use pricing contract for buy transaction
    if system_id is None:
        # Fallback: try to get system_id from destination
        system_id = getattr(destination, "system_id", None) if hasattr(destination, "system_id") else None
        if system_id is None:
            system_id = ""
    
    pricing = price_module_transaction(
        base_price_credits=base_price,
        module_id=module_id,
        system_id=system_id,
        transaction_type="buy",
        secondary_tags=None,
        world_state_engine=world_state_engine,
        logger=logger,
        turn=turn,
    )
    # C) Apply shipdock price variance multiplier (locked per market)
    final_price = pricing.final_price
    if hasattr(destination, "market") and destination.market is not None:
        final_price = final_price * destination.market.shipdock_price_multiplier
        final_price = max(1.0, round(final_price))
    price = int(final_price)
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    
    # Check presence: ship.destination_id must match player.current_destination_id
    player_destination_id = getattr(player, "current_destination_id", None)
    ship_destination_id = getattr(ship, "destination_id", None)
    if ship_destination_id != player_destination_id:
        if logger is not None:
            logger.log(
                turn=turn,
                action="shipdock_presence_check",
                state_change=(
                    f"ship_not_present ship_id={ship_id} "
                    f"player_destination_id={player_destination_id} "
                    f"ship_destination_id={ship_destination_id}"
                ),
            )
        return {"ok": False, "reason": "ship_not_present"}
    if int(player.credits) < price:
        return {"ok": False, "reason": "insufficient_credits"}

    before = _module_instances(ship)
    candidate = list(before)
    candidate.append({"module_id": module_id, "secondary_tags": []})
    try:
        assembled = assemble_ship(ship.model_id, candidate, _degradation_state(ship))
    except ValueError:
        return {"ok": False, "reason": "slot_constraints_failed"}

    _set_module_instances(ship, candidate)
    
    # Update all ship stats from assembler output
    ship.fuel_capacity = int(assembled["fuel_capacity"])
    ship.current_fuel = min(int(ship.current_fuel), int(ship.fuel_capacity))
    
    # Update cargo capacities: base from hull + module bonuses from assembler
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == ship.model_id:
            hull_data = hull
            break
    
    if hull_data:
        cargo_base = hull_data.get("cargo", {})
        physical_cargo_base = int(cargo_base.get("physical_base", 0))
        data_cargo_base = int(cargo_base.get("data_base", 0))
        utility_effects = assembled.get("ship_utility_effects", {})
        ship.physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
        ship.data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
    
    # Update subsystem bands
    bands = assembled.get("bands", {})
    effective_bands = bands.get("effective", {})
    ship.persistent_state["subsystem_bands"] = {
        "weapon": int(effective_bands.get("weapon", 0)),
        "defense": int(effective_bands.get("defense", 0)),
        "engine": int(effective_bands.get("engine", 0)),
    }
    
    ship.persistent_state["assembled"] = assembled
    player.credits = max(0, int(player.credits) - price)
    return {"ok": True, "reason": "ok", "credits": int(player.credits)}


def execute_sell_module(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    ship_id: str,
    module_id: str,
    price_modifier_multiplier: float = 1.0,
    system_id: str | None = None,
    world_state_engine=None,
    logger=None,
    turn: int = 0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    
    # Check presence: ship.destination_id must match player.current_destination_id
    player_destination_id = getattr(player, "current_destination_id", None)
    ship_destination_id = getattr(ship, "destination_id", None)
    if ship_destination_id != player_destination_id:
        if logger is not None:
            logger.log(
                turn=turn,
                action="shipdock_presence_check",
                state_change=(
                    f"ship_not_present ship_id={ship_id} "
                    f"player_destination_id={player_destination_id} "
                    f"ship_destination_id={ship_destination_id}"
                ),
            )
        return {"ok": False, "reason": "ship_not_present"}

    modules = _module_instances(ship)
    remove_index = None
    for index, instance in enumerate(modules):
        if instance.get("module_id") == module_id:
            remove_index = index
            break
    if remove_index is None:
        return {"ok": False, "reason": "module_not_found"}
    removed_module_instance = modules.pop(remove_index)

    module = _module_by_id().get(module_id)
    if module is None:
        return {"ok": False, "reason": "unknown_module"}
    assembled = assemble_ship(ship.model_id, modules, _degradation_state(ship))
    _set_module_instances(ship, modules)
    
    # Update all ship stats from assembler output
    ship.fuel_capacity = int(assembled["fuel_capacity"])
    ship.current_fuel = min(int(ship.current_fuel), int(ship.fuel_capacity))
    
    # Update cargo capacities: base from hull + module bonuses from assembler
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == ship.model_id:
            hull_data = hull
            break
    
    if hull_data:
        cargo_base = hull_data.get("cargo", {})
        physical_cargo_base = int(cargo_base.get("physical_base", 0))
        data_cargo_base = int(cargo_base.get("data_base", 0))
        utility_effects = assembled.get("ship_utility_effects", {})
        ship.physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
        ship.data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
    
    # Update subsystem bands
    bands = assembled.get("bands", {})
    effective_bands = bands.get("effective", {})
    ship.persistent_state["subsystem_bands"] = {
        "weapon": int(effective_bands.get("weapon", 0)),
        "defense": int(effective_bands.get("defense", 0)),
        "engine": int(effective_bands.get("engine", 0)),
    }
    
    ship.persistent_state["assembled"] = assembled

    # Use pricing contract for sell transaction
    secondary_tags_list = list(removed_module_instance.get("secondary_tags", []))
    if system_id is None:
        system_id = getattr(destination, "system_id", None) if hasattr(destination, "system_id") else None
        if system_id is None:
            system_id = ""
    
    pricing = price_module_transaction(
        base_price_credits=int(module["base_price_credits"]),
        module_id=module_id,
        system_id=system_id,
        transaction_type="sell",
        secondary_tags=secondary_tags_list,
        world_state_engine=world_state_engine,
        logger=logger,
        turn=turn,
    )
    # C) Apply shipdock price variance multiplier (locked per market)
    final_price = pricing.final_price * float(price_modifier_multiplier)
    if hasattr(destination, "market") and destination.market is not None:
        final_price = final_price * destination.market.shipdock_price_multiplier
    final_price = max(1.0, round(final_price))
    final_price = int(final_price)
    player.credits = max(0, int(player.credits) + final_price)
    return {"ok": True, "reason": "ok", "credits": int(player.credits), "final_price": final_price}


def execute_repair_ship(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    ship_id: str | None = None,
    system_population: int,
    logger=None,
    turn: int = 0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    if system_population not in REPAIR_POPULATION_MODIFIER:
        return {"ok": False, "reason": "invalid_population"}
    
    # Default to player's active ship if ship_id not provided
    if ship_id is None:
        ship_id = getattr(player, "active_ship_id", None)
        if ship_id is None:
            return {"ok": False, "reason": "no_active_ship"}
    
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    
    # Check presence: ship.destination_id must match player.current_destination_id
    player_destination_id = getattr(player, "current_destination_id", None)
    ship_destination_id = getattr(ship, "destination_id", None)
    if ship_destination_id != player_destination_id:
        if logger is not None:
            logger.log(
                turn=turn,
                action="shipdock_presence_check",
                state_change=(
                    f"ship_not_present ship_id={ship_id} "
                    f"player_destination_id={player_destination_id} "
                    f"ship_destination_id={ship_destination_id}"
                ),
            )
        return {"ok": False, "reason": "ship_not_present"}

    max_hull = int(ship.persistent_state.get("max_hull_integrity", 0))
    current_hull = int(ship.persistent_state.get("current_hull_integrity", max_hull))
    degradation = _degradation_state(ship)
    hull_damage = max(0, max_hull - current_hull)
    subsystem_damage = int(degradation["weapon"] + degradation["defense"] + degradation["engine"])
    base_cost = (hull_damage * HULL_REPAIR_UNIT) + (subsystem_damage * SUBSYSTEM_REPAIR_UNIT)
    final_cost = int(round(base_cost * REPAIR_POPULATION_MODIFIER[system_population]))
    if int(player.credits) < final_cost:
        return {"ok": False, "reason": "insufficient_credits", "final_cost": final_cost}

    player.credits = max(0, int(player.credits) - final_cost)
    ship.persistent_state["current_hull_integrity"] = max_hull
    _set_degradation_state(ship, {"weapon": 0, "defense": 0, "engine": 0})
    return {"ok": True, "reason": "ok", "credits": int(player.credits), "final_cost": final_cost}


def resolve_warehouse_deposit(
    *,
    player,
    destination_id: str,
    sku_id: str,
    quantity: int,
) -> dict:
    if not isinstance(destination_id, str) or not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    if not isinstance(sku_id, str) or not sku_id:
        return {"ok": False, "reason": "invalid_sku_id"}
    if not isinstance(quantity, int) or quantity <= 0:
        return {"ok": False, "reason": "invalid_quantity"}

    warehouses = getattr(player, "warehouses", {})
    if not isinstance(warehouses, dict):
        return {"ok": False, "reason": "warehouse_not_rented"}
    warehouse = warehouses.get(destination_id)
    if not isinstance(warehouse, dict):
        return {"ok": False, "reason": "warehouse_not_rented"}

    capacity = int(warehouse.get("capacity", 0) or 0)
    goods = warehouse.get("goods", {})
    if not isinstance(goods, dict):
        goods = {}
    used_before = int(sum(int(v) for v in goods.values() if isinstance(v, int) and int(v) > 0))
    available_before = max(0, int(capacity - used_before))
    if available_before < int(quantity):
        return {"ok": False, "reason": "warehouse_capacity_exceeded"}

    cargo_by_ship = getattr(player, "cargo_by_ship", {})
    if not isinstance(cargo_by_ship, dict):
        return {"ok": False, "reason": "insufficient_cargo"}
    cargo = cargo_by_ship.setdefault("active", {})
    if not isinstance(cargo, dict):
        return {"ok": False, "reason": "insufficient_cargo"}
    cargo_qty = int(cargo.get(sku_id, 0) or 0)
    if cargo_qty < int(quantity):
        return {"ok": False, "reason": "insufficient_cargo"}

    remaining = cargo_qty - int(quantity)
    if remaining <= 0:
        cargo.pop(sku_id, None)
    else:
        cargo[sku_id] = int(remaining)
    goods[sku_id] = int(goods.get(sku_id, 0) + int(quantity))
    warehouse["goods"] = goods

    used_after = int(sum(int(v) for v in goods.values() if isinstance(v, int) and int(v) > 0))
    return {
        "ok": True,
        "reason": "ok",
        "result_summary": {
            "destination_id": destination_id,
            "sku_id": sku_id,
            "quantity": int(quantity),
            "warehouse_used_after": used_after,
            "warehouse_available_after": max(0, int(capacity - used_after)),
        },
    }


def resolve_warehouse_withdraw(
    *,
    player,
    destination_id: str,
    sku_id: str,
    quantity: int,
    cargo_capacity: int | None = None,
) -> dict:
    if not isinstance(destination_id, str) or not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    if not isinstance(sku_id, str) or not sku_id:
        return {"ok": False, "reason": "invalid_sku_id"}
    if not isinstance(quantity, int) or quantity <= 0:
        return {"ok": False, "reason": "invalid_quantity"}

    warehouses = getattr(player, "warehouses", {})
    if not isinstance(warehouses, dict):
        return {"ok": False, "reason": "warehouse_not_rented"}
    warehouse = warehouses.get(destination_id)
    if not isinstance(warehouse, dict):
        return {"ok": False, "reason": "warehouse_not_rented"}

    goods = warehouse.get("goods", {})
    if not isinstance(goods, dict):
        goods = {}
    stored_qty = int(goods.get(sku_id, 0) or 0)
    if stored_qty < int(quantity):
        return {"ok": False, "reason": "insufficient_stored_goods"}

    cargo_by_ship = getattr(player, "cargo_by_ship", {})
    if not isinstance(cargo_by_ship, dict):
        return {"ok": False, "reason": "insufficient_cargo_capacity"}
    cargo = cargo_by_ship.setdefault("active", {})
    if not isinstance(cargo, dict):
        return {"ok": False, "reason": "insufficient_cargo_capacity"}
    current_cargo_units = int(sum(int(v) for v in cargo.values() if isinstance(v, int) and int(v) > 0))
    if isinstance(cargo_capacity, int) and cargo_capacity >= 0:
        if current_cargo_units + int(quantity) > int(cargo_capacity):
            return {"ok": False, "reason": "insufficient_cargo_capacity"}

    remaining_goods = stored_qty - int(quantity)
    if remaining_goods <= 0:
        goods.pop(sku_id, None)
    else:
        goods[sku_id] = int(remaining_goods)
    warehouse["goods"] = goods
    cargo[sku_id] = int(cargo.get(sku_id, 0) + int(quantity))

    used_after = int(sum(int(v) for v in goods.values() if isinstance(v, int) and int(v) > 0))
    capacity = int(warehouse.get("capacity", 0) or 0)
    return {
        "ok": True,
        "reason": "ok",
        "result_summary": {
            "destination_id": destination_id,
            "sku_id": sku_id,
            "quantity": int(quantity),
            "warehouse_used_after": used_after,
            "warehouse_available_after": max(0, int(capacity - used_after)),
        },
    }
