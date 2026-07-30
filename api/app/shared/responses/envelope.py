from typing import Any

from pydantic import BaseModel, ConfigDict

from app.core.tracing import tracing_meta


class ErrorBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, Any] = {}


class ApiResponse[T](BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: T | None
    meta: dict[str, Any]
    error: ErrorBody | None


def _resolved_meta(meta: dict[str, Any] | None) -> dict[str, Any]:
    # Tracing ids are always present; explicit meta (e.g. pagination) layers
    # on top rather than replacing them, so passing meta never silently
    # drops request_id/correlation_id from the response.
    return {**tracing_meta(), **(meta or {})}


def success_response[T](
    data: T,
    meta: dict[str, Any] | None = None,
) -> ApiResponse[T]:
    return ApiResponse(
        data=data,
        meta=_resolved_meta(meta),
        error=None,
    )


def error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> ApiResponse[None]:
    return ApiResponse(
        data=None,
        meta=_resolved_meta(meta),
        error=ErrorBody(code=code, message=message, details=details or {}),
    )
