# MetaForge ChatGPT Market App

This repository now includes a runnable **ChatGPT-ready market research app** for MetaForge ARC Raiders.

## Live API sources used

Discovered from `https://metaforge.app/arc-raiders/market`:
- `https://metaforge.app/api/arc-raiders/events-schedule`
- `https://metaforge.app/api/arc-raiders/weekly-trials`

These power the app's research center and live update stream.

## Features

- Research-center snapshot endpoint.
- Live updates via SSE for continuous monitoring.
- Trade evaluation endpoint aligned to your trader-style prompt (value delta + liquidity risk logic).
- OpenAPI schema endpoint to plug into ChatGPT Actions/App setup.

## Run

```bash
python app/main.py
```

Then use:
- `GET http://localhost:8000/market/research-center`
- `GET http://localhost:8000/market/live-updates?interval_seconds=30&max_updates=10`
- `POST http://localhost:8000/market/trade-evaluation`
- `GET http://localhost:8000/openapi.json`

## ChatGPT app wiring

1. Create a ChatGPT app/action.
2. Set schema URL to `http://<your-host>:8000/openapi.json`.
3. Use `chatgpt/app-config.json` as starter metadata.
