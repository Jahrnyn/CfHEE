# CfHEE

CfHEE is a local-first, scoped knowledge infrastructure module for storage, retrieval, and retrieval-derived context building.

It provides a reusable backend component for storing, organizing, and retrieving domain-specific knowledge with strict scope isolation and full traceability.

---

## What CfHEE does

CfHEE is responsible for:

- ingesting heterogeneous technical and enterprise data
- assigning explicit hierarchical scope metadata
- preserving raw inputs
- chunking and indexing content
- storing structured knowledge in Postgres
- enabling fast, scoped retrieval
- providing traceable, source-grounded access to stored data
- building deterministic, provider-free context from stored knowledge

---

## What CfHEE is NOT

CfHEE is not:

- an AI assistant product
- a workflow engine
- an agent framework
- an automation platform

Higher-level systems (workflows, agents, automation tools) are expected to be built **on top of CfHEE**, not inside it.

---
## Core capability

CfHEE's primary external value is:

> retrieval-derived context building

External systems are expected to:
- query CfHEE for context
- pass that context to an LLM or workflow system

---
## System role

CfHEE acts as a:

> **Knowledge Infrastructure Module**

It is intended to be used by:

- automation scripts
- workflow systems
- domain-specific tools
- agent-based systems

through its API.

---

## Built-in UI

The frontend is a **developer workbench**, not a product UI.

It provides:

- manual document ingestion
- document and chunk inspection
- scoped retrieval
- grounded answer querying (as a convenience layer)
- read-only Operations / Admin inspection of the current running instance

---

## Architecture overview

```text
External Systems / Workflows
            ↓
         CfHEE API
            ↓
   Knowledge Core (this project)
```

Core layers:

- Ingestion
- Persistence (Postgres + raw storage)
- Retrieval (scoped)
- Context building
- Answer (convenience only)

---

## Folder structure

```
apps/
  backend/
    src/cfhee_backend/
      api/
      answers/
      chunking/
      embeddings/
      enrichment/
      ingestion/
      llm/
      normalization/
      persistence/
      retrieval/
      scope_registry/
      vector_store/
  frontend/
    src/app/
      pages/
docs/
docker-compose.yml
```

---

## Run locally

Minimum runtime roles today:

- Postgres: required
- Backend: required
- Frontend workbench: required
- Chroma local vector state: required
- Ollama: optional convenience dependency for grounded answers only

Two workflows now exist side by side:

- source-based local development
- portable runtime from containers

The containerized runtime does not replace the current local dev workflow.

### DEV vs RUNTIME

Keep these workflows separate mentally:

- DEV = source-based workbench on `4200` + backend on `8000`
- RUNTIME = portable instance on `4210` + backend on `8010`

The portable runtime uses its own host-facing frontend and backend ports so it is easier to tell which environment you are using.

### Postgres

```bash
docker compose up -d postgres
```

Defaults:

- database: `cfhee`
- user: `cfhee`
- password: `cfhee`
- port: `5432`

### Backend

```bash
cd apps/backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m uvicorn cfhee_backend.main:app --reload
```

API base: `http://127.0.0.1:8000`

### Frontend

```bash
cd apps/frontend
npm install
npm start
```

Frontend: `http://localhost:4200`

### Frontend API base override

The frontend defaults to `http://127.0.0.1:8000`.

To point the workbench at a different backend without rebuilding, set `apiBaseUrl` in:

`apps/frontend/public/runtime-config.js`

Example:

```js
window.__CFHEE_RUNTIME_CONFIG__ = {
  apiBaseUrl: 'http://localhost:8010'
};
```

If no override is provided, the current localhost default remains in use.

### Backend CORS origins

The backend defaults to allowing:

- `http://localhost:4200`
- `http://127.0.0.1:4200`

To allow other frontend origins, set `CORS_ALLOW_ORIGINS` as a comma-separated list before starting the backend.

Example:

```powershell
$env:CORS_ALLOW_ORIGINS="http://localhost:4200,http://127.0.0.1:4200,http://localhost:4300"
```

### Local vector state

Chroma uses local persistent filesystem state by default.

- default path: `apps/backend/data/chroma`
- override with `CHROMA_PERSIST_DIRECTORY`

---

## Run the portable runtime

The first portable runtime slice now includes:

- frontend container
- backend container
- Postgres container
- explicit persistent state directories for Postgres and Chroma

It does not include:

- Ollama
- reverse proxy or TLS
- production hardening

### Persistent runtime data layout

The portable runtime uses visible bind-mounted directories:

- `runtime-data/postgres`
- `runtime-data/chroma`

These directories hold persistent instance state and are separate from the runtime packaging itself.

### Start the portable runtime

```bash
docker compose up --build
```

PowerShell wrapper:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-up.ps1
```

The portable runtime uses host ports that are intentionally different from the source-based dev workflow:

- `4210` for the frontend
- `8010` for the backend
- `5432` for Postgres

Portable runtime URLs:

- frontend: `http://127.0.0.1:4210`
- backend: `http://127.0.0.1:8010`
- API docs: `http://127.0.0.1:8010/docs`

### Stop the portable runtime

```bash
docker compose down
```

PowerShell wrapper:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-down.ps1
```

### Inspect runtime logs

```bash
docker compose logs
docker compose logs -f
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
```

### Portable runtime configuration

Compose now sets:

- backend `DATABASE_URL` to the Compose Postgres service
- backend `CHROMA_PERSIST_DIRECTORY` to `/app/data/chroma`
- frontend runtime `apiBaseUrl` through `CFHEE_API_BASE_URL`

Defaults in the portable runtime:

- frontend origin: `http://127.0.0.1:4210`
- backend base URL used by the frontend: `http://127.0.0.1:8010`
- backend answer provider: `deterministic`

If you want different host-facing values, override Compose environment variables before startup:

- `CFHEE_API_BASE_URL`
- `CFHEE_CORS_ALLOW_ORIGINS`
- `CFHEE_ANSWER_PROVIDER`

Container-mode wiring:

- frontend reaches backend through `runtime-config.js`
- backend reaches Postgres through the Compose hostname `postgres`
- Postgres data persists under `runtime-data/postgres`
- Chroma data persists under `runtime-data/chroma`

### Why data may appear missing between dev and runtime

The source-based dev workflow and the portable runtime are now intentionally separated at the frontend and backend ports:

- DEV frontend/backend: `4200` / `8000`
- RUNTIME frontend/backend: `4210` / `8010`

They can therefore point at different backend processes.

The most important current data difference is Chroma persistence:

- source-based local backend defaults to `apps/backend/data/chroma`
- portable runtime backend uses `runtime-data/chroma`

Postgres runtime data remains under `runtime-data/postgres`.

If documents or retrieval results look different, first confirm which frontend/backend port pair you are using before assuming data loss.

### Update the portable runtime

Current minimal flow:

1. Pull the latest repo changes.
2. Keep `runtime-data/` in place.
3. Run `docker compose up --build -d`.
4. Check `docker compose ps` and `docker compose logs`.

This updates the runtime layer without deleting the current persistent data layer.

### Back up the portable runtime data

The current helpers use the documented stopped-runtime model.

Stop the runtime first, then run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-backup.ps1
```

This creates a timestamped backup directory with:

- `postgres`
- `chroma`
- `manifest.json`

### Restore the portable runtime data

Restore is full-instance data replacement for the current data layer.

Stop the runtime first, then run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-restore.ps1 -BackupPath .\backups\cfhee-backup-YYYYMMDD-HHMMSSfff
```

The helper requires explicit confirmation before replacing:

- `runtime-data/postgres`
- `runtime-data/chroma`

### Ollama and the portable runtime

Ollama is still outside the minimum portable runtime.

The containerized slice supports storage, retrieval, inspection, and deterministic grounded answers without Ollama.

---

## API endpoints (current)

Current implemented API surface includes:

| Method | Endpoint |
|--------|----------|
| `GET` | `/` |
| `GET` | `/health` |
| `POST` | `/documents` |
| `GET` | `/documents` |
| `GET` | `/documents/{document_id}/chunks` |
| `POST` | `/retrieval/query` |
| `POST` | `/answer/query` |

Also present in the current repo:

- `GET /scope-values`
- `GET /ops/summary`
- `GET /query-logs`
- versioned `/api/v1/...` routes including retrieval, context building, document inspection, and query-log inspection

For the current external contract and freeze boundary, see `docs/API_V1.md`.

---

## Answer provider (optional)

CfHEE supports a minimal answer provider abstraction.

Environment variables:

| Variable | Values |
|----------|--------|
| `ANSWER_PROVIDER` | `auto` \| `ollama` \| `deterministic` |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | `qwen2.5:7b` |

> Ollama is optional. Retrieval, storage, and inspection do not depend on it.

---

## Development notes

- Retrieval is always scoped by default
- Scope isolation is critical
- Raw inputs are preserved
- Answer layer must not bypass retrieval

---

## Future direction

The next evolution of CfHEE focuses on:

- stable API surface for external integration
- external workflow and agent systems built on top
- containerization and cross-platform runtime (Linux support)

The first portable runtime slice now exists.

Runtime portability is still not complete:

- backup and restore now exist only as conservative stopped-runtime helpers
- hot backup and stronger validation are not implemented
- production hardening is not implemented
- Ollama remains outside the minimum portable runtime

---

## Documentation

See:

- `docs/ARCHITECTURE.md`
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/DECISIONS.md`
- `docs/RUNTIME_OPERATIONS.md`
- `docs/BACKUP_AND_RESTORE.md`
