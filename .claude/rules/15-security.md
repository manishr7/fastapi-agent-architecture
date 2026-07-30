---
description: Defines enterprise security standards, authentication, authorization, secrets management, secure coding practices, OWASP recommendations, and defense-in-depth principles.
globs: api/app/core/security.py, api/app/core/middleware.py, api/app/core/dependencies.py, api/app/api/**/*.py, api/app/modules/auth/**/*.py, api/app/modules/**/router.py
paths:
  - "api/app/core/security.py"
  - "api/app/core/middleware.py"
  - "api/app/core/dependencies.py"
  - "api/app/api/**/*.py"
  - "api/app/modules/auth/**/*.py"
  - "api/app/modules/**/router.py"
alwaysApply: false
---

# ============================================================
# Security Standards
# ============================================================

# Philosophy

Security is a system-wide responsibility.

Every layer contributes

to security

without duplicating responsibilities.

Security must be

intentional

predictable

auditable.

---

# Security Layers

Security should be applied

in layers.

Client

↓

Transport

↓

Authentication

↓

Authorization

↓

Validation

↓

Business Rules

↓

Database

Never rely

on a single protection layer.

---

# Trust Boundary

Treat all external input

as untrusted.

Examples

HTTP requests

Headers

Cookies

JWT claims

Uploaded files

Query parameters

Environment variables

Third-party APIs

Validate before use.

---

# Authentication

Authentication answers

Who is the user?

Authentication belongs

before business logic.

Unauthenticated requests

must never reach

Use Cases.

---

# Authorization

Authorization answers

Can the authenticated user perform this action?

Authorization belongs

inside

Use Cases

or

dedicated authorization services.

Never rely solely

on frontend restrictions.

---

# Ownership

Routers

↓

Authentication

Use Cases

↓

Authorization

Repositories

↓

Persistence

Domain

↓

Business Rules

Never mix responsibilities.

---

# JWT

JWTs must be

validated

before use.

Verify

signature

expiration

issuer

audience

when applicable.

Never trust

decoded payloads

without verification.

---

# Passwords

Passwords must never be

logged

returned

stored in plaintext

cached

included in exceptions.

Always use

strong password hashing.

Never implement

custom cryptography.

---

# Secrets

Secrets include

JWT signing keys

Database credentials

API keys

Encryption keys

OAuth secrets

SMTP credentials

Never hardcode secrets.

Read secrets

through centralized configuration.

---

# Configuration

Configuration belongs

inside

app/core/config.py

Never read

environment variables

throughout the application.

Inject configuration.

---

# Sensitive Data

Never expose

passwords

password hashes

refresh tokens

JWT secrets

API keys

database credentials

private keys

internal IP addresses

filesystem paths

SQL queries

stack traces

to clients.

---

# Logging

Never log

passwords

tokens

cookies

Authorization headers

API keys

credit card data

personal identifiers

unless explicitly required
and properly masked.

---

# Input Validation

Validate every external input. Validation does not replace authorization.

Layer responsibilities (Pydantic vs use case vs domain): **`11-validation.md`**.

---

# SQL Injection

Always use

parameterized SQL.

Prefer SQLAlchemy ORM

or parameterized queries.

Never build SQL

using string concatenation.

---

# Command Injection

Never execute

shell commands

using untrusted input.

If external processes

are required

validate inputs strictly.

---

# File Uploads

Validate

content type

file size

extension

business constraints.

Never trust

client-provided MIME types.

---

# Path Traversal

Never concatenate

filesystem paths

using user input.

Use

pathlib

and safe path resolution.

---

# XSS

Treat all user input

as untrusted.

Frontend

is responsible

for output encoding.

Backend

must avoid returning

unsafe HTML

unless explicitly required.

---

# CSRF

If cookie authentication

is used

implement CSRF protection.

Stateless Bearer authentication

does not require CSRF tokens.

---

# Rate Limiting

Sensitive endpoints

should support

rate limiting.

Examples

Login

Password reset

OTP verification

Public APIs

---

# Brute Force

Authentication endpoints

should detect

repeated failures.

Support

temporary lockout

or throttling.

---

# Session Management

Sessions

must expire.

Support

logout

token expiration

token rotation

when applicable.

---

# Least Privilege

Grant

minimum required permissions.

Avoid administrative access

by default.

---

# Role Checks

Authorization

must be explicit.

Never infer permissions

from usernames

or client-provided values.

---

# Multi-Step Authorization

Validate authorization

for every sensitive action.

Never assume

previous authorization

remains valid.

---

# Database Security

The database

enforces

constraints

integrity

transactions.

Application code

must not bypass

database protections.

---

# Encryption

Use established libraries.

Never implement

custom encryption algorithms.

Encrypt sensitive data

at rest

when required.

Always use TLS

for data in transit.

---

# External APIs

Treat external services

as untrusted.

Validate

responses

status codes

payloads

timeouts.

---

# Error Messages

Errors must not reveal implementation details, credentials, or security-sensitive data.

Envelope shape and client-safe messaging: **`12-errors.md`**.

---

# Global Exception Handler

Security-related exceptions propagate to the global handler; security code must not build HTTP responses directly.

Handler location, mapping, and logging: **`12-errors.md`**.

`FastAPI(debug=...)` in `main.py` MUST always be `False`, never
`settings.debug`. Starlette's `ServerErrorMiddleware` uses that flag to
render raw HTML stack traces directly to clients when an exception escapes
the registered handlers — a distinct, client-facing risk from
`settings.debug`'s legitimate job of controlling internal log verbosity
(log format, SQL echo, traceback-in-logs). Never reconnect them.

---

# Dependency Injection

Inject

security services

through FastAPI dependencies.

Avoid

global mutable security state.

---

# Audit Logging

Audit

authentication

authorization

permission changes

privileged operations

security failures.

Audit logs

must be immutable

where practical.

---

# Sensitive Operations

Examples

Delete user

Change password

Assign permissions

Reset credentials

Modify roles

Require

authentication

authorization

auditing.

---

# Data Exposure

Return

only required fields.

Never expose

internal identifiers

unless part of the API contract.

---

# Principle of Least Knowledge

Components should know

only what they need.

Avoid passing

authentication objects

through unrelated layers.

---

# Security Headers

When applicable

configure

HSTS

X-Content-Type-Options

X-Frame-Options

Content-Security-Policy

Referrer-Policy

through middleware.

---

# CORS

Use

explicit origins.

Avoid

allow_origins=["*"]

for authenticated APIs.

Restrict

methods

headers

credentials

appropriately.

---

# Dependency Security

Keep dependencies

up to date.

Remove unused packages.

Monitor security advisories.

---

# Third-Party Libraries

Prefer

actively maintained

well-reviewed

widely adopted

libraries.

Avoid unnecessary dependencies.

---

# Async Security

Never block

authentication

authorization

or cryptographic operations

inside the event loop

if heavy CPU work

is required.

---

# Background Tasks

Background jobs

must perform

authentication

authorization

when acting

on behalf of users.

Do not assume

scheduler trust.

---

# Monitoring

Monitor

failed logins

permission failures

rate limits

unexpected access

security exceptions

token validation failures.

---

# Testing

Security testing

should include

authentication

authorization

input validation

JWT validation

role checks

privilege escalation

SQL injection

path traversal

file upload validation

rate limiting.

---

# OWASP

Follow

OWASP Top 10

recommendations.

Review security

as part of

code review.

---

# Cursor and Claude MUST NEVER

Generate plaintext passwords

Generate hardcoded secrets

Generate SQL concatenation

Generate custom cryptography

Generate authorization inside repositories

Generate authentication inside repositories

Generate authorization based on client input

Generate security checks only on the frontend

Generate passwords in logs

Generate JWT secrets in code

Generate stack traces to clients

Generate wildcard CORS for authenticated APIs

Generate disabled TLS verification

Generate trust in client-provided roles

Generate security logic inside Domain Entities

Generate environment variable reads outside centralized configuration

Generate sensitive information inside exceptions

Generate hidden backdoor accounts

Generate debug endpoints in production

---

# Example Flow

HTTP Request

↓

Authentication

↓

JWT Validation

↓

Router

↓

Use Case Authorization

↓

Business Logic

↓

Repository

↓

Database

↓

Global Exception Handler

↓

Standard Response

---

# Security Checklist

Every feature should satisfy

✓ Authentication

✓ Authorization

✓ Input validation

✓ Parameterized SQL

✓ No hardcoded secrets

✓ Least privilege

✓ Audit logging

✓ Secure error handling

✓ Standard error response

✓ Sensitive data protected

✓ Security tests

✓ Dependency review

---

# Final Principle

Security is not a single feature.

It is a collection of small, consistently applied practices across the entire architecture.

Authentication identifies the caller.

Authorization verifies permissions.

Validation protects system integrity.

Transactions preserve consistency.

The global exception handler prevents information leakage.

Together, they create a secure, maintainable, and predictable backend.