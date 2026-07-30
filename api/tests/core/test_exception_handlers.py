import asyncio
import json
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import Settings
from app.core.exception_handlers import (
    application_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import (
    NotFoundException,
    PersistenceException,
    ServiceUnavailableException,
    ValidationException,
)
from app.main import app


def _handler_request(settings: Settings) -> Request:
    request = MagicMock(spec=Request)
    request.app.state.settings = settings
    return request


@pytest.mark.asyncio
async def test_method_not_allowed_returns_standard_envelope() -> None:
    """A 405 goes through http_exception_handler (StarletteHTTPException), not
    request_validation_exception_handler — verify its envelope shape and that
    tracing meta is still populated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v6/health",
            json={"unexpected": True},
        )

    assert response.status_code == 405
    body = response.json()
    assert set(body.keys()) == {"data", "meta", "error"}
    assert body["data"] is None
    assert body["error"]["code"] == "HTTP_ERROR"
    assert "request_id" in body["meta"]
    assert "correlation_id" in body["meta"]


def _last_logged_event(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.strip()]
    return json.loads(lines[-1])


@pytest.mark.asyncio
async def test_validation_exception_logs_at_info(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await application_exception_handler(
        _handler_request(settings), ValidationException("bad input")
    )

    assert _last_logged_event(capsys)["level"] == "info"


@pytest.mark.asyncio
async def test_not_found_exception_logs_at_warning(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await application_exception_handler(_handler_request(settings), NotFoundException("missing"))

    assert _last_logged_event(capsys)["level"] == "warning"


@pytest.mark.asyncio
async def test_persistence_exception_logs_at_error(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await application_exception_handler(_handler_request(settings), PersistenceException("db down"))

    assert _last_logged_event(capsys)["level"] == "error"


@pytest.mark.asyncio
async def test_unhandled_exception_logs_at_critical(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await unhandled_exception_handler(_handler_request(settings), RuntimeError("boom"))

    assert _last_logged_event(capsys)["level"] == "critical"


@pytest.mark.asyncio
async def test_chained_exception_logs_traceback_in_debug_mode(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings(DEBUG=True)

    try:
        try:
            raise PersistenceException("db connectivity check failed")
        except PersistenceException as cause:
            raise ServiceUnavailableException(
                message="Database is not available", code="DATABASE_UNAVAILABLE"
            ) from cause
    except ServiceUnavailableException as exc:
        await application_exception_handler(_handler_request(settings), exc)

    event = _last_logged_event(capsys)
    assert event["level"] == "error"
    assert "exception" in event
    assert "db connectivity check failed" in event["exception"]


@pytest.mark.asyncio
async def test_traceback_not_included_when_only_log_level_is_debug(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Regression: LOG_LEVEL=DEBUG controls event volume, not traceback verbosity."""
    settings = configured_settings(LOG_LEVEL="DEBUG", DEBUG=False)

    try:
        try:
            raise PersistenceException("db connectivity check failed")
        except PersistenceException as cause:
            raise ServiceUnavailableException(
                message="Database is not available", code="DATABASE_UNAVAILABLE"
            ) from cause
    except ServiceUnavailableException as exc:
        await application_exception_handler(_handler_request(settings), exc)

    event = _last_logged_event(capsys)
    assert "exception" not in event
    assert event["cause_type"] == "PersistenceException"


@pytest.mark.asyncio
async def test_chained_exception_logs_summary_in_production(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    try:
        try:
            raise PersistenceException("db connectivity check failed")
        except PersistenceException as cause:
            raise ServiceUnavailableException(
                message="Database is not available", code="DATABASE_UNAVAILABLE"
            ) from cause
    except ServiceUnavailableException as exc:
        await application_exception_handler(_handler_request(settings), exc)

    event = _last_logged_event(capsys)
    assert event["level"] == "error"
    assert "exception" not in event
    assert event["cause_type"] == "PersistenceException"
    assert "db connectivity check failed" in event["cause_message"]
    assert "root_cause_type" not in event
    assert "root_cause_message" not in event


@pytest.mark.asyncio
async def test_root_cause_fields_reflect_innermost_exception(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    try:
        try:
            try:
                raise RuntimeError("connection refused by driver")
            except RuntimeError as driver_error:
                raise PersistenceException("db connectivity check failed") from driver_error
        except PersistenceException as cause:
            raise ServiceUnavailableException(
                message="Database is not available", code="DATABASE_UNAVAILABLE"
            ) from cause
    except ServiceUnavailableException as exc:
        await application_exception_handler(_handler_request(settings), exc)

    event = _last_logged_event(capsys)
    assert event["cause_type"] == "PersistenceException"
    assert "db connectivity check failed" in event["cause_message"]
    assert event["root_cause_type"] == "RuntimeError"
    assert "connection refused by driver" in event["root_cause_message"]


@pytest.mark.asyncio
async def test_log_context_merged_from_cause_chain(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    try:
        try:
            raise PersistenceException(
                "db down",
                log_context={"operation": "ping"},
            )
        except PersistenceException as cause:
            raise ServiceUnavailableException(
                message="Database is not available",
                code="DATABASE_UNAVAILABLE",
                log_context={"dependency": "database"},
            ) from cause
    except ServiceUnavailableException as exc:
        await application_exception_handler(_handler_request(settings), exc)

    event = _last_logged_event(capsys)
    assert event["operation"] == "ping"
    assert event["dependency"] == "database"


@pytest.mark.asyncio
async def test_exception_without_cause_has_no_summary_fields(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await application_exception_handler(
        _handler_request(settings), ValidationException("bad input")
    )

    event = _last_logged_event(capsys)
    assert "exception" not in event
    assert "cause_type" not in event
    assert "cause_message" not in event


@pytest.mark.asyncio
async def test_log_context_is_merged_into_log_line(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    exc = NotFoundException("missing", log_context={"student_id": 42})
    await application_exception_handler(_handler_request(settings), exc)

    assert _last_logged_event(capsys)["student_id"] == 42


@pytest.mark.asyncio
async def test_log_context_never_overrides_reserved_fields(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    exc = NotFoundException("missing", code="NOT_FOUND", log_context={"code": "SPOOFED"})
    await application_exception_handler(_handler_request(settings), exc)

    assert _last_logged_event(capsys)["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_log_context_never_leaks_into_client_response(
    configured_settings: Callable[..., Settings],
) -> None:
    settings = configured_settings()
    exc = NotFoundException("missing", log_context={"student_id": 42})

    response = await application_exception_handler(_handler_request(settings), exc)

    body = json.loads(response.body)
    assert body["error"]["details"] == {}


@pytest.mark.asyncio
async def test_http_exception_logs_warning_for_4xx(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await http_exception_handler(
        _handler_request(settings),
        StarletteHTTPException(status_code=404, detail="Not Found"),
    )

    event = _last_logged_event(capsys)
    assert event["event"] == "http_exception"
    assert event["level"] == "warning"


@pytest.mark.asyncio
async def test_http_exception_logs_error_for_5xx(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()

    await http_exception_handler(
        _handler_request(settings),
        StarletteHTTPException(status_code=503, detail="Service Unavailable"),
    )

    assert _last_logged_event(capsys)["level"] == "error"


@pytest.mark.asyncio
async def test_validation_error_strips_raw_input_from_response_and_logs(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = configured_settings()
    exc = RequestValidationError(
        errors=[
            {
                "type": "string_too_short",
                "loc": ("body", "password"),
                "msg": "String should have at least 8 characters",
                "input": "hunter2",
            }
        ]
    )

    response = await request_validation_exception_handler(_handler_request(settings), exc)

    body = json.loads(response.body)
    response_error = body["error"]["details"]["errors"][0]
    assert "input" not in response_error
    assert response_error["msg"] == "String should have at least 8 characters"

    logged_error = _last_logged_event(capsys)["errors"][0]
    assert "input" not in logged_error


@pytest.mark.asyncio
async def test_log_context_named_event_does_not_crash_handler(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Regression: log_context={"event": ...} must not crash the handler —
    "event" is the positional arg every structlog logger method binds to."""
    settings = configured_settings()
    exc = NotFoundException("missing", log_context={"event": "SPOOFED"})

    response = await application_exception_handler(_handler_request(settings), exc)

    assert response.status_code == 404
    assert _last_logged_event(capsys)["event"] == "application_exception"


@pytest.mark.asyncio
async def test_circular_cause_chain_does_not_hang_handler(
    configured_settings: Callable[..., Settings],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Regression: a circular __cause__ chain must not hang the global handler."""
    settings = configured_settings()
    first = PersistenceException("first")
    second = PersistenceException("second")
    first.__cause__ = second
    second.__cause__ = first  # deliberately circular

    response = await asyncio.wait_for(
        application_exception_handler(_handler_request(settings), first), timeout=2
    )

    assert response.status_code == 500
    assert _last_logged_event(capsys)["cause_type"] == "PersistenceException"
