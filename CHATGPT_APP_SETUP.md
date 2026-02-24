# Turn This Project into a ChatGPT App (Actions)

This guide shows exactly how to wire this repository into a ChatGPT app using **Actions**.

## 1) Run the API locally

From repo root:

```bash
python app/main.py
```

Your API is now on:
- `http://localhost:8000/health`
- `http://localhost:8000/openapi.json`

## 2) Verify endpoints work before ChatGPT setup

In another terminal:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/openapi.json
curl -s http://localhost:8000/market/research-center
```

If your environment blocks outbound calls to MetaForge, `/market/research-center` may return an error until deployed on a host with open egress.

## 3) Expose your API over public HTTPS

ChatGPT Actions require a reachable HTTPS URL.

Options:
- Deploy on a cloud VM/container (recommended)
- Use a temporary tunnel for testing (e.g., ngrok/cloudflared)

Example final base URL:
- `https://your-domain.example.com`

Then your schema URL becomes:
- `https://your-domain.example.com/openapi.json`

## 4) Create the ChatGPT app and attach the Action

1. Open ChatGPT and create a new app/GPT.
2. Go to **Actions**.
3. Choose **Import from URL**.
4. Paste your schema URL:
   - `https://your-domain.example.com/openapi.json`
5. Save.

Your app now gets these callable actions:
- `GET /market/research-center`
- `GET /market/live-updates`
- `POST /market/trade-evaluation`

## 5) Add behavior/instructions to your app

Use your trade logic prompt (or `TRADE_PLAYSTYLE_PROMPTS.md`) in the GPT instructions.

Recommended instruction snippet:
- Always fetch `/market/research-center` before giving market recommendations.
- Use `/market/trade-evaluation` for explicit ACCEPT/HOLD/DECLINE decisions.
- Use `/market/live-updates` when user requests monitoring/alerts.

## 6) Production checklist

- Add auth in front of the API (API key or OAuth proxy).
- Add request logging and rate limits.
- Add retry/backoff around MetaForge upstream calls.
- Add caching for research-center snapshots (15-60s TTL).
- Add monitoring for API uptime and error rate.

## 7) Quick troubleshooting

- **Action import fails**: ensure `openapi.json` is publicly reachable via HTTPS.
- **Calls time out**: host likely cannot reach `metaforge.app`; fix outbound network rules.
- **Empty/limited data**: upstream endpoint may be rate-limited or changed.

## 8) Optional: make OpenAPI richer

Current `openapi.json` is minimal. You can improve schema details (request/response models) to help ChatGPT call actions more reliably.
