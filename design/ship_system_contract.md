# Ship System Contract
Version: 0.4.0
Status: Phase 4 Foundation

This document defines ship structure, slot distributions, combat resolution, damage and degradation, repair, destruction, insurance, and surrender behavior.
All implementation must follow this contract.


## 1. Scope

This contract defines:
- Ship frames and tier progression
- Slot types and exact slot distributions per tier and frame
- Core combat bands and how they are modified during combat
- Combat loop and resolution rules (simultaneous)
- Persistent subsystem degradation and repair rules
- Destruction, insurance, and surrender outcomes

This contract does not define numeric scaling tables for:
- Base band values by tier and frame
- Module band contributions
- Focus magnitude and crew bonuses
- Cargo capacities by tier and frame
- Repair costs and insurance costs
These numeric tables must be specified in a separate Appendix before implementation.


## 2. Definitions

Slot types:
- W: Weapon slot
- D: Defense slot
- U: Utility slot
- X: Untyped slot (accepts any module type)

Frames:
- MIL: Military
- CIV: Civilian
- FRG: Freighter
- XA: Experimental A (utility focused)
- XB: Experimental B (weapon focused)
- XC: Experimental C (defense focused)
- ALN: Alien

Tiers:
- Tier I through Tier V
- Standard total slots: Tier I=4, Tier II=5, Tier III=6, Tier IV=7, Tier V=8


## 3. Slot System

There are exactly three typed slot categories: Weapon, Defense, Utility.
Alien frames additionally have Untyped slots.

Untyped slots:
- Accept any module type
- Count toward total slot count
- Are part of the slot distribution matrix below

Alien untyped progression:
- ALN has 1 Untyped slot at Tier I
- ALN gains an additional Untyped slot at Tier III
- ALN gains an additional Untyped slot at Tier V


## 4. Slot Distribution Matrix (Authoritative)

All rows are exact and must not be inferred.

| Tier | Frame | W | D | U | X | Total |
|------|-------|---|---|---|---|-------|
| I    | MIL   | 2 | 1 | 1 | 0 | 4     |
| I    | CIV   | 1 | 2 | 1 | 0 | 4     |
| I    | FRG   | 1 | 1 | 2 | 0 | 4     |
| I    | XA    | 1 | 1 | 3 | 0 | 5     |
| I    | XB    | 3 | 1 | 1 | 0 | 5     |
| I    | XC    | 1 | 3 | 1 | 0 | 5     |
| I    | ALN   | 1 | 1 | 1 | 1 | 4     |

| Tier | Frame | W | D | U | X | Total |
|------|-------|---|---|---|---|-------|
| II   | MIL   | 3 | 1 | 1 | 0 | 5     |
| II   | CIV   | 1 | 2 | 2 | 0 | 5     |
| II   | FRG   | 1 | 1 | 3 | 0 | 5     |
| II   | XA    | 1 | 1 | 4 | 0 | 6     |
| II   | XB    | 3 | 1 | 2 | 0 | 6     |
| II   | XC    | 1 | 3 | 2 | 0 | 6     |
| II   | ALN   | 1 | 1 | 2 | 1 | 5     |

| Tier | Frame | W | D | U | X | Total |
|------|-------|---|---|---|---|-------|
| III  | MIL   | 3 | 2 | 1 | 0 | 6     |
| III  | CIV   | 2 | 2 | 2 | 0 | 6     |
| III  | FRG   | 1 | 2 | 3 | 0 | 6     |
| III  | XA    | 2 | 1 | 4 | 0 | 7     |
| III  | XB    | 4 | 1 | 2 | 0 | 7     |
| III  | XC    | 2 | 3 | 2 | 0 | 7     |
| III  | ALN   | 1 | 1 | 2 | 2 | 6     |

| Tier | Frame | W | D | U | X | Total |
|------|-------|---|---|---|---|-------|
| IV   | MIL   | 3 | 3 | 1 | 0 | 7     |
| IV   | CIV   | 2 | 2 | 3 | 0 | 7     |
| IV   | FRG   | 1 | 2 | 4 | 0 | 7     |
| IV   | XA    | 2 | 2 | 4 | 0 | 8     |
| IV   | XB    | 4 | 2 | 2 | 0 | 8     |
| IV   | XC    | 2 | 4 | 2 | 0 | 8     |
| IV   | ALN   | 2 | 1 | 2 | 2 | 7     |

| Tier | Frame | W | D | U | X | Total |
|------|-------|---|---|---|---|-------|
| V    | MIL   | 4 | 3 | 1 | 0 | 8     |
| V    | CIV   | 3 | 2 | 3 | 0 | 8     |
| V    | FRG   | 1 | 2 | 5 | 0 | 8     |
| V    | XA    | 2 | 2 | 5 | 0 | 9     |
| V    | XB    | 5 | 2 | 2 | 0 | 9     |
| V    | XC    | 3 | 4 | 2 | 0 | 9     |
| V    | ALN   | 2 | 1 | 2 | 3 | 8     |


## 5. Core Combat Bands

Each ship has four core combat bands:
- Weapon Band (integer)
- Defense Band (integer)
- Engine Band (integer)
- Hull Integrity (percent, 0 to 100)

Cargo capacity is numeric and not a band.

Band numeric scaling (base values and module contributions) is defined in Appendix.


## 6. Combat Indicators (Presentation)

Players do not see raw band numbers.

Subsystem indicators:
- Green: current effective band > 0 and not degraded
- Yellow: current effective band > 0 and degraded
- Red: current effective band == 0

Hull indicator:
- Percent remaining (0 to 100)


## 7. Focus System

Every combat round requires selecting exactly one Focus command.

Core Focus commands:
- Focus Fire: apply focus modifier to Weapon Band for the round
- Reinforce Shields: apply focus modifier to Defense Band for the round
- Evasive Maneuvers: apply focus modifier to Engine Band for the round
- Repair Systems: restore Hull only (limited amount), no subsystem repair
- Surrender: immediate surrender resolution

Focus effects:
- Apply for current round only
- Do not persist
- Do not stack across rounds

Focus modifier magnitude and any crew or module bonuses are defined in Appendix.


## 8. Combat Loop and Resolution

Combat is simultaneous.

Each round:
1. Player selects Focus.
2. Enemy selects Focus.
3. Compute effective bands:
   effective_band = base_band - persistent_degradation + focus_modifier
4. If Escape intent is declared, resolve escape first:
   - Compare effective Engine bands per Escape Model.
   - If success, combat ends immediately (no attacks this round).
5. Resolve attacks simultaneously:
   For each side:
   - If effective Weapon > opponent effective Defense:
       damage = effective Weapon - opponent effective Defense
     else:
       damage = 0
6. Apply evasive mitigation to incoming damage:
   - If effective Engine >= opponent effective Weapon:
       damage = max(1, damage - 1) if damage > 0
7. Apply damage to Hull.
8. Apply threshold-based degradation rolls (Section 9).
9. Check termination:
   - Hull <= 0
   - Escape success
   - Surrender resolved


## 9. Degradation Model (Persistent)

Hull integrity thresholds:
- Green: > 66 percent
- Yellow: 33 to 66 percent
- Red: <= 33 percent

When Hull crosses a threshold boundary during combat:
- Perform one degradation roll per threshold crossed.
- For each roll, randomly select one subsystem that currently has band > 0:
  - Weapon, Defense, Engine
- Apply -1 persistent degradation to the selected subsystem.

Persistent degradation:
- Persists after combat
- Persists across turns and encounters
- Cannot reduce a band below 0
- Is removed only by Shipdock repair


## 10. Repair Rules

Repair Systems (in combat):
- Restores Hull only
- Does not remove subsystem degradation

Shipdock repair (at Shipdock destinations only):
- Restores Hull to 100 percent
- Clears all persistent subsystem degradation
- Costs credits (defined in Appendix)


## 11. Escape Model

Escape requires:
- Focus selection is Evasive Maneuvers for that round
- Escape intent flag is true for that round

Escape resolution occurs before attacks.

Escape success formula is defined in Appendix and may reuse the Pursuit Engine structure.

If escape fails:
- Combat proceeds with normal attack resolution.


## 12. Destruction and Insurance

When Hull <= 0:
- Ship state becomes Destroyed.

Player destruction outcome:
- If player has no insurance: run ends (death).
- If player has insurance:
  - Perform survival roll.
  - Survival chance is never 100 percent.
  - If survive:
    - Insurance is consumed
    - Ship is lost
    - Cargo is lost
    - Player respawns at a valid destination
  - If fail:
    - Run ends (death)

Insurance:
- Purchasable at Bank locations only
- Consumed on destruction survival attempt
- Cost escalates after each claim (defined in Appendix)


## 13. Surrender Resolution

Surrender outcome depends on attacker type:

- Police or Patrol: fine or Tier 1 enforcement action
- Pirates: cargo confiscated, ship survives
- Blood Raiders: death (run ends)

Surrender prevents destruction resolution for that encounter.


## 14. Invariants

- Slot distributions must match Section 4 exactly.
- There are only three typed slot categories: Weapon, Defense, Utility.
- Untyped slots accept any module type and count toward total.
- Focus must be selected every combat round.
- Combat is simultaneous; no initiative order exists.
- Mitigation cannot reduce a successful hit below 1 damage.
- No band may drop below 0.
- Subsystem degradation persists until Shipdock repair.
- Insurance is Bank-only, consumed on use, and never guarantees survival.
