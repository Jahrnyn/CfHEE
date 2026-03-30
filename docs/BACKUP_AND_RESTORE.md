# Backup and Restore Design

Last reviewed: 2026-03-27

## Purpose

This document defines the first backup and restore model for the current CfHEE portable runtime and records the first implemented helper scripts.

It does not add:

- scheduling
- migration tooling
- runtime behavior changes

## Status labels used in this document

- **Observed current repo/runtime state**: verified from the current repository and docs
- **Design intent**: the intended backup and restore model for the current portable runtime
- **Not implemented yet**: explicitly not present in the repo today

## Observed current repo/runtime state

- the current portable runtime uses:
  - frontend container
  - backend container
  - Postgres container
  - Ollama container
- persistent runtime data currently lives under:
  - `runtime-data/postgres`
  - `runtime-data/chroma`
  - `runtime-data/ollama`
- `runtime-data/postgres` currently contains the active Postgres files under:
  - `runtime-data/postgres/pgdata`
- the backend uses a persistent Chroma path mounted at:
  - `runtime-data/chroma`
- runtime-local Ollama now uses a persistent model cache mounted at:
  - `runtime-data/ollama`
- runtime start and stop are currently handled through:
  - `docker compose up --build -d`
  - `docker compose down`
  - `scripts/runtime-up.ps1`
  - `scripts/runtime-down.ps1`
- backup and restore helper scripts now exist:
  - `scripts/runtime-backup.ps1`
  - `scripts/runtime-restore.ps1`
- the read-only ops summary now also exposes conservative backup visibility for the default `backups/` location:
  - expected backup root path
  - whether that location exists
  - discovered backup count
  - latest backup name
  - latest manifest/timestamp visibility when safely inferable

## Backup scope

**Design intent**

For the current portable runtime, a CfHEE instance backup should include all persistent instance data:

- `runtime-data/postgres`
- `runtime-data/chroma`

That means:

- Postgres should be backed up as the durable relational system of record for stored documents, chunks, scopes, and query logs
- Chroma should be backed up as the durable vector-state companion for retrieval and context building

Current helper-scope note:

- the current helper scripts still back up and restore only `runtime-data/postgres` and `runtime-data/chroma`
- `runtime-data/ollama` currently acts as a persisted runtime dependency cache for the packaged `bge-m3` embedding runtime
- if that Ollama cache is missing after a move or restore, the portable runtime can repull `bge-m3` on the next startup bootstrap

The runtime layer itself is not the primary backup target for this first model.

The runtime layer can be rebuilt from the repository.
The data layer cannot be recreated from nothing without losing instance state.

## Restore scope

**Design intent**

For the current model, restore should mean:

- full-instance data replacement for the current portable runtime data layer

In practical terms, a restore should replace:

- `runtime-data/postgres`
- `runtime-data/chroma`

with the selected backup copy for that same instance.

This document does not define partial restore, selective document restore, or merge behavior.

## Safety stance

**Design intent**

The initial backup and restore model should require the runtime to be stopped.

That means:

- backup should initially require the runtime to be stopped
- restore should require the runtime to be stopped

Why this conservative model fits the current repo:

- the current runtime is small and local-first
- there is no implemented consistency tooling around live Postgres and Chroma capture
- there is no implemented migration or reconciliation tooling
- stopped-runtime file capture is easier to reason about and easier to operate safely

This is intentionally conservative.

## Backup artifact shape

**Design intent**

The first backup shape should stay simple.

Recommended first implemented shape:

- a timestamped backup directory
- separate Postgres and Chroma payloads
- small `manifest.json`

Conceptual example:

```text
cfhee-backup-2026-03-27T18-45-00/
  postgres/
  chroma/
  manifest.json
```

The first helper script currently uses the directory form, not an archive.

The important point for this slice is that the backup artifact keeps Postgres and Chroma clearly visible and restorable together.

### Optional manifest content

If a manifest is included later, it should stay factual and small.

Possible fields:

- backup timestamp
- CfHEE repo revision if known
- backup format version
- notes that the backup expects a stopped-runtime restore model

## Operational rules

**Design intent**

### What should be backed up

- `runtime-data/postgres`
- `runtime-data/chroma`

### What must not be deleted casually

Do not delete:

- `runtime-data/postgres`
- `runtime-data/chroma`

Deleting those directories means deleting the current instance data.

### What is not guaranteed yet

Not guaranteed yet:

- hot backup while the runtime is running
- selective restore of one subsystem only
- compatibility across arbitrary future schema or storage changes
- automated validation of backup completeness
- automated restore safety checks

### What remains future work

- backup artifact validation
- explicit operator checks before destructive restore
- optional archive output if it later proves useful

## Relationship to the current runtime model

**Design intent**

This backup and restore model follows the existing portable-runtime rules:

- portable runtime and persistent data remain separate concerns
- source-based local development remains separate from runtime instance operations
- the minimum portable runtime still consists of frontend, backend, Postgres, and Chroma persistence
- runtime-local Ollama is now part of the portable runtime for the normal semantic embedding path

That means:

- source code checkout is not the backup target for instance preservation
- persistent instance data is the backup target
- the runtime layer can later be rebuilt or refreshed without redefining what instance data must be preserved
- the running app can now show simple read-only backup-location visibility, but backup creation and restore remain external helper-driven operations

## Restore assumptions

**Design intent**

Before restore, these assumptions should hold:

- the target runtime is stopped
- the operator understands that restore replaces the current runtime data layer
- the backup artifact contains both Postgres and Chroma payloads for the same instance snapshot

This first model assumes a restore is an intentional replacement operation, not an in-place merge.

## Recommended next implementation slice

**Design intent**

The next minimal implementation slice after these helpers should be:

- tighter backup validation
- tighter restore safety checks

That follow-up should stay narrow:

- keep the stopped-runtime model
- keep full-instance restore only
- avoid scheduling, cloud sync, encryption, or partial-restore behavior

## Summary

**Observed current repo/runtime state**

- the portable runtime already has a visible persistent data layout under `runtime-data/`
- Postgres and Chroma persistence already exist
- conservative backup and restore helper scripts now exist

**Design intent**

- a CfHEE instance backup should cover `runtime-data/postgres` and `runtime-data/chroma`
- restore should initially be full-instance data replacement
- backup and restore should initially require the runtime to be stopped
- the first backup artifact should be a simple timestamped directory with separate Postgres and Chroma payloads plus a small manifest

**Not implemented yet**

- backup validation
- restore safety automation
- backup trigger or restore trigger from the running app
