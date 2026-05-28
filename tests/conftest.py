import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def valid_payload() -> dict[str, object]:
    return {
        "transaction_id": "txn_1001",
        "customer_id": "cus_778",
        "order_amount": 129.99,
        "merchant_id": "mer_42",
        "merchant_category": "books",
        "merchant_risk_score": 10,
        "customer_tenure_days": 120,
        "number_previous_orders": 6,
        "previous_failed_payments": 0,
        "device_risk_score": 20,
        "email_domain_risk": 15,
        "payment_method": "card",
        "country": "us",
        "hour_of_day": 14,
    }
