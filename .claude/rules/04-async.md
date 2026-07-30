---
description: Enterprise async programming standards for Python 3.12+, FastAPI and SQLAlchemy Async. Event loop, blocking I/O, and AsyncSession usage at persistence and infrastructure boundaries (not routers — see 03-fastapi.md).
globs: api/app/main.py, api/app/database/**/*.py, api/app/**/repositories/**/*.py, api/app/infrastructure/**/*.py, api/app/core/dependencies.py
paths:
  - "api/app/main.py"
  - "api/app/database/**/*.py"
  - "api/app/**/repositories/**/*.py"
  - "api/app/infrastructure/**/*.py"
  - "api/app/core/dependencies.py"
alwaysApply: false
---

# Async Programming Standards

This backend is fully asynchronous.

All application code MUST be designed with asynchronous execution in mind.

The event loop is a shared resource.

Never block it.

---

# General Principles

Async exists to improve concurrency for I/O-bound work.

Async is NOT intended for CPU-bound work.

Never convert synchronous code to async unless the operation actually performs asynchronous I/O.

---

# Event Loop

The event loop MUST remain responsive.

Never block the event loop.

Never intentionally pause the event loop.

Every long-running operation should either

- await asynchronous I/O

or

- execute outside the event loop.

---

# Async Functions

Use

```python
async def
```

for

- API endpoints
- Repository methods
- Use cases performing I/O
- External API calls
- Database operations

Avoid unnecessary async functions.

Pure computation should remain synchronous.

---

# Await

Every coroutine MUST be awaited.

Never ignore coroutine objects.

Bad

```python
repository.save(user)
```

Good

```python
await repository.save(user)
```

---

# Blocking Functions

Never call blocking code inside async functions.

Forbidden

time.sleep()

requests

subprocess.run()

blocking file operations

long CPU calculations

blocking SDKs

---

# Sleep

Never use

```python
time.sleep()
```

Use

```python
await asyncio.sleep()
```

only when sleeping is genuinely required.

---

# HTTP Clients

Never use

requests

Use

httpx.AsyncClient

for outbound HTTP requests.

Reuse clients where appropriate.

Do not create unnecessary clients repeatedly.

---

# Database Drivers

Only asynchronous database drivers are permitted.

Project standard

asyncmy

Never use

pymysql

mysqlclient

inside async request handling.

---

# SQLAlchemy

Always use AsyncSession.

Never use synchronous Session.

Never mix sync and async sessions.

---

# AsyncSession Lifetime

One AsyncSession per request.

Never share AsyncSession across requests.

Never cache AsyncSession.

Never store AsyncSession globally.

Never pass AsyncSession between concurrent tasks.

---

# Session Ownership

Repositories receive AsyncSession.

Repositories do not create sessions.

Session lifecycle belongs to dependency injection.

---

# Transactions

Transactions belong to the service/use case layer.

Repositories MUST NOT

commit()

rollback()

begin()

Repositories only execute queries. Full standards: **`13-transactions.md`**.

---

# Session Closing

Never manually close injected AsyncSession.

Dependency injection manages lifecycle.

---

# Concurrent Database Operations

Never execute multiple queries simultaneously using the same AsyncSession.

An AsyncSession wraps one DBAPI connection. Concurrent `await`s on it race for
the same socket, which raises `InterfaceError`/`IllegalStateChangeError` or
silently interleaves results — it is not a performance-only concern.

Incorrect

```python
await asyncio.gather(
    repo.get_user(...),
    repo.get_roles(...)
)
```

when both repositories share one AsyncSession.

Correct — sequential on the same session

```python
user = await repo.get_user(...)
roles = await repo.get_roles(...)
```

Prefer this over the pattern above whenever the queries stay on one session.

Correct — one query via JOIN or eager load

```python
user = await repo.get_user_with_roles(...)  # selectinload()/joinedload()
```

When the two reads are related, a single query is preferable to two
round trips, sequential or not. See **`05-sqlalchemy-part-3.md`**.

Correct — true parallelism with separate sessions

```python
async with session_factory() as session_a, session_factory() as session_b:
    user, roles = await asyncio.gather(
        user_repo(session_a).get_user(...),
        role_repo(session_b).get_roles(...),
    )
```

Use only when the two operations are independent and genuinely need to run
in parallel — the common case is sequential on one session, or a single
JOIN/eager-loaded query.

---

# MissingGreenlet

Never trigger lazy loading unintentionally.

Always eagerly load required relationships.

Never rely on implicit database access during attribute access.

---

# Lazy Loading

Avoid lazy loading.

Prefer explicit loading.

selectinload()

joinedload()

containseager()

should be used intentionally.

---

# Async Generators

Use async generators for

streaming

large datasets

chunked processing

Avoid loading large datasets entirely into memory.

---

# Streaming

Prefer streaming for

CSV exports

large downloads

report generation

Avoid building huge lists first.

---

# Task Creation

Never create fire-and-forget tasks.

Bad

```python
asyncio.create_task(...)
```

without ownership.

Every task should be

awaited

tracked

or supervised.

---

# Task Groups

Prefer

TaskGroup

over raw create_task()

when multiple tasks belong together.

TaskGroup provides structured concurrency.

---

# asyncio.gather

Use gather only when

operations are independent

results are all required

shared mutable state is absent

Avoid gather when tasks share database sessions.

---

# Cancellation

Assume every coroutine may be cancelled.

Never swallow CancelledError.

Always allow cancellation to propagate.

Cleanup resources appropriately.

---

# Timeouts

Every external network request should define a timeout.

Never allow unbounded waits.

Database queries should also have appropriate limits.

---

# Retries

Retries should only occur

for transient failures.

Never blindly retry

validation errors

business errors

constraint violations

permission failures

---

# Exponential Backoff

Network retries should use exponential backoff.

Avoid immediate retry loops.

---

# Thread Safety

Never assume async code is thread-safe.

Avoid shared mutable state.

Protect shared resources when required.

---

# Locks

Avoid locks unless absolutely necessary.

Prefer immutable state.

If synchronization is required,

use asyncio.Lock.

Never use threading.Lock inside async code.

---

# Queues

Prefer asyncio.Queue

for asynchronous producer/consumer workflows.

---

# Context Variables

Use ContextVar

for request-scoped context

such as

request_id

correlation_id

Never use globals.

---

# File Operations

Large file operations should execute asynchronously where possible.

Avoid blocking disk access inside request handlers.

---

# CPU Intensive Work

Async does not improve CPU performance.

Examples

image processing

video transcoding

large PDF generation

compression

encryption

These should execute outside the event loop.

---

# Background Work

Long-running operations should not block HTTP requests.

Return immediately whenever possible.

Background execution strategy will be defined separately.

---

# Shared State

Avoid mutable module-level state.

Avoid singleton objects with mutable fields.

Async applications magnify race conditions.

Long-lived application resources (database engine, session factory, Redis, httpx clients)
belong on `app.state`, not in module-level globals.

Access them through `request.app.state` inside FastAPI dependencies.

Do not create module-level `_engine` or `_session_factory` variables.

---

# Race Conditions

Data races, locking, and idempotency under concurrent requests are defined in **`14-concurrency.md`**.

Do not rely on in-memory synchronization for database consistency.

---

# Resource Cleanup

Always release

connections

streams

files

network clients

Use async context managers.

---

# Async Context Managers

Prefer

```python
async with
```

for

database sessions

HTTP clients

streams

locks

Never manually manage cleanup when context managers exist.

---

# Async Iteration

Use

```python
async for
```

only for asynchronous iterators.

Avoid unnecessary async iteration.

---

# Exception Handling

Catch expected exceptions.

Unexpected exceptions should propagate.

Never suppress exceptions silently.

Never ignore task failures.

---

# Logging

Logging must not block request handling.

Avoid expensive formatting.

Prefer structured logging.

---

# Performance

Avoid creating unnecessary coroutines.

Avoid excessive context switching.

Avoid unnecessary await chains.

Write straightforward async code.

---

# Determinism

Concurrency must not introduce nondeterministic business behavior.

Business logic should remain deterministic.

---

# Testing

Async code should be tested using pytest with async support.

Do not test asynchronous code synchronously.

---

# Dependency Injection

Async dependencies should remain lightweight.

Avoid expensive initialization during every request.

---

# Connection Pools

Use SQLAlchemy connection pooling.

Never manually implement connection pools.

Pool sizing belongs to configuration.

Not business logic.

---

# Event Loop Ownership

Never manually create event loops inside application code.

Never call

asyncio.run()

inside FastAPI.

The ASGI server owns the event loop.

---

# Nested Event Loops

Never attempt nested event loops.

Forbidden

```python
asyncio.run(...)
```

inside

async functions

request handlers

repositories

use cases

---

# Sync to Async

Avoid converting blocking code using wrappers unless absolutely necessary.

Prefer native asynchronous libraries.

---

# Libraries

Before introducing a dependency,

prefer libraries with native asyncio support.

Avoid sync wrappers.

---

# Memory Usage

Avoid collecting huge datasets into memory.

Process incrementally.

Use pagination.

Use streaming.

---

# Backpressure

When processing large streams,

allow consumers to control throughput.

Avoid overwhelming memory.

---

# Cursor and Claude MUST NEVER

Generate synchronous database sessions.

Generate synchronous database drivers.

Generate requests inside async code.

Generate time.sleep().

Generate asyncio.run() inside application code.

Generate nested event loops.

Generate fire-and-forget tasks.

Generate shared AsyncSession instances.

Generate global AsyncSession objects.

Generate commit() inside repositories.

Generate rollback() inside repositories.

Generate lazy-loading dependent business logic.

Generate blocking CPU work inside request handlers.

Generate threading.Lock inside async code.

Generate unbounded retries.

Generate infinite retry loops.

Generate external API calls without timeouts.

Generate mutable global state.

Generate ignored coroutine warnings.

Generate un-awaited coroutines.

Generate concurrent queries using the same AsyncSession.

---

# Final Principle

Async programming exists to improve scalability through efficient I/O concurrency.

Correctness is more important than concurrency.

Readable async code is preferred over clever concurrency patterns.

Every asynchronous operation should be explicit, deterministic, and safe under high concurrency.