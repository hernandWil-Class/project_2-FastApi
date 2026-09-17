import pytest

pytestmark = pytest.mark.anyio


async def test_health_endpoint(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_version_endpoint(client):
    response = await client.get("/version")

    assert response.status_code == 200
    assert response.json()["model_or_policy_version"] == "policy-v1.0.0"


async def test_unknown_route_returns_404(client):
    response = await client.get("/missing-route")

    assert response.status_code == 404


async def test_score_route_rejects_get_method(client):
    response = await client.get("/score")

    assert response.status_code == 405


async def test_score_endpoint_returns_explainable_decision(client, valid_payload):
    response = await client.post(
        "/score", json=valid_payload, headers={"x-request-id": "req_test_123"}
    )

    body = response.json()
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req_test_123"
    assert body["transaction_id"] == valid_payload["transaction_id"]
    assert body["request_id"] == "req_test_123"
    assert body["decision"] in {"accept", "review", "reject"}
    assert isinstance(body["score_contributions"], list)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("order_amount", -1),
        ("merchant_risk_score", 101),
        ("hour_of_day", 24),
        ("payment_method", "cash"),
    ],
)
async def test_score_endpoint_rejects_invalid_input(client, valid_payload, field, value):
    response = await client.post("/score", json={**valid_payload, field: value})

    assert response.status_code == 422


async def test_batch_score_endpoint(client, valid_payload):
    second = {**valid_payload, "transaction_id": "txn_1002", "merchant_risk_score": 90}

    response = await client.post("/batch-score", json={"transactions": [valid_payload, second]})

    body = response.json()
    assert response.status_code == 200
    assert len(body["results"]) == 2
    assert body["results"][0]["transaction_id"] == "txn_1001"
    assert body["results"][1]["transaction_id"] == "txn_1002"


async def test_explain_endpoint(client):
    response = await client.get("/explain")

    body = response.json()
    assert response.status_code == 200
    assert "decision_thresholds" in body
    assert "feature_weights" in body


async def test_todo_add_invalid_input_test_for_failed_payments(client, valid_payload):
    # TODO: Replace this learning placeholder with your own invalid-input test.
    response = await client.post("/score", json={**valid_payload, "order_amount": 0})

    assert response.status_code == 422


async def test_todo_add_batch_scoring_integration_tests(client, valid_payload):
    # TODO: Add more batch integration tests, including mixed accept/review/reject examples.
    response = await client.post("/batch-score", json={"transactions": [valid_payload]})

    assert response.status_code == 200
