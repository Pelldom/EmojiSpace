from pathlib import Path
from typing import Any
import hashlib
import json


ALLOWED_POSTURES = {"neutral", "authority", "hostile", "opportunity"}
ALLOWED_INITIATIVES = {"player", "npc"}
ALLOWED_FLAGS = {
    "civilian_target",
    "authority_actor",
    "criminal_actor",
    "piracy_context",
    "salvage_possible",
    "trade_possible",
    "mission_possible",
    "anomaly_discovery_possible",
}
REQUIRED_ENCOUNTER_TYPE_FIELDS = (
    "subtype_id",
    "emoji",
    "posture",
    "initiative",
    "allows_betrayal",
    "base_weight",
    "allowed_TR_range",
    "participant_templates",
    "default_flags",
    "reward_profiles",
    "npc_response_profile",
)


class EncounterSpec:
    def __init__(
        self,
        encounter_id,
        subtype_id,
        emoji,
        posture,
        initiative,
        allows_betrayal,
        threat_rating_tr,
        participant_templates,
        default_flags,
        reward_profile_id,
        npc_response_profile,
        selection_log,
    ):
        self.encounter_id = encounter_id
        self.subtype_id = subtype_id
        self.emoji = emoji
        self.posture = posture
        self.initiative = initiative
        self.allows_betrayal = allows_betrayal
        self.threat_rating_tr = threat_rating_tr
        self.participant_templates = participant_templates
        self.default_flags = default_flags
        self.reward_profile_id = reward_profile_id
        self.npc_response_profile = npc_response_profile
        self.selection_log = selection_log


def deterministic_float(seed_string):
    try:
        encoded = seed_string.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("Seed string must be ASCII for deterministic hashing.") from error
    digest = hashlib.sha256(encoded).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return value / (2**64)


def deterministic_weighted_choice(items, weights, seed_string):
    if len(items) != len(weights):
        raise ValueError("deterministic_weighted_choice requires items and weights lengths to match.")
    if any((not isinstance(weight, int)) or weight < 0 for weight in weights):
        raise ValueError("deterministic_weighted_choice requires non-negative integer weights.")
    total = sum(weights)
    if total == 0:
        return None
    roll = deterministic_float(seed_string)
    cumulative = 0
    threshold = roll * total
    for item, weight in zip(items, weights):
        cumulative += weight
        if threshold < cumulative:
            return item
    return items[-1]


def _load_encounter_types_file() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "data" / "encounter_types.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError("encounter_types.json not found at data/encounter_types.json.") from error
    except json.JSONDecodeError as error:
        raise ValueError("encounter_types.json is not valid JSON.") from error


def _load_governments_file() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "data" / "governments.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError("governments.json not found at data/governments.json.") from error
    except json.JSONDecodeError as error:
        raise ValueError("governments.json is not valid JSON.") from error


def load_governments():
    payload = _load_governments_file()
    governments = payload.get("governments")
    if not isinstance(governments, list):
        raise ValueError("governments.json missing or invalid governments list.")

    by_id = {}
    for index, government in enumerate(governments):
        if not isinstance(government, dict):
            raise ValueError(f"governments entry {index} is invalid: expected object.")
        government_id = government.get("id")
        if not isinstance(government_id, str) or not government_id:
            raise ValueError(f"governments entry {index} has invalid id.")
        if government_id in by_id:
            raise ValueError(f"Duplicate government id in governments.json: {government_id}.")
        enforcement_strength = government.get("enforcement_strength")
        if not isinstance(enforcement_strength, int) or enforcement_strength < 0:
            raise ValueError(f"Government {government_id} has invalid enforcement_strength.")
        by_id[government_id] = government
    return by_id


def _validate_allowed_tr_range(subtype_id: str, tr_range: Any) -> None:
    if not isinstance(tr_range, dict):
        raise ValueError(f"Subtype {subtype_id} has invalid allowed_TR_range: expected object.")
    if "min" not in tr_range or "max" not in tr_range:
        raise ValueError(f"Subtype {subtype_id} missing allowed_TR_range min/max.")
    min_tr = tr_range["min"]
    max_tr = tr_range["max"]
    if not isinstance(min_tr, int) or not isinstance(max_tr, int):
        raise ValueError(f"Subtype {subtype_id} has non-integer allowed_TR_range bounds.")
    if not (1 <= min_tr <= max_tr <= 5):
        raise ValueError(f"Subtype {subtype_id} has out-of-range allowed_TR_range bounds.")


def _validate_reward_profiles(subtype_id: str, reward_profiles: Any) -> None:
    if not isinstance(reward_profiles, list):
        raise ValueError(f"Subtype {subtype_id} has invalid reward_profiles: expected list.")
    for index, entry in enumerate(reward_profiles):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Subtype {subtype_id} reward_profiles entry {index} is invalid: expected object."
            )
        if "reward_profile_id" not in entry or "weight" not in entry:
            raise ValueError(
                f"Subtype {subtype_id} reward_profiles entry {index} missing reward_profile_id or weight."
            )
        if not isinstance(entry["weight"], int) or entry["weight"] < 0:
            raise ValueError(
                f"Subtype {subtype_id} reward_profiles entry {index} has invalid weight."
            )


def _validate_participant_templates(subtype_id: str, participant_templates: Any) -> None:
    if not isinstance(participant_templates, list):
        raise ValueError(f"Subtype {subtype_id} has invalid participant_templates: expected list.")
    for index, template in enumerate(participant_templates):
        if not isinstance(template, dict):
            raise ValueError(
                f"Subtype {subtype_id} participant_templates entry {index} is invalid: expected object."
            )
        required_fields = ("template_id", "role", "min_count", "max_count")
        for field_name in required_fields:
            if field_name not in template:
                raise ValueError(
                    f"Subtype {subtype_id} participant_templates entry {index} missing {field_name}."
                )
        min_count = template["min_count"]
        max_count = template["max_count"]
        if not isinstance(min_count, int) or not isinstance(max_count, int):
            raise ValueError(
                f"Subtype {subtype_id} participant_templates entry {index} has non-integer counts."
            )
        if min_count < 1 or max_count < min_count:
            raise ValueError(
                f"Subtype {subtype_id} participant_templates entry {index} has invalid count bounds."
            )


def _validate_default_flags(subtype_id: str, default_flags: Any) -> None:
    if not isinstance(default_flags, list):
        raise ValueError(f"Subtype {subtype_id} has invalid default_flags: expected list.")
    for index, flag in enumerate(default_flags):
        if not isinstance(flag, str):
            raise ValueError(f"Subtype {subtype_id} default_flags entry {index} must be a string.")
        if flag not in ALLOWED_FLAGS:
            raise ValueError(f"Subtype {subtype_id} default_flags entry {index} is not an allowed flag.")


def _validate_optional_bias_map(subtype_id: str, field_name: str, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError(f"Subtype {subtype_id} field {field_name} must be an object when present.")
    for key, modifier in value.items():
        if not isinstance(key, str):
            raise ValueError(f"Subtype {subtype_id} field {field_name} has non-string key.")
        if not isinstance(modifier, int):
            raise ValueError(f"Subtype {subtype_id} field {field_name} has non-integer modifier.")


def load_encounter_types():
    payload = _load_encounter_types_file()
    if "version" not in payload:
        raise ValueError("encounter_types.json missing required top-level field: version.")
    encounter_types = payload.get("encounter_types")
    if not isinstance(encounter_types, list):
        raise ValueError("encounter_types.json missing or invalid encounter_types list.")

    subtype_ids: set[str] = set()
    validated_types = []
    for index, encounter_type in enumerate(encounter_types):
        if not isinstance(encounter_type, dict):
            raise ValueError(f"encounter_types entry {index} is invalid: expected object.")
        missing_fields = [field for field in REQUIRED_ENCOUNTER_TYPE_FIELDS if field not in encounter_type]
        if missing_fields:
            missing_text = ", ".join(missing_fields)
            raise ValueError(f"encounter_types entry {index} missing required fields: {missing_text}.")

        subtype_id = encounter_type["subtype_id"]
        if not isinstance(subtype_id, str) or not subtype_id:
            raise ValueError(f"encounter_types entry {index} has invalid subtype_id.")
        if subtype_id in subtype_ids:
            raise ValueError(f"Duplicate subtype_id in encounter_types.json: {subtype_id}.")
        subtype_ids.add(subtype_id)

        posture = encounter_type["posture"]
        if posture not in ALLOWED_POSTURES:
            raise ValueError(f"Subtype {subtype_id} has invalid posture: {posture}.")

        initiative = encounter_type["initiative"]
        if initiative not in ALLOWED_INITIATIVES:
            raise ValueError(f"Subtype {subtype_id} has invalid initiative: {initiative}.")

        allows_betrayal = encounter_type["allows_betrayal"]
        if not isinstance(allows_betrayal, bool):
            raise ValueError(f"Subtype {subtype_id} has invalid allows_betrayal: expected bool.")

        base_weight = encounter_type["base_weight"]
        if not isinstance(base_weight, int) or base_weight < 0:
            raise ValueError(f"Subtype {subtype_id} has invalid base_weight: must be non-negative integer.")

        _validate_allowed_tr_range(subtype_id, encounter_type["allowed_TR_range"])
        _validate_participant_templates(subtype_id, encounter_type["participant_templates"])
        _validate_default_flags(subtype_id, encounter_type["default_flags"])
        _validate_reward_profiles(subtype_id, encounter_type["reward_profiles"])

        npc_response_profile = encounter_type["npc_response_profile"]
        if not isinstance(npc_response_profile, dict):
            raise ValueError(f"Subtype {subtype_id} has invalid npc_response_profile: expected object.")

        _validate_optional_bias_map(subtype_id, "situation_bias", encounter_type.get("situation_bias"))

        validated_types.append(encounter_type)

    return validated_types


def select_subtype(
    encounter_id,
    world_seed,
    system_government_id,
    active_situations,
    travel_context=None,
):
    encounter_types = load_encounter_types()
    governments = load_governments()
    if system_government_id not in governments:
        raise ValueError(f"Unknown system_government_id: {system_government_id}.")
    enforcement_strength = governments[system_government_id]["enforcement_strength"]

    if travel_context is None:
        travel_context_mode = "in_system"
    else:
        if not isinstance(travel_context, dict):
            raise ValueError("travel_context must be None or a dict.")
        travel_context_mode = travel_context.get("mode", "in_system")
        if travel_context_mode not in {"in_system", "system_arrival"}:
            raise ValueError("travel_context.mode must be 'in_system' or 'system_arrival'.")

    normalized_situations = active_situations or []
    weighted_candidates = []
    candidate_logs = []

    for encounter_type in encounter_types:
        subtype_id = encounter_type["subtype_id"]
        base_weight = encounter_type["base_weight"]
        modifiers = []
        effective_weight = base_weight

        authority_enforcement_applied = False
        arrival_enforcement_applied = False
        if encounter_type["posture"] == "authority":
            effective_weight += enforcement_strength
            authority_enforcement_applied = True
            modifiers.append(
                {
                    "kind": "authority_enforcement",
                    "modifier": enforcement_strength,
                }
            )
            if travel_context_mode == "system_arrival":
                effective_weight += enforcement_strength
                arrival_enforcement_applied = True
                modifiers.append(
                    {
                        "kind": "arrival_enforcement",
                        "modifier": enforcement_strength,
                    }
                )

        situation_bias = encounter_type.get("situation_bias")
        if isinstance(situation_bias, dict):
            for situation in normalized_situations:
                if situation in situation_bias:
                    situation_modifier = situation_bias[situation]
                    effective_weight += situation_modifier
                    modifiers.append(
                        {
                            "kind": "situation_bias",
                            "key": situation,
                            "modifier": situation_modifier,
                        }
                    )

        clamped_weight = max(effective_weight, 0)
        candidate_log = {
            "subtype_id": subtype_id,
            "base_weight": base_weight,
            "modifiers": modifiers,
            "enforcement_strength": enforcement_strength,
            "travel_context_mode": travel_context_mode,
            "authority_enforcement_applied": authority_enforcement_applied,
            "arrival_enforcement_applied": arrival_enforcement_applied,
            "effective_weight_before_clamp": effective_weight,
            "final_weight": clamped_weight,
        }
        candidate_logs.append(candidate_log)

        if clamped_weight > 0:
            weighted_candidates.append((subtype_id, encounter_type, clamped_weight))

    weighted_candidates.sort(key=lambda row: row[0])
    items = [row[1] for row in weighted_candidates]
    weights = [row[2] for row in weighted_candidates]
    seed_string = f"{world_seed}{encounter_id}subtype"
    selected_subtype = deterministic_weighted_choice(items, weights, seed_string)

    selection_log = {
        "candidate_weights": candidate_logs,
        "enforcement_strength": enforcement_strength,
        "travel_context_mode": travel_context_mode,
        "eligible_subtype_ids_ascii": [row[0] for row in weighted_candidates],
        "eligible_weights": weights,
        "seed_string": seed_string,
        "selected_subtype_id": None if selected_subtype is None else selected_subtype["subtype_id"],
    }

    if selected_subtype is None:
        raise ValueError("No eligible encounter subtype after deterministic weighting.")
    return selected_subtype, selection_log


def assign_tr(encounter_id, world_seed, allowed_TR_range):
    min_tr = allowed_TR_range["min"]
    max_tr = allowed_TR_range["max"]
    seed_string = f"{world_seed}{encounter_id}tr"
    roll = deterministic_float(seed_string)

    span = max_tr - min_tr + 1
    tr_value = min_tr + int(roll * span)
    if tr_value < min_tr:
        tr_value = min_tr
    if tr_value > max_tr:
        tr_value = max_tr

    log = {
        "min_tr": min_tr,
        "max_tr": max_tr,
        "roll": roll,
        "seed_string": seed_string,
        "tr_value": tr_value,
    }
    return tr_value, log


def select_reward_profile(
    encounter_id,
    world_seed,
    reward_profiles,
):
    if not reward_profiles:
        return None, {
            "reward_candidates": [],
            "weights": [],
            "seed_string": None,
            "selected_reward_profile_id": None,
        }

    ordered_profiles = sorted(reward_profiles, key=lambda entry: entry["reward_profile_id"])
    items = ordered_profiles
    weights = [entry["weight"] for entry in ordered_profiles]
    seed_string = f"{world_seed}{encounter_id}reward"
    selected = deterministic_weighted_choice(items, weights, seed_string)
    reward_profile_id = None if selected is None else selected["reward_profile_id"]

    log = {
        "reward_candidates": [entry["reward_profile_id"] for entry in ordered_profiles],
        "weights": weights,
        "seed_string": seed_string,
        "selected_reward_profile_id": reward_profile_id,
    }
    return reward_profile_id, log


def generate_encounter(
    encounter_id,
    world_seed,
    system_government_id,
    active_situations,
    travel_context=None,
):
    selection_log = {}

    subtype, subtype_log = select_subtype(
        encounter_id,
        world_seed,
        system_government_id,
        active_situations,
        travel_context,
    )
    selection_log["subtype_selection"] = subtype_log

    tr_value, tr_log = assign_tr(
        encounter_id,
        world_seed,
        subtype["allowed_TR_range"],
    )
    selection_log["tr_assignment"] = tr_log

    reward_profile_id, reward_log = select_reward_profile(
        encounter_id,
        world_seed,
        subtype["reward_profiles"],
    )
    selection_log["reward_selection"] = reward_log
    selection_log["finalization"] = {
        "subtype_id": subtype["subtype_id"],
        "posture": subtype["posture"],
        "initiative": subtype["initiative"],
        "default_flags": list(subtype["default_flags"]),
    }

    spec = EncounterSpec(
        encounter_id=encounter_id,
        subtype_id=subtype["subtype_id"],
        emoji=subtype["emoji"],
        posture=subtype["posture"],
        initiative=subtype["initiative"],
        allows_betrayal=subtype["allows_betrayal"],
        threat_rating_tr=tr_value,
        participant_templates=subtype["participant_templates"],
        default_flags=subtype["default_flags"],
        reward_profile_id=reward_profile_id,
        npc_response_profile=subtype["npc_response_profile"],
        selection_log=selection_log,
    )
    return spec


def generate_travel_encounters(
    world_seed,
    travel_id,
    population,
    system_government_id,
    active_situations,
    travel_context=None,
):
    if population < 0:
        raise ValueError("population must be >= 0 for travel encounter generation.")

    cap = population * 2
    if cap == 0:
        return []

    base_chance = 0.8
    encounters = []
    i = 0
    while i < cap:
        effective_chance = base_chance * (1 - (i / (cap + 1)))
        seed_string = f"{world_seed}{travel_id}enc_roll_{i}"
        roll = deterministic_float(seed_string)

        if roll < effective_chance:
            encounter_id = f"{travel_id}_enc_{i}"
            spec = generate_encounter(
                encounter_id=encounter_id,
                world_seed=world_seed,
                system_government_id=system_government_id,
                active_situations=active_situations,
                travel_context=travel_context,
            )
            spec.selection_log["travel_roll"] = {
                "travel_id": travel_id,
                "population": population,
                "cap": cap,
                "encounter_index": i,
                "effective_chance": effective_chance,
                "roll": roll,
            }
            encounters.append(spec)
        i += 1
    return encounters


def _smoke_test_enforcement_scaling():
    encounter_id = "ENC-SMOKE-AUTH-001"
    world_seed = "WORLD-SMOKE"
    government_id = "dictatorship"
    active_situations = []

    in_system_spec = generate_encounter(
        encounter_id=encounter_id,
        world_seed=world_seed,
        system_government_id=government_id,
        active_situations=active_situations,
        travel_context=None,
    )
    arrival_spec = generate_encounter(
        encounter_id=encounter_id,
        world_seed=world_seed,
        system_government_id=government_id,
        active_situations=active_situations,
        travel_context={"mode": "system_arrival"},
    )

    # Determinism for repeated calls with identical inputs.
    in_system_spec_repeat = generate_encounter(
        encounter_id=encounter_id,
        world_seed=world_seed,
        system_government_id=government_id,
        active_situations=active_situations,
        travel_context=None,
    )
    arrival_spec_repeat = generate_encounter(
        encounter_id=encounter_id,
        world_seed=world_seed,
        system_government_id=government_id,
        active_situations=active_situations,
        travel_context={"mode": "system_arrival"},
    )
    if in_system_spec.subtype_id != in_system_spec_repeat.subtype_id:
        raise ValueError("Smoke test failed: non-deterministic subtype selection for in_system context.")
    if arrival_spec.subtype_id != arrival_spec_repeat.subtype_id:
        raise ValueError("Smoke test failed: non-deterministic subtype selection for system_arrival context.")

    in_system_candidates = in_system_spec.selection_log["subtype_selection"]["candidate_weights"]
    arrival_candidates = arrival_spec.selection_log["subtype_selection"]["candidate_weights"]
    in_system_by_id = {entry["subtype_id"]: entry for entry in in_system_candidates}
    arrival_by_id = {entry["subtype_id"]: entry for entry in arrival_candidates}

    for subtype_id, in_system_entry in in_system_by_id.items():
        if in_system_entry.get("authority_enforcement_applied"):
            arrival_entry = arrival_by_id[subtype_id]
            if not arrival_entry.get("arrival_enforcement_applied"):
                raise ValueError("Smoke test failed: expected arrival enforcement flag on authority subtype.")
            if arrival_entry["final_weight"] <= in_system_entry["final_weight"]:
                raise ValueError("Smoke test failed: arrival did not increase authority subtype final_weight.")

    return in_system_spec, arrival_spec


def _smoke_test_travel_loop():
    common_args = {
        "world_seed": "WORLD-TRAVEL-SMOKE",
        "travel_id": "TRAVEL-SMOKE-001",
        "population": 5,
        "system_government_id": "dictatorship",
        "active_situations": [],
    }
    first = generate_travel_encounters(
        travel_context=None,
        **common_args,
    )
    second = generate_travel_encounters(
        travel_context=None,
        **common_args,
    )
    if len(first) != len(second):
        raise ValueError("Smoke test failed: travel encounter count is not deterministic.")

    first_subtypes = [spec.subtype_id for spec in first]
    second_subtypes = [spec.subtype_id for spec in second]
    if first_subtypes != second_subtypes:
        raise ValueError("Smoke test failed: travel subtype sequence is not deterministic.")

    empty_result = generate_travel_encounters(
        world_seed="WORLD-TRAVEL-SMOKE",
        travel_id="TRAVEL-SMOKE-EMPTY",
        population=0,
        system_government_id="dictatorship",
        active_situations=[],
        travel_context=None,
    )
    if empty_result != []:
        raise ValueError("Smoke test failed: population=0 must return empty encounter list.")

    arrival = generate_travel_encounters(
        travel_context={"mode": "system_arrival"},
        **common_args,
    )
    authority_count_in_system = sum(1 for spec in first if spec.posture == "authority")
    authority_count_arrival = sum(1 for spec in arrival if spec.posture == "authority")
    if authority_count_arrival < authority_count_in_system:
        raise ValueError("Smoke test failed: system_arrival should not reduce authority encounter frequency.")

    return first, arrival
