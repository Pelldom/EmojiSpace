import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ActiveSituation:
    situation_id: str
    system_id: str
    scope: str  # "system" or "destination"
    target_id: Optional[str]
    remaining_days: int


@dataclass
class ActiveEvent:
    event_id: str
    event_family_id: Optional[str]
    system_id: str
    remaining_days: int


@dataclass
class ScheduledEvent:
    event_id: str
    system_id: str
    trigger_day: int


@dataclass
class WorldStateEngine:
    active_situations: dict[str, list[ActiveSituation]] = field(default_factory=dict)
    active_events: dict[str, list[ActiveEvent]] = field(default_factory=dict)
    scheduled_events: list[ScheduledEvent] = field(default_factory=list)
    situation_catalog: list[dict[str, Any]] = field(default_factory=list)

    def register_system(self, system_id: str) -> None:
        if system_id not in self.active_situations:
            self.active_situations[system_id] = []
        if system_id not in self.active_events:
            self.active_events[system_id] = []

    def get_active_situations(self, system_id: str) -> list[ActiveSituation]:
        self.register_system(system_id)
        return list(self.active_situations[system_id])

    def get_active_events(self, system_id: str) -> list[ActiveEvent]:
        self.register_system(system_id)
        return list(self.active_events[system_id])

    def add_situation(self, active_situation: ActiveSituation) -> None:
        self.register_system(active_situation.system_id)
        current = self.active_situations[active_situation.system_id]
        if len(current) >= 3:
            raise ValueError("Maximum 3 active situations per system exceeded.")
        current.append(active_situation)
        print(
            f"Situation added: {active_situation.situation_id} "
            f"system={active_situation.system_id} scope={active_situation.scope}"
        )

    def add_event(self, active_event: ActiveEvent) -> None:
        self.register_system(active_event.system_id)
        self.active_events[active_event.system_id].append(active_event)
        print(
            f"Event added: {active_event.event_id} "
            f"system={active_event.system_id}"
        )

    def schedule_event(self, scheduled_event: ScheduledEvent) -> None:
        self.register_system(scheduled_event.system_id)
        self.scheduled_events.append(scheduled_event)

    def load_situation_catalog(self, catalog_path: str | Path | None = None) -> None:
        path = Path(catalog_path) if catalog_path is not None else Path(__file__).resolve().parents[1] / "data" / "situations.json"
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        loaded: list[dict[str, Any]] = []
        for entry in payload:
            if not isinstance(entry, dict):
                continue
            loaded.append(
                {
                    "situation_id": entry.get("situation_id"),
                    "random_allowed": bool(entry.get("random_allowed", False)),
                    "event_only": bool(entry.get("event_only", False)),
                    "recovery_only": bool(entry.get("recovery_only", False)),
                    "allowed_scope": entry.get("allowed_scope"),
                    "duration_days": entry.get("duration_days"),
                }
            )
        self.situation_catalog = loaded

    def evaluate_situation_spawn(
        self,
        current_system_id: str,
        neighbor_system_ids: list[str],
        current_day: int,
        world_seed: int,
    ) -> None:
        # Evaluate only R=0,1 systems: current + direct neighbors provided by caller.
        eligible_systems: list[str] = []
        seen: set[str] = set()
        for system_id in [current_system_id, *neighbor_system_ids]:
            if system_id in seen:
                continue
            seen.add(system_id)
            eligible_systems.append(system_id)

        spawnable = [
            item
            for item in self.situation_catalog
            if bool(item.get("random_allowed"))
            and not bool(item.get("event_only"))
            and not bool(item.get("recovery_only"))
        ]

        if not spawnable:
            return

        for system_id in eligible_systems:
            self.register_system(system_id)
            if len(self.active_situations[system_id]) >= 3:
                continue

            rng_seed = _deterministic_seed(world_seed, system_id, current_day, "situation")
            rng = random.Random(rng_seed)
            if rng.random() >= 0.08:
                continue

            selected = rng.choice(spawnable)
            duration = selected.get("duration_days")
            remaining_days = int(duration) if isinstance(duration, int) else 3
            active = ActiveSituation(
                situation_id=str(selected.get("situation_id")),
                system_id=system_id,
                scope=str(selected.get("allowed_scope") or "system"),
                target_id=None,
                remaining_days=max(0, remaining_days),
            )
            self.add_situation(active)

    def decrement_durations(self) -> None:
        for system_id in sorted(self.active_situations.keys()):
            for entry in self.active_situations[system_id]:
                entry.remaining_days = max(0, entry.remaining_days - 1)

        for system_id in sorted(self.active_events.keys()):
            for entry in self.active_events[system_id]:
                entry.remaining_days = max(0, entry.remaining_days - 1)

    def resolve_expired(self) -> None:
        for system_id in sorted(self.active_situations.keys()):
            kept: list[ActiveSituation] = []
            for entry in self.active_situations[system_id]:
                if entry.remaining_days <= 0:
                    print(
                        f"Situation expired: {entry.situation_id} "
                        f"system={entry.system_id}"
                    )
                    continue
                kept.append(entry)
            self.active_situations[system_id] = kept

        for system_id in sorted(self.active_events.keys()):
            kept_events: list[ActiveEvent] = []
            for entry in self.active_events[system_id]:
                if entry.remaining_days <= 0:
                    print(
                        f"Event expired: {entry.event_id} "
                        f"system={entry.system_id}"
                    )
                    continue
                kept_events.append(entry)
            self.active_events[system_id] = kept_events


def _deterministic_seed(world_seed: int, system_id: str, current_day: int, channel: str) -> int:
    packed = f"{world_seed}|{system_id}|{current_day}|{channel}".encode("utf-8")
    return int(hashlib.sha256(packed).hexdigest(), 16)
