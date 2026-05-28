# Real-Time Fraud Scoring API with FastAPI

Production-style FastAPI API for deterministic BNPL checkout fraud scoring.

This project is designed for junior data science learners who want to practice how a scoring idea becomes a real API. The service accepts synthetic checkout transactions and returns:

- a `risk_score` from 0 to 100
- a `decision`: `accept`, `review`, or `reject`
- `reason_codes` explaining the main risk drivers
- `score_contributions` showing how each feature affected the score
- a policy version, timestamp, and request ID

The scoring logic is deterministic. That means the same input always gives the same output, which makes it easier to test, debug, and explain.

## Recommended Learning Path

Start with the Python environment first. This helps you understand the API, the request and response schemas, and the scoring rules before adding Docker.

After the API works locally with Python, use Docker Compose as the next topic. 

## Python Environment Setup

Use this path first if you are learning the project or editing the code.

```bash
make install
make run
```

This creates a local `.venv` virtual environment and installs the project dependencies there.

Then open:

- API health check: `http://localhost:8000/health`
- Interactive API docs: `http://localhost:8000/docs`

Stop the server with `Ctrl+C`.

## Endpoints

- `GET /health` checks service readiness.
- `POST /score` scores one transaction.
- `POST /batch-score` scores 1 to 100 transactions.
- `GET /explain` explains thresholds and feature weights.

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

Expected shape of the response, abbreviated:

```json
{
  "transaction_id": "txn_1001",
  "request_id": "demo-req-1",
  "risk_score": 24,
  "decision": "accept",
  "reason_codes": [
    "MERCHANT_HISTORICAL_RISK",
    "DEVICE_TRUST_AND_ANOMALY_SIGNALS",
    "EMAIL_DOMAIN_RISK",
    "HIGHER_RISK_MERCHANT_CATEGORY"
  ],
  "score_contributions": [
    {
      "feature": "merchant_risk_score",
      "value": 45,
      "points": 11,
      "reason": "Merchant historical risk"
    }
  ],
  "model_or_policy_version": "policy-v1.0.0",
  "timestamp": "2026-05-28T14:28:00Z"
}
```

The exact score and reason codes depend on the scoring rules in `app/scoring.py`.

## Batch Scoring Example

```bash
curl -s http://localhost:8000/batch-score \
  -H "content-type: application/json" \
  -d '{
    "transactions": [
      {
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
      },
      {
        "transaction_id": "txn_1002",
        "customer_id": "cus_901",
        "order_amount": 899.50,
        "merchant_id": "mer_88",
        "merchant_category": "gaming",
        "merchant_risk_score": 72,
        "customer_tenure_days": 12,
        "number_previous_orders": 1,
        "previous_failed_payments": 1,
        "device_risk_score": 65,
        "email_domain_risk": 40,
        "payment_method": "digital_wallet",
        "country": "US",
        "hour_of_day": 23
      },
      {
        "transaction_id": "txn_1003",
        "customer_id": "cus_404",
        "order_amount": 1499.00,
        "merchant_id": "mer_99",
        "merchant_category": "luxury",
        "merchant_risk_score": 95,
        "customer_tenure_days": 2,
        "number_previous_orders": 0,
        "previous_failed_payments": 4,
        "device_risk_score": 90,
        "email_domain_risk": 85,
        "payment_method": "gift_card",
        "country": "NG",
        "hour_of_day": 2
      }
    ]
  }'
```

This sends three transactions in one request. The response returns one scored result per transaction, so learners can compare a lower-risk checkout, a review-like checkout, and a high-risk checkout side by side.

## Tests

```bash
make test
```

## Make Commands

```bash
make help
make install
make run
make test
make lint
make docker-up
make docker-logs
make docker-down
make sudo-docker-up
```

## Configuration

Runtime defaults are defined in `config.yaml`.

```yaml
app_name: Real-Time Fraud Scoring API
environment: local
model_or_policy_version: policy-v1.0.0
accept_threshold: 35
reject_threshold: 70
log_level: INFO
```

The loader is defined in `app/config.py`. The `Settings` class uses Pydantic Settings and reads values in this order:

1. values passed directly in Python, mostly useful in tests
2. real environment variables
3. local `.env` file values
4. `config.yaml`
5. Python field defaults

For example, this field in `app/config.py`:

```python
accept_threshold: int = Field(default=35, ge=0, le=100)
```

can be overridden with:

```bash
FRAUD_API_ACCEPT_THRESHOLD=40
```

This means `config.yaml` is the readable baseline, and environment variables are the production-style override mechanism.

Main environment variable overrides:

- `FRAUD_API_ACCEPT_THRESHOLD`, default `35`
- `FRAUD_API_REJECT_THRESHOLD`, default `70`
- `FRAUD_API_MODEL_OR_POLICY_VERSION`, default `policy-v1.0.0`
- `FRAUD_API_LOG_LEVEL`, default `INFO`
- `FRAUD_API_ENVIRONMENT`, default `local`

For local development, edit `config.yaml` if you want to change the normal project defaults.

For one-off experiments, export variables in your terminal:

```bash
FRAUD_API_ACCEPT_THRESHOLD=40 make run
```

For machine-specific local overrides, create a local `.env` file:

```bash
FRAUD_API_ENVIRONMENT=local
FRAUD_API_ACCEPT_THRESHOLD=40
FRAUD_API_REJECT_THRESHOLD=75
FRAUD_API_LOG_LEVEL=INFO
```

Do not commit `.env`; it is ignored by Git.

Docker Compose defines container-specific values in `docker-compose.yml`:

- `FRAUD_API_ENVIRONMENT=docker`
- `FRAUD_API_ACCEPT_THRESHOLD=35`
- `FRAUD_API_REJECT_THRESHOLD=70`

Those Docker Compose values override `config.yaml` inside the container.

Decision logic:

- scores below the accept threshold are accepted
- scores from the accept threshold up to the reject threshold go to review
- scores at or above the reject threshold are rejected

## Project Structure

```text
app/
  main.py            FastAPI routes and error handling
  schemas.py         Request and response data models
  scoring.py         Fraud scoring rules
  config.py          Environment-based settings
  middleware.py      Request ID handling
  logging_config.py  JSON logging setup
tests/               Unit and integration tests
Dockerfile           Container image definition
docker-compose.yml   Local Docker Compose service
config.yaml          Readable runtime defaults
Makefile             Short commands for common tasks
```

## Learning Order

Open files in this order:

1. `app/main.py`
2. `app/schemas.py`
3. `app/scoring.py`
4. `app/config.py`
5. `tests/`

Suggested learning questions:

- What fields does one transaction need?
- Which fields increase the risk score?
- Where are invalid requests rejected?
- How does the API decide between `accept`, `review`, and `reject`?
- Which tests prove the API works?

## Docker Compose

Use this after the API works with the Python environment. Docker Compose builds the app into a container and runs it using the settings in `docker-compose.yml`.

```bash
docker compose up --build
```

Then open:

- API health check: `http://localhost:8000/health`
- Interactive API docs: `http://localhost:8000/docs`

Stop the server with `Ctrl+C`.

To run it in the background:

```bash
docker compose up --build -d
```

To stop and remove the container:

```bash
docker compose down
```

You can also use Make:

```bash
make docker-up
make docker-down
```

If Docker gives a permission error, use `sudo`:

```bash
sudo docker compose up --build
```

Or use the Make helper:

```bash
make sudo-docker-up
```

For a permanent fix, add your user to the Docker group and open a new terminal:

```bash
sudo usermod -aG docker "$USER"
```

After opening a new terminal, verify that Docker works without `sudo`:

```bash
docker ps
docker compose up --build
```

If you see `unknown flag: --build`, your machine probably has Docker installed without the Compose v2 plugin. On Ubuntu, install it with:

```bash
sudo apt install docker-compose-v2
```

The warning `Docker Compose is configured to build using Bake, but buildx isn't installed` is not fatal. The image can still build successfully.
