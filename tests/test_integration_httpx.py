import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_score_integration_using_httpx(valid_payload):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/score",
            json=valid_payload,
            headers={"x-request-id": "req_httpx_1"},
        )

    body = response.json()
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req_httpx_1"
    assert body["request_id"] == "req_httpx_1"


@pytest.mark.anyio
async def test_invalid_score_integration_using_httpx(valid_payload):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/score", json={**valid_payload, "hour_of_day": 99})

    body = response.json()
    assert response.status_code == 422
    assert body["error"] == "validation_error"
    assert body["request_id"] == response.headers["x-request-id"]
