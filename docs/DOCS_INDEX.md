# Docs Index

This file explains the role of each documentation file in the repository.

## Core architecture docs

### `docs/ARCHITECTURE.md`
High-level architecture overview of the system.
Use this to understand the module boundary, layers, integration direction, and long-term structure.
This document describes the intended architecture and does not serve as the authoritative source for current implementation status.
Use this especially when a task touches the boundary between strict scoped execution inside CfHEE and any future external orchestration or scope planning.

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

Use this when working on persistence, retrieval, scoping, scope taxonomy, and ingest metadata policy.
This is also the primary doc for the distinction between hard scope and descriptive metadata.

### `docs/API_V1.md`
Current public API v1 contract and freeze boundary.
Use this when working on versioned external endpoints, request/response shapes, and what is or is not allowed during API v1 stabilization.
This is also the contract reference for the fact that v1 retrieval requires explicit scope and does not promise query-scope inference.

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

## Runtime docs

### `docs/PORTABLE_RUNTIME.md`
Portable runtime design and current runtime packaging model.
Use this to understand the portable-instance concept, minimum runtime composition, persistent data layout, and what remains intentionally unimplemented.

### `docs/RUNTIME_OPERATIONS.md`
Current runtime operations guide for the existing containerized runtime.
Use this for start/stop/log/update workflow, runtime-vs-data ownership, and what must be preserved under `runtime-data/`.

### `docs/BACKUP_AND_RESTORE.md`
Current backup and restore model for the portable runtime.
Use this for backup scope, restore safety rules, artifact shape, and what the helper scripts do or do not guarantee.

### `docs/OPERATIONS_SURFACE.md`
Operations/Admin surface design for future app-managed maintenance behavior.
Use this to understand the current read-only ops summary surface, what should later be manageable from the running app, what should remain host-side, and how helper scripts should evolve.

## Prompting docs

### `docs/PROMPTING_GUIDE.md`
Practical rules for working with Codex in this repository.
Use this before writing or refining prompts.

### `docs/PROMPT_TEMPLATE.md`
Reusable template for future Codex prompts.
Use this to keep prompts consistent and complete.

## Frontend docs

### `docs/FRONTEND_STYLE_GUIDE.md`
Minimal frontend styling contract.
Use this when changing or adding frontend UI so dark-theme surfaces, card styling, and consistency rules stay aligned.

## Meta docs

### `docs/DOCS_INDEX.md`
Index of the documentation set.
Use this to quickly find the right source of truth before making changes.

## Suggested reading order for AI assistants

For most implementation tasks, read in this order:
1. `AGENTS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/PROJECT_STATE.md`
4. `docs/NEXT_STEPS.md`
5. `docs/DECISIONS.md`
6. `docs/DOMAIN_MODEL.md`
7. `docs/API_V1.md` if the task touches versioned external API work
8. `docs/PORTABLE_RUNTIME.md` if the task touches runtime packaging or portable-instance design
9. `docs/RUNTIME_OPERATIONS.md` if the task touches runtime usage, logs, start/stop flow, or data ownership
10. `docs/BACKUP_AND_RESTORE.md` if the task touches runtime-data backup, restore, or safety rules
11. `docs/OPERATIONS_SURFACE.md` if the task touches future admin/operations UI or helper-script evolution
12. `docs/PROMPTING_GUIDE.md`
13. `docs/CHANGELOG_DEV.md` if the task relates to recent work

## Human usage note

If you are resuming work after a break, start with:
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/CHANGELOG_DEV.md`

If you are resuming runtime-related work, also read:
- `docs/PORTABLE_RUNTIME.md`
- `docs/RUNTIME_OPERATIONS.md`
- `docs/BACKUP_AND_RESTORE.md`
- `docs/OPERATIONS_SURFACE.md`

## Authority rules

When documents disagree, prefer:
1. `docs/PROJECT_STATE.md` for current verified implementation state
2. `docs/NEXT_STEPS.md` for current intended next step
3. `docs/DECISIONS.md` for fixed technical decisions
4. `docs/ARCHITECTURE.md` for long-term structure
5. `docs/API_V1.md` for the frozen public API v1 contract
6. `docs/PORTABLE_RUNTIME.md` for portable-runtime design and current runtime packaging intent
7. `docs/RUNTIME_OPERATIONS.md` for current runtime usage and operational workflow
8. `docs/BACKUP_AND_RESTORE.md` for current backup/restore rules and helper-script behavior
9. `docs/OPERATIONS_SURFACE.md` for future app-managed operations scope and helper-script evolution intent
10. `docs/CHANGELOG_DEV.md` for recent historical context

## Notes on removed docs

`docs/MVP.md` is intentionally removed from the active documentation set.
The project is no longer framed primarily as a copilot-style MVP. The current documentation is organized around a stable module boundary, current verified state, and next integration-oriented steps.

`docs/TASKS.md` is not part of the active documentation set.
Use `docs/PROJECT_STATE.md`, `docs/NEXT_STEPS.md`, and `docs/CHANGELOG_DEV.md` instead of reviving a stale task list as external memory.
