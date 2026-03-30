# Project State

Last reviewed: 2026-03-30

## Current project identity

CfHEE is currently defined as a local-first, scoped knowledge infrastructure module for storage, retrieval, and retrieval-derived context building.

Its architectural core is:

- scoped ingest
- persistent storage
- chunking and indexing
- scoped retrieval
- retrieval-derived context building
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

- Angular frontend shell with routes for `Overview`, `Inbox / Capture`, `Documents`, `Ask`, and `Operations / Admin`
- Working frontend views for manual ingest and document listing
- Working frontend `Documents` view now also supports explicit single-document deletion with confirmation
- Manual ingest now supports reusing stored scope values through lightweight suggestions while still allowing new values
- Working frontend view for scoped retrieval in `Ask`
- Working frontend `Ask` flow for grounded answers plus retrieval-only inspection
- Working frontend read-only `Scope Explorer` view for inspecting the stored hard-scope hierarchy through `GET /api/v1/scopes/tree`, now with expandable tree sections and JSON download
- `Ask` keeps a clean minimal user-facing UI for scoped retrieval and grounded answers
- Working frontend `Operations / Admin` view for consuming the backend read-only ops summary, including backup visibility
- the frontend now also has a minimal shared dark-surface styling contract for panels and cards, and the Operations/Admin page uses that shared baseline
- FastAPI backend with `GET /`, `GET /health`, `POST /documents`, `GET /documents`, `GET /documents/{id}/chunks`, `POST /retrieval/query`, `POST /answer/query`, and `GET /query-logs`
- FastAPI backend now also exposes `GET /ops/summary` as a narrow internal read-only ops summary surface, including conservative backup visibility
- FastAPI backend also exposes `GET /scope-values` for lightweight manual-ingest scope reuse
- FastAPI backend now also exposes the first versioned external API shell with `GET /api/v1/health`, `GET /api/v1/capabilities`, `GET /api/v1/scopes/values`, `GET /api/v1/scopes/tree`, `POST /api/v1/documents`, `POST /api/v1/retrieval/query`, `POST /api/v1/context/build`, `GET /api/v1/documents`, `GET /api/v1/documents/{document_id}`, `GET /api/v1/documents/{document_id}/chunks`, and `GET /api/v1/query-logs`
- FastAPI backend now also exposes `DELETE /api/v1/documents/{document_id}` for deterministic document lifecycle cleanup
- Retrieval-to-answer handoff now uses an explicit context builder with deterministic ordering, conservative dedupe, and an answer-context limit
- Postgres schema for workspaces, domains, projects, clients, modules, documents, and chunks
- Document ingest flow that:
  - validates required scope and hierarchy
  - normalizes scope metadata conservatively for trim, collapsed whitespace, and case-insensitive scope matching
  - upserts scope rows
  - stores raw document text in Postgres without collapsing internal whitespace or line breaks
  - stores optional caller-provided document metadata in Postgres
  - chunks text by blank-line paragraph blocks with greedy paragraph packing up to the current `1200`-character target
  - applies sentence-based fallback for oversized paragraphs and a final hard character fallback when sentence boundaries still do not produce safe chunks
  - computes Ollama-backed semantic embeddings with `bge-m3` by default
  - indexes chunks into Chroma
- Windows-first local bootstrap scripts:
  - `scripts/dev-up.ps1`
  - `scripts/dev-check.ps1`
- Windows-first portable-runtime helper scripts:
  - `scripts/runtime-up.ps1`
  - `scripts/runtime-down.ps1`
  - `scripts/runtime-backup.ps1`
  - `scripts/runtime-restore.ps1`
- frontend API services now use a small runtime config surface instead of hardcoding the backend base URL in code
- backend CORS origins are now configurable through `CORS_ALLOW_ORIGINS`, while preserving localhost defaults
- backend localhost CORS defaults now cover both source-based frontend ports and portable-runtime frontend ports
- first portable runtime packaging slice:
  - backend Dockerfile
  - frontend Dockerfile
  - multi-container `docker-compose.yml` for frontend, backend, Postgres, and Ollama
  - explicit bind-mounted runtime data directories for Postgres and Chroma under `runtime-data/`
  - host-facing runtime frontend/backend port separation from source-based dev through `4210` and `8010`
- Retrieval regression guardrail:
  - fixture: `apps/backend/fixtures/retrieval_regression_cases.json`
  - runner: `apps/backend/scripts/retrieval_regression_check.py`
- Semantic regression verification helper:
  - corpus fixture: `apps/backend/fixtures/semantic_regression_documents.json`
  - runner: `apps/backend/scripts/semantic_regression_verify.py`
- Documentation alignment for operational usage now defines:
  - hard scope as `workspace` / `domain` / `project` / `client` / `module`
  - `source_type`, `language`, and `source_ref` as descriptive metadata rather than retrieval partition keys
  - deterministic ingest guidance for choosing scope values
  - the current explicit-scope retrieval stance and its limits for partial-scope questions
  - the boundary that CfHEE does not perform query-scope inference and remains a scoped execution engine rather than a discovery engine
- API v1 now also includes a scope-tree visibility helper that exposes the stored scope hierarchy without adding scope inference, scope resolution, or planning logic
- the frontend now also includes a read-only scope-tree consumer that makes existing scope combinations visible inside the workbench without adding scope editing or scope-planning behavior
- the `Scope Explorer` frontend slice now keeps the tree collapsed by default for cleaner large-tree inspection and uses JSON download instead of inline raw JSON rendering

## Verified status

Verified by code inspection:

- manual ingest is implemented end to end in backend and frontend code
- document listing and chunk inspection are implemented in backend and frontend code
- scoped retrieval is implemented in backend and frontend code
- the frontend now includes a dedicated `Scope Explorer` page that fetches the v1 scope-tree endpoint through a small focused API service and renders the stored hierarchy as a nested read-only view
- the `Scope Explorer` page now uses expandable read-only tree sections so deeper levels are shown only when opened, and it exposes a JSON download action backed by the already-fetched in-memory tree
- the first versioned external API ingest, retrieval, context-build, document-inspection, and query-log inspection shell exists under `/api/v1` with `GET /api/v1/health`, `GET /api/v1/capabilities`, `GET /api/v1/scopes/values`, `GET /api/v1/scopes/tree`, `POST /api/v1/documents`, `POST /api/v1/retrieval/query`, `POST /api/v1/context/build`, `GET /api/v1/documents`, `GET /api/v1/documents/{document_id}`, `GET /api/v1/documents/{document_id}/chunks`, and `GET /api/v1/query-logs`
- the v1 ingest slice now uses a nested public `scope` object and translates that request into the existing internal document-ingest contract
- the shared public v1 `scope` model now applies conservative normalization and hierarchy validation before document and retrieval translation handlers run
- the v1 document-create request accepts an optional `metadata` object and now persists it as document-level JSON metadata
- persisted document `metadata` is caller-provided descriptive data; it is not part of hard scope, retrieval partitioning, retrieval ranking, or current metadata-query/filter behavior
- the new v1 `GET /api/v1/scopes/tree` endpoint exposes the stored scope hierarchy as a structured tree for visibility only, without deriving or suggesting scope
- the v1 retrieval slice now uses the same nested public `scope` object and translates that request into the existing internal retrieval contract
- the v1 retrieval response adapts current retrieval results into a public contract and omits diagnostics unless they are explicitly requested
- the v1 context-build slice now exposes provider-free retrieval-derived context preparation with deterministic chunk selection, formatted context text, selected chunks, dropped chunk IDs, and optional retrieval diagnostics
- the v1 document inspection slice now exposes a scoped list envelope plus factual detail and chunk-envelope responses on top of the existing stored document and chunk data, including persisted document metadata on list/detail responses
- current chunking is intentionally simple:
  - chunk boundaries are created only from blank-line paragraph breaks in stored `raw_text`
  - consecutive paragraphs are greedily packed into a chunk until adding the next paragraph would exceed the current `1200`-character target
  - oversized paragraphs fall back to sentence-based packing, with a final hard character split only when sentence boundaries still do not keep chunk sizes safe
  - there is no overlap and no code-aware or format-aware chunking
  - if text has no blank-line paragraph boundaries, it remains a single chunk
  - a single long paragraph no longer remains one giant chunk by default; it is split by sentence boundaries when possible and by a final hard fallback when needed
- the v1 query-log slice now exposes a conservative developer-oriented list envelope for inspectable stored traces, with limit, type, and scope filters mapped onto persisted query-log fields and `workspace` + `domain` required together when scope filtering is used
- retrieval and v1 retrieval both require explicit scope input and do not infer missing scope from query text
- retrieval responses now include explicit scope, chunk and document identifiers, distance, and similarity score
- retrieval now applies a small explicit lexical rescoring step after vector candidate retrieval while preserving original vector signals
- source-grounded answers are implemented on top of retrieval using provider selection with Ollama plus deterministic fallback
- Ollama grounded-answer prompting is now built through an explicit prompt builder with conservative instructions and deterministic context formatting
- vector-store abstraction exists and is currently backed by Chroma
- document deletion now uses the existing vector-store abstraction to remove chunk vectors from the active backend
- embedding abstraction now supports explicit `ollama` and `hash` modes, with Ollama-backed `bge-m3` as the default normal path
- the active Chroma collection name now derives from the configured embedding provider/model so new semantic vectors do not collide with older hash-vector collections
- the repo now contains a first portable runtime container skeleton for frontend, backend, Postgres, and Ollama
- the portable runtime now wires backend Postgres access through the Compose service name and backend Chroma persistence through an explicit mounted runtime-data path
- the frontend portable runtime now injects its backend base URL through container-time generation of `runtime-config.js`
- the portable runtime now uses host-facing frontend/backend ports `4210` and `8010`, while the source-based dev workflow keeps `4200` and `8000`
- the portable runtime now also includes a runtime-local Ollama service for semantic embeddings, with a one-shot `bge-m3` bootstrap check that pulls only when the model is missing from the persisted runtime Ollama data directory
- the backend `GET /ops/summary` route now handles the current containerized source-tree layout without crashing
- the repo now also documents runtime operations clearly through `docs/RUNTIME_OPERATIONS.md`, including start, stop, logs, data ownership, and a minimal update flow
- query logging is implemented for retrieval-only and answer queries, including scope, result identifiers, answer text, provider used, and fallback usage
- answer context selection is now explicit and traceable, including selected and dropped chunk IDs in `query_logs`
- answer queries now persist simple deterministic evaluation fields in `query_logs`: `has_evidence`, `context_used_count`, `answer_length`, and `grounded_flag`
- query logs now also persist small retrieval diagnostics such as candidate count, top-k limit hit, returned distance values, and returned document distribution
- query logs now also preserve original vs. reranked chunk order plus whether reranking changed the final order
- a tiny backend-side retrieval regression pack now exists for rerunning a few high-signal real-document queries after retrieval changes
- a tiny semantic verification helper now exists for rebuilding a fresh `bge-m3`-indexed corpus, rerunning the existing regression pack, and cleaning up its labeled verification documents afterward
- manual ingest scope suggestions and conservative normalization are implemented as a thin usability slice, not as a full scope-management system
- current retrieval behavior remains explicit-scope-driven and does not silently widen when a query is underspecified relative to ingest scope
- current docs now explicitly place scope determination outside CfHEE, with future partial-scope or cross-scope orchestration treated as an external concern
- the new scope-tree helper can be exercised in-process and returns `200`, an empty tree for no rows, and a nested hierarchy for populated rows without duplicate module nodes in the checked cases
- the source-based dev environment now also verifies `GET /api/v1/scopes/tree` over live HTTP against Postgres-backed data, including checked cases for two modules under one parent, a separate project branch, and a separate workspace/domain branch without duplicate module nodes
- the frontend `Scope Explorer` page is read-only and introduces no scope editing, scope inference, or orchestration controls
- the `Scope Explorer` polish slice removes the inline raw JSON panel and replaces it with a download action for the current scope tree payload
- the `Documents` page now includes a narrow operational delete action that confirms before calling the new v1 delete route and refreshes the list after success

Verified in the local environment during the latest check:

- `dev-check.ps1` runs successfully when invoked with `powershell.exe -ExecutionPolicy Bypass -File ...`
- frontend production build succeeds with `npm.cmd run build`
- backend source compiles with `python -m compileall`
- local Ollama now has `bge-m3` available in this environment
- direct local Ollama embedding calls now return real `1024`-dimensional `bge-m3` vectors
- a local in-process smoke test now confirms semantic ingest, scoped retrieval, and cleanup against Postgres + Chroma using `EMBEDDING_PROVIDER=ollama`
- retrieval now returns HTTP `503` with a clear message when semantic embeddings are configured but the Ollama embedding runtime is unreachable
- the frontend runtime config helper keeps `http://127.0.0.1:8000` as the default API base URL when no override is provided
- the backend CORS helper keeps localhost frontend origins for both `4200` and `4210` as defaults and accepts a comma-separated `CORS_ALLOW_ORIGINS` override in code-level checks
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
- the semantic verification helper now ingests a tiny labeled Business Central / AL corpus through the current Ollama-backed `bge-m3` path, reruns the existing regression pack, and deletes those labeled verification documents afterward by default
- the semantic verification helper was exercised locally with:
  - `$env:PYTHONPATH='src;.packages'; .venv\Scripts\python.exe scripts/semantic_regression_verify.py`
- that local semantic run returned `4/4` passing regression cases on freshly ingested semantic data and printed the top returned results for each case
- the verification corpus used only three labeled documents:
  - `[semantic-regression] ECLSBC-1028 SuggestVendorPayments summary`
  - `[semantic-regression] ECLSBC-899 AN_08MTaxReportTempTable notes`
  - `[semantic-regression] ECLSBC-777 posting preview cleanup`
- the helper cleaned up those temporary verification documents at the end of the checked local run, so they do not remain in the local dev dataset after the default path completes
- stored scope values can now be queried through `GET /scope-values`, reused in the manual-ingest form, and matched conservatively against trim, casing, and spacing variants during document creation when exercised locally
- `GET /api/v1/scopes/tree` now returns `200` over the source-based dev backend on `http://127.0.0.1:8000`, with a nested `workspaces -> domains -> projects -> clients -> modules` shape that matched small live ingest data written through `POST /api/v1/documents`
- live source-based dev checks show repeated ingest into the same module does not duplicate that module node in the returned tree in the checked case
- live source-based dev checks also show a second project branch under the same workspace/domain remains separate, and a second workspace/domain branch remains separate
- frontend production build succeeds after adding the new `Scope Explorer` route and page
- the source-based dev frontend now serves the `/scopes` route on `http://127.0.0.1:4200`, and a live browser check showed the page rendering the fetched nested tree for the current backend data
- frontend production build still succeeds after the `Scope Explorer` polish update
- a live browser check now shows the `Scope Explorer` page rendering with collapsed workspace rows by default and a `Download JSON` action, with no inline raw JSON panel visible
- backend source still compiles after adding the document delete lifecycle slice
- frontend production build still succeeds after adding the `Documents` delete action
- live source-based dev checks now show `DELETE /api/v1/documents/{document_id}` returning `200` for an inserted test document, removing that document from the unversioned `GET /documents` list, returning no chunks from `GET /documents/{document_id}/chunks`, and removing the corresponding chunk ID from the active local Chroma collection in the checked cases
- live source-based dev checks now show `DELETE /api/v1/documents/{document_id}` returning `404` with a clear not-found message for a missing document ID
- a live headless browser DOM check now shows the `Documents` page rendering the new `Delete` action for stored documents in the source-based dev frontend
- live portable-runtime checks now show document ingest metadata persisting through `POST /api/v1/documents`, returning on `GET /api/v1/documents` and `GET /api/v1/documents/{document_id}`, and storing as Postgres `JSONB` on the checked document row
- live portable-runtime checks also show ingest without metadata still working, returning `metadata: null` on the checked v1 detail response, and leaving no `metadata-check/*` verification documents behind after cleanup
- the unversioned `POST /documents` and `GET /documents` routes still work after the metadata field was added to the shared document summary model in the checked portable-runtime smoke case
- a checked in-process chunking assessment now confirms:
  - paragraph boundaries are preserved through ingest after fixing an earlier raw-text whitespace-collapsing bug
  - very short inputs become a single chunk
  - text without blank-line paragraph breaks stays a single chunk
  - multiple paragraph blocks are split only when adding the next paragraph would exceed the current `1200`-character target
  - a single long paragraph is now split by sentence boundaries when that keeps chunk sizes under the current target
  - oversized paragraphs with poor or missing sentence boundaries fall back to deterministic hard character splits
  - mixed prose/code-like input receives no special chunking treatment beyond blank-line paragraph boundaries
- `POST /api/v1/retrieval/query` omits the `diagnostics` field unless `include_diagnostics=true`, while still returning diagnostics when explicitly requested in local in-process checks
- invalid nested v1 scope shapes and invalid `top_k` values now fail with request validation in local in-process checks instead of reaching retrieval execution
- `docker compose config` resolves successfully for the new multi-container runtime definition
- backend and frontend container images build successfully with `docker compose build`
- `docker compose up -d` now starts Postgres, Ollama, backend, and frontend successfully in the portable runtime after adding `PGDATA` for the bind-mounted Postgres data directory and runtime-local Ollama startup
- `docker ps` now shows the portable-runtime containers up with the expected published frontend/backend ports, now including runtime-local Ollama for semantic embeddings
- `docker compose down` stops and removes the portable-runtime containers while leaving `runtime-data/` intact
- `docker compose logs`, `docker compose logs backend`, `docker compose logs frontend`, `docker compose logs postgres`, `docker compose logs ollama`, and `docker compose logs ollama-model-init` are usable for runtime inspection
- backend container logs show Uvicorn startup completed in the Compose topology after rebuilding the backend image to run against the copied source tree
- frontend container serves its generated `runtime-config.js` over HTTP inside the container, with `apiBaseUrl` set from `CFHEE_API_BASE_URL`
- the portable runtime responds on `http://127.0.0.1:4210` for the frontend and `http://127.0.0.1:8010` for the backend after the host-port separation update
- the bind-mounted runtime data layout is active:
  - Postgres initializes under `runtime-data/postgres/pgdata`
  - Chroma writes persistent state under `runtime-data/chroma`
- runtime-local Ollama now persists its model cache under `runtime-data/ollama`
- the runtime data directories remain present after a `docker compose down` + `docker compose up -d` cycle
- the repo now also documents a conservative backup and restore design for the current portable runtime in `docs/BACKUP_AND_RESTORE.md`
- the repo now also contains first conservative stopped-runtime backup and restore helper scripts for the portable runtime data layer
- the repo now also documents a future Operations / Admin surface design in `docs/OPERATIONS_SURFACE.md`
- the backend `GET /ops/summary` route returns a conservative read-only summary of runtime info, config summary, storage/path visibility, and backup visibility
- the portable-runtime backend `GET /ops/summary` route now succeeds on `http://127.0.0.1:8010/ops/summary` after fixing its repo-root fallback for the containerized source layout
- a runtime-origin request to `GET /ops/summary` from `http://127.0.0.1:4210` now returns `Access-Control-Allow-Origin: http://127.0.0.1:4210`
- the frontend `Operations / Admin` page builds successfully and consumes the backend ops summary through a small dedicated frontend API service, including the new backup summary section
- the frontend Operations/Admin page now uses a shared dark-surface utility baseline so its storage/path visibility cards stay visually consistent with the rest of the workbench
- `scripts/runtime-backup.ps1` creates a timestamped backup directory under `backups/` containing `postgres`, `chroma`, and `manifest.json` when the runtime is stopped
- `scripts/runtime-restore.ps1` restores `runtime-data/postgres` and `runtime-data/chroma` from a selected backup directory when the runtime is stopped and the explicit confirmation phrase is provided
- local stopped-runtime checks show both helpers fail clearly if Compose still reports running runtime services
- local restore checks show the helper replaces the full current runtime data layer, removing marker files created after the backup snapshot

## Not implemented yet

- real scope management UI
- query-scope resolution for partial-scope or uncertain-scope questions
- explicit wider-scope retrieval orchestration across multiple scopes
- broader settings or admin UI beyond the current read-only `Operations / Admin` surface
- bulk file import, connectors, and OCR
- explicit external-integration-oriented API contracts beyond the current app-driven endpoint set
- broader document lifecycle management beyond explicit single-document deletion
- metadata-based retrieval, ranking, filtering, or first-class metadata query surfaces
- advanced chunking behavior such as code-aware splitting, language-aware splitting, overlap, or metadata-aware chunking
- versioned `/api/v1` answer, additional scope-helper, and query-log detail endpoints beyond the current health/capabilities/ingest/retrieval/document-inspection/query-log shell
- backup validation tooling
- restore safety tooling
- backend-owned ops layers or endpoints beyond the current read-only summary
- production hardening for the portable runtime
- migration tooling for runtime updates

## Current runtime model

- Postgres is required
- backend is required
- frontend developer workbench is required
- Chroma local vector state is required
- current normal semantic ingest and retrieval require Ollama reachability for embeddings
- `hash` embeddings remain available only as an explicit fallback mode through `EMBEDDING_PROVIDER=hash`
- Ollama for grounded answers remains optional because the answer layer still supports deterministic fallback
- current chunking is acceptable for the present project stage because it is inspectable and deterministic for paragraph-oriented notes, tickets, and summaries, and oversized normal-text paragraphs now degrade more safely; it is still weak for code-heavy inputs and documents whose structure is not well represented by paragraph or simple sentence boundaries

## Current portable runtime model

- frontend container is implemented
- backend container is implemented
- Postgres container is implemented
- Ollama container is implemented for the normal semantic embedding path
- Postgres persistent data is bound to `runtime-data/postgres`
- Chroma persistent data is bound to `runtime-data/chroma`
- runtime-local Ollama model cache is bound to `runtime-data/ollama`
- portable runtime backend now defaults its embedding runtime to the Compose-local Ollama service at `http://ollama:11434`
- portable runtime startup now includes a one-shot `bge-m3` bootstrap check that pulls the model only when it is missing from the persisted runtime Ollama cache
- source-based local development remains valid and separate
- portable runtime frontend/backend host ports are now intentionally separated from source-based dev
- runtime start/stop/log/update guidance now exists and is documented
- stopped-runtime backup and restore helpers now exist for the current data layout
- backup and restore remain intentionally conservative and limited to full-instance data replacement
- future app-managed operations are now doc-defined separately from host/runtime-managed operations
- a first backend-owned read-only ops summary surface now exists for future Operations/Admin UI work

## Current architectural reading

What currently exists should be read as:

- a working scoped knowledge core with a small built-in developer workbench
- not a full assistant product
- not a workflow platform
- not an orchestration system

## Immediate architectural implication

Future growth should prefer:

- deterministic scope taxonomy and metadata policy usage during ingest and retrieval operations
- external scope planning or orchestration on top of the current scoped execution core, rather than moving that responsibility into CfHEE
- frontend improvements around the frozen API
- portable runtime operations, backup, and restore on top of the current runtime slice
- first external consumer integrations
- keeping workflow-specific logic outside the module

rather than expanding the API surface or turning the module into a broader application identity.
