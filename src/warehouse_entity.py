from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class WarehouseOwnerType(str, Enum):
    SYSTEM = "system"
    FACTION = "faction"
    NPC = "npc"


@dataclass
class WarehouseEntity:
    # Identity and scope
    warehouse_id: str = ""
    system_id: str = ""
    destination_id: str = ""
    location_id: str | None = None

    # Ownership
    owner_type: WarehouseOwnerType = WarehouseOwnerType.SYSTEM
    owner_id: str = ""

    # Capacity and contents
    capacity: int = 0
    stored_goods: List[Dict[str, int]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "WarehouseEntity":
        state = cls()
        for key, value in payload.items():
            if key == "owner_type" and isinstance(value, str):
                state.owner_type = WarehouseOwnerType(value)
                continue
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "warehouse_id": self.warehouse_id,
            "system_id": self.system_id,
            "destination_id": self.destination_id,
            "location_id": self.location_id,
            "owner_type": self.owner_type.value,
            "owner_id": self.owner_id,
            "capacity": self.capacity,
            "stored_goods": list(self.stored_goods),
        }

    def add_goods(self, sku_id: str, quantity: int, logger=None, turn: int = 0) -> None:
        if quantity < 0:
            raise ValueError("Quantity must be >= 0.")
        self._adjust_goods(sku_id, quantity, logger=logger, turn=turn)

    def remove_goods(self, sku_id: str, quantity: int, logger=None, turn: int = 0) -> None:
        if quantity < 0:
            raise ValueError("Quantity must be >= 0.")
        self._adjust_goods(sku_id, -quantity, logger=logger, turn=turn)

    def adjust_goods(self, sku_id: str, delta: int, logger=None, turn: int = 0) -> None:
        self._adjust_goods(sku_id, delta, logger=logger, turn=turn)

    def _adjust_goods(self, sku_id: str, delta: int, logger=None, turn: int = 0) -> None:
        if not sku_id:
            raise ValueError("sku_id is required.")
        entry = next((item for item in self.stored_goods if item.get("sku_id") == sku_id), None)
        current = 0 if entry is None else entry.get("quantity", 0)
        new_value = current + delta
        if new_value < 0:
            raise ValueError("Quantity must be >= 0.")
        if entry is None:
            if new_value == 0:
                return
            entry = {"sku_id": sku_id, "quantity": new_value}
            self.stored_goods.append(entry)
        else:
            if new_value == 0:
                self.stored_goods = [item for item in self.stored_goods if item.get("sku_id") != sku_id]
            else:
                entry["quantity"] = new_value
        _log_state_change(logger, turn, f"stored_goods[{sku_id}]", new_value)


def _log_state_change(logger, turn: int, field: str, value: Any) -> None:
    if logger is None:
        return
    logger.log(turn=turn, action="warehouse_state_update", state_change=f"{field}={value}")
