---
description: FastAPI presentation layer — routing, dependency injection, and request handling (REST semantics: 09-api-design.md).
globs: api/app/main.py, api/app/api/**/*.py, api/app/core/dependencies.py, api/app/core/middleware.py, api/app/modules/**/router.py
paths:
  - "api/app/main.py"
  - "api/app/api/**/*.py"
  - "api/app/core/dependencies.py"
  - "api/app/core/middleware.py"
  - "api/app/modules/**/router.py"
alwaysApply: false
---

# FastAPI Standards

This project uses the latest stable version of FastAPI.

FastAPI is the HTTP presentation layer.

FastAPI MUST remain a thin layer over the application.

Business logic MUST NEVER depend on FastAPI.

---

# Responsibilities

FastAPI is responsible for

- Receiving HTTP requests
- Parsing request bodies
- Dependency injection
- Authentication
- Authorization
- Calling use cases
- Returning HTTP responses

FastAPI is NOT responsible for

- Business logic
- Database access
- Transactions
- SQL generation
- Domain validation
- Complex transformations

---

# Architecture

Every request follows Router → Use Case → Repository → Database.
Full diagram: **`project.md`**.

`main.py` mounts only `app/api/router.py`. Module routers call use cases; use cases
call repositories. Never bypass this flow.

---

# Routers

Each module MUST expose exactly one router.

Example

```text
users/router.py
roles/router.py
reports/router.py
```

Routers should only define HTTP endpoints.

---

# APIRouter

Always use APIRouter.

Never place endpoints directly inside main.py.

Good

```python
router = APIRouter()
```

---

# Route Registration

`main.py` registers **exactly one** root router:

```python
from app.api.router import router as api_router

app.include_router(api_router)
```

The `app/api/` composition layer handles all version-specific routing:

```text
app/api/router.py      ← prefix="/api", includes v6 router
app/api/v6/router.py   ← prefix="/v6", includes all module routers
```

Module routers (`app/modules/<feature>/router.py`) define resource paths only
(e.g. `/users`, `/auth`). They know nothing about `/api/v6`.

Never register module routers directly in `main.py`.

Never manually duplicate routes.

---

# API Versioning

Every endpoint MUST use the version prefix defined in **`09-api-design.md`** (currently `/api/v6`).

Versioning is composed through `app/api/v6/router.py`. Modules are version-agnostic.

Never expose unversioned public endpoints.

---

# Application State

Long-lived resources live on `app.state`, initialized in `main.py` lifespan.
Full inventory and lifecycle: **`01-folder-structure.md`**'s "Application State" section.

Dependencies access these via `request.app.state`:

```python
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    factory = request.app.state.session_factory
    ...
```

---

# Route Naming

Routes MUST use nouns.

Good

```text
/users

/users/{id}

/schools

/reports
```

Avoid verbs.

Bad

```text
/createUser

/deleteSchool

/getReport
```

---

# HTTP Methods

GET

Retrieve resources.

Must not modify state.

---

POST

Create resources.

Execute business actions.

Use only when appropriate.

---

PUT

Replace an existing resource.

Must be idempotent.

---

PATCH

Partial updates.

Should be idempotent whenever practical.

---

DELETE

Remove a resource.

Whether hard or soft delete depends on business requirements.

---

# Status Codes

Use correct HTTP status codes for each outcome.

Canonical REST semantics and status usage: **`09-api-design.md`**.

Exception → status mapping: **`12-errors.md`**.

Never always return HTTP 200.

---

# Request Models

Every request body MUST use a Pydantic schema.

Never accept raw dictionaries.

Bad

```python
payload: dict
```

Good

```python
payload: CreateUserRequest
```

---

# Response Models

Every endpoint MUST define

response_model=

Never return arbitrary dictionaries.

Never expose ORM models.

Return response DTOs only.

---

# Dependency Injection

Always use FastAPI Depends().

Example

```python
Depends(get_user_repository)

Depends(get_current_user)
```

Avoid global objects.

---

# Dependency Scope

Dependencies should be request scoped.

Never cache request-specific dependencies globally.

---

# Authentication

Authentication belongs in dependencies.

Routers should receive authenticated users via Depends().

Example

```python
current_user: CurrentUser = Depends(get_current_user)
```

Never manually decode JWTs inside routers.

---

# Authorization

Authorization checks belong inside use cases unless they are purely HTTP concerns.

Avoid duplicating permission checks.

---

# Business Logic

Routers MUST NEVER

Perform calculations.

Execute SQL.

Contain business rules.

Commit transactions.

Call external APIs.

Modify repositories directly.

Routers only orchestrate requests.

---

# Async Endpoints

All endpoints MUST use

```python
async def
```

Avoid synchronous endpoints.

---

# Blocking Code

Never call blocking libraries inside async endpoints.

Never use

```python
requests
```

inside routes.

Never use

```python
time.sleep()
```

Use asynchronous alternatives.

---

# Validation

Pydantic handles request validation.

Business validation belongs inside use cases.

---

# Response Format

Every endpoint returns the standard `data`/`meta`/`error` envelope.
Full contract: **`10-response-format.md`**.

---

# Pagination

Collection endpoints should support

page

page_size

sorting

filters

search

Offset pagination is the project standard.

---

# Query Parameters

Complex filters should use query models.

Avoid dozens of independent parameters.

---

# File Uploads

File uploads should stream data.

Avoid loading entire files into memory.

Validate file size.

Validate MIME type.

Never trust file extensions.

---

# Error Handling

Routers must not build error responses or catch application exceptions locally.

Let typed exceptions propagate to global handlers in `app/core/exception_handlers.py`.

Full standards: **`12-errors.md`**. Response envelope: **`10-response-format.md`**.

Register handlers from `main.py`.

---

# Exception Handling

Do not use

```python
try:
    ...
except Exception:
    ...
```

inside endpoints.

Unexpected exceptions should propagate to global handlers.

---

# Route Size

Endpoints should normally remain under

30 lines.

If longer,

move logic into use cases.

---

# OpenAPI

Every endpoint MUST define

summary

description

response_model

tags

Example

```python
@router.post(
    "/users",
    summary="Create user",
    description="Creates a new user.",
    response_model=ApiResponse[UserResponse],
)
```

---

# Tags

Each module uses one tag.

Example

Users

Roles

Reports

Schools

Dashboard

---

# HTTP Exceptions

Prefer project-specific `ApplicationException` subclasses.

Do not raise `HTTPException` for business rules in routers.

HTTP status mapping belongs in global exception handlers (`12-errors.md`).

---

# Streaming

Large exports should use streaming responses.

Avoid building huge responses in memory.

---

# Request Context

Never access request state globally.

Pass required information through dependencies.

---

# Middleware

Middleware responsibilities

Logging

Request IDs

Timing

Security Headers

CORS

Compression

Routers should not duplicate middleware behavior.

---

# Lifespan

Use FastAPI lifespan events.

Avoid deprecated startup/shutdown decorators.

---

# Health Checks

Expose

```text
/api/v6/health

/api/v6/ready
```

Health endpoints should not contain business logic.

---

# Documentation

Swagger remains enabled.

Document all public endpoints.

Keep examples current.

---

# Cursor and Claude MUST NEVER

Generate sync endpoints.

Generate database code inside routers.

Generate SQL inside routers.

Generate business logic inside routers.

Generate transactions inside routers.

Generate commit() inside routers.

Generate rollback() inside routers.

Generate HTTPException for business rules.

Generate print() debugging.

Generate duplicated authentication logic.

Generate duplicated authorization logic.

Generate routes without response_model.

Generate raw dictionaries as request bodies.

Generate ORM models as responses.

Generate endpoints longer than 30 lines.

Generate inconsistent response formats.

Generate unversioned APIs.

---

# Final Principle

The router is an adapter between HTTP and the application.

Its responsibility is to translate requests into use case invocations and translate results into HTTP responses.

Nothing more.