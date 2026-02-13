try:
    from reaction_engine import get_npc_outcome
except ModuleNotFoundError:
    from src.reaction_engine import get_npc_outcome
try:
    import interaction_resolvers as _interaction_resolvers
except ModuleNotFoundError:
    from src import interaction_resolvers as _interaction_resolvers


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


def destination_has_datanet_service(destination) -> bool:
    return _interaction_resolvers.destination_has_datanet_service(destination)


def destination_has_shipdock_service(destination) -> bool:
    return _interaction_resolvers.destination_has_shipdock_service(destination)


def destination_actions(destination, base_actions=None):
    return _interaction_resolvers.destination_actions(destination, base_actions=base_actions)


def execute_refuel(*, ship, player_credits: int, requested_units: int | None = None) -> dict:
    return _interaction_resolvers.execute_refuel(
        ship=ship, player_credits=player_credits, requested_units=requested_units
    )


def execute_buy_hull(**kwargs) -> dict:
    return _interaction_resolvers.execute_buy_hull(**kwargs)


def execute_sell_hull(**kwargs) -> dict:
    return _interaction_resolvers.execute_sell_hull(**kwargs)


def execute_buy_module(**kwargs) -> dict:
    return _interaction_resolvers.execute_buy_module(**kwargs)


def execute_sell_module(**kwargs) -> dict:
    return _interaction_resolvers.execute_sell_module(**kwargs)


def execute_repair_ship(**kwargs) -> dict:
    return _interaction_resolvers.execute_repair_ship(**kwargs)


def dispatch_destination_action(action_id: str, **kwargs) -> dict:
    resolver_map = {
        ACTION_REFUEL: execute_refuel,
        ACTION_BUY_HULL: execute_buy_hull,
        ACTION_SELL_HULL: execute_sell_hull,
        ACTION_BUY_MODULE: execute_buy_module,
        ACTION_SELL_MODULE: execute_sell_module,
        ACTION_REPAIR_SHIP: execute_repair_ship,
    }
    resolver = resolver_map.get(action_id)
    if resolver is None:
        return {"ok": False, "reason": "unknown_action", "action_id": action_id}
    return resolver(**kwargs)
