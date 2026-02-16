# EmojiSpace - World State Contract
Status: LOCKED (Phase 6)
Target Version: 0.10.0
File: /design/world_state_contract.md

----------------------------------------------------------------
1. Purpose
----------------------------------------------------------------

Defines the deterministic World State layer.

Introduces:

- Situations (persistent modifiers)
- Events (discrete mutations)
- Domain-typed ModifierEntry system (with ALL)
- Severity tiers (1-5)
- Emoji profile integration
- Spawn gate with cooldown
- Awareness Radius evaluation
- Structural persistence (Worldgen Lock)
- Scheduled Events (delayed triggers)

This contract extends prior systems without altering their authority.

----------------------------------------------------------------
2. Deterministic Inputs
----------------------------------------------------------------

World State resolution depends on:

- world_seed
- system_id
- current_day
- world_state_settings.event_frequency_mode
- prior world_state records

All outcomes must be reconstructible from logs and stored records.

----------------------------------------------------------------
3. Game Creation Setting
----------------------------------------------------------------

world_state_settings:
  event_frequency_mode: "low" | "normal" | "high"

Mapping to spawn_gate_p (per system per day):

- low    = 0.05
- normal = 0.08
- high   = 0.10

Immutable for the duration of a run.

----------------------------------------------------------------
4. Core Definitions
----------------------------------------------------------------

4.1 Situation

A deterministic, time-bounded modifier applied to:

- system
- destination

Situations:
- Are additive only
- Do not mutate world structure
- Expire automatically
- May be created by Events
- May spawn independently (via spawn gate)

4.2 Event

A deterministic discrete world mutation.

Events may:
- Create Situations
- Modify player progression
- Modify player assets
- Change population (+/-1)
- Change government (archetype swap)
- Mark destinations destroyed (tag)
- Add/remove system_flags
- Mutate NPC state (bounded)
- Schedule follow-up Events (delayed triggers)
- Chain to other Events (deterministic, no circular repetition)

Events may NOT:
- Delete systems
- Remove destinations from registry
- Rewrite pricing or legality logic
- Mutate world topology (starlanes)
- Regenerate markets or change SKU base lists

----------------------------------------------------------------
5. Relationship Rules (Event <-> Situation)
----------------------------------------------------------------

1. Situations may spawn independently via spawn gate.
2. Events may spawn independently via spawn gate.
3. Events may create Situations.
4. Situations may NOT create Events.
5. Situation expiration may NOT trigger Events.
6. Events may chain to other Events only through explicit
   scheduled_events declarations (Section 14).

----------------------------------------------------------------
6. Emoji Profile Integration
----------------------------------------------------------------

All Situations and Events must include:

- emoji_id (string)
- severity_tier (1-5)

Emoji does not influence simulation logic.

Tag governance note:
Any new tags introduced by this phase MUST be synchronized with:
- tags.json
- emoji.json
per the emoji profile contract requirements.

----------------------------------------------------------------
7. Severity Tier System
----------------------------------------------------------------

Tier 1: Common, minor
Tier 2: Uncommon, moderate
Tier 3: Rare, significant
Tier 4: Very rare, major
Tier 5: Exceptional, crisis-level

Tier controls:

- Spawn weighting
- Duration ranges
- Structural eligibility
- DataNet display priority

Restrictions:

Tier 1-2:
  - No structural change
  - No population change
  - No government change
  - No destination destruction

Tier 3:
  - Significant modifiers
  - No structural destruction

Tier 4-5:
  - May perform structural mutation
  - Subject to structural rate limit

----------------------------------------------------------------
8. Duration Rules (Variable, Deterministic)
----------------------------------------------------------------

Situations and Events that create time-bounded conditions MUST use
variable duration determined by deterministic RNG.

Duration ranges by tier:

Tier 1: 3-6 days
Tier 2: 4-8 days
Tier 3: 6-12 days
Tier 4: 8-15 days
Tier 5: 10-20 days

Duration selection:

duration_seed =
  hash(world_seed, system_id, start_day, object_id, "duration")

duration_days =
  min_days +
  floor(rng_u01(duration_seed) * (max_days - min_days + 1))

end_day = start_day + duration_days

No fixed durations per tier are allowed.

----------------------------------------------------------------
9. Spawn Gate Model
----------------------------------------------------------------

Evaluation is not generation.

For each (system_id, day):

If system is in cooldown:
  no generation

Else:

spawn_gate_roll =
  rng_u01(hash(world_seed, system_id, day, "spawn_gate"))

If spawn_gate_roll >= spawn_gate_p:
  no generation

Else:
  proceed to generation pipeline:

1. Determine severity tier
2. Determine spawn type (Situation vs Event)
3. Generate object
4. Apply effects
5. Log

Scheduled Events (Section 14) bypass spawn gate.

----------------------------------------------------------------
10. Cooldown Rule
----------------------------------------------------------------

If any Situation or Event is generated in a system on day D:

Cooldown days:
D+1 through D+5

Spawn gate auto-fails during cooldown.

Cooldown does not block scheduled Events.

----------------------------------------------------------------
11. Spawn Type Weighting (Situation vs Event)
----------------------------------------------------------------

After spawn gate passes and severity_tier is selected:

Base weighting:
- 70% Situation
- 30% Event

Tier override:
If severity_tier is 4 or 5:
- Event probability is at least 50%

Spawn type roll:

spawn_type_roll =
  rng_u01(hash(world_seed, system_id, day, "spawn_type"))

Deterministic rule:
- If tier <= 3: Event if roll < 0.30 else Situation
- If tier >= 4: Event if roll < 0.50 else Situation

----------------------------------------------------------------
12. ModifierEntry Model
----------------------------------------------------------------

Situations and Events may contain zero or more ModifierEntry objects.

ModifierEntry:

{
  "domain": "goods|missions|ships|modules|crew|travel",
  "target_type": "ALL|string",
  "target_id": "string|null",
  "modifier_type": "string",
  "modifier_value": integer
}

Rules:

If target_type = "ALL":
  target_id must be null.

If target_type != "ALL":
  target_id must be defined.

Multiple ModifierEntry objects are allowed per object.
A single Situation/Event may affect multiple domains and targets.

----------------------------------------------------------------
13. Domain Definitions
----------------------------------------------------------------

13.1 GOODS DOMAIN

target_type:
  - ALL
  - sku
  - category
  - tag

modifier_type:
  - price_bias_percent
  - demand_bias_percent
  - availability_delta

Caps (applied per SKU after aggregation):

  price_bias_percent: +40 / -50
  demand_bias_percent: +50 / -50
  availability_delta: +/-3

13.2 MISSIONS DOMAIN

target_type:
  - ALL
  - mission_type
  - tag

modifier_type:
  - spawn_weight_delta
  - payout_bias_percent

Caps per mission type:

  spawn_weight_delta: +/-100
  payout_bias_percent: +/-50

13.3 SHIPS DOMAIN

target_type:
  - ALL
  - hull_id
  - tag

modifier_type:
  - availability_delta
  - price_bias_percent

Caps per hull:

  availability_delta: +/-3
  price_bias_percent: +/-40

13.4 MODULES DOMAIN

target_type:
  - ALL
  - module_type
  - tag

modifier_type:
  - availability_delta
  - price_bias_percent

Caps per module:

  availability_delta: +/-3
  price_bias_percent: +/-40

13.5 CREW DOMAIN

target_type:
  - ALL
  - crew_role
  - tag

modifier_type:
  - hire_weight_delta
  - wage_bias_percent

Caps per crew role:

  hire_weight_delta: +/-100
  wage_bias_percent: +/-50

13.6 TRAVEL DOMAIN

target_type:
  - ALL
  - special
  - route_id
  - system_id

modifier_type:
  - travel_time_delta
  - risk_bias_delta
  - special_flag

Caps per route:

  travel_time_delta: +/-2
  risk_bias_delta: +/-2
  special_flag: max 1 active per system

----------------------------------------------------------------
14. Scheduled Events (Delayed Triggers)
----------------------------------------------------------------

Events may explicitly schedule follow-up events:

Event.effects.scheduled_events:
[
  {
    "event_id": "string",
    "delay_days": integer
  }
]

Rules:

1. delay_days must be >= 1.
2. scheduled trigger_day = parent.trigger_day + delay_days
3. scheduled events inherit:
   - root_event_id = parent.root_event_id
   - chain_origin_day = parent.chain_origin_day
4. scheduled events bypass spawn gate and cooldown.
5. scheduled events must still obey:
   - structural event rate limit (Section 16)
   - circular repetition rules (Section 17)

If a scheduled event is blocked by the structural rate limit:
- Defer execution to the next eligible day (deterministic).
- Do not cancel.

----------------------------------------------------------------
15. Situation Schema
----------------------------------------------------------------

{
  "situation_id": "string",
  "emoji_id": "string",
  "severity_tier": 1-5,
  "scope_type": "system|destination",
  "scope_id": "string",
  "start_day": integer,
  "end_day": integer,
  "source_event_id": "string|null",
  "modifiers": [ModifierEntry]
}

Limits:

- Max 3 active situations per system.
- Situations expire when current_day > end_day.

----------------------------------------------------------------
16. Event Schema
----------------------------------------------------------------

{
  "event_id": "string",
  "emoji_id": "string",
  "severity_tier": 1-5,
  "system_id": "string",
  "trigger_day": integer,
  "root_event_id": "string",
  "chain_origin_day": integer,
  "effects": {
    "create_situations": [SituationObject],
    "destroy_destination_ids": [string],
    "population_delta": -1|0|1,
    "government_change": "string",
    "system_flag_add": [string],
    "system_flag_remove": [string],
    "npc_mutations": [
      {
        "npc_id": "string",
        "mutation_type": "remove|faction_change|hostility_flag",
        "new_value": "string|boolean|null"
      }
    ],
    "player_progression_delta": { "track_id": integer },
    "asset_destruction": { "goods_ids": [string] },
    "scheduled_events": [
      { "event_id": "string", "delay_days": integer }
    ],
    "propagate_situations": [
      {
        "situation_id": "string",
        "radius": 1,
        "max_targets": integer,
        "delay_days": integer
      }
    ],
    "modifiers": [ModifierEntry]
  }
}

Notes:

- destroy_destination_ids does not delete destinations.
  It adds destination tag "destroyed" (Section 18).
- npc_mutations do not create NPCs.
- government_change is an archetype swap only.
- propagate_situations is only permitted if severity_tier >= 4.
- Propagation may only create Situations.
- Propagation may NOT trigger Events.
- Propagation may NOT cause structural mutation outside origin system.

----------------------------------------------------------------
15A. Cross-System Situation Propagation
----------------------------------------------------------------

Definition:
Events with severity_tier >= 4 may propagate Situations to neighboring systems.

Rules:

1. radius is fixed at 1 (direct starlane neighbors only).
2. Eligible systems = all systems at graph distance 1 from origin.
3. max_targets limits number of affected neighboring systems.
4. Target systems selected deterministically:
   - Sort eligible system_ids lexicographically.
   - Compute deterministic score:
     score = hash(world_seed, origin_system_id, trigger_day, target_system_id)
   - Select lowest N scores, where N <= max_targets.
5. delay_days >= 0.
   - If 0: Situation created same day.
   - If > 0: Scheduled for trigger_day + delay_days.
6. Propagated Situations:
   - Bypass spawn gate.
   - Do NOT bypass 3 active Situation cap per system.
   - Do NOT count toward structural rate limits.
   - May NOT recursively propagate.

Clarify:
Propagation creates only Situations.
Structural mutations are restricted to origin system only.

----------------------------------------------------------------
17. Structural Event Rate Limit
----------------------------------------------------------------

Max 1 structural event per system per 10 days.

Structural mutations are ONLY:

- population_delta != 0
- government_change
- destination destruction (tag "destroyed")

system_flags and npc_mutations are NOT structural.

----------------------------------------------------------------
18. Structural Persistence (Worldgen Lock)
----------------------------------------------------------------

Immutable after world generation:

- System identity
- Destination registry
- Location entities
- Starlane graph

Destinations may receive tags:

- destroyed (Phase 6)
- salvage_site (reserved for future)

Destroyed destinations:

- Remain in registry
- Unavailable for normal interaction
- Travel remains possible
- Future phases may treat destroyed + salvage_site as special interaction

No deletion permitted.

----------------------------------------------------------------
19. System Flags
----------------------------------------------------------------

Systems may hold:

system_flags: [string]

Flags represent temporary system-wide conditions.

Flags are not generic tags and are stored separately to avoid tag sprawl.

Flags may influence:
- mission generation weighting
- encounter weighting
- enforcement strength inputs
- travel risk inputs
via ModifierEntry or explicit handling in authoritative systems.

----------------------------------------------------------------
20. Modifier Aggregation Rules
----------------------------------------------------------------

Resolution order:

1. Collect all active Situations
2. Collect all active Events (including Event.effects.modifiers)
3. Expand ALL entries into per-target effects
4. Aggregate modifiers additively per:
   domain + target_scope + target_id + modifier_type
5. Apply caps per target entity
6. Pass final aggregated values to authoritative system

Aggregation is:

- Additive
- Order-independent
- Deterministic

Example:

ALL goods price_bias +10
tag medical price_bias +15

Medical SKUs receive +25
Other SKUs receive +10

Caps applied afterward.

----------------------------------------------------------------
21. Awareness Radius
----------------------------------------------------------------

R = graph distance in starlane network.

Daily tick:
  R = 0

DataNet query:
  R = 1

DataNet must not trigger additional generation.
It only reveals evaluated state.

----------------------------------------------------------------
22. DataNet Display Model
----------------------------------------------------------------

Display all Events and Situations within R=1.

Sort by:

1. severity_tier descending
2. trigger_day descending
3. deterministic id ordering

Display priority:

Tier 1:
  display_priority = low

Tier 2-5:
  display_priority = normal

Display priority is presentation-only.

----------------------------------------------------------------
23. Time Engine Integration
----------------------------------------------------------------

On day advance:

1. Wage deduction
2. Fuel checks
3. Situation expiration
4. Event resolution (including scheduled events due today)
5. Spawn gate evaluation

----------------------------------------------------------------
24. Phase 6 Tag Additions
----------------------------------------------------------------

Destination tags introduced/reserved by Phase 6:

- destroyed
- salvage_site (reserved for future use)

Any additional tags require explicit update to this section and
synchronized updates to tags.json and emoji.json.

----------------------------------------------------------------
25. Logging Requirements
----------------------------------------------------------------

Must log:

- system_id
- day
- spawn_gate_roll
- spawn_gate_p
- cooldown state
- generated object (event/situation)
- selected severity tier
- duration roll result and end_day
- expired situations
- structural changes
- system_flags changes
- npc_mutations applied
- scheduled events created and triggered
- propagated_situations created
- propagation target_system_ids
- propagation delay_days
- modifier aggregation results
- player deltas

Logs must enable full reconstruction.

----------------------------------------------------------------
26. Determinism Guarantee
----------------------------------------------------------------

Given identical:

- world_seed
- event_frequency_mode
- system graph
- day
- player position
- prior world_state records

World State resolves identically.

- propagation selection and scheduling

No uncontrolled simulation drift allowed.

----------------------------------------------------------------
END OF CONTRACT
----------------------------------------------------------------
