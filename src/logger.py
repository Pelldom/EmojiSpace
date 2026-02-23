from dataclasses import dataclass
from pathlib import Path

# PHASE 7.6 AUDIT NOTES
# - Current capabilities (pre-audit): formatted line logging via print only.
# - Existing gaps: no file sink, no runtime toggle, no error-safe file handling.
# - Integration status before this pass: engine events were accumulated in step results
#   but not routed into Logger, and Logger was not used as an engine-level sink.


@dataclass(frozen=True)
class LogEntry:
    turn: int
    version: str
    action: str
    state_change: str

    def format_line(self) -> str:
        return f"[v{self.version}][turn {self.turn}] action={self.action} change={self.state_change}"


class Logger:
    def __init__(self, version: str) -> None:
        self._version = version
        self._file_enabled = False
        self._file_path: str | None = None

    @property
    def version(self) -> str:
        return self._version

    def configure_file_logging(self, *, enabled: bool, log_path: str | None = None, truncate: bool = False) -> str | None:
        self._file_enabled = bool(enabled)
        if not self._file_enabled:
            self._file_path = None
            return None
        if not isinstance(log_path, str) or not log_path:
            return None
        self._file_path = log_path
        try:
            Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)
            if truncate:
                with open(self._file_path, "w", encoding="ascii", errors="replace"):
                    pass
            else:
                with open(self._file_path, "a", encoding="ascii", errors="replace"):
                    pass
        except Exception:  # noqa: BLE001
            self._file_enabled = False
            self._file_path = None
            return None
        return self._file_path

    def log(self, turn: int, action: str, state_change: str) -> None:
        entry = LogEntry(
            turn=turn,
            version=self._version,
            action=action,
            state_change=state_change,
        )
        line = entry.format_line()
        print(line)
        if not self._file_enabled or not isinstance(self._file_path, str):
            return
        try:
            with open(self._file_path, "a", encoding="ascii", errors="replace") as handle:
                handle.write(line)
                handle.write("\n")
        except Exception:  # noqa: BLE001
            return
