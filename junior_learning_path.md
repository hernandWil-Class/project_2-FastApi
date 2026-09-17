# Junior Learning Path

This is a repo-wide learning path for a junior data scientist who wants to
become comfortable enough with FastAPI, testing, Docker, and production API
thinking.

The goal is not to memorize the files. The goal is to understand how one scoring
idea becomes a usable, testable, observable API.

## Learning Outcomes

By the end, you should be able to:

- explain the request path from `curl` to FastAPI to Pydantic to scoring to JSON
- explain common HTTP status codes: `200`, `400`, `404`, `405`, `422`, `500`, and
  when this project does or does not use them
- make a small change in every important file without feeling lost
- add a new request field, scoring rule, response explanation, tests, config, and
  documentation
- run the API locally, with tests, and with Docker Compose

## Mental Model Of The API

For `POST /score`, the lifecycle is:

1. A client sends JSON to the API.
2. `RequestContextMiddleware` reads or creates an `x-request-id`.
3. FastAPI matches the route in `app/main.py`.
4. Pydantic validates the body against `TransactionRequest` in `app/schemas.py`.
5. The route calls `score_transaction()` in `app/scoring.py`.
6. The score is converted into `accept`, `review`, or `reject`.
7. FastAPI validates the response model and serializes JSON.
8. Middleware adds the request ID header and writes a JSON log.
9. Tests verify the behavior from several levels: function, API, config, and
   async HTTP integration.

## HTTP Status Code Field Guide

You must be comfortable with status codes before changing API code.

| Code | Meaning | How to see it in this project | Interview-level explanation |
| --- | --- | --- | --- |
| `200 OK` | The request succeeded and returned a body. | `GET /health`, `GET /explain`, valid `POST /score`, valid `POST /batch-score`. | Normal success for reads and scoring calls. |
| `201 Created` | A new resource was created. | Not currently used. |
| `204 No Content` | Success with no response body. | Not currently used. | Useful for deletes where the client needs no JSON. |
| `400 Bad Request` | The client sent a request the API chooses to reject as malformed or semantically bad. | Not currently used directly. | FastAPI/Pydantic validation failures usually become `422` here. |
| `401 Unauthorized` | Authentication is missing or invalid. | Not currently used. | This project has no auth yet. A real checkout API usually would. |
| `403 Forbidden` | Authentication worked, but the caller is not allowed. | Not currently used. | Useful when clients have roles or scopes. |
| `404 Not Found` | The route path does not exist. | Try `GET /missing-route`. | The API router could not match the URL. |
| `405 Method Not Allowed` | The path exists, but not for that HTTP method. | Try `GET /score`. | `/score` exists, but it only accepts `POST`. |
| `409 Conflict` | The request conflicts with current state. | Not currently used. | Could be used if duplicate transaction IDs were persisted. |
| `422 Unprocessable Content` | The route matched, but the JSON body failed validation. | Send negative `order_amount`, `hour_of_day: 99`, or `payment_method: "cash"`. | Pydantic protected the scoring code from bad input. |
| `500 Internal Server Error` | The server crashed or hit an unexpected bug. | Do not force this in normal learning; understand it from the runbook and logs. | This is the API owner failing, not the client's normal validation error. |
| `503 Service Unavailable` | The service is temporarily not ready. | Not currently used. | Often used for dependency or readiness failures in production. |

## Baseline Setup

Run the project before editing it:

```bash
make help
make install
make test
make run
```

Open:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`
- `http://localhost:8000/explain`

Then stop the server with `Ctrl+C`.

## How To Do The Exercises Slowly

Use this rhythm for every exercise:

1. Read the current behavior before editing.
2. Make one small change in one file.
3. Run the smallest useful test command.
4. Check the response, assertion, or log output.
5. Mark the item in `exercises.md` only after you can explain what changed.

Do not try to complete several exercises at the same time. If a test fails, fix
that one failure before moving to the next task.

### Baseline Walkthrough

Goal: prove the project works before you change it.

1. Open `Makefile`.
2. Find the targets named `help`, `install`, `test`, and `run`.
3. Run:

```bash
make help
```

4. Verify that the output lists the common project commands.
5. Run:

```bash
make install
make test
```

6. Verify that all tests pass.
7. Start the API:

```bash
make run
```

8. In another terminal, verify the API:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/explain
```

9. Open `http://localhost:8000/docs` in a browser.
10. Stop the server with `Ctrl+C`.
11. In `exercises.md`, check only the baseline items you actually completed.

### App Tour Before Your First Edit

Goal: understand the shape of the app before you change it.

Read these files in this order. Do not edit anything yet.

1. Open `app/__init__.py`.
2. Notice that it only has a docstring:

```python
"""Real-time fraud scoring API package."""
```

This file tells Python that `app/` is an importable package. That is why code can
write imports like `from app.config import get_settings`.

3. Open `app/config.py`.
4. Find the `Settings` class.

This file owns runtime configuration: app name, app version, app description,
thresholds, environment, policy version, and log level. The app should read
these values from settings instead of hard-coding them in route code.

Important ideas in this file:

- `class Settings(BaseSettings)`: creates a settings object using Pydantic
  Settings.
- `Field(default=35, ge=0, le=100)`: gives a default value and validation rules.
- `env_prefix="FRAUD_API_"`: means an environment variable such as
  `FRAUD_API_ACCEPT_THRESHOLD` can override `accept_threshold`.
- `@lru_cache`: remembers the result of `get_settings()` so the app does not
  rebuild settings on every request.

5. Open `app/schemas.py`.
6. Find `TransactionRequest`.

This file owns the API contract. A contract means: "this is the shape of JSON the
client must send, and this is the shape of JSON the API will return."

Important ideas in this file:

- `BaseModel`: tells Pydantic this class is a data model.
- `Annotated[int, Field(ge=0, le=100)]`: means the value must be an integer from
  `0` to `100`.
- `StrEnum`: creates string choices like `"accept"`, `"review"`, and `"reject"`.
- `@field_validator("country")`: runs custom validation for one field.
- `model_config = ConfigDict(...)`: adds example data for OpenAPI docs.

When invalid JSON arrives, FastAPI asks Pydantic to validate it against these
models. If validation fails, the route function does not run and the API returns
`422`.

7. Open `app/scoring.py`.
8. Find `score_transaction()`.

This file owns business logic. It decides how risk points are added and how a
score becomes `accept`, `review`, or `reject`.

Important ideas in this file:

- `@dataclass(frozen=True)`: creates a small immutable result object.
- `score_transaction(transaction, settings)`: receives already-validated input.
- `contributions`: a list of reasons that explain the score.
- `_add(...)`: helper function that appends one score contribution.
- `_decision_for_score(...)`: converts the numeric score into a decision.
- `scoring_explanation(...)`: powers the `/explain` endpoint.

Scoring stays outside `app/main.py` so it can be unit-tested without HTTP.

9. Open `app/main.py`.
10. Find this block:

```python
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)
```

This file owns the HTTP layer: routes, request handling, response models, and
validation error formatting.

Important ideas in this file:

- `FastAPI(...)`: creates the web application object.
- `@app.get("/health")`: registers a function as the handler for `GET /health`.
- `@app.post("/score", response_model=ScoreResponse)`: registers a `POST` route
  and tells FastAPI to validate the response shape.
- `async def`: defines an asynchronous function. FastAPI supports async route
  functions so the server can handle many requests efficiently.
- `payload: TransactionRequest`: tells FastAPI to parse the request JSON into a
  validated Pydantic model.
- `request: Request`: gives the route access to request metadata, such as
  `request.state.request_id`.
- `-> ScoreResponse`: documents and type-checks what the function returns.

Decorators are the lines that start with `@`. A decorator wraps or registers the
function below it. In this app, `@app.get(...)` and `@app.post(...)` do not call
the route immediately. They tell FastAPI: "when a request with this path and
method arrives, call this function."

11. Open `app/middleware.py`.
12. Find `RequestContextMiddleware`.

Middleware runs around every HTTP request. This middleware reads an incoming
`x-request-id` header or creates a new one, stores it on `request.state`, adds it
to the response headers, and logs the completed request.

Important ideas in this file:

- `async def __call__(...)`: lets the middleware behave like a callable ASGI app.
- `await self.app(...)`: passes the request to the next layer of the app.
- `send_wrapper(...)`: intercepts the response start message so the middleware
  can add the `x-request-id` response header.
- `try` / `finally`: makes sure the request gets logged even if something fails.

13. Open `app/logging_config.py`.
14. Find `configure_logging()`.

This file controls log formatting. It configures Python logging to write
structured JSON logs to standard output. In production, structured logs are
easier to search and filter than plain text.

Important ideas in this file:

- `logging.getLogger()`: gets the root logger.
- `root.handlers.clear()`: avoids duplicate handlers if logging is configured
  more than once.
- `jsonlogger.JsonFormatter(...)`: formats logs as JSON with fields like
  `request_id`, `method`, `path`, `status_code`, and `latency_ms`.

### Add Your First Route: `GET /version`

Goal: make one tiny API change and protect it with a test.

1. Open `app/main.py`.
2. Find the existing `health()` route.
3. Directly below `health()`, add this route:

```python
@app.get("/version")
async def version() -> dict[str, str]:
    return {"model_or_policy_version": settings.model_or_policy_version}
```

4. Open `tests/test_api.py`.
5. Add this test near `test_health_endpoint`:

```python
def test_version_endpoint(client):
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json()["model_or_policy_version"] == "policy-v1.0.0"
```

6. Run only the API tests:

```bash
pytest tests/test_api.py -q
```

7. Verify that the new test passes.
8. Optional manual check while the server is running:

```bash
curl -s http://localhost:8000/version
```

9. You are done when `/version` returns the policy version and no existing API
   tests broke.

### Add `404` And `405` Tests

Goal: understand FastAPI route matching.

1. Open `tests/test_api.py`.
2. Add this test for a path that does not exist:

```python
def test_unknown_route_returns_404(client):
    response = client.get("/missing-route")

    assert response.status_code == 404
```

3. Add this test for a real path called with the wrong HTTP method:

```python
def test_score_route_rejects_get_method(client):
    response = client.get("/score")

    assert response.status_code == 405
```

4. Run:

```bash
pytest tests/test_api.py -q
```

5. Verify both tests pass.
6. Explain the difference in your own words:
   - `404`: no route matched the path.
   - `405`: the path exists, but that method is not allowed.

### Add A New `422` Validation Test

Goal: see Pydantic reject bad input before scoring runs.

1. Open `tests/test_api.py`.
2. Find `test_score_endpoint_rejects_invalid_input`.
3. Add one new invalid case to the parametrized list, for example:

```python
("previous_failed_payments", -1),
```

4. Open `app/schemas.py`.
5. Find this field in `TransactionRequest`:

```python
previous_failed_payments: Annotated[int, Field(ge=0, le=10_000)]
```

6. Notice that `ge=0` is the rule that rejects `-1`.
7. Run:

```bash
pytest tests/test_api.py -q
```

8. Verify the invalid request returns `422`.
9. You are done when you can point to the exact schema field that caused the
   validation failure.

### Tighten Country Validation

Goal: add one small schema rule.

1. Open `app/schemas.py`.
2. Find `normalize_country()`.
3. Replace the TODO body with this:

```python
normalized = value.upper()
supported_countries = {"US", "CA", "GB", "BR", "NG", "PK", "RU", "VN"}
if normalized not in supported_countries:
    raise ValueError("country must be a supported two-letter country code")
return normalized
```

4. Open `tests/test_api.py`.
5. Add a passing normalization test:

```python
def test_score_endpoint_normalizes_country(client, valid_payload):
    response = client.post("/score", json={**valid_payload, "country": "us"})

    assert response.status_code == 200
```

6. Add a failing country test:

```python
def test_score_endpoint_rejects_unsupported_country(client, valid_payload):
    response = client.post("/score", json={**valid_payload, "country": "zz"})

    assert response.status_code == 422
```

7. Run:

```bash
pytest tests/test_api.py -q
```

8. Verify both tests pass.
9. If an existing test fails because it used another country, update that test
   payload to one of the supported country codes.

### Add A Reusable High-Risk Fixture

Goal: avoid copying the same high-risk payload into many tests.

1. Open `tests/conftest.py`.
2. Below `valid_payload()`, add:

```python
@pytest.fixture
def high_risk_payload(valid_payload) -> dict[str, object]:
    return {
        **valid_payload,
        "order_amount": 1_500,
        "merchant_category": "electronics",
        "merchant_risk_score": 95,
        "customer_tenure_days": 2,
        "number_previous_orders": 3,
        "previous_failed_payments": 3,
        "device_risk_score": 98,
        "email_domain_risk": 90,
        "payment_method": "gift_card",
        "country": "NG",
        "hour_of_day": 2,
    }
```

3. Open `tests/test_scoring.py`.
4. Change `test_high_risk_transaction_is_rejected` so it accepts the fixture:

```python
def test_high_risk_transaction_is_rejected(high_risk_payload):
    transaction = TransactionRequest(**high_risk_payload)
```

5. Delete the local `high_risk_payload = {...}` dictionary inside that test.
6. Run:

```bash
pytest tests/test_scoring.py -q
```

7. Verify the test still passes.
8. You are done when the high-risk data lives in `tests/conftest.py` and the
   scoring test reuses it.

### Add Threshold Boundary Tests

Goal: prove exactly how `accept_threshold` and `reject_threshold` behave.

1. Open `tests/test_scoring.py`.
2. Add this import if it is not already available:

```python
from app.scoring import _decision_for_score
```

3. Add these tests:

```python
def test_score_below_accept_threshold_is_accepted():
    decision = _decision_for_score(34, Settings(accept_threshold=35, reject_threshold=70))

    assert decision == Decision.accept


def test_score_at_accept_threshold_goes_to_review():
    decision = _decision_for_score(35, Settings(accept_threshold=35, reject_threshold=70))

    assert decision == Decision.review


def test_score_at_reject_threshold_is_rejected():
    decision = _decision_for_score(70, Settings(accept_threshold=35, reject_threshold=70))

    assert decision == Decision.reject
```

4. Run:

```bash
pytest tests/test_scoring.py -q
```

5. Verify all three tests pass.
6. You are done when you can say: below `accept_threshold` is `accept`, at
   `accept_threshold` is `review`, and at `reject_threshold` is `reject`.

### Add A Small Scoring Rule

Goal: add one deterministic policy rule and prove it with a unit test.

1. Open `app/scoring.py`.
2. Find the TODO near the end of `score_transaction()`.
3. Add this rule above the final `risk_score = ...` line:

```python
if (
    transaction.number_previous_orders >= 50
    and transaction.previous_failed_payments >= 2
):
    _add(
        contributions,
        "repeat_customer_failed_payments",
        transaction.previous_failed_payments,
        6,
        "Repeat customer with failed payments",
    )
```

4. Open `tests/test_scoring.py`.
5. Add this test:

```python
def test_repeat_customer_failed_payments_adds_reason_code(valid_payload):
    transaction = TransactionRequest(
        **{
            **valid_payload,
            "number_previous_orders": 50,
            "previous_failed_payments": 2,
        }
    )

    result = score_transaction(transaction, Settings())

    assert "REPEAT_CUSTOMER_WITH_FAILED_PAYMENTS" in result.reason_codes
```

6. Run:

```bash
pytest tests/test_scoring.py -q
```

7. Verify the test passes.
8. Open `/explain` later and decide whether this rule should also be documented
   in `scoring_explanation()`.

### Add Generated Request ID Coverage

Goal: prove middleware creates a request ID when the client does not send one.

1. Open `tests/test_api.py`.
2. Add this test:

```python
def test_score_endpoint_adds_request_id_when_missing(client, valid_payload):
    response = client.post("/score", json=valid_payload)

    body = response.json()
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert body["request_id"] == response.headers["x-request-id"]
```

3. Run:

```bash
pytest tests/test_api.py -q
```

4. Verify the test passes.
5. Open `app/middleware.py` and find where the request ID is read, generated,
   stored on `request.state`, and added to the response header.

### Add Async Batch-Score Coverage

Goal: test the ASGI app with `httpx.AsyncClient`.

1. Open `tests/test_integration_httpx.py`.
2. Add this test:

```python
@pytest.mark.anyio
async def test_batch_score_integration_using_httpx(valid_payload):
    second = {
        **valid_payload,
        "transaction_id": "txn_1002",
        "merchant_risk_score": 90,
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/batch-score",
            json={"transactions": [valid_payload, second]},
        )

    body = response.json()
    assert response.status_code == 200
    assert len(body["results"]) == 2
    assert body["results"][0]["transaction_id"] == "txn_1001"
    assert body["results"][1]["transaction_id"] == "txn_1002"
```

3. Run:

```bash
pytest tests/test_integration_httpx.py -q
```

4. Verify the test passes.
5. You are done when the async test proves `/batch-score` works without using
   FastAPI's synchronous `TestClient`.

### Inspect JSON Logs

Goal: understand observability without changing business logic.

1. Open `app/logging_config.py`.
2. Read the formatter and write down every field it emits.
3. Start the API:

```bash
make run
```

4. In another terminal, send:

```bash
curl -s http://localhost:8000/health
```

5. Look at the server terminal.
6. Verify the log line is JSON-shaped and includes request metadata.
7. Stop the server with `Ctrl+C`.
8. Do not add business fields to the generic log formatter unless you can
   explain why those fields belong on every request.

### Config Override Practice

Goal: understand settings precedence.

1. Open `tests/test_config.py`.
2. Read the existing YAML and environment override tests.
3. Add a `.env` precedence test:

```python
def test_environment_variables_override_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath(".env").write_text("FRAUD_API_ACCEPT_THRESHOLD=25\n")
    monkeypatch.setenv("FRAUD_API_ACCEPT_THRESHOLD", "45")

    settings = Settings()

    assert settings.accept_threshold == 45
```

4. Run:

```bash
pytest tests/test_config.py -q
```

5. Verify the test passes.
6. You are done when you can explain the order:
   direct Python values, real environment variables, `.env`, `config.yaml`,
   Python defaults.

### Docker And Make Practice

Goal: prove the app runs outside your local Python process.

1. Open `Makefile`.
2. Run:

```bash
make help
```

3. Start Docker Compose:

```bash
make docker-up
```

4. Verify the container:

```bash
make docker-ps
curl -s http://localhost:8000/health
```

5. Inspect logs:

```bash
make docker-logs
```

6. Stop Compose:

```bash
make docker-down
```

7. You are done when `/health` returns `200` from the container and Compose
   shuts down cleanly.

### Capstone: Add `orders_last_24h`

Goal: add one new scoring feature across schema, scoring, tests, and docs.

Work in this exact order.

1. Open `app/schemas.py`.
2. In `TransactionRequest`, add this field after `number_previous_orders`:

```python
orders_last_24h: Annotated[int, Field(ge=0, le=1_000)] = 0
```

3. In the `json_schema_extra` example, add:

```python
"orders_last_24h": 0,
```

4. Run:

```bash
pytest tests/test_api.py tests/test_scoring.py -q
```

5. Verify existing payloads still pass because the field defaults to `0`.
6. Open `app/scoring.py`.
7. Above `risk_score = min(...)`, add:

```python
if transaction.orders_last_24h >= 10:
    _add(
        contributions,
        "orders_last_24h",
        transaction.orders_last_24h,
        18,
        "High 24h order velocity",
    )
elif transaction.orders_last_24h >= 5:
    _add(
        contributions,
        "orders_last_24h",
        transaction.orders_last_24h,
        9,
        "Elevated 24h order velocity",
    )
```

8. In `scoring_explanation()`, add this to `feature_weights`:

```python
"orders_last_24h": "0, 9, or 18 points",
```

9. Add this reason to `reason_code_examples`:

```python
"HIGH_24H_ORDER_VELOCITY",
```

10. Open `tests/test_scoring.py`.
11. Add unit tests for low, elevated, and high velocity:

```python
def test_low_velocity_adds_no_velocity_reason(valid_payload):
    transaction = TransactionRequest(**{**valid_payload, "orders_last_24h": 4})

    result = score_transaction(transaction, Settings())

    assert "ELEVATED_24H_ORDER_VELOCITY" not in result.reason_codes
    assert "HIGH_24H_ORDER_VELOCITY" not in result.reason_codes


def test_elevated_velocity_adds_reason_code(valid_payload):
    transaction = TransactionRequest(**{**valid_payload, "orders_last_24h": 5})

    result = score_transaction(transaction, Settings())

    assert "ELEVATED_24H_ORDER_VELOCITY" in result.reason_codes


def test_high_velocity_adds_reason_code(valid_payload):
    transaction = TransactionRequest(**{**valid_payload, "orders_last_24h": 10})

    result = score_transaction(transaction, Settings())

    assert "HIGH_24H_ORDER_VELOCITY" in result.reason_codes
```

12. Run:

```bash
pytest tests/test_scoring.py -q
```

13. Open `tests/test_api.py`.
14. Add an invalid-input test case to the existing parametrized list:

```python
("orders_last_24h", 1_001),
```

15. Add an API response test:

```python
def test_score_endpoint_includes_velocity_reason(client, valid_payload):
    response = client.post("/score", json={**valid_payload, "orders_last_24h": 10})

    body = response.json()
    assert response.status_code == 200
    assert "HIGH_24H_ORDER_VELOCITY" in body["reason_codes"]
```

16. Run:

```bash
pytest tests/test_api.py -q
```

17. Open `tests/test_integration_httpx.py`.
18. Add `orders_last_24h` to one async `/batch-score` transaction and assert its
    reason code appears in that result.
19. Run:

```bash
pytest tests/test_integration_httpx.py -q
```

20. Open `README.md`.
21. Add `"orders_last_24h": 0` to example requests.
22. Mention the velocity rule in the `/explain` or scoring description.
23. Open `runbook.md`, `tradeoffs.md`, `interview_questions.md`, and
    `portfolio_notes.md`.
24. Add one short note in each file about velocity scoring, monitoring, false
    positives, or rollout.
25. Run the full verification:

```bash
make test
make lint
```

26. Start the API and verify manually:

```bash
make run
curl -s http://localhost:8000/explain
curl -s http://localhost:8000/score \
  -H "content-type: application/json" \
  -d '{
    "transaction_id": "txn_velocity_1",
    "customer_id": "cus_778",
    "order_amount": 129.99,
    "merchant_id": "mer_42",
    "merchant_category": "books",
    "merchant_risk_score": 10,
    "customer_tenure_days": 120,
    "number_previous_orders": 6,
    "orders_last_24h": 10,
    "previous_failed_payments": 0,
    "device_risk_score": 20,
    "email_domain_risk": 15,
    "payment_method": "card",
    "country": "US",
    "hour_of_day": 14
  }'
```

27. Verify the response contains `HIGH_24H_ORDER_VELOCITY`.
28. Stop the server with `Ctrl+C`.
29. Update `exercises.md` checkboxes only for the capstone work you completed.

### Application Files

| File | What to understand | Small activity | Verify |
| --- | --- | --- | --- |
| `app/__init__.py` | This marks `app` as an importable Python package. | Update the module docstring to say what the package owns. | Run `python -c "import app; print(app.__doc__)"`. |
| `app/main.py` | FastAPI app creation, route registration, response models, and custom validation error handling. | Add a tiny `GET /version` endpoint returning `model_or_policy_version`, then add an API test for `200`. | Run `pytest tests/test_api.py -q`. |
| `app/schemas.py` | Pydantic request and response contracts. This is where bad input becomes `422` before scoring runs. | Add one validation rule, such as requiring `country` to be uppercase after normalization or limiting it to supported markets. | Add a passing and failing API test; run `pytest tests/test_api.py -q`. |
| `app/scoring.py` | Deterministic fraud policy and reason-code generation. | Add one small scoring signal, such as extra points for very high `number_previous_orders` combined with failed payments. | Add a focused unit test in `tests/test_scoring.py`. |
| `app/config.py` | Runtime settings, environment variable overrides, `.env`, and `config.yaml` precedence. | Add one new setting with bounds, then test default and environment override behavior. | Run `pytest tests/test_config.py -q`. |
| `app/middleware.py` | Request ID propagation and structured request logging around every HTTP call. | Add a test proving that a request without `x-request-id` still receives one in the response header. | Run `pytest tests/test_api.py -q`. |
| `app/logging_config.py` | JSON log formatting for production-style observability. | Add one stable field to the formatter, or write down why adding dynamic business fields here would be risky. | Run one request and inspect the log shape. |

### Test Files

| File | What to understand | Small activity | Verify |
| --- | --- | --- | --- |
| `tests/conftest.py` | Shared pytest fixtures: `client`, `anyio_backend`, and `valid_payload`. | Add a `high_risk_payload` fixture and reuse it in one scoring or API test. | Run `pytest tests/test_scoring.py tests/test_api.py -q`. |
| `tests/test_api.py` | Synchronous API tests with FastAPI `TestClient`. | Add tests for `404` on an unknown path and `405` on `GET /score`. | Run `pytest tests/test_api.py -q`. |
| `tests/test_scoring.py` | Pure unit tests for scoring behavior without HTTP. | Add boundary tests for exactly `accept_threshold` and exactly `reject_threshold`. | Run `pytest tests/test_scoring.py -q`. |
| `tests/test_config.py` | Settings precedence and config safety. | Add a test proving a `.env` value overrides `config.yaml`, but a real environment variable overrides `.env`. | Run `pytest tests/test_config.py -q`. |
| `tests/test_integration_httpx.py` | Async integration tests using `httpx` and ASGI transport. | Add an async `/batch-score` test with two valid transactions. | Run `pytest tests/test_integration_httpx.py -q`. |

### Runtime, Packaging, And Tooling Files

| File | What to understand | Small activity | Verify |
| --- | --- | --- | --- |
| `config.yaml` | Human-readable local defaults. | Change `accept_threshold` temporarily and observe `/explain`; then restore it. | Run `make test` after restoring. |
| `pyproject.toml` | Project metadata, dependencies, pytest config, Ruff config, and build backend. | Add `--cov=app` to `tool.pytest.ini_options.addopts` temporarily and inspect coverage output. Decide whether to keep it. | Run `make test`. |
| `uv.lock` | Locked dependency graph for reproducible installs. | Do not hand-edit it. Find the locked `fastapi`, `pydantic`, and `uvicorn` versions and explain why lockfile reviews matter. | If dependencies change, run `uv lock`. |
| `Makefile` | Short commands for repeated developer tasks. | Add a `smoke` target that calls `/health` while the server is running. | Run `make help` and then `make smoke`. |
| `Dockerfile` | How the app becomes a container image. | Add a simple image label or a build-time import check, then build the image. | Run `make docker-build`. |
| `docker-compose.yml` | Local container runtime: build, ports, env vars, and health check. | Temporarily change `FRAUD_API_ACCEPT_THRESHOLD`, start Compose, and confirm `/explain` changed. | Run `make docker-up`, check `/explain`, then `make docker-down`. |
| `.dockerignore` | Files excluded from Docker build context. | Compare it with `.gitignore`; add any missing generated directory if needed. | Run `docker compose build` and check that build context stays small. |
| `.gitignore` | Files Git should not track, especially secrets and generated artifacts. | Create a temporary `.env` and confirm it does not appear in `git status`. | Delete the temporary `.env` after checking. |

## Required FastAPI Labs

Complete these before the capstone.

1. Route matching:
   - Add a test for `GET /missing-route`.
   - Confirm it returns `404`.
   - Explain why your route function was never called.

2. Method matching:
   - Add a test for `GET /score`.
   - Confirm it returns `405`.
   - Explain the difference between "path does not exist" and "method not allowed".

3. Validation:
   - Send invalid `order_amount`, `merchant_risk_score`, `payment_method`, and
     `hour_of_day`.
   - Confirm they return `422`.
   - Find which field rule in `app/schemas.py` caused each failure.

4. Successful scoring:
   - Send one low-risk, one review-like, and one reject-like transaction.
   - Record the `risk_score`, `decision`, `reason_codes`, and `score_contributions`.
   - Explain why the decision changed.

5. Request IDs:
   - Send one request with `x-request-id`.
   - Send one request without it.
   - Confirm both responses include an `x-request-id` header.

6. OpenAPI docs:
   - Open `/docs`.
   - Inspect the schema for `TransactionRequest`.
   - Explain how Pydantic models become API documentation.

## Required Testing Labs

You should know what each test style is buying you.

| Test style | File | What it protects |
| --- | --- | --- |
| Unit test | `tests/test_scoring.py` | Scoring rules and threshold decisions without HTTP noise. |
| API test | `tests/test_api.py` | FastAPI routes, validation, headers, response body shape. |
| Config test | `tests/test_config.py` | Settings precedence and safe runtime changes. |
| Async integration test | `tests/test_integration_httpx.py` | Real ASGI request flow with async client behavior. |
| Fixture design | `tests/conftest.py` | Reusable payloads and test setup with less duplication. |

Minimum test exercises:

1. Add one happy-path test.
2. Add one invalid-input `422` test.
3. Add one `404` or `405` test.
4. Add one scoring unit test for a boundary case.
5. Add one config override test.
6. Add one async integration test.

## Required Docker And Make Labs

You need to understand local Python and containerized execution.

1. Run locally:

```bash
make install
make run
```

2. In another terminal, call:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/explain
```

3. Run with Docker Compose:

```bash
make docker-up
```

4. Check logs and container status:

```bash
make docker-logs
make docker-ps
```

5. Stop the container:

```bash
make docker-down
```

6. Explain:
   - why the Dockerfile uses `python:3.11-slim`
   - why Compose maps `8000:8000`
   - why Compose environment variables override `config.yaml`
   - why `.dockerignore` and `.gitignore` are different files
   - why Make commands reduce onboarding friction

## Major Capstone: Add Velocity Risk Scoring

This final change should make you touch the whole project. Treat it like a real
production ticket.

### Product Requirement

The fraud team wants the API to consider short-term customer velocity:

- add a request field named `orders_last_24h`
- valid values are integers from `0` to `1_000`
- keep backward compatibility by defaulting the field to `0`, unless you decide
  and document that the API should require it
- add risk points when velocity is high
- expose the new feature in `/explain`
- test the field at unit, API, config, and integration levels
- update docs, examples, runbook, tradeoffs, and interview notes

### Suggested Scoring Policy

Start simple:

- `orders_last_24h >= 10`: add `18` points with reason `High 24h order velocity`
- `orders_last_24h >= 5`: add `9` points with reason `Elevated 24h order velocity`
- otherwise add `0` points

Then think like a senior data scientist:

- Could this punish loyal customers during holidays?
- Should velocity thresholds differ by merchant category or country?
- Should the feature be logged for monitoring?
- How would you measure false positives and false negatives?
- What metric would detect that this rule is too aggressive?

### Files To Touch

| File | Capstone work |
| --- | --- |
| `app/schemas.py` | Add `orders_last_24h` to `TransactionRequest` with validation and example data. |
| `app/scoring.py` | Add velocity scoring contributions, reason codes, and `/explain` feature weights. |
| `app/main.py` | Confirm response models still work; add route tests if behavior changes. |
| `app/config.py` | Optional advanced step: make velocity thresholds configurable. |
| `config.yaml` | Optional advanced step: add default velocity thresholds. |
| `tests/conftest.py` | Update or extend fixtures with velocity examples. |
| `tests/test_scoring.py` | Add low, elevated, and high velocity unit tests. |
| `tests/test_api.py` | Add valid and invalid `orders_last_24h` API tests. |
| `tests/test_config.py` | If configurable, test env overrides for velocity thresholds. |
| `tests/test_integration_httpx.py` | Add async `/batch-score` coverage with velocity examples. |
| `README.md` | Update example request, response, and explanation text. |
| `exercises.md` | Mark the capstone tasks complete or add follow-up tasks. |
| `runbook.md` | Add an incident scenario for a spike in review/reject rate after a policy change. |
| `tradeoffs.md` | Add a tradeoff about velocity rules and customer experience. |
| `interview_questions.md` | Add design questions about feature drift, monitoring, and rollout. |
| `portfolio_notes.md` | Add a capstone bullet explaining what production skill this demonstrates. |
| `Makefile` | Add a useful developer command such as `make smoke` or `make test-api`. |
| `Dockerfile` | Rebuild the image and confirm the new code is included. |
| `docker-compose.yml` | If thresholds are configurable, add environment overrides. |
| `.dockerignore` | Confirm no generated test or coverage artifacts enter the image context. |
| `.gitignore` | Confirm local `.env` and coverage artifacts stay untracked. |
| `pyproject.toml` | Optional: keep or remove coverage flags intentionally. |
| `uv.lock` | Regenerate only if dependency metadata changes. Never hand-edit. |

### Capstone Definition Of Done

The capstone is done only when all of this is true:

- `make test` passes
- `make lint` passes
- local `make run` serves `/health`, `/score`, `/batch-score`, and `/explain`
- Docker Compose starts and `/health` returns `200`
- invalid velocity values return `422`
- a high-velocity transaction produces a reason code for velocity
- `/explain` documents the velocity feature
- docs show the new field and the expected behavior
- you can explain the difference between a schema change, scoring change, config
  change, and API behavior change

## Senior Or Staff-Level Discussion Prompts

Practice answering these after the capstone:

1. What is the contract between the checkout client and this API?
2. Which changes are backward compatible and which are breaking?
3. Why does validation belong before scoring?
4. Why should scoring logic stay outside route functions?
5. How would you roll out a new scoring feature safely?
6. What metrics would you monitor after changing thresholds?
7. How would you detect drift in `merchant_risk_score`, `device_risk_score`, or
   `orders_last_24h`?
8. What would change if this became an ML model instead of deterministic rules?
9. How would you handle authentication, rate limits, and client-specific quotas?
10. What failure modes would cause false rejects, false accepts, or elevated
    manual review volume?

When you can answer those without reading from the files, you understand the
project at a serious level.
