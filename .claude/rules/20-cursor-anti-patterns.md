---
description: Always-on guardrails for code generation — layering, exceptions, and rule index.
alwaysApply: true
---

# Cursor and Claude generation guardrails

These rules apply to both AI assistants used on this project: **Cursor** and
**Claude Code**. Each is an implementation assistant, not an architect. Follow
existing project rules; do not invent new patterns.

## Non-negotiables

- **Layering:** Router → Use Case → Repository → Database. No bypassing.
- **Business logic:** Only in use cases or domain entities — never in routers, repositories, ORM models, Pydantic schemas, or middleware.
- **SQL / ORM:** Only in repositories. Never return ORM models outside repositories.
- **Transactions:** Only use cases commit or rollback. Repositories never `commit()` or `rollback()`.
- **Errors:** Raise typed `ApplicationException` subclasses; let them propagate. **Global handlers** in `app/core/exception_handlers.py` build HTTP responses (`12-errors.md`). Routers must not hand-build error JSON or wrap use cases in `try/except` for app exceptions.
- **HTTPException:** Only in `app/core/exception_handlers.py` (rare documented presentation cases). Not in routers, use cases, domain, or repositories.
- **Never:** generic `Exception` for business failures, bare `except`, swallowed errors, `pass` in `except`, stack traces to clients, secrets in code or logs.

## Routing and versioning

`main.py` mounts exactly one router (`app.include_router(api_router)` from
`app/api/router.py`); `app/api/` contains only `APIRouter`/`include_router()`
composition, never endpoints or an `app/api/v6/auth.py`-style duplicate of a
module router. Full rules: **`01-folder-structure.md`**'s "API Composition
Layer" section.

## Application state

Long-lived resources (`settings`, `engine`, `session_factory`) live on `app.state`,
set in `main.py` lifespan — never module-level globals. Full inventory:
**`01-folder-structure.md`**.

- **NEVER** create module-level mutable globals for engine or session factory.
- `get_db` reads `session_factory` from `request.app.state`. Never access global variables for DB connections.

## ORM model ownership

- ORM models live centrally in `app/database/models/`. Each model is owned by exactly one module.
- Only that module's repositories may import an ORM model. No other layer accesses ORM models.

## When two rules seem to conflict

Precedence order and the full rule-file index: **`project.md`**.

## When unsure

- Match conventions in the nearest existing module.
- Prefer explicit, testable code over clever abstractions.
- Preserve backward compatibility with the legacy system (`19-legacy-db.md`).
