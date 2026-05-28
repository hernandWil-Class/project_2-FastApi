import logging
import time
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("fraud_api")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get("x-request-id", str(uuid4()))
        scope.setdefault("state", {})["request_id"] = request_id
        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = MutableHeaders(scope=message)
                response_headers["x-request-id"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            _log_request(scope, request_id, status_code, start)


def _log_request(scope: Scope, request_id: str, status_code: int, start: float) -> None:
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "method": scope["method"],
            "path": scope["path"],
            "status_code": status_code,
            "latency_ms": latency_ms,
        },
    )
