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
