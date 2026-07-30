---
description: Defines concurrency control standards, race condition prevention, locking strategies, idempotency, and safe concurrent request handling.
globs: api/app/**/use_cases/**/*.py, api/app/**/repositories/**/*.py
paths:
  - "api/app/**/use_cases/**/*.py"
  - "api/app/**/repositories/**/*.py"
alwaysApply: false
---

# ============================================================
# Concurrency Standards
# ============================================================

# Philosophy

Concurrency is the normal operating condition.

Assume

multiple users

multiple workers

multiple API requests

multiple database connections

may operate on the same data simultaneously.

Correctness is more important than throughput.

---

# Source of Truth

The database

is the source of truth.

Never rely on

application memory

global variables

cached objects

request-local state

for concurrency control.

---

# Shared State

Avoid mutable shared state.

Requests must remain isolated.

Never communicate between requests using module-level variables.

Process-scoped application resources (database engine, session factory, Redis,
httpx clients) belong on `app.state`, initialized in `main.py` lifespan — not in
module-level globals. Access via `request.app.state` in dependencies. See `04-async.md`.

---

# Session Isolation

Each request

receives

its own AsyncSession.

Sessions must never be shared

between

threads

requests

background tasks

coroutines.

---

# Transaction Boundary

Concurrency protection

belongs inside

transaction boundaries.

Never perform

critical read-modify-write

operations

outside a transaction.

---

# Read Modify Write

Avoid

Read

↓

Modify

↓

Write

patterns

without concurrency protection.

Example

Bad

balance = repo.get_balance()

balance += amount

repo.save(balance)

This is vulnerable to race conditions.

---

# Atomic Operations

Prefer

atomic database operations

whenever possible.

Examples

UPDATE balance = balance + 1

INSERT ... ON DUPLICATE KEY UPDATE

UPSERT

COUNT()

EXISTS()

Avoid unnecessary application-side computation.

---

# Database Constraints

Always rely on

database constraints

for critical guarantees.

Examples

UNIQUE

PRIMARY KEY

FOREIGN KEY

CHECK

Never depend solely

on application logic.

---

# Uniqueness

Never implement uniqueness

using

if exists()

↓

insert()

without understanding

race conditions.

Prefer

database uniqueness

plus exception translation.

---

# Idempotency

Critical operations

should be idempotent.

Examples

Payments

Webhook processing

Order creation

Retry-safe APIs

Support

Idempotency-Key

where appropriate.

---

# Optimistic Concurrency

Prefer optimistic concurrency

when conflicts

are rare.

Examples

Version column

Row version

Updated timestamp

Reject conflicting updates

rather than silently overwriting.

---

# Pessimistic Locking

Use

SELECT ... FOR UPDATE

only when

strict serialization

is required.

Never lock rows

by default.

---

# Lock Scope

Lock

only

the minimum rows

required.

Avoid table locks.

---

# Lock Duration

Acquire locks

as late as possible.

Release them

as early as possible.

Never perform

external I/O

while holding locks.

---

# Deadlocks

Assume deadlocks

can happen.

Design transactions

to minimize

deadlock probability.

---

# Lock Ordering

Always acquire locks

in a consistent order.

Example

School

↓

Teacher

↓

Student

Never reverse

ordering

between different workflows.

---

# Retry Strategy

Retry only

transient failures.

Examples

Deadlock

Lock timeout

Temporary connection loss

Never retry

ValidationException

AuthorizationException

BusinessRuleViolation

ConflictException

---

# Duplicate Requests

Assume

clients

may retry requests.

APIs must behave correctly

under duplicate submissions.

---

# Concurrent Updates

Never silently overwrite

another user's changes.

Use

optimistic locking

or

business-specific conflict detection

where appropriate.

---

# Lost Updates

Protect against

lost update

problems.

Prefer

version checking

or

atomic SQL.

---

# Dirty Reads

Never rely on

uncommitted data.

Respect

database isolation guarantees.

---

# Phantom Reads

Only increase isolation level

when required

by business rules.

Avoid unnecessary locking.

---

# Background Jobs

Background workers

must follow

the same concurrency rules

as HTTP requests.

---

# Distributed Systems

Never assume

a single application instance.

Design for

multiple servers

multiple containers

multiple processes.

---

# In-Memory Locks

Do not use

Python locks

for database consistency.

threading.Lock

asyncio.Lock

only protect

one process.

They do not protect

distributed deployments.

---

# Async Safety

Never share

mutable objects

between concurrent coroutines.

Avoid race conditions

inside application memory.

---

# Cache Consistency

Caches are

performance optimizations.

Never treat

cache

as the authoritative source.

---

# Event Ordering

Do not assume

events

arrive

or are processed

in order.

Design consumers

to be idempotent.

---

# External Services

Do not depend

on external systems

for concurrency guarantees.

The database

owns persistence consistency.

---

# Bulk Processing

Large bulk operations

should execute

in manageable batches.

Avoid locking

large portions

of the database.

---

# Read Scalability

Read operations

should avoid locking

unless consistency requires it.

---

# High Contention

When contention is high

prefer

atomic SQL

over

application-level retries.

---

# Monitoring

Track

deadlocks

lock waits

retry counts

transaction duration

slow queries

concurrency failures.

---

# Testing

Concurrency tests

should include

parallel requests

duplicate submissions

deadlocks

lock timeouts

optimistic conflicts

race conditions

high contention

---

# Performance

Never sacrifice

correctness

for throughput.

Optimize

only after

measuring.

---

# Cursor and Claude MUST NEVER

Generate shared AsyncSession

Generate global mutable state

Generate module-level caches for consistency

Generate if exists() then insert() without protection

Generate SELECT FOR UPDATE everywhere

Generate table locks

Generate external API calls while holding locks

Generate Python locks for database consistency

Generate silent overwrite of concurrent updates

Generate retry loops for business exceptions

Generate long-running transactions

Generate in-memory uniqueness guarantees

Generate request-global mutable objects

Generate thread-safe assumptions in distributed systems

Generate race-condition-prone read-modify-write code

---

# Example Flow

Request A

↓

Transaction

↓

Atomic UPDATE

↓

Commit

||

Request B

↓

Transaction

↓

Atomic UPDATE

↓

Commit

Database guarantees consistency.

---

# Concurrency Checklist

Every concurrent workflow should satisfy

✓ One AsyncSession per request

✓ One transaction per Use Case

✓ Database constraints enforced

✓ Atomic operations preferred

✓ No shared mutable state

✓ Idempotent where required

✓ Deadlock-safe design

✓ Lock ordering defined

✓ External calls outside transactions

✓ Retry only transient failures

✓ Tested under concurrent load

---

# Final Principle

Concurrency is not an edge case.

Every business workflow should be designed assuming multiple requests may execute simultaneously.

Prefer database guarantees over application assumptions.

Use transactions, constraints, atomic operations, and deterministic workflows to ensure correctness.

The application should remain safe under concurrent execution without relying on in-memory coordination.