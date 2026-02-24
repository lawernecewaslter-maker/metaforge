from __future__ import annotations

import json
import time
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .analysis import evaluate_trade
from .metaforge_client import MetaForgeClient
from .models import ItemSide

client = MetaForgeClient()


class AppHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json({"status": "ok"})
            return

        if parsed.path == "/market/research-center":
            try:
                self._send_json(client.research_center_snapshot())
            except Exception as exc:  # noqa: BLE001
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_GATEWAY)
            return

        if parsed.path == "/market/live-updates":
            qs = parse_qs(parsed.query)
            interval = int(qs.get("interval_seconds", [30])[0])
            max_updates = int(qs.get("max_updates", [10])[0])
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            previous = None
            for _ in range(max_updates):
                snapshot = client.research_center_snapshot()
                update_type = "changed" if previous and previous != snapshot else "heartbeat"
                payload = {
                    "update_type": update_type,
                    "events_count": snapshot["events_count"],
                    "active_trials_count": snapshot["active_trials_count"],
                    "upcoming_trials_count": snapshot["upcoming_trials_count"],
                    "as_of_utc": snapshot["as_of_utc"],
                }
                self.wfile.write(f"data: {json.dumps(payload)}\\n\\n".encode("utf-8"))
                self.wfile.flush()
                previous = snapshot
                time.sleep(max(5, interval))
            return

        if parsed.path == "/openapi.json":
            self._send_json(
                {
                    "openapi": "3.1.0",
                    "info": {"title": "MetaForge ChatGPT Market App", "version": "1.0.0"},
                    "paths": {
                        "/market/research-center": {"get": {"summary": "Get live research snapshot"}},
                        "/market/live-updates": {"get": {"summary": "Stream live research updates"}},
                        "/market/trade-evaluation": {"post": {"summary": "Evaluate trade quality"}},
                    },
                }
            )
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/market/trade-evaluation":
            payload = self._read_json()
            giving = [ItemSide(**item) for item in payload.get("giving", [])]
            receiving = [ItemSide(**item) for item in payload.get("receiving", [])]
            result = evaluate_trade(giving, receiving)
            self._send_json(asdict(result))
            return

        self._send_json({"error": "Not found"}, status=404)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"MetaForge ChatGPT app running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
