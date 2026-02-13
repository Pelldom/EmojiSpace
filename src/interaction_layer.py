try:
    from reaction_engine import get_npc_outcome
except ModuleNotFoundError:
    from src.reaction_engine import get_npc_outcome
try:
    from data_loader import load_hulls, load_modules
    from ship_assembler import assemble_ship
    from ship_entity import ShipEntity
except ModuleNotFoundError:
    from src.data_loader import load_hulls, load_modules
    from src.ship_assembler import assemble_ship
    from src.ship_entity import ShipEntity


ACTION_IGNORE = "ignore"
ACTION_RESPOND = "respond"
ACTION_HAIL = "hail"
ACTION_ATTACK = "attack"
ACTION_INTIMIDATE = "intimidate"
ACTION_BRIBE = "bribe"
ACTION_SURRENDER = "surrender"
ACTION_COMPLY = "comply"
ACTION_FLEE = "flee"
ACTION_INVESTIGATE = "investigate"
ACTION_END_ENCOUNTER = "end_encounter"
ACTION_REFUEL = "refuel"
ACTION_BUY_HULL = "buy_hull"
ACTION_SELL_HULL = "sell_hull"
ACTION_BUY_MODULE = "buy_module"
ACTION_SELL_MODULE = "sell_module"
ACTION_REPAIR_SHIP = "repair_ship"

NPC_OUTCOME_IGNORE = "ignore"
NPC_OUTCOME_HAIL = "hail"
NPC_OUTCOME_WARN = "warn"
NPC_OUTCOME_ATTACK = "attack"
NPC_OUTCOME_PURSUE = "pursue"
NPC_OUTCOME_ACCEPT = "accept"
NPC_OUTCOME_REFUSE_STAND = "refuse_stand"
NPC_OUTCOME_REFUSE_FLEE = "refuse_flee"
NPC_OUTCOME_REFUSE_ATTACK = "refuse_attack"
NPC_OUTCOME_ACCEPT_AND_ATTACK = "accept_and_attack"

VALID_PLAYER_ACTIONS = {
    ACTION_IGNORE,
    ACTION_RESPOND,
    ACTION_HAIL,
    ACTION_ATTACK,
    ACTION_INTIMIDATE,
    ACTION_BRIBE,
    ACTION_SURRENDER,
    ACTION_COMPLY,
    ACTION_FLEE,
    ACTION_INVESTIGATE,
    ACTION_END_ENCOUNTER,
    ACTION_REFUEL,
    ACTION_BUY_HULL,
    ACTION_SELL_HULL,
    ACTION_BUY_MODULE,
    ACTION_SELL_MODULE,
    ACTION_REPAIR_SHIP,
}

VALID_NPC_OUTCOMES = {
    NPC_OUTCOME_IGNORE,
    NPC_OUTCOME_HAIL,
    NPC_OUTCOME_WARN,
    NPC_OUTCOME_ATTACK,
    NPC_OUTCOME_PURSUE,
    NPC_OUTCOME_ACCEPT,
    NPC_OUTCOME_REFUSE_STAND,
    NPC_OUTCOME_REFUSE_FLEE,
    NPC_OUTCOME_REFUSE_ATTACK,
    NPC_OUTCOME_ACCEPT_AND_ATTACK,
}

HANDLER_END = "end"
HANDLER_REACTION = "reaction"
HANDLER_COMBAT_STUB = "combat_stub"
HANDLER_LAW_STUB = "law_stub"
HANDLER_PURSUIT_STUB = "pursuit_stub"
HANDLER_MARKET_STUB = "market_stub"
HANDLER_MISSION_STUB = "mission_stub"
HANDLER_EXPLORATION_STUB = "exploration_stub"

REACTION_REQUIRED_ACTIONS = {
    ACTION_IGNORE,
    ACTION_RESPOND,
    ACTION_HAIL,
    ACTION_INTIMIDATE,
    ACTION_BRIBE,
    ACTION_SURRENDER,
}


class InteractionResult:
    def __init__(self, next_handler, handler_payload, log):
        self.next_handler = next_handler
        self.handler_payload = handler_payload
        self.log = log


def allowed_actions_initial(spec):
    if spec.initiative == "npc":
        return [ACTION_IGNORE, ACTION_RESPOND, ACTION_ATTACK]
    return [ACTION_IGNORE, ACTION_HAIL, ACTION_ATTACK]


def allowed_actions_post_contact(spec):
    if spec.posture == "neutral":
        return [ACTION_END_ENCOUNTER, ACTION_INTIMIDATE, ACTION_ATTACK, ACTION_RESPOND, ACTION_HAIL]
    if spec.posture == "authority":
        return [
            ACTION_END_ENCOUNTER,
            ACTION_INTIMIDATE,
            ACTION_ATTACK,
            ACTION_COMPLY,
            ACTION_BRIBE,
            ACTION_FLEE,
            ACTION_SURRENDER,
        ]
    if spec.posture == "hostile":
        return [ACTION_SURRENDER, ACTION_BRIBE, ACTION_FLEE, ACTION_ATTACK]
    if spec.posture == "opportunity":
        return [ACTION_INVESTIGATE, ACTION_END_ENCOUNTER, ACTION_ATTACK]
    return []


def _sorted_ascii(values):
    return sorted(values, key=lambda value: value)


def _error_result(log, error_code, error_detail):
    log["error"] = {"code": error_code, "detail": error_detail}
    log["next_handler"] = HANDLER_END
    return InteractionResult(HANDLER_END, {"error": error_code}, log)


def _npc_outcome_to_handler(npc_outcome):
    if npc_outcome == NPC_OUTCOME_IGNORE:
        return HANDLER_END
    if npc_outcome in {NPC_OUTCOME_HAIL, NPC_OUTCOME_WARN}:
        return HANDLER_REACTION
    if npc_outcome == NPC_OUTCOME_ATTACK:
        return HANDLER_COMBAT_STUB
    if npc_outcome == NPC_OUTCOME_PURSUE:
        return HANDLER_PURSUIT_STUB
    if npc_outcome == NPC_OUTCOME_ACCEPT:
        return HANDLER_END
    if npc_outcome in {NPC_OUTCOME_REFUSE_STAND, NPC_OUTCOME_REFUSE_FLEE, NPC_OUTCOME_REFUSE_ATTACK}:
        return HANDLER_REACTION
    if npc_outcome == NPC_OUTCOME_ACCEPT_AND_ATTACK:
        return HANDLER_COMBAT_STUB
    return HANDLER_END


def dispatch_player_action(
    spec,
    player_action,
    world_seed,
    ignore_count,
    reputation_band,
    notoriety_band,
):
    current_phase = "initial" if ignore_count == 0 else "post_contact"
    allowed_actions = (
        allowed_actions_initial(spec) if current_phase == "initial" else allowed_actions_post_contact(spec)
    )
    allowed_actions = _sorted_ascii(allowed_actions)

    log = {
        "encounter_id": spec.encounter_id,
        "subtype_id": spec.subtype_id,
        "posture": spec.posture,
        "initiative": spec.initiative,
        "player_action": player_action,
        "phase": current_phase,
        "allowed_actions": allowed_actions,
        "npc_outcome": None,
        "npc_log": None,
        "phase_transition_hint": (
            "post_contact_next" if player_action in {ACTION_RESPOND, ACTION_HAIL} else "none"
        ),
    }

    if player_action not in VALID_PLAYER_ACTIONS:
        return _error_result(log, "unknown_action", f"Unsupported player action: {player_action}")
    if player_action not in allowed_actions:
        return _error_result(log, "action_not_allowed", f"Action {player_action} is invalid for phase {current_phase}.")

    if player_action == ACTION_END_ENCOUNTER:
        log["next_handler"] = HANDLER_END
        return InteractionResult(HANDLER_END, {}, log)
    if player_action == ACTION_ATTACK:
        log["next_handler"] = HANDLER_COMBAT_STUB
        return InteractionResult(HANDLER_COMBAT_STUB, {}, log)
    if player_action == ACTION_FLEE:
        log["next_handler"] = HANDLER_PURSUIT_STUB
        return InteractionResult(HANDLER_PURSUIT_STUB, {}, log)
    if player_action == ACTION_COMPLY:
        if spec.posture != "authority":
            return _error_result(log, "authority_only_action", "comply requires authority posture.")
        log["next_handler"] = HANDLER_LAW_STUB
        return InteractionResult(HANDLER_LAW_STUB, {}, log)
    if player_action == ACTION_BRIBE and spec.posture == "authority":
        log["next_handler"] = HANDLER_LAW_STUB
        return InteractionResult(HANDLER_LAW_STUB, {}, log)
    if player_action == ACTION_INVESTIGATE:
        log["next_handler"] = HANDLER_EXPLORATION_STUB
        return InteractionResult(HANDLER_EXPLORATION_STUB, {}, log)

    if player_action in REACTION_REQUIRED_ACTIONS:
        npc_outcome, npc_log = get_npc_outcome(
            spec,
            player_action,
            world_seed,
            ignore_count,
            reputation_band,
            notoriety_band,
        )
        log["npc_outcome"] = npc_outcome
        log["npc_log"] = npc_log

        if npc_outcome not in VALID_NPC_OUTCOMES:
            return _error_result(log, "unknown_npc_outcome", f"Unsupported npc_outcome: {npc_outcome}")

        next_handler = _npc_outcome_to_handler(npc_outcome)
        log["next_handler"] = next_handler
        return InteractionResult(
            next_handler,
            {"npc_outcome": npc_outcome},
            log,
        )

    return _error_result(log, "unhandled_action", f"No dispatch rule for action: {player_action}")


def _smoke_test_dispatch_structure():
    try:
        from encounter_generator import generate_encounter
    except ModuleNotFoundError:
        from src.encounter_generator import generate_encounter

    spec = generate_encounter(
        encounter_id="ENC-SMOKE-001",
        world_seed="WORLD-SMOKE",
        system_government_id="empire",
        active_situations=[],
    )
    result = dispatch_player_action(
        spec=spec,
        player_action=ACTION_IGNORE,
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_band=0,
        notoriety_band=0,
    )
    if result.next_handler not in {
        HANDLER_END,
        HANDLER_REACTION,
        HANDLER_COMBAT_STUB,
        HANDLER_LAW_STUB,
        HANDLER_PURSUIT_STUB,
        HANDLER_MARKET_STUB,
        HANDLER_MISSION_STUB,
        HANDLER_EXPLORATION_STUB,
    }:
        raise ValueError("Smoke test failed: invalid next_handler.")
    if not isinstance(result.log, dict):
        raise ValueError("Smoke test failed: log is not a dict.")
    required_log_fields = {"player_action", "phase", "allowed_actions", "npc_outcome", "npc_log", "next_handler"}
    if not required_log_fields.issubset(set(result.log.keys())):
        raise ValueError("Smoke test failed: missing required log fields.")
    return result


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
    if destination_has_datanet_service(destination) and ACTION_REFUEL not in actions:
        actions.append(ACTION_REFUEL)
    if destination_has_shipdock_service(destination):
        for action in (
            ACTION_BUY_HULL,
            ACTION_SELL_HULL,
            ACTION_BUY_MODULE,
            ACTION_SELL_MODULE,
            ACTION_REPAIR_SHIP,
        ):
            if action not in actions:
                actions.append(action)
    return sorted(actions, key=lambda value: value)


def execute_refuel(*, ship, player_credits: int, requested_units: int | None = None) -> dict:
    if requested_units is not None and requested_units < 0:
        return {"ok": False, "reason": "invalid_request", "units_purchased": 0, "total_cost": 0, "credits": player_credits}

    missing = max(0, int(ship.fuel_capacity) - int(ship.current_fuel))
    units_target = missing if requested_units is None else min(requested_units, missing)
    total_cost = units_target * FUEL_PRICE_PER_UNIT
    if player_credits < total_cost:
        return {"ok": False, "reason": "insufficient_credits", "units_purchased": 0, "total_cost": 0, "credits": player_credits}

    ship.current_fuel = int(ship.current_fuel) + units_target
    return {
        "ok": True,
        "reason": "ok",
        "units_purchased": units_target,
        "total_cost": total_cost,
        "credits": player_credits - total_cost,
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


def _compute_hull_integrity_max(hull_id: str, module_instances: list[dict]) -> int:
    tier_baseline = {1: 8, 2: 10, 3: 12, 4: 15, 5: 18}
    frame_bias = {"MIL": 2, "CIV": 0, "FRG": 3, "XA": 0, "XB": -2, "XC": 4, "ALN": 1}
    hull = _hull_by_id()[hull_id]
    module_defs = _module_by_id()
    value = tier_baseline[hull["tier"]] + frame_bias[hull["frame"]]
    is_experimental = "ship:trait_experimental" in hull.get("traits", [])
    is_alien = "ship:trait_alien" in hull.get("traits", [])
    for instance in module_instances:
        module = module_defs.get(instance["module_id"])
        if module is None:
            continue
        secondaries = set(instance.get("secondary_tags", []))
        secondaries.update({entry.split("secondary:", 1)[1] for entry in secondaries if isinstance(entry, str) and entry.startswith("secondary:")})
        if "alien" in secondaries and is_alien:
            value += 1
        if "prototype" in secondaries and is_experimental:
            value += 1
        if module.get("primary_tag") == "combat:defense_armored":
            value += 1
        if "unstable" in secondaries:
            value -= 1
    return max(4, int(value))


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
    max_hull_integrity = _compute_hull_integrity_max(hull_id, [])
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
    modules.pop(remove_index)

    module = _module_by_id().get(module_id)
    if module is None:
        return {"ok": False, "reason": "unknown_module"}
    assembled = assemble_ship(ship.model_id, modules, _degradation_state(ship))
    _set_module_instances(ship, modules)
    ship.fuel_capacity = int(assembled["fuel_capacity"])
    ship.current_fuel = min(int(ship.current_fuel), int(ship.fuel_capacity))
    ship.persistent_state["assembled"] = assembled

    sell_price = float(module["base_price_credits"]) * 0.5
    final_price = int(round(sell_price * float(price_modifier_multiplier)))
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
