class PlayerState:
    def __init__(self, start_system_id: str) -> None:
        self._location_system_id = start_system_id
        self._holdings: dict[str, int] = {}
        self._reputation: int = 0
        self._reputation_by_system: dict[str, int] = {}
        self._heat_by_system: dict[str, int] = {}
        self._licenses_by_system: dict[str, dict[str, bool]] = {}
        self._warrants_by_system: dict[str, bool] = {}
        self._fines_by_system: dict[str, int] = {}

    @property
    def location_system_id(self) -> str:
        return self._location_system_id

    def move_to(self, system_id: str) -> str:
        previous = self._location_system_id
        self._location_system_id = system_id
        return previous

    def buy(self, sku: str) -> None:
        self._holdings[sku] = self._holdings.get(sku, 0) + 1

    def can_sell(self, sku: str) -> bool:
        return self._holdings.get(sku, 0) > 0

    def sell(self, sku: str) -> bool:
        if not self.can_sell(sku):
            return False
        self._holdings[sku] = self._holdings.get(sku, 0) - 1
        return True

    def holdings_snapshot(self) -> dict[str, int]:
        return dict(self._holdings)

    def confiscate(self, sku: str, amount: int | None) -> int:
        if sku not in self._holdings or self._holdings[sku] <= 0:
            return 0
        if amount is None or amount < 0:
            confiscated = self._holdings[sku]
            self._holdings[sku] = 0
            return confiscated
        confiscated = min(self._holdings[sku], amount)
        self._holdings[sku] -= confiscated
        return confiscated

    def reputation(self) -> int:
        return self._reputation

    def adjust_reputation(self, delta: int) -> None:
        self._reputation += delta

    def get_reputation(self, system_id: str) -> int:
        return self._reputation_by_system.get(system_id, 50)

    def set_reputation(self, system_id: str, value: int) -> None:
        self._reputation_by_system[system_id] = max(1, min(100, value))

    def get_heat(self, system_id: str) -> int:
        return self._heat_by_system.get(system_id, 0)

    def set_heat(self, system_id: str, value: int) -> None:
        self._heat_by_system[system_id] = max(0, min(100, value))

    def has_warrant(self, system_id: str) -> bool:
        return self._warrants_by_system.get(system_id, False)

    def set_warrant(self, system_id: str, value: bool) -> None:
        self._warrants_by_system[system_id] = value

    def get_fines(self, system_id: str) -> int:
        return self._fines_by_system.get(system_id, 0)

    def add_fines(self, system_id: str, amount: int) -> None:
        if amount < 0:
            raise ValueError("Fines amount must be >= 0.")
        self._fines_by_system[system_id] = self.get_fines(system_id) + amount

    def pay_fines(self, system_id: str, amount: int) -> None:
        if amount < 0:
            raise ValueError("Payment amount must be >= 0.")
        remaining = max(0, self.get_fines(system_id) - amount)
        self._fines_by_system[system_id] = remaining

    def has_license(self, system_id: str, sku_or_category: str) -> bool:
        return self._licenses_by_system.get(system_id, {}).get(sku_or_category, False)

    def can_purchase_license(self, system_id: str) -> bool:
        reputation = self.get_reputation(system_id)
        return 81 <= reputation <= 100

    def license_summary_count(self, system_id: str) -> int:
        return len(self._licenses_by_system.get(system_id, {}))

    def profile_view(self) -> list[str]:
        lines: list[str] = []
        systems = set(self._reputation_by_system) | set(self._heat_by_system) | set(self._warrants_by_system)
        systems |= set(self._fines_by_system) | set(self._licenses_by_system)
        for system_id in sorted(systems):
            rep = self.get_reputation(system_id)
            heat = self.get_heat(system_id)
            warrant = self.has_warrant(system_id)
            fines = self.get_fines(system_id)
            licenses = self.license_summary_count(system_id)
            rep_band = _band_label(rep)
            heat_band = _band_label(max(1, heat))
            lines.append(
                f"{system_id} rep={rep}({rep_band}) heat={heat}({heat_band}) "
                f"warrant={warrant} fines={fines} licenses={licenses}"
            )
        return lines


def _band_label(value: int) -> str:
    if value <= 20:
        return "Very Low"
    if value <= 40:
        return "Low"
    if value <= 60:
        return "Neutral"
    if value <= 80:
        return "High"
    return "Very High"
