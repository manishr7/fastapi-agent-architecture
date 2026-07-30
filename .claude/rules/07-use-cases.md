---
description: Defines Application Use Case standards. Use Cases orchestrate business workflows, transactions, repositories, and domain entities while remaining independent of HTTP, SQLAlchemy, and infrastructure.
globs: api/app/**/use_cases/**/*.py
paths:
  - "api/app/**/use_cases/**/*.py"
alwaysApply: false
---

# ============================================================
# Application Layer
# Use Case Standards
# ============================================================

# Philosophy

Use Cases represent business workflows.

They coordinate business operations.

They do NOT represent HTTP endpoints.

They do NOT represent database operations.

Every business action should exist as a dedicated Use Case.

---

# Responsibilities

A Use Case is responsible for

- orchestrating repositories
- enforcing business rules
- coordinating transactions
- validating business invariants
- interacting with multiple aggregates
- producing application results

Nothing else.

---

# Dependency Direction

Router

↓

Use Case

↓

Repository

↓

Database

Never reverse this dependency.

---

# Framework Independence

Use Cases must not depend on

- FastAPI
- SQLAlchemy
- Pydantic
- AsyncSession
- APIRouter
- Depends
- HTTPException

They must remain pure Python.

---

# Use Case Scope

Each Use Case represents

one business operation.

Examples

CreateUser

UpdateTeacher

PublishReport

AssignRole

GenerateCertificate

Never create generic use cases.

---

# Naming

Use explicit names.

Good

CreateSchoolUseCase

ApproveInvoiceUseCase

ArchiveReportUseCase

Bad

UserService

CommonService

Manager

Processor

Utility

---

# One Responsibility

One Use Case

↓

One business workflow.

Avoid multiple unrelated responsibilities.

---

# Entry Point

Every Use Case exposes

one public method.

Recommended

```python
async def execute(...)
```

Avoid multiple public entry points.

---

# Constructor

Dependencies should be injected.

Example

```python
class CreateUserUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        ...
```

Never instantiate repositories internally.

---

# Dependency Injection

Use Cases receive dependencies.

They do not create dependencies.

Good

Repository injected.

Bad

Repository instantiated.

---

# Repository Usage

Repositories provide persistence.

Use Cases decide

when

and

how

repositories are used.

---

# Business Logic

All business logic belongs here

unless it naturally belongs

inside a Domain Entity.

Never place business rules

inside repositories

or routers.

---

# Transactions

Use cases own transaction boundaries (commit, rollback, one transaction per workflow).

Repositories never commit or rollback.

Full standards: **`13-transactions.md`**.

---

# Validation

Separate HTTP validation, business validation, and database validation by layer.

Full standards: **`11-validation.md`**.

HTTP validation → router/schemas.

Business validation → use case / domain.

Database validation → database constraints (repositories surface as application exceptions).

---

# Business Invariants

Verify all invariants

before persistence

whenever possible.

---

# Domain Entities

Use Cases operate

on Domain Entities

not ORM Models.

---

# Mapping

Repositories

↓

Domain

↓

Use Case

↓

Domain

↓

Repository

Never manipulate ORM objects.

---

# Multiple Repositories

Use Cases may coordinate

multiple repositories.

Repositories should never coordinate each other.

---

# Repository Communication

Repositories should never call

other repositories.

Only Use Cases coordinate.

---

# Side Effects

Use Cases coordinate

side effects

after successful business operations.

Examples

Email

Notifications

Audit

Events

External APIs

Do not perform side effects

before successful completion.

---

# Ordering

Business workflow order

must be explicit.

Avoid hidden execution order.

---

# Idempotency

Critical operations

must be idempotent.

Examples

Payments

Purchases

Certificate Generation

Report Publishing

Avoid duplicate effects.

---

# External APIs

External services belong

outside repositories.

Use Cases coordinate

external interactions.

---

# File Storage

File operations

should be coordinated

by Use Cases

never repositories.

---

# Background Jobs

Scheduling background work

belongs

to Use Cases.

Repositories should never enqueue jobs.

---

# Domain Events

Use Cases may publish

Domain Events

after successful completion.

Entities do not publish directly.

---

# Error Handling

Handle expected

business failures.

Unexpected failures

should propagate.

---

# Exceptions

Raise

Domain Exceptions

or

Application Exceptions.

Never raise HTTPException.

---

# Return Values

Use Cases should return

- Domain Entities
- DTOs
- Result Objects

Never ORM Models.

---

# DTOs

Response DTOs belong

to the Application layer.

Avoid exposing persistence models.

---

# Determinism

A Use Case

given identical inputs

and identical persistence state

should produce identical results.

---

# Logging

Business events

may be logged.

Avoid excessive logging.

Never log sensitive information.

Never log a propagated `ApplicationException` yourself — full rule and
`log_context` mechanics: `12-errors.md`'s "Logging" section.

---

# Authorization

Authorization decisions

belong here

or dedicated authorization policies.

Do not rely solely

on routers.

---

# Authentication

Authentication

should already be complete

before entering Use Cases.

---

# Time

Avoid

datetime.now()

inside business logic.

Inject time

or pass timestamps.

---

# Randomness

Avoid generating

random values

inside business logic.

Inject randomness.

---

# Configuration

Avoid reading

environment variables

inside Use Cases.

Configuration should be injected.

---

# Async

Use Cases performing I/O

must be asynchronous.

Pure computation

may remain synchronous.

---

# Performance

Avoid unnecessary

database calls.

Avoid duplicate repository operations.

---

# Loops

Never commit

inside loops.

Never flush

inside loops

without justification.

---

# Readability

Prefer

small

focused

predictable

Use Cases.

Split large workflows

into helper methods.

---

# Size

Target

100-300 lines.

Large Use Cases

usually indicate

multiple workflows.

---

# Private Methods

Private helper methods

are encouraged

when they improve readability.

---

# Orchestration

Use Cases orchestrate.

They do not become

God Objects.

---

# State

Avoid mutable global state.

Keep execution isolated.

---

# Testing

Use Cases

must be testable

without HTTP

without SQLAlchemy

without FastAPI

Repositories may be mocked

or replaced by test implementations.

---

# Cursor and Claude MUST NEVER

Generate FastAPI imports

Generate SQLAlchemy imports

Generate ORM Models

Generate AsyncSession

Generate APIRouter

Generate Depends

Generate HTTPException

Generate commit() in repositories

Generate rollback() in repositories

Generate repository-to-repository calls

Generate routers calling multiple repositories

Generate business logic inside routers

Generate business logic inside repositories

Generate SQL inside Use Cases

Generate HTTP requests inside repositories

Generate ORM Models returned to routers

Generate environment variable reads

Generate duplicated business rules

Generate utility service classes

Generate God Objects

Generate multiple unrelated workflows

inside one Use Case

---

# Example Flow

Router

↓

Request Schema

↓

Use Case.execute()

↓

Repository

↓

Domain Entity

↓

Business Logic

↓

Repository

↓

Commit

↓

Response DTO

↓

Router

---

# Final Principle

Use Cases are the application's brain.

Routers translate HTTP.

Repositories translate persistence.

Domain Entities model business concepts.

The Use Case coordinates all of them while remaining completely independent of frameworks, databases, and transport protocols.