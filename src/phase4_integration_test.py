from pathlib import Path
import json

try:
    from encounter_generator import generate_travel_encounters, load_governments
    from interaction_layer import dispatch_player_action
    from pursuit_resolver import resolve_pursuit
    from reaction_engine import get_npc_outcome
    from reward_materializer import materialize_reward
except ModuleNotFoundError:
    from src.encounter_generator import generate_travel_encounters, load_governments
    from src.interaction_layer import dispatch_player_action
    from src.pursuit_resolver import resolve_pursuit
    from src.reaction_engine import get_npc_outcome
    from src.reward_materializer import materialize_reward


def _load_first_three_skus():
    goods_path = Path(__file__).resolve().parents[1] / "data" / "goods.json"
    payload = json.loads(goods_path.read_text(encoding="utf-8"))
    goods = payload.get("goods", [])
    sku_ids = [entry.get("sku") for entry in goods if isinstance(entry, dict) and isinstance(entry.get("sku"), str)]
    assert len(sku_ids) >= 3
    return sku_ids[:3]


def run_phase4_integration_test():
    print("=== PHASE 4 INTEGRATION TEST ===")

    world_seed = "TEST_SEED"
    travel_id = "TRAVEL_001"
    population = 3
    active_situations = []

    governments = load_governments()
    system_government_id = sorted(governments.keys(), key=lambda government_id: government_id)[0]
    print(json.dumps({"step": "setup", "system_government_id": system_government_id}, sort_keys=True))

    sku_a, sku_b, sku_c = _load_first_three_skus()
    system_markets = [
        {
            "categories": {
                "TEST_CATEGORY": {
                    "produced": [sku_a, sku_b],
                    "consumed": [sku_c],
                    "neutral": [],
                }
            }
        }
    ]

    encounters_first = generate_travel_encounters(
        world_seed=world_seed,
        travel_id=travel_id,
        population=population,
        system_government_id=system_government_id,
        active_situations=active_situations,
        travel_context=None,
    )
    encounters_second = generate_travel_encounters(
        world_seed=world_seed,
        travel_id=travel_id,
        population=population,
        system_government_id=system_government_id,
        active_situations=active_situations,
        travel_context=None,
    )

    first_subtypes = [spec.subtype_id for spec in encounters_first]
    second_subtypes = [spec.subtype_id for spec in encounters_second]
    first_tr_values = [spec.threat_rating_tr for spec in encounters_first]
    second_tr_values = [spec.threat_rating_tr for spec in encounters_second]

    print(
        json.dumps(
            {
                "step": "travel_determinism",
                "encounter_count": len(encounters_first),
                "subtypes": first_subtypes,
                "tr_values": first_tr_values,
            },
            sort_keys=True,
        )
    )
    assert len(encounters_first) == len(encounters_second)
    assert first_subtypes == second_subtypes
    assert first_tr_values == second_tr_values

    if encounters_first:
        spec = encounters_first[0]

        outcome_1, outcome_log_1 = get_npc_outcome(
            spec=spec,
            player_action="ignore",
            world_seed=world_seed,
            ignore_count=0,
            reputation_score=50,
            notoriety_score=50,
            law_score=30,
            outlaw_score=30,
        )
        outcome_2, outcome_log_2 = get_npc_outcome(
            spec=spec,
            player_action="ignore",
            world_seed=world_seed,
            ignore_count=0,
            reputation_score=50,
            notoriety_score=50,
            law_score=30,
            outlaw_score=30,
        )
        print(
            json.dumps(
                {
                    "step": "reaction_determinism",
                    "reaction_outcome": outcome_1,
                },
                sort_keys=True,
            )
        )
        assert outcome_1 == outcome_2
        assert outcome_log_1 == outcome_log_2

        dispatch_1 = dispatch_player_action(
            spec=spec,
            player_action="ignore",
            world_seed=world_seed,
            ignore_count=0,
            reputation_band=50,
            notoriety_band=50,
        )
        dispatch_2 = dispatch_player_action(
            spec=spec,
            player_action="ignore",
            world_seed=world_seed,
            ignore_count=0,
            reputation_band=50,
            notoriety_band=50,
        )
        print(
            json.dumps(
                {
                    "step": "interaction_dispatch",
                    "next_handler": dispatch_1.next_handler,
                },
                sort_keys=True,
            )
        )
        assert dispatch_1.next_handler == dispatch_2.next_handler
        assert dispatch_1.handler_payload == dispatch_2.handler_payload
        assert dispatch_1.log == dispatch_2.log

        if spec.reward_profile_id is not None:
            reward_1 = materialize_reward(
                spec=spec,
                system_markets=system_markets,
                world_seed=world_seed,
            )
            reward_2 = materialize_reward(
                spec=spec,
                system_markets=system_markets,
                world_seed=world_seed,
            )
            assert reward_1 is not None
            assert reward_2 is not None
            print(
                json.dumps(
                    {
                        "step": "reward_materialization",
                        "sku_id": reward_1.sku_id,
                        "quantity": reward_1.quantity,
                        "credits": reward_1.credits,
                        "stolen_applied": reward_1.stolen_applied,
                    },
                    sort_keys=True,
                )
            )
            assert reward_1.sku_id == reward_2.sku_id
            assert reward_1.quantity == reward_2.quantity
            assert reward_1.credits == reward_2.credits
            assert reward_1.stolen_applied == reward_2.stolen_applied
            assert reward_1.log == reward_2.log
        else:
            print(json.dumps({"step": "reward_materialization", "message": "No reward profile for first encounter"}))
    else:
        print(json.dumps({"step": "reaction_determinism", "message": "No encounters generated"}))
        print(json.dumps({"step": "interaction_dispatch", "message": "No encounters generated"}))
        print(json.dumps({"step": "reward_materialization", "message": "No encounters generated"}))

    pursuer_ship = {"speed": 4, "pilot_skill": 3}
    pursued_ship = {"speed": 6, "pilot_skill": 4}
    pursuit_1 = resolve_pursuit(
        encounter_id="PURSUIT_TEST_001",
        world_seed=world_seed,
        pursuer_ship=pursuer_ship,
        pursued_ship=pursued_ship,
    )
    pursuit_2 = resolve_pursuit(
        encounter_id="PURSUIT_TEST_001",
        world_seed=world_seed,
        pursuer_ship=pursuer_ship,
        pursued_ship=pursued_ship,
    )
    print(
        json.dumps(
            {
                "step": "pursuit_resolver",
                "threshold": pursuit_1.threshold,
                "roll": pursuit_1.roll,
                "escaped": pursuit_1.escaped,
            },
            sort_keys=True,
        )
    )
    assert pursuit_1.threshold == pursuit_2.threshold
    assert pursuit_1.roll == pursuit_2.roll
    assert pursuit_1.escaped == pursuit_2.escaped
    assert pursuit_1.log == pursuit_2.log

    arrival_encounters = generate_travel_encounters(
        world_seed=world_seed,
        travel_id=travel_id,
        population=population,
        system_government_id=system_government_id,
        active_situations=active_situations,
        travel_context={"mode": "system_arrival"},
    )
    authority_in_system = sum(1 for spec in encounters_first if spec.posture == "authority")
    authority_arrival = sum(1 for spec in arrival_encounters if spec.posture == "authority")
    print(
        json.dumps(
            {
                "step": "arrival_context",
                "authority_count_in_system": authority_in_system,
                "authority_count_arrival": authority_arrival,
            },
            sort_keys=True,
        )
    )
    assert authority_arrival >= authority_in_system

    print("PHASE 4 INTEGRATION TEST PASSED")


if __name__ == "__main__":
    run_phase4_integration_test()
