class PlayerState:
    def __init__(self, start_system_id: str) -> None:
        self._location_system_id = start_system_id
        self._holdings: dict[str, int] = {}

    @property
    def location_system_id(self) -> str:
        return self._location_system_id

    def move_to(self, system_id: str) -> str:
        previous = self._location_system_id
        self._location_system_id = system_id
        return previous

    def buy(self, good_id: str) -> None:
        self._holdings[good_id] = self._holdings.get(good_id, 0) + 1

    def can_sell(self, good_id: str) -> bool:
        return self._holdings.get(good_id, 0) > 0

    def sell(self, good_id: str) -> bool:
        if not self.can_sell(good_id):
            return False
        self._holdings[good_id] = self._holdings.get(good_id, 0) - 1
        return True

    def holdings_snapshot(self) -> dict[str, int]:
        return dict(self._holdings)
