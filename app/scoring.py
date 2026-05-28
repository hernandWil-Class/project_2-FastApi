from dataclasses import dataclass

from app.config import Settings
from app.schemas import Decision, ScoreContribution, TransactionRequest


@dataclass(frozen=True)
class ScoringResult:
    risk_score: int
    decision: Decision
    reason_codes: list[str]
    score_contributions: list[ScoreContribution]


HIGH_RISK_CATEGORIES = {"electronics", "jewelry", "gaming", "crypto", "luxury"}
HIGH_RISK_COUNTRIES = {"BR", "NG", "PK", "RU", "VN"}


def score_transaction(transaction: TransactionRequest, settings: Settings) -> ScoringResult:
    contributions: list[ScoreContribution] = []

    _add_risk_score(
        contributions,
        "merchant_risk_score",
        transaction.merchant_risk_score,
        max_points=25,
        reason="Merchant historical risk",
    )
    _add_risk_score(
        contributions,
        "device_risk_score",
        transaction.device_risk_score,
        max_points=25,
        reason="Device trust and anomaly signals",
    )
    _add_risk_score(
        contributions,
        "email_domain_risk",
        transaction.email_domain_risk,
        max_points=15,
        reason="Email domain risk",
    )

    if transaction.order_amount >= 1_000:
        _add(contributions, "order_amount", transaction.order_amount, 15, "High order amount")
    elif transaction.order_amount >= 500:
        _add(contributions, "order_amount", transaction.order_amount, 8, "Elevated order amount")

    if transaction.customer_tenure_days < 7:
        _add(
            contributions,
            "customer_tenure_days",
            transaction.customer_tenure_days,
            12,
            "Very new customer",
        )
    elif transaction.customer_tenure_days < 30:
        _add(
            contributions,
            "customer_tenure_days",
            transaction.customer_tenure_days,
            6,
            "New customer",
        )

    if transaction.number_previous_orders == 0:
        _add(
            contributions,
            "number_previous_orders",
            transaction.number_previous_orders,
            8,
            "No prior successful order history",
        )

    if transaction.previous_failed_payments >= 3:
        _add(
            contributions,
            "previous_failed_payments",
            transaction.previous_failed_payments,
            14,
            "Multiple previous failed payments",
        )
    elif transaction.previous_failed_payments >= 1:
        _add(
            contributions,
            "previous_failed_payments",
            transaction.previous_failed_payments,
            7,
            "Previous failed payment",
        )

    if transaction.merchant_category.lower() in HIGH_RISK_CATEGORIES:
        _add(
            contributions,
            "merchant_category",
            transaction.merchant_category,
            6,
            "Higher-risk merchant category",
        )

    if transaction.payment_method.value == "gift_card":
        _add(
            contributions,
            "payment_method",
            transaction.payment_method.value,
            8,
            "Risky payment method",
        )

    if transaction.country in HIGH_RISK_COUNTRIES:
        _add(contributions, "country", transaction.country, 6, "Higher-risk country corridor")

    if transaction.hour_of_day in {0, 1, 2, 3, 4, 5}:
        _add(contributions, "hour_of_day", transaction.hour_of_day, 5, "Unusual checkout hour")

    # TODO: Add one new scoring feature here, then cover it with a unit test.

    risk_score = min(sum(item.points for item in contributions), 100)
    decision = _decision_for_score(risk_score, settings)
    reason_codes = _reason_codes(contributions)

    return ScoringResult(
        risk_score=risk_score,
        decision=decision,
        reason_codes=reason_codes,
        score_contributions=contributions,
    )


def scoring_explanation(settings: Settings) -> dict[str, object]:
    return {
        "model_or_policy_version": settings.model_or_policy_version,
        "decision_thresholds": {
            "accept_below": settings.accept_threshold,
            "review_from": settings.accept_threshold,
            "reject_from": settings.reject_threshold,
        },
        "feature_weights": {
            "merchant_risk_score": "0 to 25 points",
            "device_risk_score": "0 to 25 points",
            "email_domain_risk": "0 to 15 points",
            "order_amount": "0, 8, or 15 points",
            "customer_tenure_days": "0, 6, or 12 points",
            "previous_failed_payments": "0, 7, or 14 points",
            "category/country/hour/payment_method": "small deterministic policy adjustments",
        },
        "reason_code_examples": [
            "HIGH_ORDER_AMOUNT",
            "VERY_NEW_CUSTOMER",
            "MULTIPLE_PREVIOUS_FAILED_PAYMENTS",
            "HIGHER_RISK_MERCHANT_CATEGORY",
        ],
    }


def _decision_for_score(risk_score: int, settings: Settings) -> Decision:
    if risk_score >= settings.reject_threshold:
        return Decision.reject
    if risk_score >= settings.accept_threshold:
        return Decision.review
    return Decision.accept


def _add_risk_score(
    contributions: list[ScoreContribution],
    feature: str,
    value: int,
    *,
    max_points: int,
    reason: str,
) -> None:
    points = round(value / 100 * max_points)
    if points:
        _add(contributions, feature, value, points, reason)


def _add(
    contributions: list[ScoreContribution],
    feature: str,
    value: float | int | str,
    points: int,
    reason: str,
) -> None:
    contributions.append(
        ScoreContribution(feature=feature, value=value, points=points, reason=reason)
    )


def _reason_codes(contributions: list[ScoreContribution]) -> list[str]:
    return [item.reason.upper().replace(" ", "_").replace("-", "_") for item in contributions]
