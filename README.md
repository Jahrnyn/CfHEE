# CfHEE

CfHEE is a local-first, scoped knowledge storage and retrieval module.

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

---

## What CfHEE is NOT

CfHEE is not:

- an AI assistant product
- a workflow engine
- an agent framework
- an automation platform

Higher-level systems (workflows, agents, automation tools) are expected to be built **on top of CfHEE**, not inside it.

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
- backup tooling
- restore tooling
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

If you already have the source-based frontend or backend running locally, stop those first.
The portable runtime uses the same host ports:

- `4200` for the frontend
- `8000` for the backend
- `5432` for Postgres

Portable runtime URLs:

- frontend: `http://127.0.0.1:4200`
- backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

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

- frontend origin: `http://127.0.0.1:4200`
- backend base URL used by the frontend: `http://127.0.0.1:8000`
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

### Update the portable runtime

Current minimal flow:

1. Pull the latest repo changes.
2. Keep `runtime-data/` in place.
3. Run `docker compose up --build -d`.
4. Check `docker compose ps` and `docker compose logs`.

This updates the runtime layer without deleting the current persistent data layer.

### Ollama and the portable runtime

Ollama is still outside the minimum portable runtime.

The containerized slice supports storage, retrieval, inspection, and deterministic grounded answers without Ollama.

---

## API endpoints (current)

| Method | Endpoint |
|--------|----------|
| `GET` | `/` |
| `GET` | `/health` |
| `POST` | `/documents` |
| `GET` | `/documents` |
| `GET` | `/documents/{document_id}/chunks` |
| `POST` | `/retrieval/query` |
| `POST` | `/answer/query` |

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

Runtime portability is in progress, not complete yet.

---

## Documentation

See:

- `docs/ARCHITECTURE.md`
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/DECISIONS.md`
- `docs/RUNTIME_OPERATIONS.md`
