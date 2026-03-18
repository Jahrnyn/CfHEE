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

### Backend

```bash
cd apps/backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m uvicorn cfhee_backend.main:app --reload
```

The API starts on `http://127.0.0.1:8000` and exposes:

- `GET /`
- `GET /health`
- `GET /docs`

### Frontend

```bash
cd apps/frontend
npm install
npm start
```

The Angular app starts on `http://localhost:4200`.
