# Project State

Last reviewed: 2026-03-27

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

## API v1 Code Freeze (Contract Stabilization)

CfHEE external API v1 is now in **API v1 Code Freeze (Contract Stabilization)**.

Frozen now:

- implemented `/api/v1/...` endpoints
- request and response shapes
- shared scope model and scope rules
- document contract behavior
- retrieval contract behavior
- query-log list contract behavior

Not frozen:

- frontend
- internal implementation
- performance improvements
- containerization and runtime setup
- developer tooling

Allowed during freeze:

- bugfixes without contract change
- internal refactoring without contract change
- non-breaking additions only if strictly necessary

Not allowed during freeze:

- breaking API changes
- silent contract changes
- scope model changes
- response semantic changes

## Current slice in repo

Implemented in code:

- Angular frontend shell with routes for `Overview`, `Inbox / Capture`, `Documents`, `Ask`, `Scope Manager`, and `Settings`
- Working frontend views for manual ingest and document listing
- Manual ingest now supports reusing stored scope values through lightweight suggestions while still allowing new values
- Working frontend view for scoped retrieval in `Ask`
- Working frontend `Ask` flow for grounded answers plus retrieval-only inspection
- `Ask` keeps a clean minimal user-facing UI for scoped retrieval and grounded answers
- FastAPI backend with `GET /`, `GET /health`, `POST /documents`, `GET /documents`, `GET /documents/{id}/chunks`, `POST /retrieval/query`, `POST /answer/query`, and `GET /query-logs`
- FastAPI backend also exposes `GET /scope-values` for lightweight manual-ingest scope reuse
- FastAPI backend now also exposes the first versioned external API shell with `GET /api/v1/health`, `GET /api/v1/capabilities`, `GET /api/v1/scopes/values`, `POST /api/v1/documents`, `POST /api/v1/retrieval/query`, `GET /api/v1/documents`, `GET /api/v1/documents/{document_id}`, `GET /api/v1/documents/{document_id}/chunks`, and `GET /api/v1/query-logs`
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
- frontend API services now use a small runtime config surface instead of hardcoding the backend base URL in code
- backend CORS origins are now configurable through `CORS_ALLOW_ORIGINS`, while preserving localhost defaults
- Retrieval regression guardrail:
  - fixture: `apps/backend/fixtures/retrieval_regression_cases.json`
  - runner: `apps/backend/scripts/retrieval_regression_check.py`

## Verified status

Verified by code inspection:

- manual ingest is implemented end to end in backend and frontend code
- document listing and chunk inspection are implemented in backend and frontend code
- scoped retrieval is implemented in backend and frontend code
- the first versioned external API ingest, retrieval, document-inspection, and query-log inspection shell exists under `/api/v1` with `GET /api/v1/health`, `GET /api/v1/capabilities`, `GET /api/v1/scopes/values`, `POST /api/v1/documents`, `POST /api/v1/retrieval/query`, `GET /api/v1/documents`, `GET /api/v1/documents/{document_id}`, `GET /api/v1/documents/{document_id}/chunks`, and `GET /api/v1/query-logs`
- the v1 ingest slice now uses a nested public `scope` object and translates that request into the existing internal document-ingest contract
- the shared public v1 `scope` model now applies conservative normalization and hierarchy validation before document and retrieval translation handlers run
- the v1 document-create request accepts an optional `metadata` object, which is currently ignored by the backend translation layer
- the v1 retrieval slice now uses the same nested public `scope` object and translates that request into the existing internal retrieval contract
- the v1 retrieval response adapts current retrieval results into a public contract and omits diagnostics unless they are explicitly requested
- the v1 document inspection slice now exposes a scoped list envelope plus factual detail and chunk-envelope responses on top of the existing stored document and chunk data
- the v1 query-log slice now exposes a conservative developer-oriented list envelope for inspectable stored traces, with limit, type, and scope filters mapped onto persisted query-log fields and `workspace` + `domain` required together when scope filtering is used
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
- the frontend runtime config helper keeps `http://127.0.0.1:8000` as the default API base URL when no override is provided
- the backend CORS helper keeps the current localhost frontend origins as defaults and accepts a comma-separated `CORS_ALLOW_ORIGINS` override in code-level checks
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
- `POST /api/v1/retrieval/query` omits the `diagnostics` field unless `include_diagnostics=true`, while still returning diagnostics when explicitly requested in local in-process checks
- invalid nested v1 scope shapes and invalid `top_k` values now fail with request validation in local in-process checks instead of reaching retrieval execution

## Not implemented yet

- real scope management UI
- settings UI beyond placeholder copy
- bulk file import, connectors, and OCR
- explicit external-integration-oriented API contracts beyond the current app-driven endpoint set
- versioned `/api/v1` answer, additional scope-helper, and query-log detail endpoints beyond the current health/capabilities/ingest/retrieval/document-inspection/query-log shell
- containerized cross-environment runtime

## Current runtime model

- Postgres is required
- backend is required
- frontend developer workbench is required
- Chroma local vector state is required
- Ollama is optional and only affects the built-in grounded-answer convenience flow

## Current architectural reading

What currently exists should be read as:

- a working scoped knowledge core with a small built-in developer workbench
- not a full assistant product
- not a workflow platform
- not an orchestration system

## Immediate architectural implication

Future growth should prefer:

- frontend improvements around the frozen API
- containerization and runtime portability
- first external consumer integrations
- keeping workflow-specific logic outside the module

rather than expanding the API surface or turning the module into a broader application identity.
