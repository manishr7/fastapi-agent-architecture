---
description: Defines standards for working with legacy databases, existing schemas, backward compatibility, and incremental modernization without breaking existing systems.
globs: api/app/database/**/*.py, api/migrations/**/*.py, api/app/**/repositories/**/*.py
paths:
  - "api/app/database/**/*.py"
  - "api/migrations/**/*.py"
  - "api/app/**/repositories/**/*.py"
alwaysApply: false
---

# ============================================================
# Legacy Database Standards
# ============================================================

# Philosophy

The existing database

is a business asset.

The application must adapt

to the existing schema

instead of redesigning it.

Respect stability

over architectural perfection.

---

# Primary Goal

Modernize

the application

without breaking

existing data

existing integrations

existing reports

existing clients.

---

# Source of Truth

The production database

is the source of truth.

Never assume

the ORM model

defines the database.

The ORM represents

the database

it does not replace it.

---

# Schema Ownership

Do not redesign

existing schemas

unless explicitly approved.

The application

must accommodate

legacy structures.

---

# Compatibility

Maintain backward compatibility

whenever practical.

Avoid schema changes

that require

simultaneous deployment

of every dependent system.

---

# Existing Tables

Reuse existing tables

before introducing

new ones.

Avoid duplicate representations

of the same business concept.

---

# Existing Columns

Reuse existing columns

whenever they satisfy

business requirements.

Avoid unnecessary additions.

---

# Naming

Respect

legacy naming conventions.

Do not rename

tables

columns

indexes

constraints

without explicit approval.

---

# ORM Models

ORM models

should accurately represent

the database.

Do not "improve"

legacy naming

inside the schema.

Use SQLAlchemy mapping

instead.

Example

```python
user_name = mapped_column("USR_NM")
```

Keep database names

inside persistence.

Expose clean names

through Domain Entities

and DTOs.

---

# Domain Isolation

Legacy database naming

must never leak

into

Domain Entities

Use Cases

API Responses.

Repositories perform

the translation.

---

# Mapping

Repository

↓

ORM Model

↓

Domain Entity

↓

Response DTO

Keep each layer

independent.

---

# Business Logic

Never place

business logic

inside ORM models

to compensate

for legacy schema design.

Business rules belong

inside

Use Cases

and

Domain Entities.

---

# Legacy Constraints

Respect

existing constraints.

Do not remove

legacy validation

without understanding

its purpose.

---

# Unknown Columns

Do not remove

unused columns

without verifying

they are unused

outside the application.

Other systems

may depend on them.

---

# Existing Triggers

Assume

database triggers

may exist.

Repositories

must not rely

on trigger side effects

unless documented.

---

# Existing Procedures

Stored procedures

may exist

for historical reasons.

Prefer repositories

using SQLAlchemy.

Use stored procedures

only when

required by

business

performance

or existing integrations.

---

# Views

Existing views

should be reused

when they provide

stable business projections.

Avoid recreating

identical logic

inside the application.

---

# Data Integrity

Respect

existing

primary keys

foreign keys

constraints

indexes.

Never bypass

database integrity rules.

---

# Legacy Types

Legacy databases

may contain

non-ideal types.

Examples

CHAR

TEXT

legacy enums

numeric flags

Repositories

should translate

them into

clean Domain representations.

---

# Flags

Legacy flags

Examples

Y/N

1/0

ACTIVE/INACTIVE

should become

meaningful

booleans

or enums

inside Domain Entities.

---

# Null Handling

Legacy schemas

may allow

unexpected NULL values.

Repositories

should normalize

when appropriate.

Never assume

legacy data

is perfect.

---

# Data Cleanup

Repositories

must tolerate

legacy inconsistencies.

Data cleanup

should occur

through dedicated

maintenance workflows

not normal request handling.

---

# Soft Deletes

Respect

existing soft delete

implementations.

Do not introduce

new deletion behavior

without approval.

---

# Audit Columns

Preserve

existing audit fields.

Examples

created_by

updated_by

created_on

updated_on

Do not remove

legacy audit behavior.

---

# Incremental Modernization

Prefer

small improvements

over

large migrations.

Modernize

incrementally.

---

# Schema Evolution

When schema changes

are required

prefer

additive changes.

Avoid breaking

existing integrations.

---

# Migration Strategy

Use

Expand

↓

Migrate

↓

Contract

instead of

breaking schema changes.

---

# Data Migration

Large data migrations

should execute

through

maintenance jobs

or

dedicated scripts.

Avoid request-time migration.

---

# Performance

Do not redesign

legacy queries

without measuring.

Legacy indexes

may exist

for external systems.

---

# Reporting

Assume

BI tools

reports

exports

external integrations

may depend

on existing schema.

Verify impact

before changes.

---

# Raw SQL

Raw SQL

may be acceptable

when required

to support

legacy database behavior.

Document the reason.

---

# Transactions

Respect

existing transactional behavior.

Do not change

isolation

locking

commit strategy

without analysis.

---

# Testing

Legacy support

must include

integration tests

using representative

legacy data.

---

# Documentation

Document

legacy behavior

that cannot be inferred

from the schema.

Examples

special status codes

historical business rules

trigger behavior

legacy identifiers.

---

# Refactoring

Refactor

application code

before

refactoring

database schema.

---

# Technical Debt

Do not hide

legacy complexity.

Isolate it

inside repositories

and mapping layers.

---

# Cursor and Claude MUST NEVER

Generate table renames

Generate column renames

Generate constraint renames

Generate primary key changes

Generate foreign key changes

Generate destructive schema redesign

Generate ORM models that differ from the database

Generate legacy names inside Domain Entities

Generate business logic inside ORM models

Generate assumptions that the database is clean

Generate request-time data cleanup

Generate breaking migrations

Generate unnecessary normalization of the database

Generate schema redesign without explicit instruction

Generate removal of legacy columns without impact analysis

---

# Example Flow

Legacy Database

↓

SQLAlchemy ORM Model

↓

Repository Mapper

↓

Domain Entity

↓

Response DTO

↓

API Response

The legacy schema

remains hidden

behind the persistence layer.

---

# Legacy Database Checklist

Every feature should satisfy

✓ Existing schema respected

✓ No unnecessary schema redesign

✓ Repository performs translation

✓ Domain remains clean

✓ API remains clean

✓ Legacy naming isolated

✓ Existing constraints preserved

✓ Existing audit fields respected

✓ Backward compatibility maintained

✓ Integration tested

✓ Migration reviewed

✓ External dependencies considered

---

# Final Principle

A legacy database is not a flaw.

It represents years of accumulated business knowledge.

The application's responsibility is not to force the database into a new design, but to isolate legacy concerns behind clean architectural boundaries while enabling gradual, safe modernization.