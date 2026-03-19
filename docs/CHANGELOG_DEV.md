# Dev Changelog

## 2026-03-19

- Added Windows-first local bootstrap scripts:
  - `scripts/dev-up.ps1`
  - `scripts/dev-check.ps1`
- Updated `README.md` with a short local development bootstrap section.
- Confirmed the repo currently contains:
  - manual document ingest UI
  - document list UI
  - chunk inspection UI
  - FastAPI document endpoints
  - Postgres persistence
  - paragraph-based chunking
  - Chroma indexing with local hash embeddings

## Known issues already observed

- Direct `.\scripts\*.ps1` execution can be blocked by PowerShell execution policy in this environment.
- Docker emitted a user-config warning under PowerShell in this environment; the bootstrap scripts route Docker calls through `cmd.exe` to avoid that issue.
- The latest local check found that Postgres, backend, and frontend were not running at the time of verification.
- `docs/TASKS.md` no longer reflects current implementation status and should be updated later.
