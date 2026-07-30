import logging
import sys
from typing import Any

import structlog

from app.core.config import Settings

_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "cookie",
        "api_key",
        "secret",
        "credit_card",
        "ssn",
    }
)
_REDACTED = "***REDACTED***"
_UVICORN_LOGGER_NAMES = ("uvicorn", "uvicorn.error")


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _REDACTED if key.lower() in _SENSITIVE_KEYS else _redact_value(nested)
            for key, nested in value.items()
        }
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def _redact_sensitive(
    _logger: structlog.typing.WrappedLogger,
    _method_name: str,
    event_dict: structlog.typing.EventDict,
) -> structlog.typing.EventDict:
    for key, value in event_dict.items():
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = _REDACTED
        else:
            event_dict[key] = _redact_value(value)
    return event_dict


def _add_service(service_name: str) -> structlog.typing.Processor:
    def processor(
        _logger: structlog.typing.WrappedLogger,
        _method_name: str,
        event_dict: structlog.typing.EventDict,
    ) -> structlog.typing.EventDict:
        event_dict.setdefault("service", service_name)
        return event_dict

    return processor


def configure_logging(settings: Settings) -> None:
    """Configure structlog as the single logging pipeline for app and stdlib loggers."""
    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_service(settings.app_name),
        _redact_sensitive,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.typing.Processor = (
        structlog.processors.JSONRenderer()
        if settings.resolved_log_format == "json"
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level)

    for logger_name in _UVICORN_LOGGER_NAMES:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    # RequestContextMiddleware's "request_completed" event is the project's
    # access log. uvicorn's own access logger would otherwise emit a second,
    # differently-shaped line for every request — disable it rather than
    # double the log volume the "request_started" DEBUG-gating already
    # avoids.
    logging.getLogger("uvicorn.access").disabled = True

    if not settings.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
