import asyncio
import json
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient, Response
from starlette.requests import Request

from app.core.config import Settings
from app.core.logging import _redact_sensitive, configure_logging
from app.core.middleware import RequestContextMiddleware
from app.main import app


def test_redact_sensitive_masks_known_keys() -> None:
    event_dict = {
        "event": "login_attempt",
        "password": "hunter2",
        "authorization": "Bearer xyz",
        "user_id": 42,
        "details": {"token": "abc", "note": "ok"},
    }

    redacted = _redact_sensitive(None, "info", event_dict)

    assert redacted["password"] == "***REDACTED***"
    assert redacted["authorization"] == "***REDACTED***"
    assert redacted["user_id"] == 42
    assert redacted["details"]["token"] == "***REDACTED***"
    assert redacted["details"]["note"] == "ok"


def test_redact_sensitive_masks_keys_inside_lists() -> None:
    event_dict = {
        "event": "bulk_import",
        "users": [
            {"email": "a@example.com", "password": "hunter2"},
            {"email": "b@example.com", "password": "hunter3"},
        ],
    }

    redacted = _redact_sensitive(None, "info", event_dict)

    assert redacted["users"][0]["password"] == "***REDACTED***"
    assert redacted["users"][1]["password"] == "***REDACTED***"
    assert redacted["users"][0]["email"] == "a@example.com"
    assert redacted["users"][1]["email"] == "b@example.com"


async def _get_health(
    capsys: pytest.CaptureFixture[str], **headers: str
) -> tuple[Response, list[dict[str, Any]]]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v6/health", headers=headers)
    captured = capsys.readouterr()
    events = [json.loads(line) for line in captured.out.splitlines() if line.strip()]
    return response, events


@pytest.mark.asyncio
async def test_request_completed_is_logged_with_ids(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="INFO", DEBUG=False))

    response, events = await _get_health(capsys)

    completed = [e for e in events if e.get("event") == "request_completed"]
    assert len(completed) == 1
    assert completed[0]["status_code"] == response.status_code
    assert completed[0]["level"] == "info"
    assert completed[0]["outcome"] == "success"
    assert "request_id" in completed[0]
    assert "correlation_id" in completed[0]
    assert "service" in completed[0]


@pytest.mark.asyncio
async def test_context_does_not_leak_between_requests(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="INFO", DEBUG=False))

    first_response, first_events = await _get_health(capsys)
    second_response, second_events = await _get_health(capsys)

    first_id = first_response.headers["X-Request-ID"]
    second_id = second_response.headers["X-Request-ID"]
    assert first_id != second_id

    first_completed = next(e for e in first_events if e.get("event") == "request_completed")
    second_completed = next(e for e in second_events if e.get("event") == "request_completed")
    assert first_completed["request_id"] == first_id
    assert second_completed["request_id"] == second_id
    assert first_id not in json.dumps(second_events)


@pytest.mark.asyncio
async def test_request_started_is_debug_only(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="INFO", DEBUG=False))
    _, events_at_info = await _get_health(capsys)
    assert not any(e.get("event") == "request_started" for e in events_at_info)

    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="DEBUG", DEBUG=False))
    _, events_at_debug = await _get_health(capsys)
    assert any(e.get("event") == "request_started" for e in events_at_debug)


@pytest.mark.asyncio
async def test_correlation_id_is_echoed_from_incoming_header(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="INFO", DEBUG=False))

    response, _ = await _get_health(capsys, **{"X-Correlation-ID": "fixed-correlation-id"})

    assert response.headers["X-Correlation-ID"] == "fixed-correlation-id"
    assert response.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_request_id_is_never_reused_from_client_header(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="INFO", DEBUG=False))

    response, _ = await _get_health(capsys, **{"X-Request-ID": "client-supplied-id"})

    assert response.headers["X-Request-ID"] != "client-supplied-id"


@pytest.mark.asyncio
async def test_cancelled_request_still_logs_and_reraises(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Regression: call_next raising a BaseException (e.g. a client-disconnect
    CancelledError, which unhandled_exception_handler never sees since it's
    registered for Exception only) must still produce one log line, and must
    never be swallowed."""
    configure_logging(Settings(LOG_FORMAT="json", LOG_LEVEL="INFO", DEBUG=False))
    middleware = RequestContextMiddleware(app=lambda scope, receive, send: None)
    request = Request(scope={"type": "http", "method": "GET", "path": "/health", "headers": []})

    async def failing_call_next(_request: Request) -> None:
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        await middleware.dispatch(request, failing_call_next)

    captured = capsys.readouterr()
    events = [json.loads(line) for line in captured.out.splitlines() if line.strip()]
    assert any(e.get("event") == "request_cancelled" for e in events)
    assert not any(e.get("event") == "request_completed" for e in events)
