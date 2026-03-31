# Portable Runtime Design

Last reviewed: 2026-03-31

## Purpose

This document defines the portable runtime model for CfHEE and records the first implemented runtime packaging slice.

The design intent still matters here, but this document is no longer planning-only.

## Status labels used in this document

- **Observed current repo state**: verified from the current repository
- **Design intent**: planned direction for later implementation
- **Not implemented yet**: explicitly not present in the repo today

## Observed current repo state

- local development remains Windows-first
- `scripts/dev-up.ps1` still starts:
  - Postgres through Docker Compose
  - backend through local Python / Uvicorn
  - frontend through local Angular dev server
- `scripts/dev-check.ps1` still verifies the source-based local workflow
- backend defaults to `DATABASE_URL=postgresql://cfhee:cfhee@localhost:5432/cfhee`
- backend defaults Chroma persistence to `apps/backend/data/chroma`, overridable through `CHROMA_PERSIST_DIRECTORY`
- backend now defaults `EMBEDDING_PROVIDER` to `ollama` and `EMBEDDING_MODEL` to `bge-m3`
- frontend defaults to `http://127.0.0.1:8000` and can be redirected through `apps/frontend/public/runtime-config.js`
- the portable runtime now publishes different host-facing ports than source-based dev:
  - frontend on `4210`
  - backend on `8010`
- the backend now uses Ollama-backed semantic embeddings for normal ingest and retrieval
- the portable runtime now includes an Ollama service and points backend embeddings at the runtime-local Ollama URL

## First implemented portable runtime slice

**Observed current repo state**

The first containerized portable runtime slice now includes:

- frontend container
- backend container
- Postgres container
- Ollama container
- explicit bind-mounted persistent data directories:
  - `runtime-data/postgres`
  - `runtime-data/chroma`
  - `runtime-data/ollama`

It is implemented through:

- `apps/backend/Dockerfile`
- `apps/frontend/Dockerfile`
- `docker-compose.yml`

This slice does not add:

- reverse proxy or TLS
- production hardening

Later runtime-operation slices can add backup and restore helpers on top of this runtime packaging without changing the container topology itself.

## Portable instance concept

**Design intent**

A future CfHEE portable runtime should be movable as one instance.

That means:

- the runtime may consist of multiple containers
- the instance should be reproducible from versioned runtime packaging
- the instance should carry its persistent state in a layout that is easy to copy, move, and back up
- moving the instance should not require mixing source code checkout with live runtime data

In practical terms, a portable instance is the combination of:

- a runtime layer
- a persistent data layer

Those two layers belong together operationally, but they should remain clearly separated.

## Minimum portable runtime

**Design intent**

The minimum portable runtime should include:

- frontend: required
- backend: required
- Postgres: required
- Chroma persistent state: required
- Ollama for semantic embeddings: required in the portable runtime normal path

Current repo-state note:

- the current normal semantic embedding path needs runtime-local Ollama reachability for the backend embedding runtime
- the portable runtime now packages Ollama as a Compose service for the normal semantic path

## Current Ollama dependency shape

**Observed current repo state**

- Ollama-backed `bge-m3` embeddings are now the default normal path for ingest and retrieval
- `EMBEDDING_PROVIDER=hash` remains available only as an explicit fallback mode
- grounded-answer generation still has deterministic fallback behavior and therefore does not require Ollama
- the portable runtime now points embedding traffic at the Compose-local Ollama service
- the runtime now persists the Ollama model cache under `runtime-data/ollama`
- startup now includes a one-shot bootstrap check that pulls `bge-m3` only when it is missing from that persisted runtime-local Ollama cache

Operational note:

- the built-in answer layer can still remain on deterministic mode even while the portable runtime includes Ollama for semantic embeddings

## Component model

**Design intent**

The intended minimum portable runtime is:

1. Frontend runtime
2. Backend runtime
3. Postgres runtime
4. Ollama runtime for semantic embeddings
5. Chroma persistence used by the backend

This can later be packaged as multiple cooperating containers.

This document does not require deciding yet whether Chroma remains embedded through the current backend-side persistent client usage or is later reshaped operationally. The important design point for this slice is simpler:

- Chroma-backed vector persistence is required
- its persistent state must travel with the instance

## Persistent data model

**Design intent**

Portable packaging should separate:

- runtime/package/container layer
- persistent data layer

The persistent data layer should be easy to:

- back up
- copy
- move
- keep across runtime updates

### Minimum persistent data in scope

Based on the current repo state, the minimum persistent data to carry with a portable instance is:

- Postgres persistent data
- Chroma persistent data

Current repo-state note:

- `runtime-data/ollama` is also part of the current portable-runtime data layout as a persisted runtime-local model cache
- it is not part of the current helper-driven backup payload, but preserving it avoids unnecessary `bge-m3` re-pulls after restart or move

This document does not add a separate raw-artifact storage directory to the minimum portable runtime because that is not a distinct implemented persistent runtime requirement in the repo today.

### Conceptual layout

The repo now uses this concrete first-slice layout:

```text
repo-root/
  docker-compose.yml
  runtime-data/
    postgres/
    chroma/
    ollama/
```

Meaning:

- Compose defines the packaged runtime
- `runtime-data/` holds durable instance state

The higher-level portable-instance idea still remains:

- runtime packaging should stay separate from persistent data
- instance data should remain easy to copy and move

### Important separation rule

Runtime updates should target the runtime layer.

Persistent knowledge data should remain in the data layer unless an intentional migration is being performed.

That separation is important so a user can:

- update the packaged runtime without overwriting stored knowledge
- copy the whole instance to another machine
- back up only the durable data when needed

## Dev workflow vs portable runtime workflow

**Observed current repo state**

The active workflow today is local development from source:

- code is edited locally in the repo
- backend runs from the local Python environment
- frontend runs from the local Angular dev server
- Postgres runs through the existing `docker-compose.yml`

**Design intent**

Portable runtime packaging is a separate concern and must not replace the current development workflow.

Both workflows should continue to exist with different purposes:

- local dev workflow: source editing, local testing, iteration, GitHub push
- portable runtime workflow: running a packaged instance with persistent data

The current repo now also separates those workflows by host-facing frontend and backend ports so the active environment is easier to recognize.

That means:

- developers can still work from source in the current repo
- code can still be pushed to GitHub normally
- a later packaged runtime can be rebuilt or updated from the repo or build outputs
- persistent runtime data should remain separate from source code checkout

### Why data may appear missing between dev and runtime

Source-based local work and the portable runtime can now be distinguished quickly by port:

- source-based dev frontend/backend: `4200` / `8000`
- portable runtime frontend/backend: `4210` / `8010`

They can therefore point at different backend processes.

The most important current data-path difference is Chroma persistence:

- source-based local backend defaults to `apps/backend/data/chroma`
- portable runtime backend uses `runtime-data/chroma`

Postgres portable-runtime data remains under `runtime-data/postgres`.

If retrieval or context-building output looks different between those environments, first confirm which port pair is active before assuming data loss.

The current runtime-operations workflow is now documented in:

- `docs/RUNTIME_OPERATIONS.md`

## Update model

**Observed current repo state**

The repo now has a minimal documented runtime update flow:

1. pull latest repo changes
2. keep `runtime-data/` in place
3. rebuild and restart with `docker compose up --build -d`
4. confirm the containers and logs

This is documentation only.

It is not migration tooling.

**Design intent**

A later portable-instance update flow should follow this shape:

1. Build or prepare updated runtime artifacts from the repo
2. Replace or refresh the runtime layer
3. Keep the persistent data layer intact
4. Run any explicit migrations only when needed

For the current concrete commands, use `docs/RUNTIME_OPERATIONS.md`.

## Staged implementation direction

**Design intent**

Given the current repo state, the practical staged path is:

1. Define the portable runtime model in docs first
2. Containerize the required runtime components without changing API contracts
3. Make the persistent data layout explicit and stable
4. Define update and operational workflow for moving, backing up, and refreshing instances

### Why this order fits the current repo

- the API contract is currently in freeze, so runtime work can proceed without mixing in contract churn
- the repo already has a split between dev bootstrap and runtime-related concerns
- Postgres and Chroma persistence expectations are already visible in the current setup
- the portable-instance boundary is clearer if the minimum required components are defined before packaging decisions

## Explicitly not implemented yet

- hot backup support
- partial restore or merge restore
- backup validation tooling
- restore safety automation beyond explicit confirmation
- production hardening
- non-localhost operational defaults

## Summary

**Observed current repo state**

- current development remains source-based and Windows-first
- the repo now also contains a first Compose-based portable runtime slice for frontend + backend + Postgres
- the portable runtime now also includes Compose-local Ollama for semantic embeddings
- Chroma already uses local persistent filesystem state
- the Ollama model cache now also uses local persistent filesystem state under `runtime-data/ollama`
- conservative stopped-runtime backup and restore helpers now exist for the current runtime-data layout
- the current normal semantic path now runs inside the portable runtime through runtime-local Ollama embeddings

**Design intent**

- future portable CfHEE should be a movable instance made of runtime layer plus persistent data layer
- minimum runtime should require frontend, backend, Postgres, runtime-local Ollama for semantic embeddings, and Chroma persistence
- portable runtime packaging should complement, not replace, the current dev workflow

**Not implemented yet**

- fuller runtime operations around stronger backup validation, restore safety, and updates
