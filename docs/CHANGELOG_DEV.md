# Dev Changelog

## 2026-03-19

- Added Windows-first local bootstrap scripts:
  - `scripts/dev-up.ps1`
  - `scripts/dev-check.ps1`
- Added the first scoped retrieval vertical slice:
  - backend retrieval request/response models
  - backend retrieval service
  - `POST /retrieval/query`
  - Chroma scoped query support through the existing vector-store layer
  - `Ask Copilot` UI for scoped retrieval-only queries
- Hardened the retrieval slice:
  - added `top_k` support while keeping retrieval scoped by default
  - added explicit missing-scope validation
  - added similarity score plus explicit chunk/document identifiers in results
  - added retrieval service logging for query text, scope, and returned result count
  - added clearer loading and empty states on the Ask page
- Added the first grounded answer vertical slice:
  - backend answer service reusing the existing retrieval flow
  - minimal answer-provider abstraction
  - deterministic local answer provider
  - `POST /answer/query`
  - Ask page support for grounded answer requests and cited supporting chunks
- Updated `README.md` with a short local development bootstrap section.
- Confirmed the repo currently contains:
  - manual document ingest UI
  - document list UI
  - chunk inspection UI
  - scoped retrieval UI
  - FastAPI document endpoints
  - FastAPI retrieval endpoint
  - Postgres persistence
  - paragraph-based chunking
  - Chroma indexing with local hash embeddings

## Known issues already observed

- Direct `.\scripts\*.ps1` execution can be blocked by PowerShell execution policy in this environment.
- Docker emitted a user-config warning under PowerShell in this environment; the bootstrap scripts route Docker calls through `cmd.exe` to avoid that issue.
- Scoped retrieval verification required starting Postgres with escalated Docker access in this environment.
- `docs/TASKS.md` no longer reflects current implementation status and should be updated later.

## 2026-03-20

- Added the first Ollama-backed grounded answer provider behind the existing answer abstraction.
- Added minimal answer-provider selection with safe fallback behavior:
  - `ANSWER_PROVIDER=auto` prefers Ollama and falls back to deterministic
  - `ANSWER_PROVIDER=ollama` still falls back to deterministic if Ollama is not ready
  - `ANSWER_PROVIDER=deterministic` forces the local fallback
- Kept retrieval as the only answer-context source.
- Updated the Ask page to show the active provider and whether deterministic fallback was used.
- Updated `scripts/dev-up.ps1` and `scripts/dev-check.ps1` to check Ollama reachability, configured model presence, and answer-provider readiness.
- Updated `README.md` with local Ollama setup and provider-selection notes.

## 2026-03-24

- Added a minimal `query_logs` table in Postgres for retrieval and answer traceability.
- Added explicit query-log persistence for:
  - query text
  - active scope
  - `top_k`
  - retrieved chunk and document identifiers
  - result count and empty-result state
  - answer text
  - provider used
  - fallback usage
- Integrated logging into retrieval-only queries and grounded answer queries while keeping logging failures non-blocking.
- Added a minimal `GET /query-logs` endpoint for inspecting recent traces.
- Added a minimal context builder between retrieval and grounded answer generation.
- Added deterministic answer-context ordering, conservative duplicate-text filtering, and an explicit answer-context limit.
- Extended query-log traceability with selected and dropped context chunk IDs for answer queries.
- Added a minimal deterministic evaluation layer for answer queries.
- Extended `query_logs` with simple inspectable evaluation fields:
  - `has_evidence`
  - `context_used_count`
  - `answer_length`
  - `grounded_flag`
- Integrated evaluation into the answer flow while keeping evaluation failures non-blocking.
- Added an explicit grounded-answer prompt builder for Ollama-backed answers.
- Switched prompt construction from inline string concatenation to a small readable module with:
  - conservative grounding instructions
  - explicit active-scope formatting
  - deterministic retrieved-context formatting
  - short-answer and no-speculation response rules
- Added minimal prompt-version traceability through provider logging.
- Removed the recent Ask-page manual-check and verification snapshot panels to restore a cleaner end-user UI.
- Kept backend query logging, evaluation, and traceability intact while removing direct debug rendering from the main Ask page.
- Added explicit answer-language guidance for grounded answers so Hungarian queries prefer Hungarian answers and English queries prefer English answers.
- Applied the same language preference to the deterministic fallback provider and the no-evidence/provider-failure answer messages.
- Extended `query_logs` with small retrieval diagnostics fields:
  - `candidate_count`
  - `top_k_limit_hit`
  - `returned_distance_values`
  - `returned_document_distribution`
- Extended `GET /query-logs` to expose those diagnostics for backend inspection without adding new Ask-page debug panels.
- Added a small post-retrieval lexical rescoring step on top of scoped vector candidates.
- The rescoring conservatively rewards:
  - exact identifier hits such as ticket-like terms
  - exact query-term matches in chunk text
  - title overlap for explicit technical terms
- Kept original vector distance/similarity intact and exposed reranking diagnostics through:
  - `original_ranked_chunk_ids`
  - `reranked_chunk_ids`
  - `reranking_applied`
- Added a tiny retrieval regression pack for rerunning a few real Business Central developer-document queries locally.
- Added:
  - `apps/backend/fixtures/retrieval_regression_cases.json`
  - `apps/backend/scripts/retrieval_regression_check.py`
- The regression pack is intentionally small and checks only a few high-signal cases such as:
  - exact identifier retrieval
  - specific function-name lookup
  - explicit temp-table lookup
- The runner prints plain pass/fail output plus the returned top results and reranking diagnostics.
- Added a small ingest-usability slice for scope metadata reuse and normalization.
- Added `GET /scope-values` for reading existing stored scope values for manual-ingest suggestions.
- Updated the manual-ingest form to:
  - reuse stored workspace/domain/project/client/module values through lightweight datalist suggestions
  - still allow entering new values when needed
  - show a small close-match hint for likely typo-like scope inputs
- Added conservative scope normalization during document creation:
  - trim leading/trailing whitespace
  - collapse repeated internal whitespace
  - reuse existing scope rows through case-insensitive scope matching
- Kept this slice intentionally narrow:
  - no file import
  - no connectors
  - no full scope-management subsystem

## 2026-03-26

- Added the first external API v1 routing shell under `/api/v1`.
- Added:
  - `GET /api/v1/health`
  - `GET /api/v1/capabilities`
- Kept the slice intentionally narrow:
  - existing unversioned routes remain active
  - no other `/api/v1` endpoints were added yet
  - no ingest, retrieval, answer, or query-log behavior was changed
- The capabilities response currently reports only backend capabilities that already exist in code:
  - document ingest
  - document inspection
  - scoped retrieval
  - grounded answer
  - query logs
  - scope values
