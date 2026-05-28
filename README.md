# Real-Time Fraud Scoring API with FastAPI

Production-style FastAPI API for deterministic BNPL checkout fraud scoring. It accepts synthetic checkout payloads and returns a risk score, decision, reason codes, score contributions, policy version, timestamp, and request ID.

## Endpoints

- `GET /health` checks service readiness.
- `POST /score` scores one transaction.
- `POST /batch-score` scores 1 to 100 transactions.
- `GET /explain` explains thresholds and feature weights.

## Local Setup

```bash
make install
make run
```

This creates a local `.venv` virtual environment and installs the project dependencies there.

Open API docs at `http://localhost:8000/docs`.

## Example Request

```bash
curl -s http://localhost:8000/score \
  -H "content-type: application/json" \
  -H "x-request-id: demo-req-1" \
  -d '{
    "transaction_id": "txn_1001",
    "customer_id": "cus_778",
    "order_amount": 129.99,
    "merchant_id": "mer_42",
    "merchant_category": "electronics",
    "merchant_risk_score": 45,
    "customer_tenure_days": 120,
    "number_previous_orders": 6,
    "previous_failed_payments": 0,
    "device_risk_score": 20,
    "email_domain_risk": 15,
    "payment_method": "card",
    "country": "US",
    "hour_of_day": 14
  }'
```

## Tests

```bash
make test
```

## Docker

```bash
docker compose up --build
```

## Configuration

Environment variables use the `FRAUD_API_` prefix.

- `FRAUD_API_ACCEPT_THRESHOLD`, default `35`
- `FRAUD_API_REJECT_THRESHOLD`, default `70`
- `FRAUD_API_MODEL_OR_POLICY_VERSION`, default `policy-v1.0.0`
- `FRAUD_API_LOG_LEVEL`, default `INFO`

## Learning Order

Open files in this order:

1. `app/main.py`
2. `app/schemas.py`
3. `app/scoring.py`
4. `app/config.py`
5. `tests/`
