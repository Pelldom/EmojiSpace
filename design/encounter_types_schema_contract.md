# Encounter Types Schema Contract
Version: 0.5.x
Status: Locked

Each encounter subtype defines structural behavior only.
Government influence is NOT defined in encounter_types.json.

Government enforcement impact is derived dynamically from governments.json
via enforcement_strength.

------------------------------------------------------------
Required Fields Per Encounter Type Object
------------------------------------------------------------

- subtype_id: string (unique, ASCII)
- emoji: string (placeholder allowed)
- posture: "neutral" | "authority" | "hostile" | "opportunity"
- initiative: "player" | "npc"
- allows_betrayal: boolean
- base_weight: integer >= 0
- allowed_TR_range: { "min": 1-5, "max": 1-5 }
- participant_templates: array
- default_flags: array of strings
- reward_profiles: array of { reward_profile_id, weight }
- npc_response_profile: object

------------------------------------------------------------
Removed Fields
------------------------------------------------------------

- government_bias (REMOVED)

Government effects are no longer encoded in encounter_types.json.

------------------------------------------------------------
Authority Weight Scaling
------------------------------------------------------------

Authority subtype frequency is derived as:

effective_weight =
    base_weight
    + enforcement_strength
    + (enforcement_strength if travel_context.mode == "system_arrival")

Where enforcement_strength is read from governments.json
for the system's government.

No other government fields influence encounter frequency.

------------------------------------------------------------
Determinism Requirement
------------------------------------------------------------

All weighting must be deterministic.
All weights must clamp to >= 0.
Sorting must be ASCII by subtype_id before weighted selection.
