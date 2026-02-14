from __future__ import annotations

import argparse
from collections import Counter

from combat_resolver import ModuleDef, ShipLoadout, make_action_plan_selector, resolve_combat


def _build_loadouts() -> dict[str, ShipLoadout]:
    return {
        "t1_mil_raider": ShipLoadout(
            name="T1 MIL Raider",
            tier=1,
            frame="MIL",
            weapon_slots=2,
            defense_slots=1,
            utility_slots=1,
            untyped_slots=0,
            modules=[
                ModuleDef("w1", "weapon", {"combat:weapon_kinetic"}),
                ModuleDef("w2", "weapon", {"combat:weapon_energy"}, secondary="secondary:unstable"),
                ModuleDef("d1", "defense", {"combat:defense_shielded"}),
                ModuleDef("u1", "utility", {"combat:utility_targeting"}),
            ],
            crew=["crew:gunner", "crew:pilot"],
            seed_salt="t1_mil_raider",
        ),
        "t1_civ_escape": ShipLoadout(
            name="T1 CIV Escape",
            tier=1,
            frame="CIV",
            weapon_slots=1,
            defense_slots=2,
            utility_slots=1,
            untyped_slots=0,
            modules=[
                ModuleDef("w1", "weapon", {"combat:weapon_energy"}),
                ModuleDef("d1", "defense", {"combat:defense_armored"}),
                ModuleDef("d2", "defense", {"combat:defense_shielded"}),
                ModuleDef("u1", "utility", {"combat:utility_cloak"}),
            ],
            crew=["crew:pilot", "crew:pilot", "crew:engineer"],
            seed_salt="t1_civ_escape",
        ),
        "t3_xa_support": ShipLoadout(
            name="T3 XA Support",
            tier=3,
            frame="XA",
            weapon_slots=2,
            defense_slots=1,
            utility_slots=4,
            untyped_slots=0,
            modules=[
                ModuleDef("w1", "weapon", {"combat:weapon_disruptive"}),
                ModuleDef("w2", "weapon", {"combat:weapon_kinetic"}),
                ModuleDef("d1", "defense", {"combat:defense_adaptive"}),
                ModuleDef("u1", "utility", {"combat:utility_repair_system"}, secondary="secondary:efficient"),
                ModuleDef("u2", "utility", {"combat:utility_signal_scrambler"}),
                ModuleDef("u3", "utility", {"ship:utility_probe_array"}),
                ModuleDef("u4", "utility", {"combat:utility_engine_boost"}),
            ],
            crew=["crew:mechanic", "crew:engineer", "crew:pilot"],
            seed_salt="t3_xa_support",
        ),
        "t3_frg_tank": ShipLoadout(
            name="T3 FRG Tank",
            tier=3,
            frame="FRG",
            weapon_slots=1,
            defense_slots=2,
            utility_slots=3,
            untyped_slots=0,
            modules=[
                ModuleDef("w1", "weapon", {"combat:weapon_energy"}),
                ModuleDef("d1", "defense", {"combat:defense_armored"}, secondary="secondary:enhanced"),
                ModuleDef("d2", "defense", {"combat:defense_shielded"}),
                ModuleDef("u1", "utility", {"combat:utility_repair_system"}),
                ModuleDef("u2", "utility", {"ship:utility_interdiction"}),
                ModuleDef("u3", "utility", {"combat:utility_overcharger"}),
            ],
            crew=["crew:engineer", "crew:mechanic"],
            seed_salt="t3_frg_tank",
        ),
        "t5_xb_striker": ShipLoadout(
            name="T5 XB Striker",
            tier=5,
            frame="XB",
            weapon_slots=5,
            defense_slots=2,
            utility_slots=2,
            untyped_slots=0,
            modules=[
                ModuleDef("w1", "weapon", {"combat:weapon_kinetic"}),
                ModuleDef("w2", "weapon", {"combat:weapon_kinetic"}),
                ModuleDef("w3", "weapon", {"combat:weapon_energy"}, secondary="secondary:prototype"),
                ModuleDef("w4", "weapon", {"combat:weapon_disruptive"}),
                ModuleDef("w5", "weapon", {"combat:weapon_kinetic"}),
                ModuleDef("d1", "defense", {"combat:defense_armored"}),
                ModuleDef("d2", "defense", {"combat:defense_adaptive"}),
                ModuleDef("u1", "utility", {"combat:utility_targeting"}),
                ModuleDef("u2", "utility", {"combat:utility_engine_boost"}),
            ],
            crew=["crew:gunner", "crew:gunner", "crew:pilot"],
            seed_salt="t5_xb_striker",
        ),
        "t5_aln_hybrid": ShipLoadout(
            name="T5 ALN Hybrid",
            tier=5,
            frame="ALN",
            weapon_slots=2,
            defense_slots=1,
            utility_slots=2,
            untyped_slots=3,
            modules=[
                ModuleDef("w1", "weapon", {"combat:weapon_disruptive"}, secondary={"secondary:alien", "secondary:efficient"}),
                ModuleDef("w2", "weapon", {"combat:weapon_energy"}),
                ModuleDef("d1", "defense", {"combat:defense_adaptive"}),
                ModuleDef("u1", "utility", {"combat:utility_repair_system"}, secondary={"secondary:alien", "secondary:efficient"}),
                ModuleDef("u2", "utility", {"ship:utility_probe_array"}),
                ModuleDef("xw", "weapon", {"combat:weapon_kinetic"}),
                ModuleDef("xd", "defense", {"combat:defense_armored"}),
                ModuleDef("xu", "utility", {"combat:utility_cloak"}),
            ],
            crew=["crew:pilot", "crew:mechanic", "crew:gunner"],
            seed_salt="t5_aln_hybrid",
        ),
    }


def _scenarios(loadouts: dict[str, ShipLoadout]) -> dict[str, dict]:
    return {
        "duel_t1": {
            "player": loadouts["t1_mil_raider"],
            "enemy": loadouts["t1_civ_escape"],
            "player_selector": make_action_plan_selector(["Focus Fire", "Focus Fire", "Attempt Escape", "Focus Fire"]),
            "enemy_selector": make_action_plan_selector(["Reinforce Shields", "Evasive Maneuvers", "Attempt Escape", "Focus Fire"]),
        },
        "mid_tier_mix": {
            "player": loadouts["t3_xa_support"],
            "enemy": loadouts["t3_frg_tank"],
            "player_selector": make_action_plan_selector(
                ["Scan", "Focus Fire", "Repair Systems", "Reinforce Shields", "Focus Fire"]
            ),
            "enemy_selector": make_action_plan_selector(
                ["Focus Fire", "Reinforce Shields", "Focus Fire", "Attempt Escape", "Focus Fire"]
            ),
        },
        "endgame": {
            "player": loadouts["t5_xb_striker"],
            "enemy": loadouts["t5_aln_hybrid"],
            "player_selector": make_action_plan_selector(
                ["Focus Fire", "Focus Fire", "Evasive Maneuvers", "Focus Fire", "Focus Fire"]
            ),
            "enemy_selector": make_action_plan_selector(
                ["Scan", "Repair Systems", "Attempt Escape", "Focus Fire", "Focus Fire"]
            ),
        },
    }


def run_simulation(seed: int, scenario_id: str, combats: int, verbose: bool) -> None:
    loadouts = _build_loadouts()
    scenarios = _scenarios(loadouts)
    if scenario_id not in scenarios:
        valid = ", ".join(sorted(scenarios.keys()))
        raise ValueError(f"Unknown scenario '{scenario_id}'. Valid scenario ids: {valid}")

    scenario = scenarios[scenario_id]
    print(f"seed={seed} scenario={scenario_id} combats={combats}")
    print(f"player={scenario['player'].name} enemy={scenario['enemy'].name}")

    outcome_counts: Counter[str] = Counter()
    rounds_total = 0
    sample_result = None

    for index in range(combats):
        result = resolve_combat(
            world_seed=seed,
            combat_id=f"{scenario_id}_{index}",
            player_loadout=scenario["player"],
            enemy_loadout=scenario["enemy"],
            player_action_selector=scenario["player_selector"],
            enemy_action_selector=scenario["enemy_selector"],
            max_rounds=20,
        )
        if sample_result is None:
            sample_result = result
        rounds_total += result.rounds
        outcome_counts[result.outcome] += 1

    print(
        "player_rcp_tr={}/{} enemy_rcp_tr={}/{}".format(
            sample_result.rcp_player,
            sample_result.tr_player,
            sample_result.rcp_enemy,
            sample_result.tr_enemy,
        )
    )
    print("outcomes=" + ",".join(f"{key}:{outcome_counts[key]}" for key in sorted(outcome_counts.keys())))
    print(f"avg_rounds={rounds_total / combats:.2f}")

    if verbose and sample_result is not None:
        print("sample_log_begin")
        for entry in sample_result.log:
            player_hull = entry.get("hull", {}).get("player", {}).get("current")
            enemy_hull = entry.get("hull", {}).get("enemy", {}).get("current")
            print(
                "r={r} aP={ap} aE={ae} dPtoE={dp} dEtoP={de} hP={hp} hE={he}".format(
                    r=entry["round"],
                    ap=entry["actions"].get("player"),
                    ae=entry["actions"].get("enemy"),
                    dp=entry.get("attacks", {}).get("player_to_enemy", {}).get("damage"),
                    de=entry.get("attacks", {}).get("enemy_to_player", {}).get("damage"),
                    hp=player_hull,
                    he=enemy_hull,
                )
            )
        print("sample_log_end")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic combat simulation harness.")
    parser.add_argument("--seed", type=int, required=True, help="World seed used for deterministic combat runs.")
    parser.add_argument("--scenario", type=str, default="duel_t1", help="Scenario id to run.")
    parser.add_argument("--combats", type=int, default=10, help="Number of combats to run.")
    parser.add_argument("--verbose", action="store_true", help="Print sample round-by-round logs.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    run_simulation(seed=args.seed, scenario_id=args.scenario, combats=args.combats, verbose=args.verbose)


if __name__ == "__main__":
    print("Deprecated harness entry point. Use src/cli_run.py.")
