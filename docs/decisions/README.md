# Architecture decisions

This folder holds short records of *why* specific rules in `.claude/rules/`
say what they say. It exists because the rule files themselves are written
as terse, machine-directed prose ("Never do X") — that format works for an
AI agent loading path-scoped context, but it buries the reasoning a human
reader would want.

Nothing here is new thinking. Every ADR below condenses reasoning that
already exists in a specific rule file — each one names its source. If an
ADR and its source rule ever disagree, the rule file is authoritative; treat
the disagreement as a bug in the ADR, not a license to follow the ADR
instead.

## Template

```markdown
# ADR-000X: <Title>

## Context
What problem or tension existed that made a decision necessary.

## Decision
What was decided, stated plainly.

## Why
The reasoning — specific enough to cite the mechanism, not just the rule.

## Rejected or deferred alternatives
What else was considered and explicitly not done, and why.

## Rule reference
Which `.claude/rules/*.md` file(s) this is sourced from.
```

## Index

| ADR | Decision |
|---|---|
| [0001](0001-async-session-as-unit-of-work.md) | `AsyncSession` as the Unit of Work — no separate transaction abstraction |
