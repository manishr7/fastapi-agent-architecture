---
description: Defines enterprise testing standards, testing philosophy, test organization, unit testing, integration testing, end-to-end testing, fixtures, and quality requirements.
globs: api/tests/**/*.py, api/**/conftest.py, api/pyproject.toml, api/app/api/**/*.py
paths:
  - "api/tests/**/*.py"
  - "api/**/conftest.py"
  - "api/pyproject.toml"
  - "api/app/api/**/*.py"
alwaysApply: false
---

# ============================================================
# Testing Standards
# ============================================================

# Philosophy

Testing is a first-class engineering activity.

Code should be written

to be testable

before it is written

to be feature complete.

Every layer should be

independently testable.

---

# Testing Pyramid

Prefer

Unit Tests

↓

Integration Tests

↓

End-to-End Tests

Unit tests should be the majority.

Avoid relying primarily

on end-to-end tests.

---

# Test Organization

Tests should mirror the application structure.

Example (under `api/`):

```text
api/tests/

    api/
        test_routing.py      ← verify all routes live under /api/v6, OpenAPI shape

    modules/

        users/
            test_router.py
            test_use_cases.py
            test_repository.py
            test_domain.py

    core/

    shared/
```

Layout mirrors `app/modules/<module>/` (see `01-folder-structure.md`).

`tests/api/` contains routing smoke tests: correct prefix, router composition, OpenAPI docs.
These verify the `app/api/` layer wires correctly without duplicating business tests.

---

# Naming

Test files

must begin with

test_

Test functions

must begin with

test_

Examples

test_create_user()

test_duplicate_email()

test_invalid_role()

---

# Test Independence

Every test

must be independent.

Tests must never

depend on execution order.

Tests must never

depend on previous tests.

---

# Determinism

Tests must produce

identical results

for identical inputs.

Avoid flaky tests.

---

# Isolation

Each test

should verify

one behavior.

Avoid testing

multiple unrelated scenarios

in one test.

---

# Unit Tests

Unit tests

must isolate

the component

being tested.

Mock only

external collaborators.

---

# Integration Tests

Integration tests

should verify

interaction

between components.

Examples

Use Case

↓

Repository

↓

Database

Use

a real test database

whenever practical.

---

# End-to-End Tests

End-to-End tests

should verify

complete workflows.

Avoid excessive

E2E coverage.

---

# Repository Tests

Repositories should be tested

against

a real database.

Avoid mocking SQLAlchemy

unless absolutely necessary.

Verify

queries

constraints

transactions

mappings.

---

# Use Case Tests

Use Cases

should be tested

using mocked repositories

or lightweight fakes.

Verify

business rules

authorization

transactions

domain behavior.

---

# Router Tests

Router tests

should verify

routing

dependency injection

request validation

response serialization

status codes

global exception handling.

Routers should not

require business logic assertions.

---

# Domain Tests

Domain Entities

must be tested

without

FastAPI

SQLAlchemy

database

network

filesystem.

They should be

pure unit tests.

---

# Global Exception Handler

Verify that

application exceptions

are translated into

the standard error response.

Test

status codes

error codes

messages

response envelope.

---

# Validation Tests

Test

valid input

invalid input

missing fields

boundary values

unexpected values.

---

# Authorization Tests

Verify

authorized users

unauthorized users

forbidden users

role-based access

permission checks.

---

# Authentication Tests

Verify

valid tokens

expired tokens

invalid tokens

missing tokens.

---

# Database Tests

Verify

transactions

rollback

constraints

foreign keys

unique constraints

optimistic conflicts

locking

when applicable.

---

# Async Tests

Async code

must be tested

using

pytest

and

pytest-asyncio

Never block

the event loop

inside tests.

---

# Fixtures

Use fixtures

for reusable setup.

Examples

database session

authenticated user

JWT token

sample entities

configuration.

Avoid duplicated setup.

---

# Fixture Scope

Choose

the smallest scope

that satisfies

the test.

Avoid unnecessary

session-scoped fixtures.

---

# Test Data

Create

minimal

explicit

representative

test data.

Avoid

large fixture dumps.

---

# Factories

Prefer

factory functions

or factory libraries

for creating

test entities.

Avoid duplicated object creation.

---

# Mocking

Mock

external systems

Examples

Email

SMS

Redis

RabbitMQ

Cloud storage

HTTP APIs

Do not mock

the code under test.

---

# Database Cleanup

Tests

must leave

the database

clean.

Rollback

or recreate state

between tests.

---

# Environment

Testing configuration

must be isolated

from production.

Never use

production databases

or production credentials.

---

# Assertions

Assert

behavior

not implementation.

Avoid asserting

private methods

internal variables

SQL query text.

---

# Coverage

Focus coverage on

business-critical paths.

Coverage percentage

is not

a quality metric

by itself.

---

# Boundary Tests

Always test

minimum

maximum

empty

null

invalid

duplicate

edge cases.

---

# Performance Tests

Critical workflows

should include

performance benchmarks

when appropriate.

Do not mix

performance tests

with functional tests.

---

# Concurrency Tests

Verify

concurrent requests

race conditions

deadlock handling

idempotency

retry behavior.

---

# Security Tests

Verify

authentication

authorization

input validation

SQL injection protection

path traversal protection

file validation.

---

# API Tests

Verify

status codes

response models

response envelope

pagination

filtering

sorting

error responses.

---

# Logging Tests

Verify

important failures

are logged

when appropriate.

Avoid asserting

log formatting.

---

# Snapshot Tests

Use snapshot testing

sparingly.

Prefer explicit assertions

for API contracts.

---

# Randomness

Avoid

random input

unless testing randomness.

Seed random generators

when required.

---

# Time

Avoid relying

on the current time.

Mock

or freeze time

when appropriate.

---

# External Services

Never call

real external services

during automated tests.

Use

mocks

stubs

or local test servers.

---

# CI

All tests

must execute

in CI.

No test

should require

manual intervention.

---

# Speed

Unit tests

should execute

quickly.

Slow tests

should be clearly separated.

---

# Failure Messages

Assertions

should provide

clear failure messages

when appropriate.

---

# Regression Tests

Every bug fix

should include

a regression test

preventing recurrence.

---

# Test Review

Tests

must be reviewed

with the same rigor

as production code.

---

# Cursor and Claude MUST NEVER

Generate tests that depend on execution order

Generate shared mutable state

Generate sleeps for synchronization

Generate production credentials

Generate production database usage

Generate assertions on implementation details

Generate mocked code under test

Generate network calls to real services

Generate duplicate test setup

Generate hardcoded timestamps

Generate flaky tests

Generate unnecessary mocks

Generate tests without assertions

Generate business logic inside test fixtures

Generate ignored failing tests

Generate commented-out tests

---

# Example Testing Strategy

Domain Entity

↓

Pure Unit Test

Use Case

↓

Unit Test with mocked repositories

Repository

↓

Integration Test with test database

Router

↓

Integration Test with FastAPI TestClient

Entire API

↓

End-to-End Test

---

# Testing Checklist

Every feature should satisfy

✓ Domain tests

✓ Use Case tests

✓ Repository tests

✓ Router tests

✓ Validation tests

✓ Authorization tests

✓ Global exception handler tests

✓ Transaction tests

✓ Concurrency tests

✓ Security tests

✓ Regression tests

✓ CI execution

---

# Final Principle

A well-designed architecture is naturally testable.

Each layer should be verified independently while remaining easy to compose into larger integration and end-to-end tests.

Tests should improve confidence, prevent regressions, and document expected behavior rather than merely increase coverage percentages.