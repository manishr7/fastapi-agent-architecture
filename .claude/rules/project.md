---
description: fastapi-agent-architecture — stack, layout, and cross-cutting conventions
alwaysApply: true
---

# FastAPI Agent Architecture

Open this repository's root as your workspace — the Cursor workspace folder, or
the directory you launch `claude` from — so rule globs and paths resolve
correctly.

| Path | Stack | Role |
|------|--------|------|
| `web/` | Next.js (App Router), TypeScript, React | Web UI |
| `api/` | FastAPI, Python 3.12+ | REST API, use cases, persistence |

Application code lives under **`api/app/`**.

## Architecture (non-negotiable)

```text
main.py (bootstrap only)
  └── app/api/router.py          ← /api
        └── app/api/v6/router.py ← /v6 (routing composition only)
              └── modules/*/router.py

HTTP Request → Router → Use Case → Repository → Database
```

- `main.py` — pure composition root: factory, `app.state`, middleware, exception handlers, lifespan.
- `app/api/` — HTTP routing composition only. No endpoints, no business logic.
- `app/modules/<feature>/router.py` — all endpoint implementations. Version-agnostic.
- Domain and use cases remain framework-independent.
- HTTP error translation: **global exception handlers** in `api/app/core/exception_handlers.py` (see `12-errors.md`).

## Application State

Long-lived resources are stored on `app.state`, set in `main.py` lifespan.
Full inventory: **`01-folder-structure.md`**'s "Application State" section.

## Rule precedence (when rules overlap)

1. `12-errors.md` — HTTP errors, handlers, status mapping
2. `13-transactions.md` — commits, rollbacks, session boundaries
3. `11-validation.md` — validation layer split
4. `10-response-format.md` — JSON response envelope
5. `09-api-design.md` — REST semantics and HTTP codes
6. `00-philosophy.md` — decision priority

## Backend rule index (`00`–`22`)

| File | Topic |
|------|--------|
| `00-philosophy.md` | Constitution, SOLID, layering |
| `01-folder-structure.md` | Project and module layout, `app/api/` layer, `app.state` |
| `02-python.md` | Python language and style |
| `03-fastapi.md` | Routers, DI, `app.state`, presentation wiring |
| `04-async.md` | Async runtime, event loop, no module globals |
| `05-sqlalchemy-part-1.md` | Engine, AsyncSession lifecycle, `app.state` |
| `05-sqlalchemy-part-2.md` | ORM models, relationships |
| `05-sqlalchemy-part-3.md` | Queries, N+1, DB performance |
| `06-domain-entities.md` | Domain entities |
| `07-use-cases.md` | Use cases |
| `08-repositories.md` | Repositories, ORM model ownership |
| `09-api-design.md` | REST API design, versioning via `app/api/` |
| `10-response-format.md` | Response envelope |
| `11-validation.md` | Validation by layer |
| `12-errors.md` | Exceptions and handlers |
| `13-transactions.md` | Transactions |
| `14-concurrency.md` | DB concurrency, idempotency |
| `15-security.md` | Security |
| `16-performance.md` | Application performance |
| `17-testing.md` | Tests |
| `18-alembic.md` | Migrations |
| `19-legacy-db.md` | Legacy database |
| `20-cursor-anti-patterns.md` | Always-on generation guardrails |
| `21-logging.md` | Structured logging, request/correlation ids, log levels |
| `22-redis.md` | Redis lifecycle, cache vs lock, deferred rate-limiting/pubsub |

## Backend tooling

- **Lint/format:** `ruff check --fix` + `ruff format` via pre-commit (see `.pre-commit-config.yaml`)
- **Tests:** `pytest` (`17-testing.md`)
- **Type checking:** add pyright/basedpyright when codebase grows

Configure in `api/pyproject.toml`.

## Frontend and CI

- **Frontend rules:** TBD — `nextjs-frontend.md` applies under `web/` when content is added.
- **CI / Docker:** TBD when `.github/` or `docker/` exist.
