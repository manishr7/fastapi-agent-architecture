---
description: Defines enterprise validation standards across API, Application, Domain, Repository, and Database layers. Validation responsibilities must remain separated and deterministic.
globs: api/app/modules/**/schemas/**/*.py, api/app/**/use_cases/**/*.py, api/app/**/domain/**/*.py
paths:
  - "api/app/modules/**/schemas/**/*.py"
  - "api/app/**/use_cases/**/*.py"
  - "api/app/**/domain/**/*.py"
alwaysApply: false
---

# ============================================================
# Validation Standards
# ============================================================

# Philosophy

Validation exists at multiple layers.

Each layer validates different concerns.

Never duplicate validation unnecessarily.

Validation responsibilities must remain clearly separated.

---

# Validation Layers

Validation occurs in the following order

HTTP Request

↓

Pydantic Validation

↓

Business Validation

↓

Domain Validation

↓

Persistence Validation

↓

Database Constraints

Never skip layers.

---

# Layer Responsibilities

Router

↓

Request shape

Application (Use Case)

↓

Business rules

Domain

↓

Business invariants

Repository

↓

Persistence translation

Database

↓

Data integrity

---

# HTTP Validation

HTTP validation ensures

- required fields
- types
- formats
- ranges
- request structure

HTTP validation belongs to Pydantic.

---

# Business Validation

Business validation verifies

permissions

workflow

uniqueness requirements

cross-aggregate rules

business policies

Business validation belongs to Use Cases.

---

# Domain Validation

Domain validation protects

business invariants.

Entities should never exist

in invalid business state.

---

# Persistence Validation

Repositories do not validate business rules.

Repositories translate

database failures

into domain-specific persistence exceptions.

---

# Database Validation

The database is the final authority for

- uniqueness
- foreign keys
- check constraints
- nullability
- referential integrity

Never depend solely on application validation.

---

# Pydantic

Use Pydantic

only for

transport validation.

Never place business rules

inside Pydantic validators.

---

# Request Models

Every request body

must have

a dedicated Request DTO.

Never accept

dict

Any

object

---

# Field Types

Use precise field types.

Prefer

EmailStr

UUID

Decimal

datetime

PositiveInt

Literal

Enum

instead of generic

str

int

float

---

# Required Fields

Required fields

must be explicit.

Avoid Optional

unless business meaning exists.

---

# Optional Fields

Optional means

absence is meaningful.

Do not use Optional

to simplify implementation.

---

# Field Constraints

Use Pydantic constraints.

Examples

minimum length

maximum length

regex

numeric ranges

string length

These belong in Request DTOs.

---

# Cross Field Validation

Validation involving multiple fields

belongs in

Pydantic model validators

only when

it concerns request consistency.

Business relationships

belong in Use Cases.

---

# Default Values

Avoid hidden defaults

for business data.

Defaults should be explicit.

---

# Empty Strings

Treat empty strings

according to business rules.

Avoid silently converting

invalid input.

---

# Enums

Use Enums

instead of free-form strings.

Avoid magic values.

---

# Date Validation

Validate

date format

timezone

range

inside Request DTOs.

Business meaning

belongs elsewhere.

---

# File Validation

Validate

file size

content type

extension

before business processing.

---

# Pagination Validation

Validate

offset

limit

sort

search

before entering business logic.

---

# Query Parameters

Use dedicated query schemas

for complex filtering.

Avoid large numbers

of primitive parameters.

---

# Path Parameters

Validate identifiers

before reaching Use Cases.

---

# Business Rules

Business rules belong

inside Use Cases

or Domain Entities.

Examples

Maximum active sessions

Cannot publish twice

Cannot delete root user

Cannot approve own request

---

# Business Invariants

Domain Entities

must guarantee

valid state.

Constructors should reject

invalid entities.

---

# Duplicate Validation

Avoid validating

the same business rule

in multiple layers.

---

# Trust Boundaries

Never trust

client input.

Always validate

external data.

---

# Internal Calls

Even internal APIs

should validate

their inputs.

---

# Repository Validation

Repositories validate

nothing

except persistence translation.

---

# Database Constraints

Always implement

critical constraints

inside the database.

Examples

UNIQUE

FOREIGN KEY

CHECK

NOT NULL

Application validation

is not sufficient.

---

# Exception Handling

Validation failures

must produce

standardized error responses.

Never expose

framework internals.

---

# Error Messages

Messages should be

clear

consistent

actionable.

Avoid technical jargon.

---

# Sensitive Information

Validation messages

must not expose

database schema

SQL

stack traces

implementation details.

---

# Localization

Validation messages

should support localization

when required.

Error codes remain stable.

---

# Error Codes

Every validation error

must include

a stable machine-readable code.

Examples

INVALID_EMAIL

INVALID_DATE

INVALID_FILE

MISSING_REQUIRED_FIELD

INVALID_RANGE

---

# Error Details

Field-level validation

belongs inside

error.details

Example

```json
{
    "details": {
        "email": [
            "Invalid email format."
        ]
    }
}
```

---

# Domain Exceptions

Business validation

should raise

Domain Exceptions.

Never raise HTTPException

inside Domain

or Use Cases.

---

# Database Exceptions

Database constraint failures

must be translated

into application exceptions.

Never expose SQLAlchemy exceptions.

---

# Normalization

Normalize input

only when deterministic.

Examples

trim whitespace

lowercase email

strip surrounding spaces

Avoid changing

business meaning.

---

# Sanitization

Sanitize

only when appropriate.

Validation

does not replace

security measures.

---

# Authorization

Authorization

is not validation.

Treat them separately.

---

# Authentication

Authentication

is not validation.

Treat them separately.

---

# Performance

Validation

should fail fast.

Avoid expensive work

before validation succeeds.

---

# Async Validation

Only perform asynchronous validation

when external resources

are required.

Examples

checking uniqueness

calling external identity providers

Most validation

should remain synchronous.

---

# Value Objects

Complex business values

should be represented

using Value Objects.

Examples

Money

Email

PhoneNumber

Percentage

AcademicYear

PINCode

---

# Testing

Validation should be tested

at every layer.

Test

valid input

invalid input

boundary values

missing fields

duplicate values

unexpected values

---

# Boundary Testing

Always test

minimum

maximum

empty

null

overflow

underflow

edge cases.

---

# Determinism

Validation

must produce

consistent results

for identical input.

---

# Cursor and Claude MUST NEVER

Generate business validation inside routers

Generate SQLAlchemy validation

Generate HTTPException inside Domain

Generate HTTPException inside Use Cases

Generate business rules inside Pydantic validators

Generate duplicate validation

Generate database validation inside repositories

Generate Optional for required fields

Generate magic strings

Generate raw dictionaries

Generate Any for request models

Generate unvalidated external input

Generate SQL error messages

Generate stack traces

Generate client-trusted data

Generate hidden defaults

Generate business logic inside validators

---

# Example Flow

Client Request

↓

Pydantic Request Validation

↓

Use Case Business Validation

↓

Domain Entity Validation

↓

Repository

↓

Database Constraints

↓

Standard Error Response

---

# Validation Checklist

Every feature should satisfy

✓ Request DTO

✓ Query DTO

✓ Path validation

✓ Field validation

✓ Business validation

✓ Domain invariants

✓ Database constraints

✓ Standard error response

✓ Stable error codes

✓ Boundary tests

✓ No duplicated rules

✓ No framework leakage

---

# Final Principle

Validation is layered.

Each layer validates only what it owns.

Pydantic validates transport.

Use Cases validate business workflows.

Domain Entities enforce business invariants.

Repositories translate persistence failures.

The database guarantees data integrity.

A rule should exist in exactly one layer unless redundancy is intentionally required for correctness or security.