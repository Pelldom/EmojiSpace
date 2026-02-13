try:
    from encounter_generator import deterministic_weighted_choice
except ModuleNotFoundError:
    from src.encounter_generator import deterministic_weighted_choice


ACTION_TO_BLOCK = {
    "ignore": "on_ignore",
    "respond": "on_respond",
    "hail": "on_respond",
    "intimidate": "on_intimidate",
    "bribe": "on_bribe",
    "surrender": "on_surrender",
}

OUTCOME_KEYS = [
    "ignore",
    "hail",
    "warn",
    "attack",
    "pursue",
    "accept",
    "refuse_stand",
    "refuse_flee",
    "refuse_attack",
    "accept_and_attack",
]


def _band_from_score(score):
    if score is None:
        return 3
    if score < 1:
        score = 1
    if score > 100:
        score = 100
    return ((score - 1) // 20) + 1


def get_npc_outcome(
    spec,
    player_action,
    world_seed,
    ignore_count,
    reputation_score,
    notoriety_score,
    law_score=None,
    outlaw_score=None,
):
    block_name = ACTION_TO_BLOCK.get(player_action)
    if block_name is None:
        return ("ignore", {"reason": "no_response_block"})

    law_band = _band_from_score(law_score) if law_score is not None else None
    outlaw_band = _band_from_score(outlaw_score) if outlaw_score is not None else None
    if law_band is not None and outlaw_band is not None:
        player_tr = max(law_band, outlaw_band)
    elif law_band is not None:
        player_tr = law_band
    elif outlaw_band is not None:
        player_tr = outlaw_band
    else:
        player_tr = 1

    reputation_band = _band_from_score(reputation_score)
    notoriety_band = _band_from_score(notoriety_score)

    profile = spec.npc_response_profile if isinstance(spec.npc_response_profile, dict) else {}
    response_block = profile.get(block_name, {})
    if not isinstance(response_block, dict):
        response_block = {}

    outcomes = []
    weights = []
    for outcome_key in OUTCOME_KEYS:
        if outcome_key == "accept_and_attack" and not spec.allows_betrayal:
            continue
        weight = response_block.get(outcome_key, 0)
        if isinstance(weight, int) and weight > 0:
            outcomes.append(outcome_key)
            weights.append(weight)

    if sum(weights) == 0:
        return ("ignore", {"reason": "zero_total_weight"})

    baseline_weights = list(weights)
    ignore_escalation_applied = False
    modifiers_applied = []

    # Single-step ignore escalation.
    if player_action == "ignore" and ignore_count >= 1:
        ignore_escalation_applied = True
        if "ignore" in outcomes:
            ignore_index = outcomes.index("ignore")
            weights[ignore_index] = 0
            modifiers_applied.append("ignore_to_zero")
        if "attack" in outcomes:
            attack_index = outcomes.index("attack")
            weights[attack_index] += 1
            modifiers_applied.append("attack_plus_one_on_ignore")
        if "pursue" in outcomes:
            pursue_index = outcomes.index("pursue")
            weights[pursue_index] += 1
            modifiers_applied.append("pursue_plus_one_on_ignore")

    npc_tr = spec.threat_rating_tr if isinstance(spec.threat_rating_tr, int) else 1
    tr_delta = npc_tr - player_tr

    # TR delta modifier.
    if tr_delta >= 2:
        if "attack" in outcomes:
            attack_index = outcomes.index("attack")
            weights[attack_index] += 1
            modifiers_applied.append("attack_plus_one_high_tr_delta")
        if "accept" in outcomes:
            accept_index = outcomes.index("accept")
            weights[accept_index] -= 1
            modifiers_applied.append("accept_minus_one_high_tr_delta")
    elif tr_delta <= -2:
        if "accept" in outcomes:
            accept_index = outcomes.index("accept")
            weights[accept_index] += 1
            modifiers_applied.append("accept_plus_one_low_tr_delta")
        if "refuse_flee" in outcomes:
            refuse_flee_index = outcomes.index("refuse_flee")
            weights[refuse_flee_index] += 1
            modifiers_applied.append("refuse_flee_plus_one_low_tr_delta")

    # Reputation modifier.
    if reputation_band >= 4 and spec.posture in {"neutral", "authority"}:
        if "attack" in outcomes:
            attack_index = outcomes.index("attack")
            weights[attack_index] -= 1
            modifiers_applied.append("attack_minus_one_high_reputation")
    if reputation_band >= 4 and player_action == "intimidate":
        if "accept" in outcomes:
            accept_index = outcomes.index("accept")
            weights[accept_index] -= 1
            modifiers_applied.append("accept_minus_one_high_reputation_intimidate")
    if reputation_band <= 2 and spec.posture in {"neutral", "authority"}:
        if "attack" in outcomes:
            attack_index = outcomes.index("attack")
            weights[attack_index] += 1
            modifiers_applied.append("attack_plus_one_low_reputation")
    weights_after_reputation = list(weights)

    # Notoriety modifier.
    if notoriety_band >= 4 and player_action == "intimidate":
        if "accept" in outcomes:
            accept_index = outcomes.index("accept")
            weights[accept_index] += 1
            modifiers_applied.append("accept_plus_one_high_notoriety_intimidate")
        if "refuse_flee" in outcomes:
            refuse_flee_index = outcomes.index("refuse_flee")
            weights[refuse_flee_index] += 1
            modifiers_applied.append("refuse_flee_plus_one_high_notoriety_intimidate")
    if notoriety_band <= 2 and player_action == "intimidate":
        if "accept" in outcomes:
            accept_index = outcomes.index("accept")
            weights[accept_index] -= 1
            modifiers_applied.append("accept_minus_one_low_notoriety_intimidate")
    weights_after_notoriety = list(weights)

    # Clamp negative weights to zero.
    for index, weight in enumerate(weights):
        if weight < 0:
            weights[index] = 0

    total_after_modifiers = sum(weights)
    zero_after_modifiers = total_after_modifiers == 0
    if zero_after_modifiers:
        return ("ignore", {"reason": "zero_total_after_modifiers"})

    seed_string = f"{world_seed}{spec.encounter_id}{player_action}{ignore_count}"
    selected_outcome = deterministic_weighted_choice(outcomes, weights, seed_string)
    if selected_outcome is None:
        selected_outcome = "ignore"

    return (
        selected_outcome,
        {
            "player_action": player_action,
            "block_used": block_name,
            "baseline_weights": dict(response_block),
            "effective_outcomes": outcomes,
            "effective_weights": baseline_weights,
            "weights_after_modifiers": list(weights),
            "weights_after_reputation": weights_after_reputation,
            "weights_after_notoriety": weights_after_notoriety,
            "seed": seed_string,
            "selected_outcome": selected_outcome,
            "player_tr": player_tr,
            "derived_player_tr": player_tr,
            "npc_tr": npc_tr,
            "tr_delta": tr_delta,
            "ignore_escalation_applied": ignore_escalation_applied,
            "zero_after_modifiers": zero_after_modifiers,
            "reputation_score": reputation_score,
            "reputation_band": reputation_band,
            "notoriety_score": notoriety_score,
            "notoriety_band": notoriety_band,
            "law_score": law_score,
            "outlaw_score": outlaw_score,
            "modifiers_applied": modifiers_applied,
        },
    )


def _smoke_test_reaction_baseline():
    try:
        from encounter_generator import generate_encounter
    except ModuleNotFoundError:
        from src.encounter_generator import generate_encounter

    spec = generate_encounter(
        encounter_id="ENC-SMOKE-REACTION-001",
        world_seed="WORLD-SMOKE",
        system_government_id="empire",
        active_situations=["war"],
    )
    first_outcome, first_log = get_npc_outcome(
        spec=spec,
        player_action="ignore",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=0,
        notoriety_score=0,
        law_score=10,
        outlaw_score=20,
    )
    second_outcome, second_log = get_npc_outcome(
        spec=spec,
        player_action="ignore",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=0,
        notoriety_score=0,
        law_score=10,
        outlaw_score=20,
    )
    if first_outcome != second_outcome:
        raise ValueError("Smoke test failed: non-deterministic outcome.")
    if first_log.get("seed") != second_log.get("seed"):
        raise ValueError("Smoke test failed: non-deterministic seed.")

    # Ignore escalation path: verify modifier changes weights when ignore_count increases.
    _, ignore_zero_log = get_npc_outcome(
        spec=spec,
        player_action="ignore",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=0,
        notoriety_score=0,
        law_score=10,
        outlaw_score=20,
    )
    _, ignore_one_log = get_npc_outcome(
        spec=spec,
        player_action="ignore",
        world_seed="WORLD-SMOKE",
        ignore_count=1,
        reputation_score=0,
        notoriety_score=0,
        law_score=10,
        outlaw_score=20,
    )
    if ignore_zero_log.get("weights_after_modifiers") == ignore_one_log.get("weights_after_modifiers"):
        raise ValueError("Smoke test failed: ignore escalation did not change modifier weights.")

    # TR delta path: use a synthetic spec to guarantee accept/refuse_flee keys exist.
    class _SyntheticSpec:
        def __init__(self):
            self.encounter_id = "ENC-SMOKE-REACTION-TR-001"
            self.allows_betrayal = True
            self.threat_rating_tr = 3
            self.posture = "authority"
            self.npc_response_profile = {
                "on_bribe": {
                    "accept": 2,
                    "refuse_flee": 1,
                    "attack": 1,
                },
                "on_intimidate": {
                    "accept": 2,
                    "refuse_flee": 1,
                    "attack": 2,
                }
            }

    synthetic_spec = _SyntheticSpec()
    _, high_delta_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="bribe",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=50,
        law_score=1,
        outlaw_score=10,
    )
    _, low_delta_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="bribe",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=50,
        law_score=100,
        outlaw_score=99,
    )
    if high_delta_log.get("tr_delta", 0) < 2:
        raise ValueError("Smoke test failed: expected high TR delta path not reached.")
    if low_delta_log.get("tr_delta", 0) > -2:
        raise ValueError("Smoke test failed: expected low TR delta path not reached.")
    if high_delta_log.get("weights_after_modifiers") == low_delta_log.get("weights_after_modifiers"):
        raise ValueError("Smoke test failed: TR delta modifiers did not alter weights.")

    # Player TR derivation changes with law/outlaw tracks.
    _, low_tr_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="bribe",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=50,
        law_score=1,
        outlaw_score=1,
    )
    _, high_tr_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="bribe",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=50,
        law_score=100,
        outlaw_score=1,
    )
    if low_tr_log.get("derived_player_tr") == high_tr_log.get("derived_player_tr"):
        raise ValueError("Smoke test failed: derived player TR did not change with law/outlaw scores.")

    # High reputation lowers attack weight for neutral/authority.
    _, high_rep_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="intimidate",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=90,
        notoriety_score=50,
        law_score=50,
        outlaw_score=50,
    )
    _, low_rep_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="intimidate",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=10,
        notoriety_score=50,
        law_score=50,
        outlaw_score=50,
    )
    high_rep_outcomes = high_rep_log.get("effective_outcomes", [])
    low_rep_outcomes = low_rep_log.get("effective_outcomes", [])
    if "attack" in high_rep_outcomes and "attack" in low_rep_outcomes:
        high_rep_attack = high_rep_log["weights_after_reputation"][high_rep_outcomes.index("attack")]
        low_rep_attack = low_rep_log["weights_after_reputation"][low_rep_outcomes.index("attack")]
        if high_rep_attack >= low_rep_attack:
            raise ValueError("Smoke test failed: high reputation did not reduce attack weight.")

    # High notoriety on intimidate increases accept weight.
    _, high_not_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="intimidate",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=90,
        law_score=50,
        outlaw_score=50,
    )
    _, low_not_log = get_npc_outcome(
        spec=synthetic_spec,
        player_action="intimidate",
        world_seed="WORLD-SMOKE",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=10,
        law_score=50,
        outlaw_score=50,
    )
    high_not_outcomes = high_not_log.get("effective_outcomes", [])
    low_not_outcomes = low_not_log.get("effective_outcomes", [])
    if "accept" in high_not_outcomes and "accept" in low_not_outcomes:
        high_not_accept = high_not_log["weights_after_notoriety"][high_not_outcomes.index("accept")]
        low_not_accept = low_not_log["weights_after_notoriety"][low_not_outcomes.index("accept")]
        if high_not_accept <= low_not_accept:
            raise ValueError("Smoke test failed: high notoriety did not increase accept weight on intimidate.")

    return first_outcome, first_log
