# Architecture: layering and `app.state`

This documents the architecture as it already exists — it's a diagram, not a
proposal. Every edge here corresponds to a rule already in `.claude/rules/`;
where useful, the rule file is named directly on the diagram.

```mermaid
flowchart TD
    Client(["HTTP client"]) --> ApiRouter

    subgraph Composition["app/api/ — composition only (01-folder-structure.md)"]
        ApiRouter["app/api/router.py<br/>prefix=/api"]
        V6Router["app/api/v6/router.py<br/>prefix=/v6"]
        ApiRouter --> V6Router
    end

    V6Router --> ModuleRouter

    subgraph Module["app/modules/&lt;module&gt;/ (per-module layout)"]
        ModuleRouter["router.py"]
        UseCase["use_cases/*.py"]
        Repository["repositories/*.py"]
        Domain["domain/*.py"]

        ModuleRouter -->|"Depends()"| UseCase
        UseCase -->|"one transaction<br/>(13-transactions.md)"| Repository
        Repository -->|"maps to/from"| Domain
        UseCase -.->|"operates on"| Domain
    end

    ModuleRouter -.->|"Depends(get_db)"| GetDb
    UseCase -.->|"Cache / acquire_lock<br/>(22-redis.md)"| RedisInfra["infrastructure/redis/"]

    subgraph State["app.state — set once in main.py lifespan"]
        Settings["settings"]
        SessionFactory["session_factory"]
        RedisClient["redis"]
    end

    GetDb["core/dependencies.get_db()"] -->|reads| SessionFactory
    GetDb -->|"one AsyncSession<br/>per request (04-async.md)"| Repository
    RedisInfra -->|reads| RedisClient
```

## What this diagram deliberately doesn't show

- **Exception flow.** A failure in `Repository` or `UseCase` propagates
  upward and is translated to an HTTP response in exactly one place —
  `app/core/exception_handlers.py`, not shown here since it isn't part of
  the request's happy-path layering. See
  [`docs/decisions/0003-global-exception-handlers-own-http-translation.md`](decisions/0003-global-exception-handlers-own-http-translation.md).
- **Every rule this architecture enforces** — this is the layering shape,
  not the full rule set. See `.claude/rules/` for everything else
  (logging, validation, security, testing).
- **The skip-level import gap** noted in `api/pyproject.toml`'s
  `[tool.importlinter]` — a router importing a repository directly,
  bypassing the use case, isn't drawn as forbidden here because the
  current enforcement (import-linter's layers contract) doesn't actually
  catch that specific case either. The diagram shows the intended shape;
  it doesn't claim more enforcement than exists.

## Enforcement, not just diagram

What actually checks this shape today, per Milestone 3/5's CI:

- `import-linter` (`api/pyproject.toml`) — router/use_cases/repositories/domain
  layering, and `app/api/` composition-only.
- `api/tests/test_architecture_boundaries.py` — repositories never call
  `commit()`/`rollback()`.
- `api/tests/test_async_session_concurrency.py` — a real `AsyncSession`
  rejects concurrent queries, reproducing 04-async.md's hazard directly
  rather than asserting it.
