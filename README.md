# Copilot for Hostile Enterprise Environment

Initial project skeleton for the Phase 1 foundation described in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/MVP.md](docs/MVP.md).

## Folder structure

```text
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

## Run locally

### Postgres

```bash
docker compose up -d postgres
```

Postgres will be available on `localhost:5432` with:

- database: `cfhee`
- user: `cfhee`
- password: `cfhee`

The initial schema for `workspaces`, `domains`, `projects`, `clients`, `modules`, `documents`, and `chunks`
is defined in `apps/backend/sql/schema.sql`. It is mounted into the Postgres container on first database
initialization, and the backend also runs the same schema on startup with `CREATE TABLE IF NOT EXISTS`.

### Backend

```bash
cd apps/backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m uvicorn cfhee_backend.main:app --reload
```

The backend also creates a local Chroma index under `apps/backend/data/chroma` by default.
You can override that location with `CHROMA_PERSIST_DIRECTORY`.

Grounded answers support a small provider-selection mechanism:

- `ANSWER_PROVIDER=auto` (default): use Ollama when it is reachable and the configured model exists locally, otherwise fall back to the deterministic provider
- `ANSWER_PROVIDER=ollama`: prefer Ollama, but still fall back to deterministic if Ollama is unavailable
- `ANSWER_PROVIDER=deterministic`: always use the deterministic local fallback

Ollama defaults:

- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `OLLAMA_MODEL=qwen2.5:7b`

If you want Ollama-backed answers, make sure Ollama is installed, running, and the model exists locally:

```powershell
ollama pull qwen2.5:7b
ollama serve
```

The API starts on `http://127.0.0.1:8000` and exposes:

- `GET /`
- `GET /health`
- `POST /answer/query`
- `POST /documents`
- `GET /documents`
- `GET /documents/{document_id}/chunks`
- `POST /retrieval/query`
- `GET /docs`

If you need a different Postgres connection, set `DATABASE_URL` before starting the backend.

### Frontend

```bash
cd apps/frontend
npm install
npm start
```

The Angular app starts on `http://localhost:4200`.

The current vertical slices are available at:

- `Inbox / Capture` for manual document ingestion
- `Documents` for listing stored documents and inspecting generated chunks
- `Ask Copilot` for grounded answers backed only by scoped retrieval results, plus a retrieval-only view for raw matching chunks

## Local Dev Bootstrap

For a Windows-first local setup, use the PowerShell scripts in `scripts/` from the repo root:

```powershell
.\scripts\dev-up.ps1
```

`dev-up.ps1` checks Docker availability, starts Postgres with `docker compose`, creates `apps/backend/.venv` if needed, installs backend and frontend dependencies only when their manifest files changed, and opens backend plus frontend in separate PowerShell windows.
It also checks whether Ollama is reachable, tries to start `ollama serve` in a new PowerShell window when practical, and warns clearly when the configured local model is missing.

If your PowerShell execution policy blocks local scripts, run them with:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\dev-up.ps1
```

After the services are up, run:

```powershell
.\scripts\dev-check.ps1
```

`dev-check.ps1` verifies:

- the `cfhee-postgres` container is running
- the backend responds on `http://127.0.0.1:8000/health`
- the frontend responds on `http://127.0.0.1:4200`
- whether Ollama is reachable at the configured local URL
- whether the configured local Ollama model is present
- whether Ollama-backed answers appear ready or the deterministic fallback is expected
