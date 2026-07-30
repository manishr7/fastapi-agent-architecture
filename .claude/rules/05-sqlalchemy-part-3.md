---
description: SQLAlchemy 2.0 Async standards. Part 3 — performance, concurrency, and production practices.
globs: api/app/**/repositories/**/*.py, api/app/database/**/*.py
paths:
  - "api/app/**/repositories/**/*.py"
  - "api/app/database/**/*.py"
alwaysApply: false
---


# ============================================================
# SQLAlchemy Standards
# Part 3
# Performance, Concurrency & Production
# ============================================================

# Performance Philosophy

Correctness is always more important than speed.

Optimize only after measuring.

Avoid premature optimization.

---

# Query Performance

Every query should fetch only the data it needs.

Never select unnecessary columns.

Never load unnecessary relationships.

Never perform unnecessary round trips.

---

# Large Result Sets

Avoid loading large datasets into memory.

Prefer

- pagination
- batching
- streaming

---

# Streaming

Large exports should be streamed.

Avoid

```python
rows = result.scalars().all()
```

for very large datasets.

Process incrementally whenever possible.

---

# Projection

If only three columns are needed,

fetch only three columns.

Avoid loading entire ORM objects.

---

# N+1 Detection

Repositories should be reviewed for N+1 queries.

Every loop accessing relationships should be questioned.

Never assume lazy loading is acceptable.

---

# Explain Plans

Complex queries should be verified using

EXPLAIN

or

EXPLAIN ANALYZE

before optimization.

Never optimize blindly.

---

# Index Usage

Indexes should support actual query patterns.

Do not create speculative indexes.

Indexes are not free.

They increase

- storage
- INSERT cost
- UPDATE cost
- DELETE cost

---

# Composite Indexes

Composite indexes should follow

left-most prefix

rules.

Design indexes around production queries.

---

# Covering Indexes

Consider covering indexes

only for high-frequency read queries.

---

# Full Table Scans

Avoid full table scans on large tables.

Investigate execution plans when scans appear.

---

# ORDER BY

ORDER BY should use indexed columns whenever practical.

Avoid sorting millions of rows unnecessarily.

---

# LIKE Queries

Avoid

```sql
LIKE '%value%'
```

on large tables.

Prefer

- prefix searches
- full text indexes
- dedicated search services

when appropriate.

---

# IN Clauses

Large IN clauses should be avoided.

Consider batching.

---

# Bulk Inserts

Bulk inserts are acceptable

for migration

ETL

administrative tasks

Understand ORM lifecycle hooks may be bypassed.

---

# Bulk Updates

Bulk updates should be explicit.

Never use bulk updates

for business logic

that depends on ORM state.

---

# Bulk Deletes

Bulk deletes require caution.

Database cascades may differ from ORM cascades.

---

# Flush Frequency

Do not flush repeatedly inside loops.

Prefer

build

↓

flush once

↓

continue

---

# Commit Frequency

Never commit inside loops.

One transaction.

One commit.

---

# Database Round Trips

Reduce unnecessary database calls.

Avoid

query

↓

query

↓

query

when one query is sufficient.

---

# Concurrency

Assume multiple requests

modify the same data simultaneously.

Design accordingly.

---

# Race Conditions

Business logic must not rely on

"check then insert"

without protection.

Prefer

database constraints

or

locking.

---

# Unique Constraints

Unique constraints are the primary protection

against duplicate data.

Application validation is secondary.

---

# SELECT FOR UPDATE

Use

with_for_update()

only when business rules require pessimistic locking.

Never lock rows unnecessarily.

---

# Lock Scope

Lock only the rows that are required.

Smaller lock scope

↓

higher concurrency.

---

# Lock Duration

Keep transactions short.

Never hold locks

while

calling APIs

sending emails

performing CPU work

waiting for user input

---

# NOWAIT

Use

NOWAIT

when immediate failure is preferable to waiting.

---

# SKIP LOCKED

Use

SKIP LOCKED

for queue-style processing.

Avoid it for user-facing business operations.

---

# Deadlocks

Deadlocks are expected

in highly concurrent systems.

Applications must tolerate them.

---

# Deadlock Prevention

Always access tables

in a consistent order.

Keep transactions short.

Avoid unnecessary locks.

---

# Optimistic Locking

Prefer optimistic locking

when conflicts are uncommon.

---

# Pessimistic Locking

Prefer pessimistic locking

only for high-conflict resources.

---

# Isolation Levels

Use the database default isolation level

unless business requirements demand otherwise.

Never change isolation levels

inside repositories.

---

# Retry Strategy

Retry only transient failures.

Examples

Deadlocks

Lock wait timeout

Temporary network interruption

Never retry

validation failures

authorization failures

business rule violations

---

# Connection Pool

Connection pool configuration belongs

to infrastructure.

Repositories must never modify pooling behavior.

---

# Pool Exhaustion

Long-running transactions increase pool exhaustion.

Finish transactions quickly.

---

# Idle Connections

Do not keep sessions open unnecessarily.

Close request scope promptly.

---

# Exception Translation

Repositories should translate SQLAlchemy exceptions

into domain-specific persistence exceptions.

Business layers should not depend on SQLAlchemy exceptions.

---

# IntegrityError

Convert IntegrityError

into meaningful domain exceptions.

Never expose raw SQL errors to clients.

---

# OperationalError

Treat OperationalError

as infrastructure failure.

Avoid exposing implementation details.

---

# ProgrammingError

ProgrammingError usually indicates

developer mistakes.

Fail fast.

Fix the code.

---

# Database Errors

Unexpected database exceptions

should be logged

with sufficient diagnostic information.

Sensitive data must never be logged.

---

# Logging

Log

query failures

deadlocks

timeouts

constraint violations

Avoid logging every successful query.

---

# Slow Queries

Slow queries should be logged.

Monitor

execution time

frequency

affected tables.

---

# SQL Logging

Verbose SQL logging is acceptable

during development.

Avoid enabling verbose SQL logging

in production.

---

# Observability

Database performance should be measurable.

Track

- query count
- latency
- connection pool usage
- deadlocks
- timeout frequency

---

# Migrations

Schema changes belong exclusively

to Alembic migrations.

Repositories must never create schema.

---

# Schema Drift

Production schema

must always match

migration history.

Manual production schema changes

are prohibited.

---

# Legacy Database

Legacy schema must be respected.

Adapt code

to the database

not the reverse

unless migration is approved.

---

# Backward Compatibility

Repository changes

must preserve existing behavior

unless explicitly approved.

---

# Testing

Repositories should be tested

against a real database

whenever practical.

Mocking SQLAlchemy

should remain minimal.

---

# Determinism

Repository methods

must produce deterministic results.

Avoid hidden side effects.

---

# Code Review Checklist

During review verify

- correct transaction boundary
- no ORM leakage
- eager loading used intentionally
- no N+1 queries
- pagination present
- indexes considered
- proper exception handling
- no commits in repositories
- no raw SQL unless justified
- correct domain mapping

---

# Cursor and Claude MUST NEVER

Generate session.query()

Generate synchronous SQLAlchemy APIs

Generate lazy loading inside business logic

Generate commit() inside repositories

Generate rollback() inside repositories

Generate transaction.begin() inside repositories

Generate multiple commits in one use case

Generate check-then-insert race conditions

Generate long-running transactions

Generate API calls while holding database locks

Generate FOR UPDATE by default

Generate SELECT *

Generate unbounded result sets

Generate ORM models outside repositories

Generate leaked AsyncSession instances

Generate hidden implicit transactions

Generate duplicated SQL

Generate ignored IntegrityError exceptions

Generate swallowed database exceptions

Generate raw SQL without documented justification

Generate database schema changes outside Alembic

Generate verbose SQL logging in production

Generate business logic depending on SQLAlchemy exceptions

---

# Production Checklist

Every repository should satisfy

✓ SQLAlchemy 2.x API only

✓ AsyncSession only

✓ Request-scoped session

✓ One transaction per use case

✓ No commit in repositories

✓ No rollback in repositories

✓ Domain entities returned

✓ No ORM leakage

✓ Explicit eager loading

✓ No N+1 queries

✓ Explicit pagination

✓ Explicit ordering

✓ Database constraints enforced

✓ Proper exception translation

✓ Short transactions

✓ No unnecessary flush()

✓ No unnecessary refresh()

✓ Connection pooling configured

✓ Slow queries monitored

✓ Alembic manages schema

✓ Code reviewed for concurrency

---

# Final Principle

SQLAlchemy is an implementation detail.

The domain should remain independent of persistence.

Every query should be explicit.

Every transaction should be intentional.

Every repository should be deterministic.

Correctness, clarity, and maintainability always take precedence over clever optimizations.