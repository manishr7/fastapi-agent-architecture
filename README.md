# FastAPI Agent Architecture

[![CI](https://github.com/manishr7/fastapi-agent-architecture/actions/workflows/ci.yml/badge.svg)](https://github.com/manishr7/fastapi-agent-architecture/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A FastAPI reference backend where the layered architecture (Router → Use Case
→ Repository → Database) is enforced through a rule set that both human
contributors and AI coding agents (Claude Code, Cursor) are expected to
follow. Extracted from a larger private codebase as a standalone reference —
see [Project status](#project-status) for exactly what that means in
practice.

## Project status

This is a reference architecture, not a finished product.

- **Implemented and tested:** the `health` module
  (`api/app/modules/health/`) — router, use case, domain, repository,
  schemas — is a complete, working vertical slice. Cross-cutting
  infrastructure (`api/app/core/`, `api/app/database/`,
  `api/app/infrastructure/redis/`, `api/app/shared/responses/`) is
  implemented, not stubbed.
- **Not implemented:** the `auth` module is a stub — `router.py` only; its
  `domain/`, `repositories/`, `schemas/`, and `use_cases/` folders are
  intentionally empty (see `.claude/rules/01-folder-structure.md`'s
  per-module layout rule, which this stub does not yet satisfy).
- **Backend only.** The rule set anticipates a Next.js frontend under
  `web/` (see `.claude/rules/nextjs-frontend.md`, a deliberate stub) — no
  such directory exists in this repository today.
- **Not production-proven.** This repository has not been deployed or run
  under real traffic. Claims here describe what's checkable in the code and
  CI, not operational history.

## Known limitations

What the enforcement mechanisms above don't cover, stated plainly rather
than discovered by surprise:

- **Layer skipping isn't caught.** The `import-linter` layers contract
  (`api/pyproject.toml`) forbids a lower layer importing a higher one, but
  it doesn't forbid a higher layer skipping an adjacent one — e.g. a router
  importing a repository directly, bypassing its use case. Catching that
  would need a second contract type or a custom check; neither exists yet.
- **No database or Redis in CI.** Tests mock `AsyncSession` and the Redis
  client rather than exercising a real MySQL or Redis instance — nothing in
  CI currently verifies real connectivity, only the translation/business
  logic built on top of it.
- **The rule-tree sync is manual.** `.claude/rules/*.md` and
  `.cursor/rules/*.mdc` are kept in sync by hand, not by tooling — see
  `CONTRIBUTING.md`. It has already drifted once in this repository's own
  history; nothing currently prevents it from happening again.
- **One real module.** The five-folder per-module pattern
  (`01-folder-structure.md`) has been exercised by exactly one complete
  implementation (`health`). It hasn't been proven across enough modules to
  know how it holds up at more realistic scale.

## Repository layout

| Path | Stack | Role |
|------|--------|------|
| `api/` | FastAPI, Python 3.12+ | REST API, use cases, persistence |
| `.claude/rules/` | Markdown | Architecture rules for Claude Code (authoritative) |
| `.cursor/rules/` | Markdown | Same rules, synced for Cursor — see `CLAUDE.md` |

Open this repository's root as your workspace so rule paths resolve correctly.

## Documentation

The rule files (`.claude/rules/`) are written as terse, machine-directed
prose — correct, but not where the reasoning lives. For the "why," not just
the "what":

- [`docs/decisions/`](docs/decisions/) — short ADRs condensing reasoning
  already in the rules: `AsyncSession` as the Unit of Work, Redis's
  fail-open cache vs. fail-closed locks, why global exception handlers own
  HTTP translation, `log_context` vs. `details`.
- [`docs/rule-system.md`](docs/rule-system.md) — how the two rule trees
  (`.claude/rules/` vs. `.cursor/rules/`) stay in sync, why rules load
  always-on vs. path-scoped, and rule precedence when two files overlap.
- [`docs/architecture.md`](docs/architecture.md) — a diagram of the
  layering flow and `app.state` resources, plus exactly what enforces it
  today (import-linter, the repository-boundary test, the `AsyncSession`
  concurrency test) versus what's diagram-only intent.

---

## Prerequisites

| Area | Requirement |
|------|-------------|
| **Backend** | Python 3.12+ on PATH; **[uv](https://docs.astral.sh/uv/)** (install below) |
| **Database** | MySQL (async driver: `asyncmy` via `DB_HOST`/`DB_USER`/`DB_PASSWORD`/etc.) |

---

## Backend (`api/`)

FastAPI application code lives under `api/app/`. Dependencies are defined in [`api/pyproject.toml`](api/pyproject.toml) and installed with **uv**. Run commands from **`api/`**.

### Install uv (one-time)

**Windows (PowerShell):**

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux / macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart the terminal, then run `uv --version`. If the command is missing, add the install path shown by the installer to your PATH.

### Environment file

| Platform | Command |
|----------|---------|
| Linux / macOS | `cp .env.example .env` |
| Windows (PowerShell) | `Copy-Item .env.example .env` |
| Windows (cmd) | `copy .env.example .env` |

Edit `api/.env` — set `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`, `CORS_ORIGINS`, and other values. Template: `api/.env.example`.

### Install and run (development)

1. **Install dependencies** (from `api/`):

   ```bash
   cd api
   uv sync --extra dev
   ```

2. **Configure environment** — if you have not already, copy `api/.env.example` to `api/.env` and set `DB_HOST`/`DB_USER`/`DB_PASSWORD`, `CORS_ORIGINS`, etc. (see [Environment file](#environment-file) above).

3. **Start the API** (from `api/`):

   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Install Git hooks** (once per clone, from the **repo root**, with `uv` on PATH). Commits then run `ruff check --fix` and `ruff format` on staged Python files under `api/`:

   ```bash
   uv run --project api pre-commit install
   ```

**While developing**

- API docs: http://localhost:8000/docs
- `GET /api/v6/health` — liveness (no DB)
- `GET /api/v6/ready` — readiness (requires a working `DB_HOST`/`DB_USER`/`DB_PASSWORD` connection)

**Other commands**

| Task | Command (from `api/`) |
|------|------------------------|
| Tests | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |

| Task | Command (from repo root) |
|------|---------------------------|
| Pre-commit (all files) | `uv run --project api pre-commit run --all-files` |

### Backend conventions

Follow [`.claude/rules/`](.claude/rules/) (authoritative) or [`.cursor/rules/`](.cursor/rules/) (synced copy) — layered architecture: `main.py` → `app/api/` composition → module routers → Use Case → Repository → Database.

---

## Environment variables

| Variable | Where | Purpose |
|----------|--------|---------|
| `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` | `api/.env` | MySQL connection (driver: `mysql+asyncmy`, assembled via `URL.create()`) |
| `DB_SSL_CA`/`DB_SSL_CERT`/`DB_SSL_KEY` | `api/.env` | Optional TLS — CA-only or mutual TLS (cert+key must be set together) |
| `CORS_ORIGINS` | `api/.env` | Allowed origins |

Never commit secrets. Use `.env.example` with placeholders only.

---

## Cursor AI / Claude Code

**`project.md`**/**`.mdc`** and **`20-cursor-anti-patterns.md`**/**`.mdc`** always apply; other rules load by file path. See `.claude/rules/` (authoritative) and `.cursor/rules/` (synced copy) for the full index — `CLAUDE.md` explains how the two trees are kept in sync and why.

---

## Deployment (Linux server)

Assumes a single Linux host (Ubuntu/Debian-style). The paths, user, and service name below (`/opt/fastapi-agent-architecture`, `fastapi-agent-architecture-api.service`) are examples — adjust for your environment; this repository has not itself been deployed anywhere under these names.

### 1. Server packages

```bash
sudo apt update
sudo apt install -y git nginx mysql-server   # or use managed MySQL
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a deploy user and app directory, e.g. `/opt/fastapi-agent-architecture`.

### 2. Application code

```bash
sudo mkdir -p /opt/fastapi-agent-architecture
sudo chown "$USER:$USER" /opt/fastapi-agent-architecture
git clone <your-repo-url> /opt/fastapi-agent-architecture
cd /opt/fastapi-agent-architecture
```

### 3. Backend

```bash
cd /opt/fastapi-agent-architecture/api
cp .env.example .env
# Edit .env: DB_HOST/DB_USER/DB_PASSWORD (+ DB_SSL_* if the DB requires TLS),
# CORS_ORIGINS (production frontend URL, if any), DEBUG=false

uv sync                    # production deps only (omit --extra dev)
uv run alembic upgrade head   # when migrations exist
```

Run API with a process manager (example **systemd** unit `/etc/systemd/system/fastapi-agent-architecture-api.service`):

```ini
[Unit]
Description=FastAPI Agent Architecture API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/fastapi-agent-architecture/api
EnvironmentFile=/opt/fastapi-agent-architecture/api/.env
ExecStart=/home/deploy/.local/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Use the real path to `uv` from `which uv`. Do not expose uvicorn directly to the internet; bind to `127.0.0.1` and proxy with nginx.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now fastapi-agent-architecture-api
```

Minimal **nginx** snippet:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable TLS with **certbot** (`certbot --nginx`) for production.

### 4. Checks

- `curl -s http://127.0.0.1:8000/api/v6/health` on the server
- `curl -s https://api.example.com/api/v6/ready` after DB is configured
- Firewall allows 80/443 only; MySQL not exposed publicly

### 5. Updates

```bash
cd /opt/fastapi-agent-architecture && git pull
cd api && uv sync && uv run alembic upgrade head && sudo systemctl restart fastapi-agent-architecture-api
```

Document your exact service names and process manager in your ops runbook.
