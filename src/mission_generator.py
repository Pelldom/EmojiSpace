import random
from typing import Any


def select_weighted_mission_type(
    *,
    eligible_missions: list[dict[str, Any]],
    rng: random.Random,
    world_state_engine: Any | None = None,
    system_id: str | None = None,
) -> tuple[str | None, dict[str, float]]:
    """
    Select one mission_type using weighted random selection.

    This function preserves baseline behavior when world_state_engine/system_id are
    not provided by using base weights only.
    """
    adjusted_weights = _compute_adjusted_weights(
        eligible_missions=eligible_missions,
        world_state_engine=world_state_engine,
        system_id=system_id,
    )
    weighted_items: list[tuple[str, float]] = []
    for mission in eligible_missions:
        mission_type_id = _mission_type_id(mission)
        if mission_type_id == "":
            continue
        weighted_items.append((mission_type_id, float(adjusted_weights.get(mission_type_id, 0.0))))
    selected = _weighted_pick(weighted_items, rng)
    return selected, adjusted_weights


def _compute_adjusted_weights(
    *,
    eligible_missions: list[dict[str, Any]],
    world_state_engine: Any | None = None,
    system_id: str | None = None,
) -> dict[str, float]:
    base_weights: dict[str, float] = {}
    entity_views: list[dict[str, Any]] = []
    for mission in eligible_missions:
        mission_type_id = _mission_type_id(mission)
        if mission_type_id == "":
            continue
        base_weight = float(mission.get("base_weight", 0.0))
        mission_tags = [tag for tag in mission.get("mission_tags", mission.get("tags", [])) if isinstance(tag, str)]
        base_weights[mission_type_id] = base_weight
        entity_views.append(
            {
                "entity_id": mission_type_id,
                "category_id": None,
                "tags": mission_tags,
            }
        )

    resolved_by_id: dict[str, dict[str, int]] = {}
    if world_state_engine is not None and system_id:
        resolved = world_state_engine.resolve_modifiers_for_entities(
            system_id=system_id,
            domain="missions",
            entity_views=entity_views,
        )
        resolved_by_id = resolved.get("resolved", {})

    adjusted: dict[str, float] = {}
    for mission_type_id, base_weight in base_weights.items():
        row = resolved_by_id.get(mission_type_id, {})
        # mission_weight_percent is Slice 9 mission weighting input.
        # spawn_weight_delta is accepted for compatibility with older mission entries.
        mission_weight_percent = int(row.get("mission_weight_percent", row.get("spawn_weight_delta", 0)))
        adjusted_weight = base_weight * (1.0 + (float(mission_weight_percent) / 100.0))
        adjusted[mission_type_id] = max(0.0, adjusted_weight)
    return adjusted


def _weighted_pick(weighted_items: list[tuple[str, float]], rng: random.Random) -> str | None:
    total = sum(weight for _, weight in weighted_items)
    if total <= 0:
        return None
    threshold = rng.random() * total
    running = 0.0
    for mission_type_id, weight in weighted_items:
        running += weight
        if threshold <= running:
            return mission_type_id
    return weighted_items[-1][0] if weighted_items else None


def _mission_type_id(mission: dict[str, Any]) -> str:
    value = mission.get("mission_type_id", mission.get("mission_type", ""))
    return str(value) if value is not None else ""
