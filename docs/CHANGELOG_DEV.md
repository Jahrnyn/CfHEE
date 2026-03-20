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
