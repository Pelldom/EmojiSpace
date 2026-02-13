# Ship System Appendix: Scaling and Numeric Rules
Version: 0.4.1
Status: Phase 4 Appendix A (Locked)

This appendix defines numeric scaling and deterministic math rules used by /design/ship_system_contract.md.
All implementation must follow this appendix.


## 1. Baseline Bands by Tier

Tier baselines apply to Weapon, Defense, and Engine bands prior to frame bias, slot-fill, module bonuses, focus, and degradation.

| Tier | Baseline Band |
|------|---------------|
| I    | 1             |
| II   | 1             |
| III  | 2             |
| IV   | 2             |
| V    | 3             |


## 2. Frame Band Bias Table (Locked)

Frame bias applies to all three bands: Weapon, Defense, Engine.

Bias is applied as:
band_pre = tier_baseline + frame_bias

Band floors:
- band_pre is clamped to a minimum of 0 before further additions.

| Frame | Weapon Bias | Defense Bias | Engine Bias |
|-------|-------------|--------------|-------------|
| MIL   | +1          | +1           | -1          |
| CIV   | 0           | 0            | 0           |
| FRG   | -1          | 0            | -1          |
| XA    | 0           | 0            | +1          |
| XB    | +2          | 0            | -1          |
| XC    | 0           | +2           | -1          |
| ALN   | 0           | 0            | +1          |


## 3. Band Computation Model

For a given ship and band (Weapon, Defense, Engine):

band_base = max(0, tier_baseline + frame_bias)

Then apply:
- slot_fill_bonus
- module_bonus_total
- persistent_degradation_penalty
- focus_modifier (if applicable this round)

Final clamp:
- band_effective is clamped to a minimum of 0.


## 4. Slot-Fill Band Bonuses (Locked)

Weapon slots:
- Each filled Weapon slot adds +1 to Weapon band.

Defense slots:
- Each filled Defense slot adds +1 to Defense band.

Utility slots:
- No slot-fill bonus applies to Engine band.

Untyped slots:
- see untyped slot resolution rule below
- Any band contribution depends on the installed module.


## 5. Module Bonus Layer (Locked)

Modules may define a numeric module bonus for a band or action modifier.
Default module bonuses must not exceed 1.

Rule:
- No default module bonus may be greater than 1.

Efficient and Alien secondary modifiers apply only to module-provided numeric bonuses.
They do not modify slot-fill bonuses.


## 6. Focus Modifier (Locked)

Base focus modifier magnitude is +1.

Focus applies to one band per round depending on the selected Focus command:
- Focus Fire: +1 to Weapon band for the round
- Reinforce Shields: +1 to Defense band for the round
- Evasive Maneuvers: +1 to Engine band for the round

Focus does not persist between rounds.


## 7. Combat Utility Tag Numeric Effects (Locked)

These tags modify specific Focus actions or escape behavior.

combat:utility_engine_boost
- When Focus is Evasive Maneuvers: Engine band +1 for that round

combat:utility_overcharger
- When Focus is Evasive Maneuvers: Engine band +1 for that round

combat:utility_signal_scrambler
- When Focus is Reinforce Shields: Defense band +1 for that round

combat:utility_targeting
- When Focus is Focus Fire: Weapon band +1 for that round

combat:utility_cloak
- Escape Attempt: passive +1 to escape resolution (not tied to focus)

combat:utility_repair_system
- Unlocks the Repair Systems focus command (no numeric modifier by itself)


## 8. Ship Utility Tag Numeric Effects (Locked)

ship:utility_interdiction
- Passive +1 pursuer (applies in combat escape and pursuit)

ship:utility_extra_cargo
- +5 physical cargo slots

ship:utility_data_array
- +5 data cargo slots

ship:utility_smuggler_hold
- Passive reduction to discovery of illegal cargo (integration point with enforcement)

ship:utility_mining_equipment
- Unlocks mining action

ship:utility_probe_array
- Unlocks future data/exploration encounter actions (not pre-combat scanning in current scope)

ship:utility_extra_fuel

Effect:
fuel_capacity_bonus = +5 per module

Stacking:
Yes

Authority:
Applied by ship assembler when computing final fuel_capacity.


## 9. RPS Integration Point (Alignment Rule)

Weapon/Defense RPS tags and their matchup logic are defined in combat_and_ship_tag_contract.md.

RPS is applied as defined there, prior to hit evaluation, and must not be applied again elsewhere in the pipeline.


## 10. Secondary Tags: Constraints and Mechanics (Locked)

Secondary tag constraint:
- Each module may have at most 1 non-alien secondary tag.
- secondary:alien does not count toward that limit and may stack with one non-alien secondary.

secondary:compact
- Each compact module consumes 0.5 of a slot of its own slot type.
- For every two compact modules of the same slot type, 1 full slot is freed.
- No cap.

secondary:enhanced
- Increases subsystem degradation capacity by +1 for the subsystem it belongs to.

secondary:unstable
- Decreases subsystem degradation capacity by -1 for the subsystem it belongs to.
- Minimum subsystem degradation capacity floor is 1.

secondary:prototype
- On non-experimental hulls: behaves exactly as secondary:unstable.
- On experimental hulls (ship:trait_experimental): has no degradation-capacity penalty.

secondary:efficient
- Flat +1 to the module's main numeric bonus (including action-conditional bonuses).
- No effect on unlock-only tags (no numeric bonus to modify).
- Does not modify slot-fill bonuses.

secondary:alien
- Only applies its effect if the module is installed on ship:trait_alien hull.
- Adds +1 to the module's main numeric bonus (including action-conditional bonuses).
- May stack with secondary:efficient (effective +2 in that case).


## 11. Secondary Tag Rarity Distribution (Locked)

Base distribution for selecting a primary secondary outcome:

- 50% = none
- 20% = unstable
- 10% = prototype
- 5%  = compact
- 5%  = enhanced
- 5%  = efficient
- 5%  = alien

Alien stacking procedure (Option A):
1) Roll once on the distribution above.
2) If result is not alien, stop.
3) If result is alien:
   - Apply secondary:alien
   - Roll again on the same distribution excluding alien
   - The second roll may result in none or one non-alien secondary


## 12. Deferred Note: Pricing Impact of Secondary Tags

Secondary tags must affect module pricing:
- unstable: large price reduction
- prototype: slight price reduction
- compact: price increase
- enhanced: price increase
- efficient: price increase
- alien: substantial price increase
- alien + (any non-alien secondary): substantial additional price increase

Pricing formulas are deferred until module purchase availability is implemented.


## 13. Deferred Note: Purchase Location Refactor

Modules are purchased at Shipdock locations (same as ships and repairs).
This requires updating location capabilities to support shipdock module inventory.
This change is deferred until purchase/availability implementation work.

## 4A. Untyped Slot Resolution Rule (Locked)

Untyped slots are flexible containers that adopt the behavior of the installed module.
They are not a fourth slot category.

When a module is installed in an Untyped slot, it is treated exactly as if it were installed in a slot of its own type.

Resolution rules:

1. If a Weapon module is installed in an Untyped slot:
   - It is treated as a Weapon slot for all purposes.
   - Grants +1 Weapon band from slot fill.
   - Counts toward Weapon subsystem degradation capacity.
   - Counts toward Weapon compact pairing calculations.

2. If a Defense module is installed in an Untyped slot:
   - It is treated as a Defense slot for all purposes.
   - Grants +1 Defense band from slot fill.
   - Counts toward Defense subsystem degradation capacity.
   - Counts toward Defense compact pairing calculations.

3. If a Utility module is installed in an Untyped slot:
   - It is treated as a Utility slot for all purposes.
   - Does not grant any slot-fill band bonus.
   - May grant Engine band or other numeric bonuses only if defined by the module's tag.
   - Counts toward Utility compact pairing calculations.

Additional constraints:

- Untyped slots do not grant inherent band bonuses.
- Untyped slots do not modify module behavior beyond adopting the module’s slot type.
- Subsystem degradation capacity is determined by the number of installed modules in that subsystem, including modules installed in Untyped slots.
- Compact slot calculations are grouped by effective slot type (Weapon, Defense, Utility), regardless of whether the module is installed in a typed or Untyped slot.
