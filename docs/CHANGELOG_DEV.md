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
