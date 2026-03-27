# Operations / Admin Surface Design

Last reviewed: 2026-03-27

## Purpose

This document defines the future Operations / Admin surface for CfHEE and records the first implemented read-only backend ops summary slice.

It does not add:

- a frontend Operations page
- changes to runtime behavior
- changes to helper-script behavior

## Status labels used in this document

- **Observed current repo state**: verified from the current repository and docs
- **Design intent**: planned direction for later implementation
- **Not implemented yet**: explicitly not present in the repo today

## Observed current repo state

- the frontend is a developer workbench with routes for:
  - `Overview`
  - `Inbox / Capture`
  - `Documents`
  - `Ask`
  - `Scope Manager`
  - `Settings`
- `Scope Manager` and `Settings` are still placeholder views
- the backend route layout currently focuses on:
  - system status
  - document ingest and inspection
  - retrieval
  - grounded answers
  - scope values
  - query-log inspection
  - read-only ops summary
  - frozen `/api/v1` routes
- runtime helper scripts currently exist for:
  - runtime start
  - runtime stop
  - runtime backup
  - runtime restore
- runtime packaging is Compose-based and host-managed
- backup and restore currently follow a conservative stopped-runtime model
- the backend now exposes a narrow read-only ops summary route at:
  - `GET /ops/summary`

## Design goal

**Design intent**

CfHEE should eventually expose a small Operations / Admin workbench surface for app-managed maintenance and visibility.

That surface should help an operator understand and manage the running CfHEE instance.

It should not turn CfHEE into:

- a Docker control panel
- a host orchestration tool
- a container lifecycle manager

## Core split

**Design intent**

Future operations should be divided into two groups:

1. app-managed operations
2. host/runtime-managed operations

That split matters because the running app can safely expose some information and maintenance actions, but it cannot safely own the whole host runtime lifecycle.

## Safe future in-app operations

**Design intent**

These are good candidates for a future Operations / Admin workbench surface because they fit the running app boundary.

The first implemented slice now covers a small subset of these:

- runtime info
- config summary
- storage/path visibility
- query-log inspection
- backup trigger
- restore preparation and guarded restore planning

### Meaning of those candidates

- **runtime info**
  - current app version if known
  - current API version
  - active answer-provider mode
  - visible runtime paths and basic environment summary
- **config summary**
  - current frontend-facing backend URL
  - current backend CORS origins
  - current Chroma persistence path
  - current Postgres connection target summary without exposing secrets
- **storage/path visibility**
  - where Postgres runtime data lives
  - where Chroma runtime data lives
  - whether those directories are visible and writable from the current runtime
- **query-log inspection**
  - this already conceptually fits the workbench and mostly exists through current backend routes
- **backup trigger**
  - later, a running app may be able to trigger a backend-managed backup action if that action can be performed safely inside the app boundary
- **restore preparation and guarded restore planning**
  - list available backups
  - validate backup shape
  - show restore warnings
  - prepare a restore plan

## Operations that should remain outside the frontend

**Design intent**

These operations should remain host-side or runtime-side concerns:

- `docker compose up`
- `docker compose down`
- image rebuild
- container lifecycle control
- host-level port management
- host filesystem setup outside the runtime data layer
- destructive final restore cutover when the app must stop itself

These activities control the host runtime rather than the knowledge module itself.

## Important restore boundary

**Design intent**

The current stopped-runtime restore model creates an important boundary:

- a running CfHEE app can help prepare and validate a restore
- the final destructive restore step should remain outside the running app if it requires the runtime to be stopped and the data layer to be replaced

That means the future frontend should not be designed as a one-click self-destruct/self-restore surface.

The safer model is:

1. inspect and prepare in the app
2. perform the final stopped-runtime replacement through an external helper
3. start the runtime again

## Classification of current helper scripts

**Observed current repo state**

### `scripts/runtime-up.ps1`

- current role: host/runtime-only
- later app-managed candidate: no
- reason: it controls Compose startup and host runtime lifecycle

### `scripts/runtime-down.ps1`

- current role: host/runtime-only
- later app-managed candidate: no
- reason: it controls Compose shutdown and host runtime lifecycle

### `scripts/runtime-backup.ps1`

- current role: host-side helper around the current runtime-data layout
- later app-managed candidate: partial yes
- reason: the underlying backup operation may later move into backend-owned reusable logic, while a host-side wrapper can still remain useful for stopped-runtime and offline operation

### `scripts/runtime-restore.ps1`

- current role: host-side destructive restore helper
- later app-managed candidate: partial yes
- reason: restore validation and planning can later be backend-managed, but the final stopped-runtime replacement step should remain external in the current model

## Target architecture direction

**Design intent**

The long-term shape should be:

```text
Frontend Operations/Admin surface
            |
            v
Backend internal ops layer
            |
            +-- safe app-managed maintenance actions
            +-- runtime info and config summary
            +-- backup/restore validation and planning

Host-side helper scripts
            |
            +-- runtime lifecycle wrappers
            +-- stopped-runtime backup wrapper if still useful
            +-- stopped-runtime restore cutover wrapper
```

## Role of a future backend internal ops layer

**Design intent**

The backend internal ops layer should eventually own reusable maintenance logic that belongs inside the app boundary.

Examples:

- collecting runtime info
- producing a safe config summary
- exposing storage/path visibility
- listing backups if a known backup location is used
- validating backup payload shape
- preparing a guarded restore request

This layer should not become a general host-control subsystem.

## How scripts should evolve

**Design intent**

The current helper scripts should gradually become thinner where that makes sense.

### Good candidates for thinner wrappers later

- backup helper
- restore helper

Possible later shape:

- backend/Python ops logic handles validation, manifest creation, path checks, and backup inventory behavior
- PowerShell wrappers call that same logic for local host-side usage
- a future frontend can call safe parts of that logic through backend routes

### Poor candidates for backend-owned logic

- runtime up
- runtime down

Those should remain simple host/runtime wrappers because they manage Compose itself rather than app-level maintenance behavior.

## Suggested future workbench surface

**Design intent**

When this is implemented later, the workbench surface should stay small.

A practical first Operations/Admin page could contain:

- runtime summary
- config summary
- storage locations
- backup list or last backup summary if available
- restore warnings and preparation state
- query-log inspection entry point

It should avoid trying to become:

- a system dashboard for everything on the host
- a replacement for Docker tooling
- a broad settings or orchestration product

## Recommended next implementation slice

**Design intent**

The best next implementation slice after the current read-only summary is:

- add a minimal frontend Operations/Admin page that reads the existing summary
- or extend the backend summary with a little more safe visibility if the frontend is still deferred

That slice should stay narrow:

- no runtime lifecycle control
- no destructive restore endpoint
- no API v1 changes

Practical first contents:

- runtime info
- config summary
- storage/path visibility
- explicit statement that runtime lifecycle remains external

## Summary

**Observed current repo state**

- CfHEE already has a developer workbench frontend and a small runtime-helper script set
- the backend already exposes system, retrieval, document, scope, context, query-log, and read-only ops-summary routes
- runtime lifecycle remains host-managed
- backup and restore are currently conservative script-driven operations

**Design intent**

- future app-managed operations should cover safe runtime visibility and selected maintenance actions
- host/runtime-level control should remain outside the frontend
- reusable maintenance logic should gradually move toward a backend internal ops layer where that logic belongs inside the app boundary
- runtime lifecycle wrappers should remain external

**Not implemented yet**

- frontend Operations/Admin page
- backend ops layers or endpoints beyond the current read-only summary
- shared backend-owned backup/restore validation logic
