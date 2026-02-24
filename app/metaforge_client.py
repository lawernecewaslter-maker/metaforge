from __future__ import annotations

from datetime import datetime, timezone
from json import loads
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://metaforge.app"


class MetaForgeClient:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def _get_json(self, path: str) -> dict[str, Any]:
        req = Request(f"{BASE_URL}{path}", headers={"User-Agent": "metaforge-chatgpt-app/1.0"})
        try:
            with urlopen(req, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                data = loads(payload)
                if not isinstance(data, dict):
                    raise ValueError(f"Unexpected payload type for {path}")
                return data
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"MetaForge request failed for {path}: {exc}") from exc

    def events_schedule(self) -> list[dict[str, Any]]:
        payload = self._get_json("/api/arc-raiders/events-schedule")
        return payload.get("data", [])

    def weekly_trials(self) -> list[dict[str, Any]]:
        payload = self._get_json("/api/arc-raiders/weekly-trials")
        return payload.get("data", [])

    def research_center_snapshot(self) -> dict[str, Any]:
        events = self.events_schedule()
        trials = self.weekly_trials()
        active_trials = [t for t in trials if t.get("is_active")]
        upcoming_trials = [t for t in trials if t.get("upcoming")]
        return {
            "source": f"{BASE_URL}/arc-raiders/market",
            "api_endpoints": [
                f"{BASE_URL}/api/arc-raiders/events-schedule",
                f"{BASE_URL}/api/arc-raiders/weekly-trials",
            ],
            "as_of_utc": datetime.now(timezone.utc).isoformat(),
            "events_count": len(events),
            "active_trials_count": len(active_trials),
            "upcoming_trials_count": len(upcoming_trials),
            "events": events,
            "active_trials": active_trials,
            "upcoming_trials": upcoming_trials,
        }
