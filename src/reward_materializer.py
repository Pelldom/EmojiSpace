from pathlib import Path
import json

try:
    from encounter_generator import deterministic_float, deterministic_weighted_choice
except ModuleNotFoundError:
    from src.encounter_generator import deterministic_float, deterministic_weighted_choice


REWARD_KINDS = {"cargo", "credits", "mixed", "none"}
QUANTITY_BANDS = {"very_low", "low", "medium", "high", "very_high"}
STOLEN_BEHAVIORS = {"always", "none", "probabilistic"}


class RewardResult:
    def __init__(
        self,
        encounter_id,
        reward_profile_id,
        reward_kind,
        sku_id,
        quantity,
        credits,
        stolen_applied,
        log,
    ):
        self.encounter_id = encounter_id
        self.reward_profile_id = reward_profile_id
        self.reward_kind = reward_kind
        self.sku_id = sku_id
        self.quantity = quantity
        self.credits = credits
        self.stolen_applied = stolen_applied
        self.log = log


def _load_reward_profiles_file():
    path = Path(__file__).resolve().parents[1] / "data" / "reward_profiles.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError("reward_profiles.json not found at data/reward_profiles.json.") from error
    except json.JSONDecodeError as error:
        raise ValueError("reward_profiles.json is not valid JSON.") from error


def _load_goods_file():
    path = Path(__file__).resolve().parents[1] / "data" / "goods.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError("goods.json not found at data/goods.json.") from error
    except json.JSONDecodeError as error:
        raise ValueError("goods.json is not valid JSON.") from error


def _load_valid_sku_ids():
    payload = _load_goods_file()
    goods = payload.get("goods")
    if not isinstance(goods, list):
        raise ValueError("goods.json missing or invalid goods list.")
    sku_ids = set()
    for index, good in enumerate(goods):
        if not isinstance(good, dict):
            raise ValueError(f"goods entry {index} is invalid: expected object.")
        sku_id = good.get("sku")
        if not isinstance(sku_id, str) or not sku_id:
            raise ValueError(f"goods entry {index} has invalid sku.")
        sku_ids.add(sku_id)
    return sku_ids


def load_reward_profiles():
    payload = _load_reward_profiles_file()
    if "version" not in payload:
        raise ValueError("reward_profiles.json missing required top-level field: version.")
    profiles = payload.get("reward_profiles")
    if not isinstance(profiles, list):
        raise ValueError("reward_profiles.json missing or invalid reward_profiles list.")

    by_id = {}
    for index, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            raise ValueError(f"reward_profiles entry {index} is invalid: expected object.")
        reward_profile_id = profile.get("reward_profile_id")
        if not isinstance(reward_profile_id, str) or not reward_profile_id:
            raise ValueError(f"reward_profiles entry {index} has invalid reward_profile_id.")
        if reward_profile_id in by_id:
            raise ValueError(f"Duplicate reward_profile_id in reward_profiles.json: {reward_profile_id}.")

        reward_kind = profile.get("reward_kind")
        if reward_kind not in REWARD_KINDS:
            raise ValueError(f"Reward profile {reward_profile_id} has invalid reward_kind.")
        quantity_band = profile.get("quantity_band")
        if quantity_band not in QUANTITY_BANDS:
            raise ValueError(f"Reward profile {reward_profile_id} has invalid quantity_band.")
        stolen_behavior = profile.get("stolen_behavior")
        if stolen_behavior not in STOLEN_BEHAVIORS:
            raise ValueError(f"Reward profile {reward_profile_id} has invalid stolen_behavior.")

        if reward_kind in {"credits", "mixed"}:
            credit_range = profile.get("credit_range")
            if not isinstance(credit_range, dict):
                raise ValueError(f"Reward profile {reward_profile_id} missing credit_range.")
            min_credits = credit_range.get("min")
            max_credits = credit_range.get("max")
            if not isinstance(min_credits, int) or not isinstance(max_credits, int):
                raise ValueError(f"Reward profile {reward_profile_id} has invalid credit_range bounds.")
            if min_credits > max_credits:
                raise ValueError(f"Reward profile {reward_profile_id} has reversed credit_range bounds.")

        if stolen_behavior == "probabilistic":
            probability = profile.get("stolen_probability")
            if not isinstance(probability, (int, float)):
                raise ValueError(f"Reward profile {reward_profile_id} missing stolen_probability.")
            if probability < 0.0 or probability > 1.0:
                raise ValueError(f"Reward profile {reward_profile_id} has invalid stolen_probability.")

        by_id[reward_profile_id] = profile
    return by_id


def _extract_category_skus(category_obj):
    if not isinstance(category_obj, dict):
        return []
    sku_ids = []
    for key in ("produced", "consumed", "neutral"):
        values = category_obj.get(key, [])
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str):
                    sku_ids.append(value)
    return sku_ids


def aggregate_system_skus(system_markets):
    if not system_markets:
        return []

    valid_skus = _load_valid_sku_ids()
    unique_skus = set()
    for market in system_markets:
        if not isinstance(market, dict):
            continue
        categories = market.get("categories")
        if isinstance(categories, list):
            for category_obj in categories:
                for sku_id in _extract_category_skus(category_obj):
                    if sku_id in valid_skus:
                        unique_skus.add(sku_id)
        elif isinstance(categories, dict):
            for category_obj in categories.values():
                for sku_id in _extract_category_skus(category_obj):
                    if sku_id in valid_skus:
                        unique_skus.add(sku_id)
        else:
            # Allow market object itself to directly expose category payloads.
            for category_obj in market.values():
                if isinstance(category_obj, dict):
                    for sku_id in _extract_category_skus(category_obj):
                        if sku_id in valid_skus:
                            unique_skus.add(sku_id)
    return sorted(unique_skus, key=lambda sku_id: sku_id)


def resolve_quantity_band(band, seed_string):
    if band == "very_low":
        return 1
    if band == "low":
        min_value, max_value = 1, 2
    elif band == "medium":
        min_value, max_value = 2, 3
    elif band == "high":
        min_value, max_value = 3, 4
    elif band == "very_high":
        min_value, max_value = 4, 5
    else:
        raise ValueError(f"Unknown quantity band: {band}")

    roll = deterministic_float(seed_string)
    span = max_value - min_value + 1
    value = min_value + int(roll * span)
    if value < min_value:
        value = min_value
    if value > max_value:
        value = max_value
    return value


def _resolve_stolen_applied(profile, seed_string):
    stolen_behavior = profile["stolen_behavior"]
    if stolen_behavior == "always":
        return True, None
    if stolen_behavior == "none":
        return False, None
    stolen_roll = deterministic_float(f"{seed_string}_stolen")
    probability = float(profile.get("stolen_probability", 0.0))
    return stolen_roll < probability, stolen_roll


def _resolve_credits(profile, seed_string):
    credit_range = profile["credit_range"]
    min_credits = credit_range["min"]
    max_credits = credit_range["max"]
    credit_roll = deterministic_float(f"{seed_string}_credits")
    span = max_credits - min_credits + 1
    credits = min_credits + int(credit_roll * span)
    if credits < min_credits:
        credits = min_credits
    if credits > max_credits:
        credits = max_credits
    return credits, credit_roll


def materialize_reward(
    spec,
    system_markets,
    world_seed,
):
    if spec.reward_profile_id is None:
        return None

    profiles = load_reward_profiles()
    if spec.reward_profile_id not in profiles:
        raise ValueError(f"Unknown reward_profile_id: {spec.reward_profile_id}")
    profile = profiles[spec.reward_profile_id]
    reward_kind = profile["reward_kind"]
    seed_string = f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}"

    sku_id = None
    quantity = None
    credits = None
    stolen_applied = False
    stolen_roll = None
    credit_roll = None
    base_quantity = None

    if reward_kind == "none":
        credits = 0
        quantity = 0
        return RewardResult(
            encounter_id=spec.encounter_id,
            reward_profile_id=spec.reward_profile_id,
            reward_kind=reward_kind,
            sku_id=None,
            quantity=0,
            credits=0,
            stolen_applied=False,
            log={
                "sku_pool_size": 0,
                "selected_sku": None,
                "base_quantity": 0,
                "tr_multiplier": spec.threat_rating_tr,
                "final_quantity": 0,
                "stolen_roll": None,
                "credit_roll": None,
            },
        )

    needs_cargo = reward_kind in {"cargo", "mixed"}
    needs_credits = reward_kind in {"credits", "mixed"}

    sku_pool = aggregate_system_skus(system_markets) if needs_cargo else []
    if needs_cargo and not sku_pool:
        return RewardResult(
            encounter_id=spec.encounter_id,
            reward_profile_id=spec.reward_profile_id,
            reward_kind=reward_kind,
            sku_id=None,
            quantity=0,
            credits=0,
            stolen_applied=False,
            log={
                "sku_pool_size": 0,
                "selected_sku": None,
                "base_quantity": 0,
                "tr_multiplier": spec.threat_rating_tr,
                "final_quantity": 0,
                "stolen_roll": None,
                "credit_roll": None,
            },
        )

    if needs_cargo:
        sku_seed = f"{world_seed}{spec.encounter_id}_sku"
        sku_weights = [1 for _ in sku_pool]
        sku_id = deterministic_weighted_choice(sku_pool, sku_weights, sku_seed)

        quantity_seed = f"{world_seed}{spec.encounter_id}_qty"
        base_quantity = resolve_quantity_band(profile["quantity_band"], quantity_seed)
        quantity = base_quantity * spec.threat_rating_tr
        stolen_applied, stolen_roll = _resolve_stolen_applied(profile, seed_string)

    if needs_credits:
        credits, credit_roll = _resolve_credits(profile, seed_string)

    return RewardResult(
        encounter_id=spec.encounter_id,
        reward_profile_id=spec.reward_profile_id,
        reward_kind=reward_kind,
        sku_id=sku_id,
        quantity=quantity,
        credits=credits,
        stolen_applied=stolen_applied,
        log={
            "sku_pool_size": len(sku_pool),
            "selected_sku": sku_id,
            "base_quantity": base_quantity,
            "tr_multiplier": spec.threat_rating_tr,
            "final_quantity": quantity,
            "stolen_roll": stolen_roll,
            "credit_roll": credit_roll,
        },
    )


def _smoke_test_reward_materializer():
    class _FakeSpec:
        def __init__(self):
            self.encounter_id = "ENC-REWARD-SMOKE-001"
            self.reward_profile_id = "raider_loot"
            self.threat_rating_tr = 3

    fake_spec = _FakeSpec()
    synthetic_markets = [
        {
            "categories": {
                "ORE": {
                    "produced": ["iron_ore"],
                    "consumed": ["copper_ore"],
                    "neutral": ["nickel_ore"],
                },
                "FOOD": {
                    "produced": ["basic_rations"],
                    "consumed": [],
                    "neutral": [],
                },
            }
        }
    ]

    first = materialize_reward(fake_spec, synthetic_markets, "WORLD-REWARD-SMOKE")
    second = materialize_reward(fake_spec, synthetic_markets, "WORLD-REWARD-SMOKE")

    if first is None or second is None:
        raise ValueError("Smoke test failed: expected RewardResult.")
    if first.sku_id != second.sku_id:
        raise ValueError("Smoke test failed: non-deterministic SKU selection.")
    if first.quantity != second.quantity:
        raise ValueError("Smoke test failed: non-deterministic quantity selection.")
    if first.stolen_applied != second.stolen_applied:
        raise ValueError("Smoke test failed: non-deterministic stolen behavior.")

    expected_base = first.log["base_quantity"]
    if first.quantity != expected_base * fake_spec.threat_rating_tr:
        raise ValueError("Smoke test failed: TR multiplier was not applied to quantity.")

    return first, second
