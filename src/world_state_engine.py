from dataclasses import dataclass, field
from typing import Optional


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
