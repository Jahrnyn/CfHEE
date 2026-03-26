# Docs Index

This file explains the role of each documentation file in the repository.

## Core architecture docs

### `docs/ARCHITECTURE.md`
High-level architecture overview of the system.
Use this to understand the module boundary, layers, integration direction, and long-term structure.
This document describes the intended architecture and does not serve as the authoritative source for current implementation status.

### `docs/DECISIONS.md`
Architecture decisions that should not be re-debated casually.
Use this to avoid drifting away from agreed technical choices.

### `docs/DOMAIN_MODEL.md`
Defines the core domain hierarchy:
- workspace
- domain
- project
- client
- module
- document
- chunk

Use this when working on persistence, retrieval, and scoping.

## Live project state docs

### `docs/PROJECT_STATE.md`
Current verified status of the project.
Use this first when you need to know what already exists.

### `docs/NEXT_STEPS.md`
The current recommended next development target.
Use this to avoid scope drift.

### `docs/CHANGELOG_DEV.md`
Chronological development log.
Use this to understand what changed recently and what issues were observed.

### `docs/PROMPTING_GUIDE.md`
Practical rules for working with Codex in this repository.
Use this before writing or refining prompts.

### `docs/PROMPT_TEMPLATE.md`
Reusable template for future Codex prompts.
Use this to keep prompts consistent and complete.

### `docs/API_V1.md` 
Initial design for a compact, stable, reusable module API

## Suggested reading order for AI assistants

For most implementation tasks, read in this order:
1. `AGENTS.md`
2. `docs/PROJECT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `docs/ARCHITECTURE.md`
5. `docs/DECISIONS.md`
6. `docs/DOMAIN_MODEL.md`
7. `docs/PROMPTING_GUIDE.md`
8. `docs/API_V1.md` 
9. `docs/CHANGELOG_DEV.md` if the task relates to recent work

## Human usage note

If you are resuming work after a break, start with:
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/CHANGELOG_DEV.md`

## Authority rules

When documents disagree, prefer:
1. `docs/PROJECT_STATE.md` for current verified implementation state
2. `docs/NEXT_STEPS.md` for current intended next step
3. `docs/DECISIONS.md` for fixed technical decisions
4. `docs/ARCHITECTURE.md` for long-term structure
5. `docs/CHANGELOG_DEV.md` for recent historical context

## Notes on removed docs

`docs/MVP.md` is intentionally removed from the active documentation set.
The project is no longer framed primarily as a copilot-style MVP. The current documentation is organized around a stable module boundary, current verified state, and next integration-oriented steps.
