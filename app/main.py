from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.logging_config import configure_logging
from app.middleware import RequestContextMiddleware
from app.schemas import (
    BatchScoreRequest,
    BatchScoreResponse,
    ErrorResponse,
    ExplainResponse,
    ScoreResponse,
    TransactionRequest,
)
from app.scoring import score_transaction, scoring_explanation

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Low-latency deterministic fraud scoring API for BNPL checkout decisions.",
)
app.add_middleware(RequestContextMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    detail = _validation_detail(exc)
    return JSONResponse(
        status_code=422,
        headers={"x-request-id": request_id},
        content=ErrorResponse(
            request_id=request_id,
            error="validation_error",
            detail=detail,
        ).model_dump(),
    )


def _validation_detail(exc: RequestValidationError) -> str:
    return "Invalid request body. Check required fields, value ranges, and enum choices."


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "model_or_policy_version": settings.model_or_policy_version,
    }


@app.post("/score", response_model=ScoreResponse)
async def score(payload: TransactionRequest, request: Request) -> ScoreResponse:
    result = score_transaction(payload, settings)
    return ScoreResponse(
        transaction_id=payload.transaction_id,
        request_id=request.state.request_id,
        risk_score=result.risk_score,
        decision=result.decision,
        reason_codes=result.reason_codes,
        score_contributions=result.score_contributions,
        model_or_policy_version=settings.model_or_policy_version,
    )


@app.post("/batch-score", response_model=BatchScoreResponse)
async def batch_score(payload: BatchScoreRequest, request: Request) -> BatchScoreResponse:
    results = []
    for transaction in payload.transactions:
        result = score_transaction(transaction, settings)
        results.append(
            ScoreResponse(
                transaction_id=transaction.transaction_id,
                request_id=request.state.request_id,
                risk_score=result.risk_score,
                decision=result.decision,
                reason_codes=result.reason_codes,
                score_contributions=result.score_contributions,
                model_or_policy_version=settings.model_or_policy_version,
            )
        )
    return BatchScoreResponse(request_id=request.state.request_id, results=results)


@app.get("/explain", response_model=ExplainResponse)
async def explain() -> dict[str, object]:
    return scoring_explanation(settings)
