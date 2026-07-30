# ADR-0003: Global exception handlers own HTTP translation

## Context

Every layer — repository, use case, router — can fail, and each failure
eventually needs to become one consistent HTTP response with a stable
error code, status, and envelope shape. If each router decided for itself
how to render a given failure, the mapping from exception to HTTP response
would only be a convention every author has to remember, not something
the codebase actually guarantees.

## Decision

Exceptions propagate upward — Repository → Use Case → Router — becoming
more abstract as they go (a raw persistence exception becomes an
`ApplicationException` subclass before it leaves the repository). They are
converted to HTTP responses in exactly one place: `app/core/
exception_handlers.py`, registered once in `main.py`. Routers never wrap
use case calls in `try/except` for application exceptions, never build
error JSON manually, and never raise `HTTPException` for business rules.

## Why

Centralizing translation is what makes the "one exception → one HTTP
status" mapping (`12-errors.md`'s Recommended Mapping table) an actual
guarantee instead of a convention. If ten different routers each
individually decided how to render a `ConflictException`, the mapping
would only hold as long as every author remembered it correctly. It also
means routers stay completely ignorant of HTTP-response mechanics for
error cases — matching `00-philosophy.md`'s separation-of-concerns
principle — and it's the only place that needs to know the
log-level-per-exception-category table (`12-errors.md`/`21-logging.md`),
so that mapping can't drift between call sites either.

## Rejected or deferred alternatives

- **Per-router `try/except` blocks translating exceptions locally.**
  Rejected explicitly — `12-errors.md`: "Routers MUST NOT wrap use cases in
  try/except for application exceptions... duplicate handler logic per
  endpoint."
- **Raising `HTTPException` directly for business failures.** Rejected —
  `HTTPException` is reserved for `app/core/exception_handlers.py` and rare,
  explicitly documented presentation-only cases, never for business rules
  raised anywhere else in the stack.
- **A response-building helper function routers call individually.**
  Rejected for the same reason as the first alternative — it still
  distributes response-shaping logic across every router instead of
  centralizing it in one place that's registered once.

## Rule reference

`12-errors.md`, `03-fastapi.md`.
