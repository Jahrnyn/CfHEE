# Prompting Guide

Use this repo with a thin-slice mindset.

## Default instructions for future work

- Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/NEXT_STEPS.md`, and `docs/ARCHITECTURE.md` first.
- Keep changes small and practical.
- Prefer vertical slices over scaffolding.
- Treat user-provided scope metadata as authoritative.
- Preserve strict scope isolation.
- Treat CfHEE as a reusable knowledge module, not as a copilot product that should absorb higher-level workflow logic.

## Good prompts

- "Implement the smallest stable external-facing retrieval contract using the existing backend flow."
- "Review the ingest flow for bugs and missing validation."
- "Improve local dev workflow without changing the module boundary."
- "Tighten the API response contract for external consumers of scoped retrieval."

## State-awareness rules

- Distinguish clearly between:
  - implemented in code
  - verified by running locally
  - planned in docs only
- If services are not running, say that explicitly instead of implying runtime verification.
- Prefer file-based evidence over assumptions.

## Current known constraints

- Windows-first local development is the active path.
- Frontend API calls are currently pointed at `http://127.0.0.1:8000`.
- `Ask Copilot` is implemented as a convenience interface; `Scope Manager` and `Settings` are still placeholder pages.
- Retrieval and answers should remain scoped by default.
- Workflow engines, orchestration logic, and agent loops should remain outside CfHEE.

## Long-term note

After the API boundary is stable, a later infrastructure step is to make the system easier to package and run across environments through containerization and more portable deployment shape.
