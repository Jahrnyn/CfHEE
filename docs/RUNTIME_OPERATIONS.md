# Runtime Operations

Last reviewed: 2026-03-27

## Purpose

This document explains how to operate the current CfHEE portable runtime instance.

It covers:

- what a CfHEE instance is
- what belongs to the runtime layer vs. the data layer
- how to start and stop the runtime
- how to inspect logs
- how to inspect the current read-only ops summary surface
- how to back up and restore the current data layer safely
- how to update the runtime without deleting stored data

It does not add:

- migration tooling
- production hardening

## What a CfHEE instance is

A CfHEE instance is the current runnable portable runtime plus its persistent data.

Today that means:

- frontend container
- backend container
- Postgres container
- persistent runtime data under `runtime-data/`

## Runtime layer vs data layer

### Runtime layer

The runtime layer is the runnable packaging:

- `docker-compose.yml`
- `apps/backend/Dockerfile`
- `apps/frontend/Dockerfile`
- container configuration and startup behavior

You can rebuild or restart the runtime layer.

### Data layer

The data layer is the persistent instance state:

- `runtime-data/postgres`
- `runtime-data/chroma`

This data should survive container rebuilds and restarts.

## Persistent data ownership

### Where data lives

- Postgres data lives under `runtime-data/postgres`
  - the current container writes its active database files under `runtime-data/postgres/pgdata`
- Chroma data lives under `runtime-data/chroma`

### What should be backed up

For the current portable runtime, the important persistent data to back up is:

- `runtime-data/postgres`
- `runtime-data/chroma`

### What must not be deleted casually

Do not delete:

- `runtime-data/postgres`
- `runtime-data/chroma`

Deleting those directories means deleting the current portable instance data.

### Backup and restore helpers

The current repo now includes:

- `scripts/runtime-backup.ps1`
- `scripts/runtime-restore.ps1`

These helpers are intentionally conservative:

- they require the portable runtime to be stopped
- they operate only on `runtime-data/postgres` and `runtime-data/chroma`
- restore is full-instance data replacement only

## Start the runtime

From the repo root:

```powershell
docker compose up --build -d
```

Or use the helper wrapper:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-up.ps1
```

What this does:

- builds updated images when needed
- starts Postgres
- starts backend
- starts frontend

Default host ports:

- frontend: `4210`
- backend: `8010`
- Postgres: `5432`

## Stop the runtime

From the repo root:

```powershell
docker compose down
```

Or use the helper wrapper:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-down.ps1
```

This stops and removes the runtime containers and network.

It does not delete `runtime-data/`.

## Inspect logs

All service logs:

```powershell
docker compose logs
```

Follow all logs:

```powershell
docker compose logs -f
```

Single-service examples:

```powershell
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
```

## Inspect the read-only ops summary

The backend now exposes a small read-only operational summary at:

```powershell
GET /ops/summary
```

It provides conservative app-visible information such as:

- runtime mode summary
- answer-provider mode
- backend CORS origins summary
- Postgres target summary without secrets
- Chroma persistence path
- storage/path visibility as seen by the running backend

It does not provide:

- runtime start or stop control
- image rebuild control
- backup trigger
- restore trigger

## Back up the runtime data

The current backup helper creates a timestamped backup directory containing:

- `postgres/`
- `chroma/`
- `manifest.json`

From the repo root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-backup.ps1
```

Optional destination root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-backup.ps1 -DestinationRoot .\backups
```

Safety rules:

- the runtime must be stopped first
- the helper fails if Compose still reports running CfHEE runtime services
- the helper backs up both data directories together

## Restore the runtime data

The current restore helper replaces the active runtime data layer from a selected backup directory.

From the repo root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-restore.ps1 -BackupPath .\backups\cfhee-backup-YYYYMMDD-HHMMSSfff
```

The helper requires explicit confirmation before replacement.

For a non-interactive explicit confirmation:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\runtime-restore.ps1 -BackupPath .\backups\cfhee-backup-YYYYMMDD-HHMMSSfff -ConfirmRestore RESTORE
```

Safety rules:

- the runtime must be stopped first
- restore replaces `runtime-data/postgres` and `runtime-data/chroma`
- partial restore and merge restore are not supported
- if the confirmation phrase is not provided exactly, the helper cancels

## Runtime config in container mode

### Port exposure

The current runtime exposes:

- frontend on `http://127.0.0.1:4210`
- backend on `http://127.0.0.1:8010`
- Postgres on `localhost:5432`

### Frontend to backend path

In container mode, the frontend image writes `runtime-config.js` at container startup.

That file sets `apiBaseUrl` from:

- `CFHEE_API_BASE_URL`

Default:

- `http://127.0.0.1:8010`

### Backend to Postgres path

In container mode, the backend reaches Postgres through the Compose service name:

- `postgresql://cfhee:cfhee@postgres:5432/cfhee`

### Backend CORS

The backend still uses `CORS_ALLOW_ORIGINS`.

In the current portable runtime, Compose defaults it to:

- `http://localhost:4210`
- `http://127.0.0.1:4210`

Without an override, the backend code-level localhost defaults now also include the source-based frontend origins on `4200` plus the portable-runtime frontend origins on `4210`.

## Why data may appear missing between dev and runtime

The portable runtime is now intentionally separated from the source-based dev workflow by host-facing frontend and backend ports:

- source-based dev uses `4200` for the frontend and `8000` for the backend
- portable runtime uses `4210` for the frontend and `8010` for the backend

That means it is easier to tell which environment is currently serving the workbench and API.

The current data-path difference that most often matters is Chroma persistence:

- source-based local backend defaults to `apps/backend/data/chroma`
- portable runtime backend uses `runtime-data/chroma`

Postgres instance data for the portable runtime remains under `runtime-data/postgres`.

If retrieval or context-building results look different, first confirm which frontend/backend port pair you are using before assuming data has been deleted.

## Update the runtime

Current minimal update flow:

1. Pull the latest repo changes.
2. Keep `runtime-data/` in place.
3. Rebuild and restart the runtime:

```powershell
docker compose up --build -d
```

4. Confirm the runtime is up:

```powershell
docker compose ps
docker compose logs backend --tail 20
docker compose logs frontend --tail 20
```

5. Confirm persistent data is still present under:

- `runtime-data/postgres`
- `runtime-data/chroma`

This update flow rebuilds the runtime layer without deleting the current instance data layer.

## Current limits

Not implemented yet:

- schema/data migration tooling
- multi-instance management
- production hardening
- hot backup support
- partial restore
- backup validation tooling
- runtime lifecycle control from the app
