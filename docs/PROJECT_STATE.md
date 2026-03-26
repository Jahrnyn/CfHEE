# Project State

Last reviewed: 2026-03-26

## Current project identity

CfHEE is currently defined as a local-first, scoped knowledge storage and retrieval module.

Its architectural core is:

- scoped ingest
- persistent storage
- chunking and indexing
- scoped retrieval
- traceability

The built-in grounded-answer capability exists as a convenience consumer on top of retrieval.
The frontend should be understood primarily as a lightweight developer workbench, not as the core identity of the system.

## Current slice in repo

Implemented in code:

- Angular frontend shell with routes for `Overview`, `Inbox / Capture`, `Documents`, `Ask Copilot`, `Scope Manager`, and `Settings`
- Working frontend views for manual ingest and document listing
- Manual ingest now supports reusing stored scope values through lightweight suggestions while still allowing new values
- Working frontend view for scoped retrieval in `Ask Copilot`
- Working frontend `Ask Copilot` flow for grounded answers plus retrieval-only inspection
- `Ask Copilot` keeps a clean minimal user-facing UI for scoped retrieval and grounded answers
- FastAPI backend with `GET /`, `GET /health`, `POST /documents`, `GET /documents`, `GET /documents/{id}/chunks`, `POST /retrieval/query`, `POST /answer/query`, and `GET /query-logs`
- FastAPI backend also exposes `GET /scope-values` for lightweight manual-ingest scope reuse
- FastAPI backend now also exposes the first versioned external API shell with `GET /api/v1/health` and `GET /api/v1/capabilities`
- Retrieval-to-answer handoff now uses an explicit context builder with deterministic ordering, conservative dedupe, and an answer-context limit
- Postgres schema for workspaces, domains, projects, clients, modules, documents, and chunks
- Document ingest flow that:
  - validates required scope and hierarchy
  - normalizes scope metadata conservatively for trim, collapsed whitespace, and case-insensitive scope matching
  - upserts scope rows
  - stores raw document text in Postgres
  - chunks text by paragraph blocks
  - computes local hash-based embeddings
  - indexes chunks into Chroma
- Windows-first local bootstrap scripts:
  - `scripts/dev-up.ps1`
  - `scripts/dev-check.ps1`
- Retrieval regression guardrail:
  - fixture: `apps/backend/fixtures/retrieval_regression_cases.json`
  - runner: `apps/backend/scripts/retrieval_regression_check.py`

## Verified status

Verified by code inspection:

- manual ingest is implemented end to end in backend and frontend code
- document listing and chunk inspection are implemented in backend and frontend code
- scoped retrieval is implemented in backend and frontend code
- the first versioned external API routing shell exists under `/api/v1` with `GET /api/v1/health` and `GET /api/v1/capabilities`
- retrieval responses now include explicit scope, chunk and document identifiers, distance, and similarity score
- retrieval now applies a small explicit lexical rescoring step after vector candidate retrieval while preserving original vector signals
- source-grounded answers are implemented on top of retrieval using provider selection with Ollama plus deterministic fallback
- Ollama grounded-answer prompting is now built through an explicit prompt builder with conservative instructions and deterministic context formatting
- vector-store abstraction exists and is currently backed by Chroma
- embedding abstraction exists and is currently backed by a local hash embedding service
- query logging is implemented for retrieval-only and answer queries, including scope, result identifiers, answer text, provider used, and fallback usage
- answer context selection is now explicit and traceable, including selected and dropped chunk IDs in `query_logs`
- answer queries now persist simple deterministic evaluation fields in `query_logs`: `has_evidence`, `context_used_count`, `answer_length`, and `grounded_flag`
- query logs now also persist small retrieval diagnostics such as candidate count, top-k limit hit, returned distance values, and returned document distribution
- query logs now also preserve original vs. reranked chunk order plus whether reranking changed the final order
- a tiny backend-side retrieval regression pack now exists for rerunning a few high-signal real-document queries after retrieval changes
- manual ingest scope suggestions and conservative normalization are implemented as a thin usability slice, not as a full scope-management system

Verified in the local environment during the latest check:

- `dev-check.ps1` runs successfully when invoked with `powershell.exe -ExecutionPolicy Bypass -File ...`
- frontend production build succeeds with `npm.cmd run build`
- backend source compiles with `python -m compileall`
- retrieval endpoint accepts `top_k`, returns explicit empty results, logs query, scope, and result count, and rejects missing scope with a clear validation error when exercised against local Postgres and Chroma
- answer endpoint returns a grounded short answer with cited chunks for matching scope, returns an explicit no-evidence state for empty retrieval, and rejects missing scope with the same scoped validation
- Ollama is reachable locally at the default local URL and `qwen2.5:7b` is present locally in this environment
- answer provider selection uses Ollama successfully when the model is available and falls back to the deterministic provider when the configured Ollama model is unavailable
- `dev-check.ps1` now reports Ollama reachability, configured model presence, and answer-provider readiness
- retrieval-only queries and answer queries now persist inspectable `query_logs`, and `GET /query-logs` returns recent traces with provider and fallback information when exercised locally
- answer queries now enforce a bounded final context and persist selected vs. dropped context chunk IDs when exercised locally
- answer queries now populate simple evaluation fields in `query_logs`, and `GET /query-logs` returns those fields when exercised locally
- Ollama grounded answers now run through the explicit prompt builder, and local checks show shorter scope-bound answers with the same retrieved citations
- the Ask page keeps the core scoped query, retrieval, and grounded-answer flow without exposing debug panels in the main UI
- grounded answers now follow the query language more explicitly for Hungarian and English queries in local checks, and `GET /query-logs` exposes richer retrieval diagnostics for inspection
- targeted local checks now show exact identifier queries surfacing more reliable top-ranked chunks in at least the tested cases, without any Ask-page debug UI changes
- the retrieval regression pack can now be run locally against the existing Postgres and Chroma data to re-check a few exact-identifier and explicit-term cases with plain pass/fail output
- local run command for that guardrail is:
  - `$env:PYTHONPATH="$PWD\apps\backend\src;$PWD\apps\backend\.packages"; python apps/backend/scripts/retrieval_regression_check.py`
- stored scope values can now be queried through `GET /scope-values`, reused in the manual-ingest form, and matched conservatively against trim, casing, and spacing variants during document creation when exercised locally

## Not implemented yet

- real scope management UI
- settings UI beyond placeholder copy
- bulk file import, connectors, and OCR
- explicit external-integration-oriented API contracts beyond the current app-driven endpoint set
- versioned `/api/v1` document, retrieval, answer, scope-helper, and query-log endpoints beyond the initial health/capabilities shell
- containerized cross-environment runtime

## Current architectural reading

What currently exists should be read as:

- a working scoped knowledge core with a small built-in developer workbench
- not a full copilot product
- not a workflow platform
- not an orchestration system

## Immediate architectural implication

Future growth should prefer:

- API stabilization
- external integration
- keeping workflow-specific logic outside the module

rather than expanding the built-in UI and answer layer into a broader application identity.
