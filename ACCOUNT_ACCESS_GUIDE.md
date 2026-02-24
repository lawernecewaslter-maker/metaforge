# Account Access Guide (Trades + Inventory)

If you want this assistant to evaluate **your exact trades/inventory**, connect it using official and secure methods.

## Recommended integration order

1. **Official API/OAuth first** (best)
2. **Export-based sync** (CSV/JSON uploads)
3. **Read-only browser automation** only if no API exists

## 1) Best option: Official API + OAuth

Use provider-issued OAuth so users grant access without sharing passwords.

Required scopes (read-only):
- `inventory:read`
- `trades:read`
- `listings:read`

Flow:
1. User clicks **Connect Account** in your app.
2. User logs in on the provider site.
3. Provider returns access token to your backend.
4. Backend stores encrypted refresh token.
5. App calls provider API and merges into trade evaluator.

## 2) Safe fallback: Export upload

If no API is available:
- Let users upload inventory/trade exports.
- Parse and normalize into local schema.
- Run evaluation without account credential storage.

Pros: high safety, low compliance burden.

## 3) Last resort: read-only automation

Only consider if terms allow it.
- Never collect account password in your app.
- Use user-run local agent/session.
- Keep extraction read-only.

## Security requirements

- Never request raw passwords in your app UI.
- Encrypt tokens at rest.
- Rotate keys regularly.
- Separate prod/dev credentials.
- Log access to account-linked operations.
- Provide account disconnect + token revoke.

## Minimal schema for personal evaluation

Store these fields:
- `account_id`
- `item_id`
- `item_name`
- `quantity`
- `avg_cost_basis`
- `current_floor_price`
- `open_trades[]`
- `recent_fills[]`

Then augment evaluator with:
- portfolio exposure check
- max loss constraints
- liquidity filter per held item

## What to build next

1. Add a `Connect Account` button in desktop UI.
2. Add backend endpoint `/account/sync`.
3. Add `/trade/evaluate-personal` using holdings + open trades.
4. Add alert rules aware of your current positions.
