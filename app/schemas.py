from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Decision(StrEnum):
    accept = "accept"
    review = "review"
    reject = "reject"


class PaymentMethod(StrEnum):
    card = "card"
    bank_account = "bank_account"
    digital_wallet = "digital_wallet"
    gift_card = "gift_card"


class TransactionRequest(BaseModel):
    transaction_id: Annotated[str, Field(min_length=1, max_length=64)]
    customer_id: Annotated[str, Field(min_length=1, max_length=64)]
    order_amount: Annotated[float, Field(gt=0, le=100_000)]
    merchant_id: Annotated[str, Field(min_length=1, max_length=64)]
    merchant_category: Annotated[str, Field(min_length=1, max_length=64)]
    merchant_risk_score: Annotated[int, Field(ge=0, le=100)]
    customer_tenure_days: Annotated[int, Field(ge=0, le=20_000)]
    number_previous_orders: Annotated[int, Field(ge=0, le=100_000)]
    previous_failed_payments: Annotated[int, Field(ge=0, le=10_000)]
    device_risk_score: Annotated[int, Field(ge=0, le=100)]
    email_domain_risk: Annotated[int, Field(ge=0, le=100)]
    payment_method: PaymentMethod
    country: Annotated[str, Field(min_length=2, max_length=2)]
    hour_of_day: Annotated[int, Field(ge=0, le=23)]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
                "hour_of_day": 14,
            }
        }
    )

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        # TODO: Add one new validation rule, such as limiting countries to supported markets.
        return value.upper()


class BatchScoreRequest(BaseModel):
    transactions: Annotated[list[TransactionRequest], Field(min_length=1, max_length=100)]


class ScoreContribution(BaseModel):
    feature: str
    value: float | int | str
    points: int
    reason: str


class ScoreResponse(BaseModel):
    transaction_id: str
    request_id: str
    risk_score: Annotated[int, Field(ge=0, le=100)]
    decision: Decision
    reason_codes: list[str]
    score_contributions: list[ScoreContribution]
    model_or_policy_version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BatchScoreResponse(BaseModel):
    request_id: str
    results: list[ScoreResponse]


class ExplainResponse(BaseModel):
    model_or_policy_version: str
    decision_thresholds: dict[Literal["accept_below", "review_from", "reject_from"], int]
    feature_weights: dict[str, str]
    reason_code_examples: list[str]


class ErrorResponse(BaseModel):
    request_id: str
    error: str
    detail: list[dict[str, object]] | str
