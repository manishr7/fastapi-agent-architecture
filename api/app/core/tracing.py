import structlog


def tracing_meta() -> dict[str, str]:
    """Request-scoped tracing ids from structlog contextvars (empty outside HTTP)."""
    ctx = structlog.contextvars.get_contextvars()
    meta: dict[str, str] = {}
    if correlation_id := ctx.get("correlation_id"):
        meta["correlation_id"] = str(correlation_id)
    if request_id := ctx.get("request_id"):
        meta["request_id"] = str(request_id)
    return meta
