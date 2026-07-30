---
description: Defines enterprise Domain Entity standards. Domain entities represent business concepts and remain completely independent of infrastructure, persistence, and frameworks.
globs: api/app/**/domain/**/*.py
paths:
  - "api/app/**/domain/**/*.py"
alwaysApply: false
---

# ============================================================
# Domain Entity Standards
# ============================================================

# Philosophy

The Domain layer is the center of the application.

Everything else exists to support it.

The Domain must never depend on

- FastAPI
- SQLAlchemy
- Pydantic
- MySQL
- HTTP
- JSON
- Environment variables
- Infrastructure

Dependencies always point inward.

---

# Purpose

Domain Entities represent

business concepts

not

database tables.

A User entity represents a user.

It does NOT represent a SQLAlchemy model.

---

# Independence

The Domain layer must compile independently.

It should be possible to import every domain module without installing

- FastAPI
- SQLAlchemy
- asyncmy
- Alembic

---

# Domain Contents

The Domain layer may contain

- Entities
- Value Objects
- Enums
- Business Rules
- Domain Exceptions
- Domain Services
- Specifications
- Constants

Nothing else.

---

# Forbidden Dependencies

Never import

fastapi

sqlalchemy

pydantic

requests

httpx

AsyncSession

APIRouter

Depends

BaseModel

mapped_column

relationship

Engine

Session

---

# Entity Definition

Entities model business concepts.

Entities are NOT ORM models.

Entities are NOT DTOs.

Entities are NOT API schemas.

---

# Identity

Every Entity has an identity.

Identity defines equality.

Do not compare entities by memory address.

---

# Equality

Entities with the same identity

represent the same business object.

Equality should be identity-based.

---

# Immutability

Entities should be immutable whenever practical.

Prefer

```python
@dataclass(frozen=True, slots=True)
```

Mutable entities require explicit justification.

---

# Slots

Always use

slots=True

unless mutation or dynamic attributes require otherwise.

---

# Dataclasses

Prefer dataclasses.

Avoid handwritten boilerplate.

---

# Constructors

Constructors should guarantee

valid business state.

Never allow invalid entities to exist.

---

# Validation

Business validation belongs

inside the Domain.

Database validation belongs

inside the database.

HTTP validation belongs

inside API schemas.

---

# Invariants

Entities enforce invariants.

Invalid business state should be impossible.

Example

A negative quantity should never exist.

---

# Business Behavior

Entities should contain behavior.

Avoid anemic models.

Good

```python
order.cancel()

invoice.mark_paid()

teacher.assign_class()
```

Bad

```python
order.status = "cancelled"
```

---

# Encapsulation

Protect internal state.

Avoid exposing mutable collections directly.

---

# Collections

Prefer tuples

over mutable lists

for read-only collections.

---

# Primitive Obsession

Avoid excessive primitive types.

Prefer Value Objects.

Good

Email

Money

Percentage

PhoneNumber

AcademicYear

SchoolCode

Bad

str

str

float

str

str

---

# Value Objects

Value Objects

have no identity.

Equality is based entirely on values.

They should be immutable.

---

# Enums

Business constants should be Enums.

Avoid magic strings.

Good

```python
UserStatus.ACTIVE
```

Bad

```python
"ACTIVE"
```

---

# Exceptions

Business rule violations should raise

Domain Exceptions.

Never raise HTTPException.

---

# Domain Services

Use Domain Services

only when behavior

does not naturally belong

to a single entity.

Avoid unnecessary services.

---

# Side Effects

Entities should not perform

I/O

database access

HTTP requests

logging

email

RabbitMQ publishing

file operations

---

# Time

Avoid directly calling

datetime.now()

inside entities.

Inject time

or

pass timestamps

when needed.

---

# Randomness

Avoid generating random values

inside entities.

Inject randomness

when required.

---

# IDs

Entity IDs should be immutable.

Never change identity.

---

# Business Rules

Business rules belong

inside the Domain.

Never duplicate them

inside routers

repositories

or schemas.

---

# Persistence Ignorance

Entities must not know

how they are stored.

They should remain persistence ignorant.

---

# Serialization

Entities should not implement

JSON serialization

API serialization

database serialization

Frameworks perform serialization.

---

# Mapping

Repositories map

ORM

↓

Domain Entity

Use Cases consume

Domain Entity

Routers consume

DTOs

Never bypass mapping.

---

# ORM

Never inherit from SQLAlchemy Base.

Never use

Mapped

relationship

mapped_column

Column

ForeignKey

inside Domain.

---

# Pydantic

Never inherit from BaseModel.

Domain Entities are not request models.

---

# Business Methods

Methods should express

business language.

Good

activate()

archive()

publish()

withdraw()

approve()

reject()

Bad

set_status()

update_flag()

modify_state()

---

# Nullability

Avoid optional fields

unless optionality exists

in the business domain.

---

# Domain Constants

Business constants belong

inside Domain.

Avoid scattering constants

through repositories.

---

# Domain Events

Entities may produce

Domain Events.

They should never publish them directly.

Publishing belongs elsewhere.

---

# Circular References

Avoid circular entity references.

Prefer IDs

when relationships become large.

---

# Aggregate Roots

Each aggregate should have

one Aggregate Root.

External code should interact

through the root.

---

# Aggregate Consistency

Business invariants

must remain consistent

inside one aggregate.

---

# Size

Entities should remain focused.

Large entities usually indicate

multiple aggregates.

---

# Helper Methods

Private helper methods

are acceptable

when they improve readability.

---

# Static Methods

Avoid unnecessary static methods.

Prefer instance behavior.

---

# Factory Methods

Use factories

for complex construction.

Avoid constructors

with excessive parameters.

---

# DTO Separation

Never reuse

Domain Entities

as API DTOs.

Never reuse

Domain Entities

as database models.

---

# Documentation

Document

business intent

not implementation details.

---

# Testing

Domain tests

should require

no database

no HTTP server

no FastAPI

no SQLAlchemy

They should run as pure Python tests.

---

# Determinism

Domain behavior

must be deterministic.

Given identical inputs,

identical outputs

should occur.

---

# Cursor and Claude MUST NEVER

Generate SQLAlchemy imports

Generate FastAPI imports

Generate BaseModel inheritance

Generate SQL inside entities

Generate AsyncSession

Generate repository calls

Generate HTTP requests

Generate logging

Generate ORM annotations

Generate mapped_column()

Generate relationship()

Generate database access

Generate HTTPException

Generate JSON serialization

Generate mutable global state

Generate anemic entities

Generate magic strings

Generate business rules inside repositories

Generate setters replacing business methods

---

# Example Flow

Router

↓

Request DTO

↓

Use Case

↓

Repository

↓

ORM Model

↓

Mapper

↓

Domain Entity

↓

Business Logic

↓

Mapper

↓

ORM Model

↓

Database

The Domain remains independent throughout the entire flow.

---

# Final Principle

The Domain is the business.

Everything else is infrastructure.

Protect the Domain from frameworks, persistence, transport protocols, and implementation details.

A well-designed Domain should survive framework rewrites, database migrations, and infrastructure changes with little or no modification.