# Emoji Profile Contract
Version: 0.9.1
Status: LOCKED
Applies To:
- Crew System
- Ship System
- Entity System
- Government System
- Location System
- Mission System
- Any future tiered entity

----------------------------------------------------------------

1. Purpose

Defines a deterministic composite identity representation called
"Emoji Profile".

Emoji Profile is presentation-layer metadata only.
It has no simulation authority.

All emojis used in the game must be defined in data/emoji.json.

emoji.json is the single source of truth for all emoji glyphs and
descriptions.

----------------------------------------------------------------

2. Definitions

Primary Emoji:
- Exactly one emoji stored directly on an entity.
- Required by entity_contract.md.
- Immutable once entity is created.
- Stored as emoji_id referencing emoji.json.
- Must resolve to a valid emoji_id in data/emoji.json.

Tier Emoji:
- Roman numeral character derived from entity tier value.
- Always displayed if entity defines a tier field.
- Inserted immediately after Primary Emoji.
- Not stored independently.
- Derived dynamically from entity tier.
- Roman numeral glyph must resolve via emoji.json.

Secondary Emojis:
- Emojis derived from tags, modules, traits, or other
  secondary identity attributes.
- Stored as emoji_id references.
- Resolved via emoji.json.
- May appear multiple times if multiple identical
  secondary sources exist.

Emoji Profile:
- A deterministic composite string composed of:
  1. Primary Emoji
  2. Tier Emoji (if applicable)
  3. Secondary Emojis (sorted deterministically)

Emoji Profile is:
- Derived
- Deterministic
- Not stored as independent state
- Reconstructible from entity data
- Fully dependent on emoji.json for glyph resolution

----------------------------------------------------------------

3. Construction Rules

Emoji Profile construction order:

1. Primary Emoji
2. Tier Emoji (if entity has a tier value)
3. Secondary Emojis sorted by system-defined deterministic rules

Multiplicity is preserved.

If multiple identical secondary emojis exist,
each instance must appear in the Emoji Profile.

No deduplication is allowed unless explicitly defined
by the owning system contract.

Example (Crew):

Primary: pilot
Tier: III
Tags:
- alien
- wanted

Sorted tag order:
alien
wanted

Profile:
PILOT_EMOJI + ROMAN_III + ALIEN_EMOJI + WANTED_EMOJI

Example (Ship):

Primary: trait_military
Tier: II
Modules:
- weapon_energy
- weapon_energy

Profile:
TRAIT_MILITARY_EMOJI + ROMAN_II + ENERGY_EMOJI + ENERGY_EMOJI

----------------------------------------------------------------

4. Tier Emoji Rule

Tier Emoji must:

- Always appear if tier field exists.
- Appear immediately after Primary Emoji.
- Use roman numeral characters defined in emoji.json.
- Be derived from stored tier integer.
- Never be manually inserted.
- Never be treated as a tag.
- Never be omitted.

Tier I must be displayed as ROMAN_I.
Tier display is mandatory for tiered entities.

----------------------------------------------------------------

5. Determinism Requirements

Emoji Profile must:

- Be reproducible from entity state.
- Not depend on runtime ordering.
- Not depend on RNG.
- Not depend on UI logic.
- Preserve multiplicity of secondary sources.
- Use deterministic sorting rules defined by owning system.
- Resolve glyphs only through emoji.json.

----------------------------------------------------------------

6. Storage Rules

Entities store:

- Exactly one Primary Emoji (as emoji_id).
- Tier value (if applicable).
- Secondary source identifiers (tag_ids, module_ids, etc.).

Entities do NOT store:

- Emoji Profile string.
- Derived composite emoji strings.
- Roman numeral glyphs directly.
- Raw emoji glyphs.

Emoji Profile must always be computed from:

- entity.emoji_id
- entity.tier
- secondary identifiers
- emoji.json glyph resolution

----------------------------------------------------------------

7. Authority Boundaries

Emoji Profile:

- Must not affect simulation.
- Must not be used for branching logic.
- Must not alter behavior.
- Must not replace primary emoji storage.
- Must not contain behavioral metadata.
- Must not introduce hidden state.

Emoji Profile is strictly presentation metadata.

----------------------------------------------------------------

8. Global Emoji Registry

All emoji_id references must resolve to entries in data/emoji.json.

emoji.json defines:

- glyph
- description

emoji.json does NOT define behavior.

Systems must not embed raw emoji glyphs directly.
All references must use emoji_id.

emoji.json is additive by default.
Existing emoji_id entries may not be redefined
without explicit version update.

----------------------------------------------------------------

9. Extensibility

Future systems may define:

- Additional secondary emoji sources
- Additional tiered entity types

All such systems must conform to:

- Deterministic ordering
- Multiplicity preservation
- Mandatory tier display rule
- Non-authoritative behavior
- emoji.json resolution

----------------------------------------------------------------

10. Contract Authority

This contract defines the global Emoji Profile abstraction.

Any system implementing composite emoji identities must conform.
No system may override ordering or tier rules.
No system may bypass emoji.json resolution.
