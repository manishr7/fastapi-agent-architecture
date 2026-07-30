# Claude Code setup

Project conventions are **not** duplicated here. They live in `.claude/rules/*.md`
(authoritative). `.cursor/rules/*.mdc` are **copies** for Cursor — on Windows they
are not symlinks; after editing `.claude/rules`, sync the matching `.mdc` file and
transform cross-references (see [Editing rules](#editing-rules)).

## How the rules load

| Rule | Loading |
| ---- | ------- |
| `project.md`, `20-cursor-anti-patterns.md` (no `paths:`) | Every session — stack, layering, guardrails, rule precedence |
| Everything else (`00`–`19`, `nextjs-frontend`) | On demand, when I read a file matching their `paths:` |

Path scoping is what keeps this affordable: the full rule set is ~35k tokens, so
loading it all every session would be wasteful. Only the ~1.2k tokens of always-on
guardrails plus the rules for the layer I'm actually editing enter context.

Consequence worth knowing: I see `08-repositories.md` when I open a file under
`api/app/**/repositories/`, but **not** while discussing repositories abstractly.
If a conversation about backend design happens before any file is opened, ask me
to read the relevant rule first.

## Editing rules

Edit `.claude/rules/*.md` first, then sync to `.cursor/rules/*.mdc`.

**Cross-references inside rule bodies** use the tool-specific extension:

| Location | Cross-reference example |
| -------- | ----------------------- |
| `.claude/rules/*.md` | `12-errors.md`, `17-testing.md` |
| `.cursor/rules/*.mdc` | `12-errors.mdc`, `17-testing.mdc` |

When syncing to Cursor, copy content and rewrite rule cross-references from `.md` to `.mdc`
(e.g. `12-errors.md` → `12-errors.mdc`). Do not change paths like `api/app/main.py`.

Frontmatter must carry **both** keys, kept identical:

```yaml
globs: api/app/**/use_cases/**/*.py     # Cursor (comma-separated)
paths:                                  # Claude Code (YAML list)
  - "api/app/**/use_cases/**/*.py"
```

- A rule with `globs:` but no `paths:` loads on **every** session in Claude Code —
  that's how the 35k creeps back in.
- An always-on rule (`alwaysApply: true`) correctly has neither key.
- Brace globs are fine: Claude Code expands `web/**/*.{ts,tsx,js,jsx}` into four
  patterns (budget: 1,000 expanded patterns per rule). Escape a literal `[` as
  `\[`, or the pattern matches nothing.

New rule file → create under `.claude/rules/`, add `paths:` and `globs:`, then copy
to `.cursor/rules/<name>.mdc` with cross-references using `.mdc`. On Unix, symlinks
are an alternative:

```bash
ln -sfn ../../.claude/rules/21-foo.md .cursor/rules/21-foo.mdc
```

(Symlinks require cross-references to stay `.md` in both trees, or use copies with
the extension convention above.)

## Commands

Run these from inside `api/` or `web/`, not the repo root.

Backend (`api/`): `uvicorn app.main:app --reload --port 8000` · `pytest` ·
`ruff check .` · `alembic revision --autogenerate -m "..."` · `alembic upgrade head`

Frontend (`web/`): `npm run dev` · `npm run build` · `npm run lint`

Treat both lists as the intended commands, not a guarantee they're wired up yet.
`api/pyproject.toml` and `web/package.json` are the authority — check there if a
command fails, and update this section if the real scripts diverge.

## Rule coverage follows the tree

A path-scoped rule stays silent until a file matching its `paths:` exists. That is
the one durable consequence of this setup, and it cuts both ways:

- Coverage **grows on its own** as the scaffold fills in. No rule edits needed.
- "The rule didn't fire" almost always means "that directory doesn't exist yet,"
  not "the rule is broken."

So don't assume the layout from anything written here — check it:

```bash
git ls-files api web            # what actually exists
grep -L '^paths:' .claude/rules/*.md   # rules that load every session
```

`/context` lists what really entered context under **Memory files**. Use it when a
rule seems missing.

`api/` and `web/` fill in independently, so expect them to be at different stages.
Backend layers arrive in the shape `01-folder-structure.md` defines; a new module
under `api/app/modules/<module>/` means all five of `router.py`, `schemas/`,
`use_cases/`, `domain/`, `repositories/` — never a partial module.

`nextjs-frontend.md` is a deliberate stub. Fill it when `web/` gets real code;
until then it correctly contributes nothing.
