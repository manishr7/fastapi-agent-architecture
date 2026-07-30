# ADR-0001: `AsyncSession` as the Unit of Work

## Context

A single business operation (a use case) often needs to touch more than one
repository — e.g. creating a user and assigning a role. That operation must
either fully succeed or fully fail; it must never leave the database with
half the change applied. Something has to own that all-or-nothing boundary.

## Decision

The `AsyncSession` itself is the Unit of Work. No separate `UnitOfWork` or
`TransactionManager` class wraps it. One HTTP request gets exactly one
`AsyncSession` (`04-async.md`); one use case owns exactly one transaction
boundary on that session (`13-transactions.md`); every repository the use
case calls during that operation receives and shares the same session
instance. Only the use case may call `commit()` or `rollback()` —
repositories never do either.

## Why

SQLAlchemy's `AsyncSession` already tracks pending changes and exposes
`commit()`/`rollback()` natively — it already *is* a unit of work in
everything but name. Wrapping it in a dedicated abstraction would duplicate
functionality the session already provides, which `00-philosophy.md`'s KISS
and YAGNI sections argue against directly ("Avoid unnecessary abstraction
layers," "The Rule of Three applies. Only extract abstractions after the
third duplication"). The actual discipline needed — one transaction per
business operation, no partial commits — comes from restricting *who* is
allowed to call `commit()`/`rollback()` (the use case only), not from adding
a new class between the use case and the session.

This also means a use case can coordinate multiple repositories
(`UserRepository` → `RoleRepository` → `PermissionRepository`) inside one
transaction and issue a single `commit()` at the end — the session already
supports that naturally, without any additional coordination object.

## Rejected or deferred alternatives

- **A dedicated `UnitOfWork`/`TransactionManager` class wrapping
  `AsyncSession`.** Rejected: `13-transactions.md` states this explicitly —
  "Do not create additional transaction abstractions unless justified." No
  such justification exists yet at this project's scale.
- **Per-repository commits** (each repository commits its own change).
  Rejected: this would let a single business operation partially succeed —
  directly contradicting `13-transactions.md`'s Philosophy section: "Either
  everything succeeds or everything fails. Never leave the database in a
  partially updated state."
- **Nested transactions / savepoints as the default.** Rejected as the
  common case — `13-transactions.md` treats savepoints as rare, only for a
  genuine partial-rollback business requirement, not a default pattern.

## Rule reference

`13-transactions.md`, `04-async.md`.
