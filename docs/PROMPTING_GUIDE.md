# Prompting Guide

Use this repo with a thin-slice mindset.

## Default instructions for future work

- Read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/MVP.md` first.
- Keep changes small and practical.
- Prefer vertical slices over scaffolding.
- Treat user-provided scope metadata as authoritative.
- Do not claim retrieval, answer generation, or Ollama support already exists.

## Good prompts

- "Implement the smallest scoped retrieval endpoint using the existing Chroma adapter."
- "Add a minimal Ask page wired to a retrieval-only backend response."
- "Review the ingest flow for bugs and missing validation."
- "Improve local dev workflow on Windows without turning it into a task runner."

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
- `Ask Copilot`, `Scope Manager`, and `Settings` are placeholder pages today.
- Retrieval and answers should remain scoped by default when implemented.
