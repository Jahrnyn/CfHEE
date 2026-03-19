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

The API starts on `http://127.0.0.1:8000` and exposes:

- `GET /`
- `GET /health`
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
- `Ask Copilot` for scoped retrieval of matching chunks and source metadata; workspace and domain are required so global retrieval is never implicit

## Local Dev Bootstrap

For a Windows-first local setup, use the PowerShell scripts in `scripts/` from the repo root:

```powershell
.\scripts\dev-up.ps1
```

`dev-up.ps1` checks Docker availability, starts Postgres with `docker compose`, creates `apps/backend/.venv` if needed, installs backend and frontend dependencies only when their manifest files changed, and opens backend plus frontend in separate PowerShell windows.

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
