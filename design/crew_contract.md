# Crew System Contract
Phase: 5 - Crew and Social Systems
Target Version: 0.9.x
Status: LOCKED (Phase 5 Design)

---

## 1. Purpose

The Crew system introduces hireable personnel that attach to ships and provide deterministic, additive stat modifiers within defined domains.

Crew are Tier 2 NPC entities and persist independently of ships unless permanently removed under defined destruction rules.

Crew:
- Have exactly one primary role.
- May have 0–2 secondary tags.
- Provide deterministic additive modifiers only.
- Never introduce randomness at runtime.
- Never override authority boundaries of other systems.

Crew are permanently deleted only under conditions defined in Section 13.

---

## 2. Data Dependencies

Requires:
- data/crew_roles.json
- data/crew_rarity.json
- data/tags.json (global tag registry; crew tags are filtered by prefix `crew_*`)
- emoji_profile_contract.md
- npc_entity_contract.md
- ship_entity_contract.md
- time_engine_contract.md
- law_enforcement_contract.md

Crew tags are not stored in a separate file. All tags reside in `tags.json`.

---

## 3. Crew Entity Structure

Crew extend NPCEntity (Tier 2) with:

Persistent Fields:
- npc_id
- name
- role_id
- tag_ids (0–2; must reference tags with prefix `crew_`)
- rarity_tier
- hiring_cost
- wage_per_day
- assigned_ship_id (nullable)
- current_location_id (if unassigned)

Crew do NOT store derived bonus values. All modifiers are computed at runtime from role_id and tag_ids.

---

## 4. Role Structure

Each crew member has exactly one role.

Roles define:
- Primary domain
- Base modifier values
- Emoji identity
- Hiring cost baseline
- Wage baseline

Domains:
- Combat
- Ship
- Market
- Legal
- Travel
- Utility

Example Roles:
- pilot
- gunner
- engineer
- mechanic
- tactician
- broker
- quartermaster
- lawyer
- navigator
- science

Multiple crew members may share the same role on a single ship.

---

## 5. Tag Structure

Crew may have 0–2 tags.

Tags:
- Must use prefix `crew_*`
- Must belong to same domain as role
- Provide smaller magnitude effects than roles
- May be positive or negative
- Stack additively unless otherwise defined

Cross-domain tags are forbidden in Phase 5.

---

## 6. Emoji Profile

Crew emoji profile consists of:
- Primary: role emoji
- Secondary: tag emojis (0–2)

Constructed using emoji_profile_contract.md.
Emoji ordering:
1. Role emoji
2. Tag emojis in deterministic sorted order

---

## 7. Modifier Aggregation

Crew modifiers are aggregated per domain before system resolution.

Combat:
- Additive band adjustments
- Hard cap: +3 per band
- Negative effects allowed

Market:
- Multiplicative adjustments
- No hard cap

Ship:
- Additive capacity or efficiency changes

Legal:
- May reduce fines or downgrade Tier 1 penalties
- May NOT change legality classification
- May NOT override government tag interpretation
- Tier 2 arrest may only be converted via Lawyer sacrifice rule

Travel:
- Additive efficiency modifiers

Ordering:
1. Base system resolution
2. Apply crew domain modifiers
3. Apply clamping rules (if any)

Deterministic ordering enforced.

---

## 8. Crew Capacity Enforcement

ShipEntity must define:
- crew_capacity
- crew_slots (list of npc_id)

Rules:
- crew_slots length - crew_capacity
- Hiring blocked if capacity full
- Removing ship invalidates crew assignments

---

## 9. Wage System

Crew wages are applied at each TimeEngine day advancement event.

TimeEngine advances:
- Inter-system travel
- In-system movement

At start of each day advancement:
- Total wage_per_day is calculated
- If player credits < wages:
  - Deduct wages
- If player credits < wages:
  - Prevent time advancement
  - Return deterministic error: "Insufficient funds for crew wages"

No debt.
No partial retention.
No morale impact.

---

## 10. Hiring and Dismissal

Hiring:
- Only at location_bar
- Deterministic generation per location seed
- Deduct hiring_cost
- Assign to ship if capacity available

Dismissal:
- Allowed only at any destination
- Crew removed from ship
- Crew relocated per relocation algorithm
- No refund

---

## 11. Relocation Algorithm (Dismissed Crew)

When dismissed:
1. Identify nearest system containing a location_bar
2. If multiple candidates:
   - Select lowest location_id
3. Set crew.current_location_id
4. assigned_ship_id = null

Relocation does not consume time.

---

## 12. Lawyer Sacrifice Rule

If Tier 2 arrest triggered:
- Player prompted to select lawyer
- Selected lawyer permanently deleted
- Arrest prevented
- If no lawyer:
  - Standard Tier 2 arrest applies

Only applies to Tier 2 detention.

---

## 13. Destruction Rules

Crew permanently deleted only if:
- Assigned ship destroyed
- Sacrificed via Lawyer rule

All other removals are relocation.

---

## 14. Deterministic Generation

Crew generation seed:

hash(world_seed, system_id, location_id, crew_slot_index)

RNG stream name:
"crew_generation"

Generation determines:
- Name
- Role
- Tags (0–2)
- Rarity
- Costs

No dynamic weighting.
No runtime rerolls.

---

## 15. Rarity

rarity_tier:
- common
- uncommon
- rare

Affects:
- Hiring cost
- Wage
- Magnitude scaling

Does not introduce cross-domain effects.

---

## 16. Phase Scope

In Phase 5:
- Crew mechanics are fully implemented for player-controlled ships.
- NPC ships do not utilize crew modifiers.
- This contract is reusable for NPC ships in future phases.

No loyalty.
No morale.
No betrayal.
No narrative arcs.
No crew death outside destruction rules.

---

## 17. Authority Boundaries

Crew may:
- Modify numeric outcomes within domain.

Crew may NOT:
- Override combat resolution structure
- Override government legality classification
- Modify pricing formulas directly
- Introduce randomness
- Affect mission generation
- Affect encounter generation

All effects are deterministic and additive.

---

## 18. Crew Effect Matrix (Authoritative Numeric Definitions)

This section defines all mechanical effects of Crew Roles and Crew Tags in Phase 5.

All effects are deterministic.
All values are final unless amended by future contract revision.
Tags apply only one mechanical effect unless explicitly stated.

---

### 18.1 Roles

#### Pilot
+1 engine_band

#### Gunner
+1 attack_band

#### Tactician
+1 defense_band

#### Engineer
+1 repair_uses_per_combat

#### Mechanic
+1 repair_amount_per_use

#### Navigator
-2 fuel per travel event (minimum fuel cost per event = 1)

#### Broker
Buy price multiplier: 0.90  
Sell price multiplier: 1.10

#### Quartermaster
+3 cargo capacity (flat)

#### Lawyer
- Tier 1 arrest converts to Tier 0 (fine only)
- Fine amount reduced by 50%
- Enables Tier 2 sacrifice mechanic

#### Science
+1 scanner resolution
+2 data cargo capacity (flat)

---

### 18.2 Combat Focus Tags

These modify only the selected Focus action in combat.

#### crew:steady_aim
+1 Focus Fire

#### crew:trigger_happy
-1 Focus Fire

#### crew:evasive
+1 Evasive Maneuvers

#### crew:slow_reactions
-1 Evasive Maneuvers

#### crew:damage_control
+1 Repair focus

#### crew:overconfident
-1 Reinforce Shields

#### crew:ex_navy
No Phase 5 mechanical effect (story hook)

#### crew:ex_pirate
No Phase 5 mechanical effect (story hook)

---

### 18.3 Travel Tags

#### crew:fuel_efficient
-1 fuel per travel event (minimum 1)

#### crew:wasteful
+1 fuel per travel event

---

### 18.4 Cargo Tags

#### crew:organized
+1 cargo capacity (flat)

#### crew:cluttered
-1 cargo capacity (flat)

---

### 18.5 Market Tags

#### crew:haggler
+5% sell price

#### crew:bargain_hunter
-5% buy price

#### crew:awkward
-5% sell price

#### crew:blacklisted
+5% buy price

---

### 18.6 Legal Tags

#### crew:undercover
Reduced inspection chance

#### crew:wanted
Increased inspection chance

---

### 18.7 Scanner / Data Tags

#### crew:data_savvy
+1 scanner resolution

---

### 18.8 Economy Tags

#### crew:high_maintenance
+5 daily wage

---

### 18.9 Mission Tags

#### crew:connected
+1 mission slot at:
- location_bar
- location_administration

---

### 18.10 Alien Synergy Tag

#### crew:alien

For each ship, module, weapon, cargo system, or component containing a tag ending in `_alien`:

Apply +1 to that element’s numeric modifier.

Rules:

- Applies per aligned `_alien` element.
- Combat band modifiers remain subject to the standard +3 per-band cap.
- Non-combat modifiers are not capped unless capped by their own subsystem.
- Alien synergy does not create new modifiers.
- Alien synergy does not increase combat caps.

---

### 18.11 Story Hooks (No Phase 5 Effect)

#### crew:loyal
No mechanical effect in Phase 5.

#### crew:opportunist
No mechanical effect in Phase 5.

