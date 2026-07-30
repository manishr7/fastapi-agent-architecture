---
description: Defines transaction management standards, transaction boundaries, Unit of Work responsibilities, rollback strategy, and concurrency-safe persistence.
globs: api/app/**/use_cases/**/*.py, api/app/database/session.py
paths:
  - "api/app/**/use_cases/**/*.py"
  - "api/app/database/session.py"
alwaysApply: false
---

# ============================================================
# Transaction Standards
# ============================================================

# Philosophy

Transactions protect consistency.

A transaction represents

one complete business operation.

Either

everything succeeds

or

everything fails.

Never leave the database
in a partially updated state.

---

# Transaction Ownership

Transaction ownership belongs exclusively
to Use Cases.

Routers never manage transactions.

Repositories never manage transactions.

Domain Entities never manage transactions.

---

# Transaction Boundary

One Use Case

↓

One Transaction

A transaction should represent
one business workflow.

---

# Session Ownership

A request receives

one AsyncSession.

The same session is shared

across all repositories

participating in the Use Case.

Repositories must never
create sessions.

---

# Commit

Only the Use Case

may call

commit().

Repositories must never commit.

---

# Rollback

Only the Use Case

may call

rollback().

Repositories must never rollback.

---

# Flush

Repositories may call

flush()

only when

database-generated values

are required immediately.

Flush is not a commit.

---

# Refresh

Repositories may call

refresh()

only when
fresh database state
is required.

Avoid unnecessary refreshes.

---

# Transaction Scope

Keep transactions

as short as possible.

Avoid unnecessary work

while a transaction
remains open.

---

# Business Logic

Perform business validation

before expensive persistence

whenever practical.

Fail fast.

---

# External Services

Never keep a transaction open
while waiting for

email

SMS

RabbitMQ

Redis

HTTP APIs

cloud storage

payment gateways.

External communication should occur

after a successful commit

or

through an asynchronous workflow.

---

# Repository Responsibilities

Repositories perform

database operations only.

Repositories never decide

when work becomes permanent.

---

# Multiple Repositories

A Use Case

may coordinate

multiple repositories

within

one transaction.

Example

UserRepository

↓

RoleRepository

↓

PermissionRepository

↓

Single Commit

---

# Nested Transactions

Avoid nested transactions.

Design Use Cases

to own a single
transaction boundary.

---

# Savepoints

Use savepoints

only when

partial rollback

is a genuine business requirement.

They should be rare.

---

# Unit of Work

The AsyncSession

acts as the Unit of Work.

Do not create
additional transaction abstractions

unless justified.

---

# Exception Handling

If any operation fails

rollback the transaction

then re-raise
the exception.

Never suppress exceptions.

The global exception handler

is responsible for

creating the HTTP response.

---

# Global Exception Handler

Transactions must never

construct API responses.

Transactions must never

return error dictionaries.

Transactions only

rollback

cleanup

propagate exceptions.

Error serialization belongs

to

app/core/exception_handlers.py

---

# Exception Flow

Repository

↓

Persistence Exception

↓

Use Case

↓

Rollback

↓

Re-raise

↓

Global Exception Handler

↓

Standard Error Response

---

# Domain Exceptions

Business exceptions

must rollback

the transaction.

Never commit
after a business failure.

---

# Persistence Exceptions

Database failures

must rollback

the transaction.

Repositories translate

SQLAlchemy exceptions

before propagation.

---

# Idempotency

Critical operations

should be idempotent.

Examples

Payment

Order creation

Webhook processing

Retry-safe workflows

---

# Lock Duration

Acquire locks

as late as possible.

Release them

as early as possible.

Never perform

expensive computation

while holding locks.

---

# SELECT FOR UPDATE

Use

SELECT ... FOR UPDATE

only when

business consistency

requires pessimistic locking.

Avoid locking by default.

---

# Deadlocks

Assume deadlocks

can occur.

Design transactions

to be

small

predictable

consistent.

Acquire locks

in a consistent order.

---

# Isolation

Use the default isolation level

unless a Use Case

requires stronger guarantees.

Avoid increasing isolation

without justification.

---

# Read Only Operations

Pure read Use Cases

must not commit.

Avoid opening unnecessary transactions.

---

# Batch Operations

Large batch operations

should be divided

into manageable units

when business rules allow.

Avoid long-running transactions.

---

# Async

Transactions must remain

fully asynchronous.

Never perform

blocking I/O

inside a transaction.

---

# Concurrency

Never rely

on application memory

for consistency.

The database

is the source of truth.

---

# Retry

Retry only

transient failures.

Examples

Deadlock

Lock timeout

Temporary connection loss

Never retry

ValidationException

BusinessRuleViolation

AuthorizationException

AuthenticationException

---

# Audit Fields

Audit fields

should be persisted

within the same transaction

as the business change.

---

# Event Publishing

Never publish events

before commit.

Publish only

after successful persistence

or

through an Outbox Pattern.

---

# Outbox Pattern

When reliable event delivery

is required

persist the event

inside the same transaction.

Publish asynchronously

after commit.

---

# Performance

Avoid transactions

that remain open

for a long time.

Keep transactions

small

focused

deterministic.

---

# Testing

Test

successful commit

rollback

deadlock retry

constraint violations

multi-repository transactions

concurrent requests

idempotency

---

# Cursor and Claude MUST NEVER

Generate commit() inside repositories

Generate rollback() inside repositories

Generate begin() inside repositories

Generate nested transactions

Generate transaction logic inside routers

Generate transaction logic inside Domain Entities

Generate HTTP responses inside transactions

Generate error dictionaries inside transactions

Generate suppressed exceptions

Generate external API calls before commit

Generate email sending before commit

Generate RabbitMQ publishing before commit

Generate long-running transactions

Generate blocking code inside transactions

Generate multiple independent commits inside one business workflow

Generate partial commits without explicit business requirements

---

# Example Flow

HTTP Request

↓

Router

↓

Use Case

↓

Repository A

↓

Repository B

↓

Repository C

↓

commit()

↓

Return

OR

Repository B throws exception

↓

rollback()

↓

Re-raise

↓

Global Exception Handler

↓

Standard Error Response

---

# Transaction Checklist

Every transaction should satisfy

✓ One Use Case

✓ One AsyncSession

✓ One transaction boundary

✓ Repository never commits

✓ Repository never rollbacks

✓ Rollback on failure

✓ Exceptions propagated

✓ Global exception handler formats responses

✓ No external calls before commit

✓ Short-lived transaction

✓ Deterministic behavior

✓ Tested under concurrency

---

# Final Principle

A transaction represents a complete business operation.

Use Cases own transaction boundaries.

Repositories perform persistence.

Domain Entities enforce business rules.

If a failure occurs, rollback the transaction, propagate the exception unchanged, and allow the global exception handler to produce the standardized API response.

Transaction management should guarantee consistency without knowing anything about HTTP, FastAPI, or response serialization.