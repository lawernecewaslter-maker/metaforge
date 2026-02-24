from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json


@dataclass
class BuildHistoryEntry:
    started_at: str
    finished_at: str
    status: str
    output_exe: str
    duration_seconds: float
    log_file: str


class BuildHistoryStore:
    def __init__(self, path: Path = Path("build_history.json")) -> None:
        self.path = path

    def append(self, entry: BuildHistoryEntry) -> None:
        existing = self.read_all()
        existing.append(asdict(entry))
        self.path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            backup = self.path.with_suffix(f".broken-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json")
            self.path.replace(backup)
            return []
