# Encounter Generator Contract
Version: 0.5.x
Status: Locked

------------------------------------------------------------
Subtype Weight Calculation
------------------------------------------------------------

For each subtype:

effective_weight =
    base_weight
    + situation_bias (if applicable)
    + authority_enforcement_bonus (if applicable)

------------------------------------------------------------
Authority Enforcement Bonus
------------------------------------------------------------

If subtype.posture == "authority":

    effective_weight += enforcement_strength

    If travel_context.mode == "system_arrival":
        effective_weight += enforcement_strength

Where enforcement_strength is read from governments.json
for the current system government.

No regulation_level.
No government_bias mapping.
No penalty_severity scaling.

------------------------------------------------------------
Clamp Rule
------------------------------------------------------------

If effective_weight < 0:
    effective_weight = 0

Ensure this section replaces any prior government_bias logic.
