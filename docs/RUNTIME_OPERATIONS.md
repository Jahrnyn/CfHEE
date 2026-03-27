# Runtime Operations

Last reviewed: 2026-03-27

## Purpose

This document explains how to operate the current CfHEE portable runtime instance.

It covers:

- what a CfHEE instance is
- what belongs to the runtime layer vs. the data layer
- how to start and stop the runtime
- how to inspect logs
- how to update the runtime without deleting stored data

It does not add:

- backup tooling
- restore tooling
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

- frontend: `4200`
- backend: `8000`
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

## Runtime config in container mode

### Port exposure

The current runtime exposes:

- frontend on `http://127.0.0.1:4200`
- backend on `http://127.0.0.1:8000`
- Postgres on `localhost:5432`

### Frontend to backend path

In container mode, the frontend image writes `runtime-config.js` at container startup.

That file sets `apiBaseUrl` from:

- `CFHEE_API_BASE_URL`

Default:

- `http://127.0.0.1:8000`

### Backend to Postgres path

In container mode, the backend reaches Postgres through the Compose service name:

- `postgresql://cfhee:cfhee@postgres:5432/cfhee`

### Backend CORS

The backend still uses `CORS_ALLOW_ORIGINS`.

In the current portable runtime, Compose defaults it to:

- `http://localhost:4200`
- `http://127.0.0.1:4200`

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

- one-command backup
- restore flow
- schema/data migration tooling
- multi-instance management
- production hardening
