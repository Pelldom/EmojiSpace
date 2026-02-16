from __future__ import annotations

try:
    from data_loader import load_hulls, load_modules
    from ship_assembler import assemble_ship, compute_hull_max_from_ship_state
    from ship_entity import ShipEntity
except ModuleNotFoundError:
    from src.data_loader import load_hulls, load_modules
    from src.ship_assembler import assemble_ship, compute_hull_max_from_ship_state
    from src.ship_entity import ShipEntity


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
        player.credits = int(updated_credits)
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


def _ship_present_at_destination(ship, destination_id: str) -> bool:
    return getattr(ship, "location_id", None) == destination_id


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
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    price = _inventory_hull_price(inventory, hull_id)
    if price is None:
        return {"ok": False, "reason": "hull_not_in_inventory"}
    if int(player.credits) < price:
        return {"ok": False, "reason": "insufficient_credits"}
    if ship_id in fleet_by_id:
        return {"ok": False, "reason": "ship_id_exists"}

    assembled = assemble_ship(hull_id, [], {"weapon": 0, "defense": 0, "engine": 0})
    max_hull_integrity = compute_hull_max_from_ship_state({"hull_id": hull_id, "module_instances": []})
    ship = ShipEntity(
        ship_id=ship_id,
        model_id=hull_id,
        owner_id=getattr(player, "player_id", "player"),
        activity_state="inactive",
        location_id=destination_id,
        current_location_id=destination_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
    )
    ship.persistent_state["module_instances"] = []
    ship.persistent_state["degradation_state"] = {"weapon": 0, "defense": 0, "engine": 0}
    ship.persistent_state["max_hull_integrity"] = int(max_hull_integrity)
    ship.persistent_state["current_hull_integrity"] = int(max_hull_integrity)
    ship.persistent_state["active_flag"] = False
    fleet_by_id[ship_id] = ship
    if ship_id not in player.owned_ship_ids:
        player.owned_ship_ids.append(ship_id)
    player.credits = int(player.credits) - price
    return {"ok": True, "reason": "ok", "ship_id": ship_id, "credits": int(player.credits)}


def execute_sell_hull(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    ship_id: str,
    price_modifier_multiplier: float = 1.0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    if not _ship_present_at_destination(ship, destination_id):
        return {"ok": False, "reason": "ship_not_present"}

    is_active = _is_ship_active(ship, player)
    if is_active:
        others = sorted(
            [
                other_id
                for other_id, other_ship in fleet_by_id.items()
                if other_id != ship_id and _ship_present_at_destination(other_ship, destination_id)
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
    sell_price = float(hull["base_price_credits"]) * 0.5
    final_price = int(round(sell_price * float(price_modifier_multiplier)))
    player.credits = int(player.credits) + final_price
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
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    price = _inventory_module_price(inventory, module_id)
    if price is None:
        return {"ok": False, "reason": "module_not_in_inventory"}
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    if not _ship_present_at_destination(ship, destination_id):
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
    ship.fuel_capacity = int(assembled["fuel_capacity"])
    ship.current_fuel = min(int(ship.current_fuel), int(ship.fuel_capacity))
    ship.persistent_state["assembled"] = assembled
    player.credits = int(player.credits) - price
    return {"ok": True, "reason": "ok", "credits": int(player.credits)}


def execute_sell_module(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    ship_id: str,
    module_id: str,
    price_modifier_multiplier: float = 1.0,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    if not _ship_present_at_destination(ship, destination_id):
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
    ship.fuel_capacity = int(assembled["fuel_capacity"])
    ship.current_fuel = min(int(ship.current_fuel), int(ship.fuel_capacity))
    ship.persistent_state["assembled"] = assembled

    sell_price = float(module["base_price_credits"]) * 0.5
    resale_multiplier = 1.0
    secondary_tags = set(removed_module_instance.get("secondary_tags", []))
    if "secondary:prototype" in secondary_tags:
        resale_multiplier *= 1.5
    if "secondary:alien" in secondary_tags:
        resale_multiplier *= 2.0
    final_price = int(round(sell_price * resale_multiplier * float(price_modifier_multiplier)))
    player.credits = int(player.credits) + final_price
    return {"ok": True, "reason": "ok", "credits": int(player.credits), "final_price": final_price}


def execute_repair_ship(
    *,
    destination,
    player,
    fleet_by_id: dict[str, ShipEntity],
    ship_id: str,
    system_population: int,
) -> dict:
    destination_id = _destination_id(destination)
    if not destination_has_shipdock_service(destination):
        return {"ok": False, "reason": "shipdock_required"}
    if not destination_id:
        return {"ok": False, "reason": "invalid_destination"}
    if system_population not in REPAIR_POPULATION_MODIFIER:
        return {"ok": False, "reason": "invalid_population"}
    ship = fleet_by_id.get(ship_id)
    if ship is None:
        return {"ok": False, "reason": "ship_not_found"}
    if not _ship_present_at_destination(ship, destination_id):
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

    player.credits = int(player.credits) - final_cost
    ship.persistent_state["current_hull_integrity"] = max_hull
    _set_degradation_state(ship, {"weapon": 0, "defense": 0, "engine": 0})
    return {"ok": True, "reason": "ok", "credits": int(player.credits), "final_cost": final_cost}

