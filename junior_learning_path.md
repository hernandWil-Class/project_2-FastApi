# Junior Learning Path

Open `app/main.py` first, then `schemas.py`, `scoring.py`, `config.py`, and `tests`.

## 1. What The API Does

This API receives checkout transactions and returns a fraud risk decision: `accept`, `review`, or `reject`.

## 2. What Happens In `/score`

FastAPI receives JSON, Pydantic validates it, `score_transaction()` calculates risk, and the route returns a structured response with explanations.

## 3. How Pydantic Validates Input

`TransactionRequest` in `app/schemas.py` defines required fields and rules such as positive order amounts, risk scores from 0 to 100, and valid hours from 0 to 23. Invalid input returns HTTP `422`.

## 4. Where Scoring Logic Lives

Scoring lives in `app/scoring.py`, not inside the route. This makes it easier to test and change without rewriting API code.

## 5. How The Decision Is Created

The scorer adds deterministic points for risky signals. Scores below the accept threshold are accepted, scores from the accept threshold are reviewed, and scores at or above the reject threshold are rejected.

## 6. Run Locally

```bash
make install
make run
```

## 7. Send A Request With Curl

Use the example in `README.md`. A successful response includes `risk_score`, `decision`, `reason_codes`, and `score_contributions`.

## 8. Run Tests

```bash
make test
```

## 9. Use Docker

```bash
docker compose up --build
```

## 10. Debug Common Errors

- `422`: your JSON shape or value is invalid.
- `404`: the URL path is wrong.
- `500`: the API has a bug or unexpected runtime failure.
- Docker port error: another process is already using port `8000`.

## Tiny Exercise

Send one valid `/score` request from `README.md`. Then send an invalid request with `"order_amount": -10`.

The valid request returns `200` because all fields pass validation. The invalid request returns `422` because `order_amount` must be greater than zero.
