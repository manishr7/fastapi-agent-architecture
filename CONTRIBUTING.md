# Contributing

This repository's architecture is frozen — contributions should conform to
the existing layered design (`Router → Use Case → Repository → Database`),
not propose alternatives. See `.claude/rules/00-philosophy.md` and
`.claude/rules/01-folder-structure.md` for what's non-negotiable.

## The one process you need to get right: rule sync

Architecture rules live in two trees that must stay in sync:

- `.claude/rules/*.md` — **authoritative.** Edit here first.
- `.cursor/rules/*.mdc` — a synced copy for Cursor. Not a symlink on
  Windows; on Unix a symlink is an option (see `CLAUDE.md`), but this
  repository uses plain copies.

**Workflow:** edit the `.md` file, then copy the change to the matching
`.mdc` file, rewriting any cross-references from `.md` to `.mdc` as you go
(`12-errors.md` → `12-errors.mdc`). Never change file paths like
`api/app/main.py` — only rule-file cross-references get the extension
swap.

**Frontmatter must carry both keys, kept identical:**

```yaml
globs: api/app/**/use_cases/**/*.py     # Cursor (comma-separated)
paths:                                  # Claude Code (YAML list)
  - "api/app/**/use_cases/**/*.py"
```

A rule with `globs:` but no `paths:` loads on *every* Claude Code session —
that defeats the path-scoping this project relies on to keep context cheap.
An always-on rule (`alwaysApply: true`) correctly has neither key.

**Before opening a PR that touches `.claude/rules/` or `.cursor/rules/`:**
diff the `.md` you changed against its `.mdc` counterpart (accounting for
the `.md`→`.mdc` cross-reference swap) and confirm they still say the same
thing. This repository's own history includes rule pairs that drifted
silently — the audit that caught it is not automated yet, so doing this by
hand is currently the only check.

## Everything else

- Backend commands run from `api/` — see the README's "Backend (`api/`)"
  section.
- Lint/format: `ruff check --fix` + `ruff format`, enforced via
  `.pre-commit-config.yaml`. Run `uv run --project api pre-commit install`
  once per clone.
- Tests: `uv run pytest` from `api/`.
