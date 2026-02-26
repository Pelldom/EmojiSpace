# Combat Resolution Contract
Version: 0.11.2
Status: Phase 4.x � Combat Resolver (Locked)

This contract defines the combat resolution system for EmojiSpace.
All combat execution must follow this specification exactly.
No implicit behavior is permitted.


============================================================
DETERMINISM AND RNG (Authoritative)
============================================================

- World generation, travel, markets, encounters, and pursuit remain deterministic as specified by their contracts.
- Combat is stochastic. The combat RNG seed is created at the moment combat begins.
- combat_rng_seed must be generated using a non-deterministic source (e.g., secrets or os.urandom) and then used to seed a local RNG instance for the duration of combat.
- combat_rng_seed must be:
  - stored in the combat state (if any),
  - logged at combat start,
  - included in the CombatResult payload.
- Replays are supported only if combat_rng_seed is known; combat is not required to be reproducible from world_seed alone.


============================================================
1. COMBAT TRIGGER
============================================================

Combat is triggered when:
- An encounter resolves into hostile action, OR
- A player initiates hostile action during interaction, OR
- A pursuit escalation converts to combat.

Combat begins immediately after the current phase resolves.


============================================================
2. COMBAT STRUCTURE
============================================================

Combat is simultaneous and round-based.
There is no initiative system.

Round numbering rule (critical):
- Round numbers start at 1.
- If resolve_combat is called, combat has already started. No "round 0" is permitted.

Each round consists of:

1. Player selects one action.
2. Enemy selects one action.
3. Bands are calculated for both sides.
4. Resolution executes in both directions.
5. Damage and degradation are applied.
6. Termination conditions are checked.
7. If none met, next round begins.


============================================================
3. CORE ACTIONS
============================================================

Always available:
- Focus Fire
- Reinforce Shields
- Evasive Maneuvers
- Attempt Escape
- Surrender

Additional actions may be unlocked by modules.


============================================================
4. BAND CALCULATION PIPELINE
============================================================

For each ship:

Step 1: Baseline
band_base = max(0, tier_baseline + frame_bias)

Step 2: Slot Fill Bonuses
- Weapon: +1 per filled Weapon slot
- Defense: +1 per filled Defense slot
- Engine: no slot-fill bonus
- Untyped slots adopt installed module type

Step 3: Module Bonuses
- Add numeric module bonuses
- Apply secondary:efficient (+1)
- Apply secondary:alien (+1 if on alien frame)
- Apply action-conditional bonuses

Step 4: Apply crew bonuses
- crew:gunner: +1 Weapon band per instance
- crew:engineer: +1 Defense band per instance
- crew:pilot: +1 Engine band per instance

Step 5: Apply persistent degradation penalties

Step 6: Apply focus modifier
Base focus = +1 to selected band

Step 7: Apply RPS adjustment
As defined in combat_and_ship_tag_contract.md

Step 8: Clamp
band_effective = max(0, computed_value)

RED override:
If a subsystem is RED (inoperable), its effective band is 0 regardless of bonuses.


============================================================
5. HIT AND DAMAGE DETERMINATION
============================================================

For A attacking B:

band_delta = weapon_effective_A - defense_effective_B

Case 1: band_delta > 0
    max_damage = band_delta
    damage_roll = RNG(1, max_damage)

Case 2: band_delta == 0
    damage_roll = RNG(0, 1)

Case 3: band_delta < 0
    damage_roll = 0

Mitigation:

If defender selected Evasive Maneuvers:
    mitigation_roll = RNG(0, 1)
Else:
    mitigation_roll = 0

Final damage:
damage = max(0, damage_roll - mitigation_roll)

Damage may be 0.

All RNG within combat must use the combat RNG (derived from combat_rng_seed).


============================================================
6. HULL MODEL
============================================================

Hull is point-based.

Each ship has:
- hull_max (integer)
- hull_current (integer)

Tier Baseline Hull:
Tier I: 8
Tier II: 10
Tier III: 12
Tier IV: 15
Tier V: 18

Frame Hull Bias:
MIL: +2
CIV: 0
FRG: +3
XA: 0
XB: -2
XC: +4
ALN: +1

Tag Modifiers:
+1 per instance of:
- secondary:alien (if on alien frame)
- secondary:prototype (if on experimental frame)
- defense_armored

-1 per instance of:
- secondary:unstable

hull_max floor = 4

Damage Application:
hull_current = max(0, hull_current - damage)

Hull percent for display:
hull_percent = floor((hull_current / hull_max) * 100)

Color Bands:
Green: > 66%
Yellow: > 33% and <= 66%
Red: <= 33%

Upward repair crossing:
- Updates color band immediately
- Does not reverse degradation
- Does not trigger new degradation


============================================================
7. SUBSYSTEM DEGRADATION
============================================================

When hull crosses a threshold downward:

1. Randomly select subsystem:
   - Weapon
   - Defense
   - Engine

2. Apply -1 degradation.

Subsystem capacity:
- Equal to number of installed modules in that subsystem
- Includes modules in Untyped slots behaving as that subsystem
- Modified by:
  secondary:enhanced (+1)
  secondary:unstable (-1)
  secondary:prototype (-1 unless experimental hull)
- Minimum capacity = 1

If degradation >= capacity:
Subsystem becomes RED.
Effective band = 0.

Degradation persists until dock repair.


============================================================
8. IN-COMBAT REPAIR
============================================================

Unlocked by combat:utility_repair_system.

Repair magnitude per use:
- Base: 2 hull points
- With secondary:efficient: 3
- With secondary:alien + secondary:efficient on alien hull: 4

Non-combat crew:
- crew:mechanic: +1 repair magnitude per instance

Repair restores hull_current only.
Cannot exceed hull_max.
Does not restore degradation.

Usage limits:
- Each installed repair module provides 2 repair uses per combat.
- Repair magnitude does not stack across modules.
- Each module tracks its own 2 uses.
- Repair uses reset after combat ends.


============================================================
9. ESCAPE RESOLUTION
============================================================

If Attempt Escape selected during combat:

- Escape is resolved inside combat using combat RNG and the same engine band comparison logic (engine delta + modifiers).
- Engine band is primary driver.
- Apply modifiers:
    combat:utility_cloak = +1 escape modifier
    ship:utility_interdiction = +1 pursuer modifier
    crew:pilot = +1 escape modifier per instance
- Roll with the combat RNG (local RNG from combat_rng_seed).
- The pursuit_resolver is for pre-combat flee resolution and is NOT invoked from the combat loop.

If success:
Combat ends immediately, no attacks that round.

If failure:
Combat continues.


============================================================
10. SURRENDER
============================================================

If Surrender selected:
Combat ends immediately.

Consequences determined by attacker type.


============================================================
11. DESTRUCTION
============================================================

If hull_current == 0:

Player:
If insured:
    Roll survival probability (defined elsewhere).
    If success:
        Insurance consumed.
        Ship destroyed.
        Player survives.
    Else:
        Game Over.
Else:
    Game Over.

NPC:
Ship destroyed.
Rewards resolved via encounter system.


============================================================
12. TERMINATION CONDITIONS
============================================================

Combat ends when:
- One ship destroyed
- Escape succeeds
- One side surrenders


============================================================
13. COMBAT INFORMATION AND SCANNING
============================================================

Default combat information:

Player sees (self):
- hull_current
- hull_max
- hull_percent
- color band
- subsystem status indicators (Green/Yellow/Red)

Player sees (enemy, unscanned):
- hull_percent
- color band
- Threat Rating (TR)
- No numeric hull points
- No modules/crew/secondaries

Combat scan:

If player has ship:utility_probe_array AND chooses Scan action:
- Resolve scan success in the encounter/interaction layer (deterministic, seeded).
- On success, enemy ship becomes "scanned" for the remainder of the combat.

Player sees (enemy, scanned):
- hull_max (numeric)
- hull_current (numeric)
- full module list (including secondaries)
- full crew list
- subsystem degradation state


============================================================
14. THREAT RATING (TR) DERIVATION (Locked)
============================================================

TR is a 1-5 rating derived from ship combat capability.
TR is computed deterministically at ship build time for both players and NPCs.

RCP (Raw Combat Power) formula:

Let:
W = weapon_band_base_potential
D = defense_band_base_potential
E = engine_band_base_potential
H = hull_max
R = number_of_repair_modules_installed

Definitions:
- "band_base_potential" uses the band calculation pipeline but excludes:
  - focus modifiers
  - RPS adjustments
  - temporary combat round effects
- Crew bonuses ARE included in band_base_potential.
- Degradation is not included (TR reflects pre-combat capability).

Compute:
RCP = W + D + floor(E / 2) + floor(H / 4) + (2 * R)

TR mapping bands:

TR 1: 0 to 6
TR 2: 7 to 13
TR 3: 14 to 20
TR 4: 21 to 26
TR 5: 27 or higher

NPC parity requirement:
- NPC ships must use the same RCP and TR pipeline as player ships.
- NPC ships must have access to the same module, secondary, and crew generation rules.


============================================================
15. LOGGING REQUIREMENTS
============================================================

Per-combat log header must include:
- combat_rng_seed

Log each round:
- Round number
- Actions selected
- Effective bands
- RPS result
- band_delta
- damage_roll
- mitigation_roll
- Final damage
- Hull current/max and percent
- Subsystem degradation events
- Repair usage (module id and remaining uses)
- Escape result
- Scan success/failure and scanned state
- Destruction outcome

Combat can be replayed if combat_rng_seed is known:
- Given combat_rng_seed, ship configuration, and action selections, the exact combat outcome can be reproduced.
- Combat is not required to be reproducible from world_seed alone.


============================================================
16. INPUT FORMAT REQUIREMENTS
============================================================

The only allowed ship input format is ship_state (dict) with at minimum:
- hull_id (string)
- module_instances (list of module instance dicts)
- degradation_state (dict with keys weapon/defense/engine integers, default 0)
- optional: crew (list), tags (list)

ShipLoadout as an input to the combat resolver is Forbidden.
