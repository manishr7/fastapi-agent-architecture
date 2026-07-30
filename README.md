# PEXM Exams

Exam management platform: **Next.js** in `web/` and **FastAPI** in `api/`.

## Repository layout

| Path | Stack | Role |
|------|--------|------|
| `web/` | Next.js (App Router), TypeScript, React | Web UI, SSR/SSG, API route proxies if needed |
| `api/` | FastAPI, Python 3.12+ | REST API, business logic, persistence |

Open the **`pexm-exams`** folder as your Cursor workspace so project rules match `api/app/` and `web/` paths.

---

## Prerequisites

| Area | Requirement |
|------|-------------|
| **Frontend** | Node.js 20 LTS; **npm** or **pnpm** (match lockfile in `web/` when present) |
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

Edit `api/.env` — set `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`, `CORS_ORIGINS`, and other values. Template: `api/.env.example` or [`api/env.example.md`](api/env.example.md).

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

Follow [`.cursor/rules/`](.cursor/rules/) (layered architecture: `main.py` → `app/api/` composition → module routers → Use Case → Repository → Database).

---

## Frontend (`web/`)

Run commands from **`web/`**.

```bash
cd web
npm install          # or: pnpm install
cp .env.example .env.local   # when present
npm run dev
```

| Task | Command (from `web/`) |
|------|------------------------|
| Dev server | `npm run dev` |
| Production build | `npm run build` |
| Lint | `npm run lint` |

App (dev): http://localhost:3000

---

## Environment variables

| Variable | Where | Purpose |
|----------|--------|---------|
| `NEXT_PUBLIC_API_URL` | `web/.env.local` | Browser-facing API base URL |
| `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` | `api/.env` | MySQL connection (driver: `mysql+asyncmy`, assembled via `URL.create()`) |
| `DB_SSL_CA`/`DB_SSL_CERT`/`DB_SSL_KEY` | `api/.env` | Optional TLS — CA-only or mutual TLS (cert+key must be set together) |
| `CORS_ORIGINS` | `api/.env` | Allowed origins (include frontend URL in dev) |

Never commit secrets. Use `.env.example` / `.env.local.example` with placeholders only.

---

## Development workflow

1. Run **api** and **web** in separate terminals.
2. Share contracts via OpenAPI (FastAPI) and TypeScript types in `web/`.
3. Keep UI in `web/` and domain/HTTP logic in `api/`.
4. Use Cursor rules under `.cursor/rules/` for consistent architecture.

---

## Cursor AI

**`project.mdc`** and **`20-cursor-anti-patterns.mdc`** always apply; other rules load by file path. See `.cursor/rules/` for the full index.

---

## Deployment (Linux server)

Assumes a single Linux host (Ubuntu/Debian-style). Adjust paths, users, and domains for your environment.

### 1. Server packages

```bash
sudo apt update
sudo apt install -y git nginx mysql-server   # or use managed MySQL
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install Node 20 (e.g. NodeSource or nvm) for the frontend build
```

Create a deploy user and app directory, e.g. `/opt/pexm-exams`.

### 2. Application code

```bash
sudo mkdir -p /opt/pexm-exams
sudo chown "$USER:$USER" /opt/pexm-exams
git clone <your-repo-url> /opt/pexm-exams
cd /opt/pexm-exams
```

### 3. Backend

```bash
cd /opt/pexm-exams/api
cp .env.example .env
# Edit .env: DB_HOST/DB_USER/DB_PASSWORD (+ DB_SSL_* if the DB requires TLS),
# CORS_ORIGINS (production frontend URL), DEBUG=false

uv sync                    # production deps only (omit --extra dev)
uv run alembic upgrade head   # when migrations exist
```

Run API with a process manager (example **systemd** unit `/etc/systemd/system/pexm-api.service`):

```ini
[Unit]
Description=PEXM Exams API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/pexm-exams/api
EnvironmentFile=/opt/pexm-exams/api/.env
ExecStart=/home/deploy/.local/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Use the real path to `uv` from `which uv`. Do not expose uvicorn directly to the internet; bind to `127.0.0.1` and proxy with nginx.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pexm-api
```

### 4. Frontend

```bash
cd /opt/pexm-exams/web
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL to public API URL
npm ci
npm run build
```

Serve with **nginx** static + Node standalone, or `npm run start` behind nginx (or PM2). Example: proxy `https://your-domain/` to Next on port 3000 and `https://your-domain/api` or `api.your-domain` to port 8000.

Minimal **nginx** snippet (API on subdomain):

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

### 5. Checks

- `curl -s http://127.0.0.1:8000/api/v6/health` on the server  
- `curl -s https://api.example.com/api/v6/ready` after DB is configured  
- Frontend loads and calls `NEXT_PUBLIC_API_URL`  
- Firewall allows 80/443 only; MySQL not exposed publicly  

### 6. Updates

```bash
cd /opt/pexm-exams && git pull
cd api && uv sync && uv run alembic upgrade head && sudo systemctl restart pexm-api
cd ../web && npm ci && npm run build && sudo systemctl restart pexm-web   # if using a web service
```

Document your exact service names and Node process manager in your ops runbook.
