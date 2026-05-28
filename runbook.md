# Runbook

## Service

Real-Time Fraud Scoring API

## Health Check

```bash
curl http://localhost:8000/health
```

Expected: HTTP `200` and `"status": "ok"`.

## Start Locally

```bash
make run
```

## Start With Docker

```bash
docker compose up --build
```

## Logs

Logs are JSON and include:

- `request_id`
- `method`
- `path`
- `status_code`
- `latency_ms`

## Common Incident: Elevated 422 Rate

Impact: checkout calls are rejected before scoring because payload validation fails.

Actions:

1. Check logs for paths returning `422`.
2. Inspect FastAPI validation response bodies from failing clients.
3. Compare client payloads against `TransactionRequest` in `app/schemas.py`.
4. Confirm whether a recent schema change broke compatibility.
5. Coordinate with checkout engineers before relaxing or changing validation.

## TODO

Add one more production incident scenario after you practice operating the API.
