# Project State

Last reviewed: 2026-03-19

## Current slice in repo

Implemented in code:

- Angular frontend shell with routes for `Overview`, `Inbox / Capture`, `Documents`, `Ask Copilot`, `Scope Manager`, and `Settings`
- Working frontend views for manual ingest and document listing
- Working frontend view for scoped retrieval in `Ask Copilot`
- FastAPI backend with `GET /`, `GET /health`, `POST /documents`, `GET /documents`, `GET /documents/{id}/chunks`, and `POST /retrieval/query`
- Postgres schema for workspaces, domains, projects, clients, modules, documents, and chunks
- Document ingest flow that:
  - validates required scope and hierarchy
  - upserts scope rows
  - stores raw document text in Postgres
  - chunks text by paragraph blocks
  - computes local hash-based embeddings
  - indexes chunks into Chroma
- Windows-first local bootstrap scripts:
  - `scripts/dev-up.ps1`
  - `scripts/dev-check.ps1`

## Verified status

Verified by code inspection:

- manual ingest is implemented end to end in backend and frontend code
- document listing and chunk inspection are implemented in backend and frontend code
- scoped retrieval is implemented in backend and frontend code
- vector-store abstraction exists and is currently backed by Chroma
- embedding abstraction exists and is currently backed by a local hash embedding service

Verified in the local environment during the latest check:

- `dev-check.ps1` runs successfully when invoked with `powershell.exe -ExecutionPolicy Bypass -File ...`
- frontend production build succeeds with `npm.cmd run build`
- backend source compiles with `python -m compileall`
- retrieval endpoint returns scoped chunk results for a matching scope and zero results for a wrong workspace when exercised against local Postgres + Chroma

Not implemented yet:

- answer generation / source-grounded answer composer
- Ollama integration
- real scope management UI
- settings UI beyond placeholder copy

## Current alignment with MVP docs

Already present:

- Angular shell
- FastAPI backend
- Postgres schema
- manual ingest form
- document list
- scoped retrieval UI
- workspace/domain/project/client/module metadata
- raw text storage
- basic chunking
- vector indexing hook on ingest

Still missing from the broader architecture direction:

- source-grounded prose answers
- enrichment
- provider-backed LLM answer layer
