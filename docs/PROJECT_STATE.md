# Project State

Last reviewed: 2026-03-24

## Current slice in repo

Implemented in code:

- Angular frontend shell with routes for `Overview`, `Inbox / Capture`, `Documents`, `Ask Copilot`, `Scope Manager`, and `Settings`
- Working frontend views for manual ingest and document listing
- Working frontend view for scoped retrieval in `Ask Copilot`
- Working frontend `Ask Copilot` flow for grounded answers plus retrieval-only inspection
- FastAPI backend with `GET /`, `GET /health`, `POST /documents`, `GET /documents`, `GET /documents/{id}/chunks`, `POST /retrieval/query`, `POST /answer/query`, and `GET /query-logs`
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
- retrieval responses now include explicit scope, chunk/document identifiers, distance, and similarity score
- source-grounded answers are implemented on top of retrieval using provider selection with Ollama plus deterministic fallback
- vector-store abstraction exists and is currently backed by Chroma
- embedding abstraction exists and is currently backed by a local hash embedding service
- query logging is implemented for retrieval-only and answer queries, including scope, result identifiers, answer text, provider used, and fallback usage

Verified in the local environment during the latest check:

- `dev-check.ps1` runs successfully when invoked with `powershell.exe -ExecutionPolicy Bypass -File ...`
- frontend production build succeeds with `npm.cmd run build`
- backend source compiles with `python -m compileall`
- retrieval endpoint accepts `top_k`, returns explicit empty results, logs query/scope/result count, and rejects missing scope with a clear validation error when exercised against local Postgres + Chroma
- answer endpoint returns a grounded short answer with cited chunks for matching scope, returns an explicit no-evidence state for empty retrieval, and rejects missing scope with the same scoped validation
- Ollama is reachable locally at the default local URL and `qwen2.5:7b` is present locally in this environment
- answer provider selection uses Ollama successfully when the model is available and falls back to the deterministic provider when the configured Ollama model is unavailable
- `dev-check.ps1` now reports Ollama reachability, configured model presence, and answer-provider readiness
- retrieval-only queries and answer queries now persist inspectable `query_logs`, and `GET /query-logs` returns recent traces with provider and fallback information when exercised locally

Not implemented yet:

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
- grounded answer UI
- workspace/domain/project/client/module metadata
- raw text storage
- basic chunking
- vector indexing hook on ingest

Still missing from the broader architecture direction:

- enrichment
- broader provider routing beyond the current minimal Ollama-or-deterministic selection
