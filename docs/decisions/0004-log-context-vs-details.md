# ADR-0004: `log_context` vs. `details` on `ApplicationException`

## Context

An exception often needs to carry two different kinds of extra
information: data that helps a developer diagnose the failure later (an
internal id, a driver error code, an entity's internal state) and data
that's genuinely part of the API contract shown to the client. A single
field for "extra info" forces every author to choose between
under-informing whoever debugs the incident or over-exposing internals to
whoever calls the API.

## Decision

`ApplicationException` carries two separate fields. `details` is part of
the API contract — serialized to the client via `_envelope_json` in
`exception_handlers.py`. `log_context` is a sibling `dict[str, Any]` merged
into the global handler's log line but **never** serialized to a response.

```python
# Good
raise ConflictException(
    message="Report already published",
    code="REPORT_ALREADY_PUBLISHED",
    log_context={"report_id": report_id},
)

# Bad — leaks an internal id to the client
raise ConflictException(
    message="Report already published",
    code="REPORT_ALREADY_PUBLISHED",
    details={"report_id": report_id},
)
```

## Why

Without this split, a developer attaching diagnostic context to help debug
an incident (`student_id`, `exam_id`, an internal driver message) has
nowhere to put it except `details` — which means it either leaks to the
client or gets left out of the log entirely, making the incident harder to
diagnose later. The split lets both needs be met without trading one off
against the other.

It also composes with exception chaining: `application_exception_handler`
merges `log_context` from the *entire* `__cause__` chain (inner layers
first, outer wins on conflict), so context attached at a low layer — e.g. a
repository translating a persistence failure — still reaches the final log
line even though only the outermost exception is what actually propagates
up to the router.

## Rejected or deferred alternatives

- **A single `details` field used for both purposes.** Rejected as the
  exact failure mode this decision exists to prevent — `12-errors.md`'s own
  worked "Bad" example is precisely this: passing `report_id` via `details`
  "leaks an internal id to the client."
- **A separate `logger.*` call instead of `log_context`.** Rejected — if
  the exception is about to propagate or be re-raised, the global handler
  will already log it once; a second explicit log call produces two log
  lines for one incident (`12-errors.md`'s Logging section). `logger.*` is
  only appropriate when a failure is caught and handled, not re-raised.

## Rule reference

`12-errors.md` ("Log Context vs Details", "Logging").
