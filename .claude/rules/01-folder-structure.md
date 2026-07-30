---
description: Defines the mandatory backend project structure and high-level organization.
globs: api/app/main.py, api/app/**/__init__.py, api/app/api/**/*.py
paths:
  - "api/app/main.py"
  - "api/app/**/__init__.py"
  - "api/app/api/**/*.py"
alwaysApply: false
---

# Backend Folder Structure

This project follows a **feature-first architecture**.

Business domains are the primary organizational unit.

The folder structure is considered part of the architecture and must remain consistent across the codebase.

---

# Goals

The structure should promote:

- High cohesion
- Low coupling
- Clear ownership
- Predictable navigation
- Scalability
- Testability

Avoid organizing code primarily by technical type.

Avoid large global folders containing unrelated files.

---

# Root Structure

Application code MUST remain inside `app/`.

Recommended project layout:

```text
api/

    alembic.ini

    migrations/

        versions/

    tests/

    app/

        api/             ← HTTP composition layer (routing only)

        core/

        modules/

        shared/

        infrastructure/

        database/

        scripts/

        main.py
```

Additional top-level folders are allowed only for:

- documentation
- deployment
- Docker
- CI/CD
- tooling
- infrastructure

Examples

```text
docs/

docker/

deploy/

.github/
```

Business code must never exist outside `app/`.

---

# API Composition Layer

`app/api/` contains **HTTP routing composition only**.

```text
app/api/
    router.py          ← root router: prefix="/api", includes v6
    v6/
        router.py      ← v6 router: prefix="/v6", includes all module routers
    v7/
        router.py      ← (future) when breaking API changes require a new version
```

**Rules for `app/api/`:**

- Contains ONLY `APIRouter` instantiation and `include_router()` calls.
- MUST NOT contain endpoint implementations, business logic, use cases, repositories, SQL, or schemas.
- MUST NOT duplicate module routers. No `app/api/v6/auth.py` or `app/api/v6/health.py`.
- All endpoint implementations remain exclusively inside `app/modules/<feature>/router.py`.
- Module routers are version-agnostic: they define `/users`, `/auth`, `/health`.
- The `app/api/` layer adds `/api/v6` through composition only.

`main.py` imports only `api_router` from `app/api/router.py` and calls `app.include_router(api_router)` once.

---

# Core

`app/core/`

Contains application-wide functionality.

Examples

```text
config.py

security.py

middleware.py

logging.py

exceptions.py

exception_handlers.py

tracing.py

dependencies.py

constants.py
```

Core may contain:

- configuration
- logging
- middleware
- dependency providers (`get_db`, `get_current_user`)
- security utilities
- global exception handling

Core MUST NOT contain:

- business logic
- repositories
- ORM models
- use cases

Core must not depend on feature modules.

---

# Modules

Business functionality belongs inside:

```text
app/modules/
```

Example

```text
auth/

users/

roles/

permissions/

schools/

dashboard/

reports/
```

Each module owns its business logic.

Modules should communicate through public Use Cases when interaction is necessary.

Modules must not directly manipulate another module's database models.

---

# Per-module layout

Every module under `app/modules/<module>/` MUST use this layout:

```text
app/modules/<module>/
    router.py
    schemas/
    use_cases/
    domain/
    repositories/
```

- `router.py` — sole HTTP entry for the module (one router per module). Module-specific DI factories (`_get_*_repository`, `_get_*_use_case`) may live here.
- `schemas/` — Pydantic request/response DTOs.
- `use_cases/` — application workflows and transaction ownership.
- `domain/` — domain entities and business invariants.
- `repositories/` — persistence and ORM access.

Do not place business logic in `router.py` or `schemas/`.

Every router must remain version-agnostic. Versioning is the `app/api/` layer's concern.

---

# ORM Model Ownership

ORM models live in `app/database/models/` (centralized, for Alembic and shared metadata).

Each ORM model file is **owned by exactly one feature module**.

Only that module's repositories may import and use that model.

No other module or layer may import ORM models directly.

Cross-module data access must go through the owning module's public Use Case interface.

---

# Shared

Contains reusable components.

Examples

```text
pagination/

responses/

filters/

types/

enums/

utils/
```

Shared code must remain generic.

If functionality is only used by one module, it belongs inside that module.

---

# Infrastructure

Contains external integrations.

Examples

```text
email/

sms/

storage/

cloud/

third_party/

redis/         ← client lifecycle, cache, distributed locks (see 22-redis.md)
```

Infrastructure implements external concerns.

Business logic must never live here.

---

# Database

Contains persistence configuration.

```text
database/

    session.py     ← factory functions only; no global state

    base.py

    models/        ← ORM model files (owned per-module, centralized for Alembic)
```

Responsibilities

- SQLAlchemy engine and session factory creation functions
- database base class and metadata
- ORM models

Engine and session factory lifecycle is managed via `app.state` in `main.py` lifespan.

Repositories are the only layer that should interact with ORM models.

---

# Application State (`app.state`)

Long-lived application resources are stored on `app.state` and initialized in `main.py`'s lifespan.

Minimum required:

- `app.state.settings` — set in `create_app()` before lifespan
- `app.state.engine` — set in lifespan startup, cleared on shutdown
- `app.state.session_factory` — set in lifespan startup, cleared on shutdown
- `app.state.redis` — set in lifespan startup, cleared on shutdown (`22-redis.md`)

Future resources (httpx.AsyncClient, metrics, tracing) follow the same pattern: initialize in lifespan, store on `app.state`, access via `request.app.state` in dependencies.

---

# Migrations

Alembic lives at the **`api/`** package root (not inside `app/`). Standards: **`18-alembic.md`**.

```text
api/migrations/

    versions/

api/alembic.ini
```

Rules

- Never edit migration history manually.
- Every schema change requires a migration.
- Schema changes must remain reversible whenever practical.

---

# Tests

Tests should mirror the application structure.

```text
api/tests/

    api/       ← routing smoke tests (prefix, registration, OpenAPI)

    modules/

    core/

    shared/
```

Each module should have corresponding tests under `tests/modules/<module>/` (see `17-testing.md`).

---

# Scripts

Operational scripts belong here.

Examples

- seed database
- import legacy data
- maintenance
- scheduled jobs

Scripts must never become part of request handling.

---

# Folder Creation Rules

Before creating a new folder, consider:

1. Is this a new business domain?
2. Can this live inside an existing module?
3. Will this folder contain more than one meaningful file?

Avoid unnecessary nesting.

Avoid placeholder folders.

This guidance governs ad hoc folders outside the standard module layout.
The five folders required under "Per-module layout" above are a fixed
structural convention, not a case-by-case judgment call — they remain
required even when a given module's folder holds only one file.

---

# General Rules

- Organize by business domain.
- Keep related code together.
- Prefer explicit folder names.
- Avoid ambiguous names.
- Folder structure should remain predictable across the project.

Folder structure changes should be deliberate architectural decisions.
