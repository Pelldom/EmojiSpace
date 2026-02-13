try:
    from encounter_generator import deterministic_float
except ModuleNotFoundError:
    from src.encounter_generator import deterministic_float


class PursuitResult:
    def __init__(
        self,
        encounter_id,
        pursuer_speed,
        pursued_speed,
        speed_delta,
        pilot_delta,
        tr_delta,
        engine_delta,
        outcome,
        threshold,
        roll,
        escaped,
        log,
    ):
        self.encounter_id = encounter_id
        self.pursuer_speed = pursuer_speed
        self.pursued_speed = pursued_speed
        self.speed_delta = speed_delta
        self.pilot_delta = pilot_delta
        self.tr_delta = tr_delta
        self.engine_delta = engine_delta
        self.outcome = outcome
        self.threshold = threshold
        self.roll = roll
        self.escaped = escaped
        self.log = log


def _validated_ship_fields(ship, role_name):
    if "speed" not in ship:
        raise ValueError(f"{role_name} ship missing required field: speed.")
    speed = ship["speed"]
    if not isinstance(speed, int) or speed < 0:
        raise ValueError(f"{role_name} ship has invalid speed.")

    pilot_skill = ship.get("pilot_skill", 3)
    if not isinstance(pilot_skill, int) or pilot_skill < 1 or pilot_skill > 5:
        raise ValueError(f"{role_name} ship has invalid pilot_skill.")

    return speed, pilot_skill


def _clamp_band(value, default=1):
    if value is None:
        return int(default)
    if not isinstance(value, int):
        raise ValueError("Band values must be integers.")
    return max(1, min(5, value))


def _derive_bands(ship, speed):
    engine_band = _clamp_band(ship.get("engine_band"), default=max(1, min(5, speed)))
    tr_band = _clamp_band(ship.get("tr_band"), default=engine_band)
    return tr_band, engine_band


def resolve_pursuit(
    encounter_id,
    world_seed,
    pursuer_ship,
    pursued_ship,
):
    pursuer_speed, pursuer_pilot = _validated_ship_fields(pursuer_ship, "pursuer")
    pursued_speed, pursued_pilot = _validated_ship_fields(pursued_ship, "pursued")

    pursuer_cloak = pursuer_ship.get("cloaking_device", False)
    pursued_cloak = pursued_ship.get("cloaking_device", False)
    pursuer_interdiction = pursuer_ship.get("interdiction_device", False)
    pursuer_tr_band, pursuer_engine_band = _derive_bands(pursuer_ship, pursuer_speed)
    pursued_tr_band, pursued_engine_band = _derive_bands(pursued_ship, pursued_speed)

    speed_delta = pursued_speed - pursuer_speed
    engine_delta = pursued_engine_band - pursuer_engine_band
    if engine_delta >= 2:
        threshold = 0.7
    elif engine_delta == 1:
        threshold = 0.6
    elif engine_delta == 0:
        threshold = 0.5
    elif engine_delta == -1:
        threshold = 0.4
    else:
        threshold = 0.3
    base_threshold_before_modifiers = threshold

    tr_delta = pursued_tr_band - pursuer_tr_band
    threshold += 0.05 * tr_delta

    cloak_applied = bool(pursued_cloak)
    if cloak_applied:
        threshold += 0.1

    interdiction_applied = bool(pursuer_interdiction)
    if interdiction_applied:
        threshold -= 0.15

    pilot_delta = pursued_pilot - pursuer_pilot
    threshold += 0.1 * pilot_delta

    if threshold < 0.05:
        threshold = 0.05
    if threshold > 0.95:
        threshold = 0.95

    seed_string = f"{world_seed}{encounter_id}_pursuit"
    roll = deterministic_float(seed_string)
    escaped = roll < threshold
    outcome = "escape_success" if escaped else "escape_fail"

    log = {
        "seed": seed_string,
        "speed_delta": speed_delta,
        "engine_delta": engine_delta,
        "tr_delta": tr_delta,
        "pilot_delta": pilot_delta,
        "pursuer_tr_band": pursuer_tr_band,
        "pursued_tr_band": pursued_tr_band,
        "pursuer_engine_band": pursuer_engine_band,
        "pursued_engine_band": pursued_engine_band,
        "cloak_applied": cloak_applied,
        "interdiction_applied": interdiction_applied,
        "base_threshold_before_modifiers": base_threshold_before_modifiers,
        "final_threshold": threshold,
        "probability_distribution": {"escape_success": threshold, "escape_fail": 1.0 - threshold},
        "outcome": outcome,
        "pursuer_cloak_present": bool(pursuer_cloak),
    }

    return PursuitResult(
        encounter_id=encounter_id,
        pursuer_speed=pursuer_speed,
        pursued_speed=pursued_speed,
        speed_delta=speed_delta,
        pilot_delta=pilot_delta,
        tr_delta=tr_delta,
        engine_delta=engine_delta,
        outcome=outcome,
        threshold=threshold,
        roll=roll,
        escaped=escaped,
        log=log,
    )


def _smoke_test_pursuit():
    pursuer = {"speed": 4, "pilot_skill": 3}
    pursued = {"speed": 6, "pilot_skill": 4}

    first = resolve_pursuit("ENC-PURSUIT-SMOKE-001", "WORLD-SMOKE", pursuer, pursued)
    second = resolve_pursuit("ENC-PURSUIT-SMOKE-001", "WORLD-SMOKE", pursuer, pursued)
    if first.escaped != second.escaped:
        raise ValueError("Smoke test failed: pursuit outcome is not deterministic.")
    if first.roll != second.roll:
        raise ValueError("Smoke test failed: pursuit roll is not deterministic.")
    if first.threshold != second.threshold:
        raise ValueError("Smoke test failed: pursuit threshold is not deterministic.")

    no_interdiction = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-002",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 3, "interdiction_device": False},
        {"speed": 6, "pilot_skill": 4},
    )
    with_interdiction = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-002",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 3, "interdiction_device": True},
        {"speed": 6, "pilot_skill": 4},
    )
    if with_interdiction.threshold >= no_interdiction.threshold:
        raise ValueError("Smoke test failed: interdiction did not reduce threshold.")

    no_cloak = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-003",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 3},
        {"speed": 6, "pilot_skill": 4, "cloaking_device": False},
    )
    with_cloak = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-003",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 3},
        {"speed": 6, "pilot_skill": 4, "cloaking_device": True},
    )
    if with_cloak.threshold <= no_cloak.threshold:
        raise ValueError("Smoke test failed: cloak did not increase threshold.")

    lower_pursued_pilot = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-004",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 3},
        {"speed": 6, "pilot_skill": 3},
    )
    higher_pursued_pilot = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-004",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 3},
        {"speed": 6, "pilot_skill": 5},
    )
    if higher_pursued_pilot.threshold <= lower_pursued_pilot.threshold:
        raise ValueError("Smoke test failed: higher pursued pilot did not increase threshold.")

    lower_pursuer_pilot = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-005",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 2},
        {"speed": 6, "pilot_skill": 4},
    )
    higher_pursuer_pilot = resolve_pursuit(
        "ENC-PURSUIT-SMOKE-005",
        "WORLD-SMOKE",
        {"speed": 4, "pilot_skill": 5},
        {"speed": 6, "pilot_skill": 4},
    )
    if higher_pursuer_pilot.threshold >= lower_pursuer_pilot.threshold:
        raise ValueError("Smoke test failed: higher pursuer pilot did not decrease threshold.")

    return first, second
