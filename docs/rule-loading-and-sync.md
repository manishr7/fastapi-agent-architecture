# How the rule system works

This is the part of the repository most worth understanding on its own
terms — the mechanism, not just the individual rules. It's explained
operationally in `CLAUDE.md` (instructions written *for* Claude Code), but
not anywhere aimed at a human reader. This doc is that.

## Two trees, one authoritative

- `.claude/rules/*.md` — read by Claude Code. **Authoritative.** Edit here
  first.
- `.cursor/rules/*.mdc` — read by Cursor. A synced copy, not a symlink (this
  repository was developed on Windows, where symlinking a tracked file
  reliably is its own source of friction). On Unix, a symlink is a valid
  alternative — see `CONTRIBUTING.md`.

Every rule file exists in both trees with matching content. Cross-references
inside a rule body use the tool-specific extension: `12-errors.md` in the
`.claude` tree, `12-errors.mdc` in the `.cursor` tree, pointing at the same
underlying rule either way.

## Always-on vs. path-scoped

Two files load in every session, regardless of what's being edited:
`project.md` (stack, layout, cross-cutting conventions, rule precedence) and
`20-cursor-anti-patterns.md` (the non-negotiable guardrails). Together
they're the constitution — small enough (~1.2k tokens) to always be in
context.

Everything else — `00`–`19`, `21`, `22` — loads **on demand**, only when a
file matching that rule's `paths:` (Claude Code) / `globs:` (Cursor) pattern
is actually opened. `08-repositories.md` enters context when a file under
`api/app/**/repositories/` is touched, and not otherwise.

This is a deliberate token-budget decision, not an oversight: the full rule
set is roughly 35k tokens. Loading all of it into every session — including
sessions that never touch a repository, or a use case, or Redis — would be
wasteful. Path-scoping means a session editing `app/modules/health/router.py`
only pays for `03-fastapi.md` and whatever else that path matches, not the
other twenty-odd files.

The frontmatter convention that makes this work:

```yaml
globs: api/app/**/use_cases/**/*.py     # Cursor (comma-separated)
paths:                                  # Claude Code (YAML list)
  - "api/app/**/use_cases/**/*.py"
```

Both keys must be present and kept identical. A rule with `globs:` but no
`paths:` silently loads on *every* Claude Code session — that's the
mechanism by which the 35k-token budget creeps back in by accident, one
missing key at a time. A rule with neither key (`alwaysApply: true`) is
correctly always-on; that combination should be rare and deliberate, not a
copy-paste default.

## Precedence, when rules overlap

`project.md` fixes an explicit order for the handful of places two rule
files could plausibly disagree: `12-errors.md` (HTTP errors) outranks
`13-transactions.md` (commits/rollbacks), which outranks `11-validation.md`,
then `10-response-format.md`, then `09-api-design.md`, then `00-philosophy.md`
as the final tiebreaker. This exists so "which rule wins" has one documented
answer instead of being re-litigated per conflict.

## The sync process, honestly

Editing a rule is a two-step, currently-manual process: change the `.md`,
then copy the change into the matching `.mdc`, rewriting cross-reference
extensions as you go. There is no automated check enforcing that the two
trees stay identical.

That's not a hypothetical risk — it already happened. An earlier audit of
this repository found a rule correction that had been applied to
`04-async.md` but not propagated to `05-sqlalchemy-part-1.md`'s copy of the
same example, plus six dangling cross-references left over from a file
rename (`pexm-exams-project.md` → `project.md`) that a text search caught
and a human wouldn't necessarily notice by reading either file in isolation.
Both were fixed by a manual diff pass across every `.md`/`.mdc` pair, not by
tooling — that check doesn't run automatically today. Automating it is a
reasonable next step; it hasn't been built.
