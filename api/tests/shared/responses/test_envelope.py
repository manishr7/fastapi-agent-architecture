import structlog

from app.shared.responses.envelope import error_response, success_response


def test_success_response_has_empty_meta_outside_request_context() -> None:
    # tracing_meta() reads structlog.contextvars, which only middleware
    # binds during a real HTTP request — a plain unit test outside that
    # context gets an empty dict, not an error.
    response = success_response({"status": "ok"})

    assert response.data == {"status": "ok"}
    assert response.meta == {}
    assert response.error is None


def test_success_response_includes_bound_tracing_ids() -> None:
    with structlog.contextvars.bound_contextvars(
        correlation_id="corr-1",
        request_id="req-1",
    ):
        response = success_response({"status": "ok"})

    assert response.meta == {"correlation_id": "corr-1", "request_id": "req-1"}


def test_explicit_meta_layers_on_top_of_tracing_ids_not_replacing_them() -> None:
    # 10-response-format.md / envelope.py's own comment: passing meta must
    # never silently drop request_id/correlation_id from the response.
    with structlog.contextvars.bound_contextvars(
        correlation_id="corr-1",
        request_id="req-1",
    ):
        response = success_response({"status": "ok"}, meta={"total": 5})

    assert response.meta == {
        "correlation_id": "corr-1",
        "request_id": "req-1",
        "total": 5,
    }


def test_error_response_shape() -> None:
    response = error_response(
        code="NOT_FOUND",
        message="The requested resource does not exist.",
        details={"resource_id": 42},
    )

    assert response.data is None
    assert response.error is not None
    assert response.error.code == "NOT_FOUND"
    assert response.error.message == "The requested resource does not exist."
    assert response.error.details == {"resource_id": 42}


def test_error_response_defaults_details_to_empty_dict() -> None:
    response = error_response(code="NOT_FOUND", message="Not found")

    assert response.error is not None
    assert response.error.details == {}
