from app.config import Settings
from app.schemas import Decision, TransactionRequest
from app.scoring import score_transaction


def test_low_risk_transaction_is_accepted(valid_payload):
    transaction = TransactionRequest(**valid_payload)

    result = score_transaction(transaction, Settings())

    assert result.decision == Decision.accept
    assert 0 <= result.risk_score < 35


def test_high_risk_transaction_is_rejected(valid_payload):
    high_risk_payload = {
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
    transaction = TransactionRequest(**high_risk_payload)

    result = score_transaction(transaction, Settings())

    assert result.decision == Decision.reject
    assert result.risk_score >= 70
    assert "MULTIPLE_PREVIOUS_FAILED_PAYMENTS" in result.reason_codes


def test_configurable_thresholds_can_change_decision(valid_payload):
    transaction = TransactionRequest(**{**valid_payload, "merchant_risk_score": 80})

    result = score_transaction(transaction, Settings(accept_threshold=10, reject_threshold=90))

    assert result.decision == Decision.review
