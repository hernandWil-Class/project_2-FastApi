import pytest


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_score_endpoint_returns_explainable_decision(client, valid_payload):
    response = client.post("/score", json=valid_payload, headers={"x-request-id": "req_test_123"})

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
def test_score_endpoint_rejects_invalid_input(client, valid_payload, field, value):
    response = client.post("/score", json={**valid_payload, field: value})

    assert response.status_code == 422


def test_batch_score_endpoint(client, valid_payload):
    second = {**valid_payload, "transaction_id": "txn_1002", "merchant_risk_score": 90}

    response = client.post("/batch-score", json={"transactions": [valid_payload, second]})

    body = response.json()
    assert response.status_code == 200
    assert len(body["results"]) == 2
    assert body["results"][0]["transaction_id"] == "txn_1001"
    assert body["results"][1]["transaction_id"] == "txn_1002"


def test_explain_endpoint(client):
    response = client.get("/explain")

    body = response.json()
    assert response.status_code == 200
    assert "decision_thresholds" in body
    assert "feature_weights" in body


def test_todo_add_invalid_input_test_for_failed_payments(client, valid_payload):
    # TODO: Replace this learning placeholder with your own invalid-input test.
    response = client.post("/score", json={**valid_payload, "order_amount": 0})

    assert response.status_code == 422


def test_todo_add_batch_scoring_integration_tests(client, valid_payload):
    # TODO: Add more batch integration tests, including mixed accept/review/reject examples.
    response = client.post("/batch-score", json={"transactions": [valid_payload]})

    assert response.status_code == 200
