from dataclasses import dataclass, field
from typing import Dict, List

from npc_entity import NPCEntity, NPCPersistenceTier


@dataclass
class NPCRegistry:
    _by_id: Dict[str, NPCEntity] = field(default_factory=dict)
    _by_location: Dict[str, List[str]] = field(default_factory=dict)

    def add(self, npc: NPCEntity, logger=None, turn: int = 0) -> None:
        if npc.persistence_tier == NPCPersistenceTier.TIER_1:
            return
        self._by_id[npc.npc_id] = npc
        if npc.current_location_id is not None:
            self._by_location.setdefault(npc.current_location_id, [])
            if npc.npc_id not in self._by_location[npc.current_location_id]:
                self._by_location[npc.current_location_id].append(npc.npc_id)
        _log_registry_change(logger, turn, "add", npc.npc_id)

    def remove(self, npc_id: str, logger=None, turn: int = 0) -> None:
        npc = self._by_id.pop(npc_id, None)
        if npc is None:
            return
        if npc.current_location_id is not None:
            ids = self._by_location.get(npc.current_location_id, [])
            self._by_location[npc.current_location_id] = [value for value in ids if value != npc_id]
        _log_registry_change(logger, turn, "remove", npc_id)

    def update(self, npc: NPCEntity, logger=None, turn: int = 0) -> None:
        if npc.persistence_tier == NPCPersistenceTier.TIER_1:
            return
        self.remove(npc.npc_id, logger=logger, turn=turn)
        self.add(npc, logger=logger, turn=turn)

    def get(self, npc_id: str) -> NPCEntity | None:
        return self._by_id.get(npc_id)

    def list_by_location(self, location_id: str) -> List[NPCEntity]:
        ids = self._by_location.get(location_id, [])
        return [self._by_id[npc_id] for npc_id in ids if npc_id in self._by_id]

    def to_dict(self) -> Dict[str, dict]:
        return {npc_id: npc.to_dict() for npc_id, npc in self._by_id.items()}

    @classmethod
    def from_dict(cls, payload: Dict[str, dict]) -> "NPCRegistry":
        registry = cls()
        for npc_id, npc_payload in payload.items():
            npc = NPCEntity.from_dict(npc_payload)
            npc.npc_id = npc_id
            registry.add(npc)
        return registry


def _log_registry_change(logger, turn: int, action: str, npc_id: str) -> None:
    if logger is None:
        return
    logger.log(turn=turn, action="npc_registry", state_change=f"{action} npc_id={npc_id}")
