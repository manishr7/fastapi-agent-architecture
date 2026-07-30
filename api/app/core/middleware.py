import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"

logger = structlog.get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Binds request-scoped tracing context and logs one line per request.

    `request_id` identifies this hop only and is never trusted from a client
    header. `correlation_id` is accepted from an incoming request if present
    (or generated) so it can keep propagating across future service
    boundaries (Next.js -> FastAPI -> queue -> worker) even though both
    values are equal for a request that originates here.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
            http_method=request.method,
            http_path=request.url.path,
        )
        try:
            logger.debug("request_started")
            start = time.perf_counter()
            try:
                response = await call_next(request)
            except BaseException:
                # call_next can raise BaseException subclasses that never
                # reach unhandled_exception_handler (registered for
                # Exception only) — notably asyncio.CancelledError on a
                # client disconnect. Without this, such a request would
                # never produce any request_completed/access-log line at
                # all. Never swallow it — log, then propagate unchanged.
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.warning("request_cancelled", duration_ms=round(elapsed_ms, 2))
                raise
            elapsed_ms = (time.perf_counter() - start) * 1000
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
            self._log_completed(status_code=response.status_code, duration_ms=elapsed_ms)
            return response
        finally:
            structlog.contextvars.clear_contextvars()

    @staticmethod
    def _outcome_for(status_code: int) -> str:
        if status_code >= 500:
            return "server_error"
        if status_code >= 400:
            return "client_error"
        return "success"

    @staticmethod
    def _log_completed(*, status_code: int, duration_ms: float) -> None:
        logger.info(
            "request_completed",
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            outcome=RequestContextMiddleware._outcome_for(status_code),
        )
