# Debugging Scenarios

## Invalid JSON

Symptom: `/score` returns `422`.

Check the response body. FastAPI tells you which field failed validation.

## Wrong Decision

Symptom: a transaction is accepted when you expected review.

Open `app/scoring.py`, inspect the score contributions, then check thresholds in `app/config.py`.

## Missing Request ID

Symptom: logs or responses do not contain the expected request ID.

Send `x-request-id` in the request header. If you omit it, the middleware generates one.

## Docker Port Conflict

Symptom: Docker cannot bind to port `8000`.

Stop the process using port `8000` or change the host port in `docker-compose.yml`.
