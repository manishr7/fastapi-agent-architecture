from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import Settings
from app.core.constants import DEFAULT_ERROR_MESSAGE, UNEXPECTED_ERROR_CODE
from app.core.exceptions import (
    ApplicationException,
    AuthenticationException,
    AuthorizationException,
    BusinessRuleViolation,
    ConflictException,
    ExternalServiceException,
    NotFoundException,
    PersistenceException,
    ServiceUnavailableException,
    ValidationException,
)
from app.shared.responses.envelope import error_response

logger = structlog.get_logger(__name__)

_CAUSE_MESSAGE_MAX_LEN = 500

_STATUS_BY_EXCEPTION: dict[type[ApplicationException], int] = {
    ValidationException: 400,
    AuthenticationException: 401,
    AuthorizationException: 403,
    NotFoundException: 404,
    ConflictException: 409,
    BusinessRuleViolation: 422,
    PersistenceException: 500,
    ExternalServiceException: 502,
    ServiceUnavailableException: 503,
}

# Mirrors the logging-level table in `12-errors.md`:
# Validation -> INFO, Business failures -> WARNING, Infrastructure failures -> ERROR.
_LOG_METHOD_BY_EXCEPTION: dict[type[ApplicationException], str] = {
    ValidationException: "info",
    AuthenticationException: "warning",
    AuthorizationException: "warning",
    NotFoundException: "warning",
    ConflictException: "warning",
    BusinessRuleViolation: "warning",
    PersistenceException: "error",
    ExternalServiceException: "error",
    ServiceUnavailableException: "error",
}

# Fields the handler always sets itself; log_context from any layer can never
# override these, even if it happens to use one of these names. "event" is
# the positional argument every structlog logger method binds to — a
# log_context value there would crash the log(...) call below via **log_fields.
_RESERVED_LOG_FIELDS = frozenset(
    {
        "event",
        "code",
        "message",
        "status_code",
        "exc_info",
        "cause_type",
        "cause_message",
        "root_cause_type",
        "root_cause_message",
    }
)


def _log_method_for(exc: ApplicationException) -> str:
    for exc_type, method in _LOG_METHOD_BY_EXCEPTION.items():
        if isinstance(exc, exc_type):
            return method
    return "error"


def _envelope_json(exc: ApplicationException, status_code: int) -> JSONResponse:
    body = error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _status_for(exc: ApplicationException) -> int:
    for exc_type, status in _STATUS_BY_EXCEPTION.items():
        if isinstance(exc, exc_type):
            return status
    return 500


def _should_include_traceback(settings: Settings) -> bool:
    # Traceback verbosity and log volume (LOG_LEVEL) are independent knobs —
    # bumping LOG_LEVEL to DEBUG to see more events must not also start
    # dumping full tracebacks into every chained-exception log line.
    return settings.debug


def _sanitize_cause_message(message: str) -> str:
    single_line = " ".join(message.split())
    if len(single_line) <= _CAUSE_MESSAGE_MAX_LEN:
        return single_line
    return single_line[: _CAUSE_MESSAGE_MAX_LEN - 3] + "..."


def _merged_log_context(exc: ApplicationException) -> dict[str, Any]:
    """Merge log_context from the full __cause__ chain (inner first, outer wins)."""
    chain: list[ApplicationException] = []
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, ApplicationException):
            chain.append(current)
        current = current.__cause__
    merged: dict[str, Any] = {}
    for app_exc in reversed(chain):
        for key, value in app_exc.log_context.items():
            if key not in _RESERVED_LOG_FIELDS:
                merged[key] = value
    return merged


def _root_cause(cause: BaseException) -> BaseException:
    seen: set[int] = {id(cause)}
    root = cause
    while root.__cause__ is not None and id(root.__cause__) not in seen:
        root = root.__cause__
        seen.add(id(root))
    return root


def _cause_summary(exc: ApplicationException) -> dict[str, str]:
    cause = exc.__cause__
    if cause is None:
        return {}
    summary = {
        "cause_type": type(cause).__name__,
        "cause_message": _sanitize_cause_message(str(cause)),
    }
    root = _root_cause(cause)
    if root is not cause:
        # e.g. ServiceUnavailableException -> PersistenceException -> the raw
        # driver/SQLAlchemy error. cause_* is the curated boundary message;
        # root_cause_* is what actually failed, for on-call diagnosis.
        summary["root_cause_type"] = type(root).__name__
        summary["root_cause_message"] = _sanitize_cause_message(str(root))
    return summary


async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
) -> JSONResponse:
    status = _status_for(exc)
    settings: Settings = request.app.state.settings
    log = getattr(logger, _log_method_for(exc))
    log_fields = _merged_log_context(exc)
    log_fields.update(code=exc.code, message=exc.message, status_code=status)
    log_fields.update(_cause_summary(exc))
    if _should_include_traceback(settings) and exc.__cause__ is not None:
        log_fields["exc_info"] = exc.__cause__
    log("application_exception", **log_fields)
    return _envelope_json(exc, status)


def _sanitize_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Pydantic includes the raw offending value under "input" for every
    # error. For fields like passwords that value must never reach the
    # client response or the logs, and there is no per-field way to tell
    # which fields are sensitive, so it is dropped for all fields.
    return [{key: value for key, value in error.items() if key != "input"} for error in errors]


async def request_validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    sanitized_errors = _sanitize_validation_errors(exc.errors())
    details: dict[str, Any] = {"errors": sanitized_errors}
    logger.info("request_validation_error", errors=sanitized_errors)
    body = error_response(
        code="REQUEST_VALIDATION_ERROR",
        message="Request validation failed",
        details=details,
    )
    return JSONResponse(status_code=422, content=body.model_dump())


async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.critical("unhandled_exception", exc_info=exc)
    body = error_response(
        code=UNEXPECTED_ERROR_CODE,
        message=DEFAULT_ERROR_MESSAGE,
    )
    return JSONResponse(status_code=500, content=body.model_dump())


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail_message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    log = logger.error if exc.status_code >= 500 else logger.warning
    log("http_exception", detail=detail_message, status_code=exc.status_code)
    body = error_response(
        code="HTTP_ERROR",
        message=detail_message,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationException, application_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
