---
description: Defines REST API design standards, endpoint conventions, request/response schemas, versioning, pagination, filtering, and HTTP semantics.
globs: api/app/api/**/*.py, api/app/modules/**/router.py, api/app/modules/**/schemas/**/*.py, api/app/shared/**/responses/**/*.py
paths:
  - "api/app/api/**/*.py"
  - "api/app/modules/**/router.py"
  - "api/app/modules/**/schemas/**/*.py"
  - "api/app/shared/**/responses/**/*.py"
alwaysApply: false
---

# ============================================================
# API Design Standards
# ============================================================

# Philosophy

APIs are contracts.

Once published,

they should remain stable.

API consistency is more important than personal preference.

Every endpoint should behave predictably.

---

# REST

Use REST principles.

Resources are nouns.

Operations are HTTP methods.

Avoid action-oriented URLs.

Good

/users

/users/{id}

/schools/{id}

/reports

Bad

/createUser

/deleteSchool

/getReport

/updateRole

---

# API Versioning

Every endpoint must be versioned.

Current standard

/api/v6

Versioning is composed through the `app/api/` presentation layer:

- `app/api/router.py` — `prefix="/api"`
- `app/api/v6/router.py` — `prefix="/v6"`, includes all module routers
- Module routers define resource paths only (e.g. `/users`, `/health`)

When a new version requires breaking changes, add `app/api/v7/router.py`.
Feature modules remain version-agnostic; only `app/api/` changes.

Never expose unversioned endpoints.

Never register module routers directly in `main.py`.

---

# URL Naming

Use lowercase.

Use hyphens only when necessary.

Avoid camelCase.

Good

/student-attendance

/user-roles

Bad

/studentAttendance

/UserRoles

---

# Plural Resources

Collection endpoints should be plural.

Good

/users

/teachers

/reports

Bad

/user

/teacher

/report

---

# HTTP Methods

GET

Read

POST

Create

PUT

Complete replacement

PATCH

Partial update

DELETE

Delete

Never misuse HTTP verbs.

---

# Idempotency

GET

PUT

DELETE

must be idempotent.

Critical POST operations

should support idempotency keys.

---

# Resource Identifiers

Path parameters identify resources.

Good

/users/{user_id}

Bad

/users?id=10

when referring to one resource.

---

# Query Parameters

Query parameters belong to

filtering

sorting

pagination

search

Never use query parameters

for resource identity.

---

# Nested Resources

Use nested resources

only for true ownership.

Good

/schools/{school_id}/teachers

Avoid excessive nesting.

Maximum depth

2

---

# Endpoint Size

Each endpoint should perform

one operation.

Avoid endpoints

with multiple unrelated behaviors.

---

# Request Models

Every request body

must use

Pydantic models.

Never accept raw dictionaries.

---

# Response Models

Every endpoint

must declare

response_model.

Never return arbitrary dictionaries.

---

# Response Envelope

Every response — success or error — uses the standard envelope
(`data`/`meta`/`error`). Full contract: **`10-response-format.md`**.

Never invent custom response formats. Never expose stack traces.

---

# Status Codes

200

Successful GET

201

Created

202

Accepted

204

Successful delete

400

Bad Request — application `ValidationException` or invalid client input at the application layer.

401

Unauthorized

403

Forbidden

404

Not Found

409

Conflict

422

Unprocessable Entity — FastAPI/Pydantic `RequestValidationError` or `BusinessRuleViolation`.

Canonical mapping: `12-errors.md`.

429

Rate Limited

500

Internal Error

503

Service Unavailable — dependency unreachable (`ServiceUnavailableException`). Canonical mapping: `12-errors.md`.

Use the correct status code.

---

# Pagination

Large collections

must support pagination.

Current standard

offset

limit

Never return

unbounded datasets.

---

# Pagination Metadata

Meta should include

offset

limit

total

has_next

Example

```json
{
  "meta": {
    "offset": 0,
    "limit": 20,
    "total": 134,
    "has_next": true
  }
}
```

---

# Filtering

Filtering belongs

in query parameters.

Example

GET

/users?status=ACTIVE

Never encode filters

inside request bodies

for GET requests.

---

# Sorting

Sorting uses

sort_by

sort_order

Example

/users?sort_by=name&sort_order=asc

Allowed values

asc

desc

---

# Searching

Use

search

for keyword searches.

Example

/users?search=john

---

# Field Names

Use

snake_case

throughout the API.

Do not mix

camelCase

snake_case

PascalCase.

---

# Dates

Use ISO-8601.

Always include timezone

when applicable.

Good

2026-07-28T10:30:00Z

---

# Null Values

Use null

only when

absence is meaningful.

Avoid unnecessary null fields.

---

# Empty Collections

Return

[]

Never return

null

for collections.

---

# Booleans

Return proper booleans.

Never use

0

1

"true"

"false"

---

# Validation

Input validation belongs

to Pydantic.

Business validation belongs

to Use Cases.

Database validation belongs

to the database.

---

# Authentication

Authentication

should occur

before entering business logic.

---

# Authorization

Authorization

should occur

before sensitive operations.

Never rely solely

on frontend restrictions.

---

# File Uploads

Use multipart/form-data.

Never encode files

inside JSON.

---

# File Downloads

Large downloads

should stream responses.

Avoid loading files

fully into memory.

---

# OpenAPI

Every endpoint

must include

summary

description

response_model

tags

---

# Tags

Group endpoints

by business module.

Examples

Users

Schools

Reports

Teachers

---

# Deprecation

Deprecated endpoints

must remain documented.

Provide migration guidance.

Avoid immediate removal.

---

# Backward Compatibility

Avoid breaking changes

within the same API version.

Introduce

new versions

for breaking changes.

---

# Performance

Avoid endpoints

that execute

multiple expensive operations.

Split responsibilities.

---

# Batch Operations

Batch endpoints

must be explicit.

Examples

/users/bulk-delete

/users/bulk-import

Avoid hidden batching.

---

# Sensitive Data

Never expose

passwords

tokens

internal IDs

secrets

database implementation details.

---

# Error Messages

Errors should be

human-readable

consistent

non-sensitive

Avoid leaking

SQL

stack traces

framework internals.

---

# Logging

Log

failures

warnings

security events.

Avoid logging

sensitive request data.

---

# Rate Limiting

Endpoints

should support

rate limiting

where appropriate.

---

# Async

Endpoints performing I/O

must be async.

Never use blocking libraries.

---

# Documentation

API documentation

must stay synchronized

with implementation.

---

# Testing

Every endpoint

should have

integration tests.

Critical endpoints

should also have

authorization tests.

---

# Cursor and Claude MUST NEVER

Generate unversioned endpoints

Generate action-based URLs

Generate camelCase fields

Generate raw dictionaries

Generate inconsistent response formats

Generate missing response_model

Generate SQL inside routers

Generate business logic inside routers

Generate ORM models in responses

Generate stack traces in API responses

Generate passwords in responses

Generate unbounded GET endpoints

Generate POST for reads

Generate GET with request bodies

Generate file uploads in JSON

Generate HTTP 200 for creation

Generate inconsistent pagination

Generate undocumented endpoints

Generate blocking operations inside routers

---

# Example Flow

HTTP Request

↓

Router

↓

Pydantic Request Model

↓

Use Case

↓

Repository

↓

Domain Entity

↓

Response DTO

↓

Standard Response Envelope

↓

HTTP Response

---

# API Checklist

Every endpoint should satisfy

✓ Versioned

✓ RESTful

✓ One responsibility

✓ Async

✓ Request model

✓ Response model

✓ Standard response envelope

✓ Correct HTTP status

✓ Pagination support

✓ Validation

✓ Authorization

✓ No business logic

✓ No ORM leakage

✓ Integration tested

---

# Final Principle

An API is a public contract.

Every endpoint should be predictable, consistent, versioned, well-documented, and independent of internal implementation details.