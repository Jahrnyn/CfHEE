# CfHEE External API v1

## API v1 Code Freeze (Contract Stabilization)

CfHEE external API v1 is now in **API v1 Code Freeze (Contract Stabilization)**.

This is a freeze of the public API contract only.
It is not a full project freeze.

### Frozen now

- all implemented `/api/v1/...` endpoints
- request and response shapes
- the shared scope model and scope rules
- document contract behavior
- retrieval contract behavior
- query-log list contract behavior

### Not frozen

- frontend workbench behavior
- internal implementation details
- internal refactoring without contract change
- performance improvements
- containerization and runtime setup
- developer tooling

### Allowed after freeze

- bugfixes that preserve the public contract
- internal refactoring that does not change request or response contracts
- non-breaking additions only if they are strictly necessary

### Not allowed after freeze

- breaking API changes
- silent contract changes
- scope model changes
- changing response semantics

### Module responsibility during freeze

CfHEE API v1 is frozen as a contract for:

- scoped knowledge storage
- scoped retrieval
- retrieval-derived context building
- inspection
- observability

CfHEE API v1 is not frozen as a contract for:

- answer generation as a core responsibility
- workflow orchestration

## Goal

The purpose of CfHEE API v1 is to:

- make the module usable without a frontend
- provide a stable entry point for external apps and scripts
- respect the current module boundary
- expose a knowledge service, not a workflow engine

The key statement:

> **CfHEE API v1 = scoped ingest + scoped retrieval + context building + inspectability**

---

## What is in v1

Implemented versioned capabilities:

- Scope-aware document ingest
- Scope-aware document and chunk inspection
- Scope-aware retrieval
- Retrieval-derived context building
- Query-log inspection for developer use
- Scope-value reuse for ingest helpers
- Scope-tree visibility for external callers

Module note:

- the module has a built-in grounded-answer capability on the unversioned convenience route
- there is no `POST /api/v1/answer/query` route in the current frozen v1 slice

---

## What is NOT in v1

Explicitly out of scope:

- no workflow orchestration
- no async job engine
- no agent loop
- no external connector abstraction
- no file parser platform
- no bulk ingest pipeline framework
- no cross-scope implicit search
- no versioned answer endpoint in the current freeze slice
- no domain-specific business endpoints

---

## API Design Principles

### 1. Scope is mandatory

Retrieval is already scoped by default. The API must enforce this strictly.
CfHEE does not perform query-scope inference.
Scope determination is the responsibility of the caller or an external orchestration layer.
CfHEE is a scoped execution engine, not a discovery engine.

### 2. Hard scope is distinct from descriptive metadata

Hard scope / retrieval partitioning fields:

- `workspace`
- `domain`
- `project`
- `client`
- `module`

Descriptive metadata fields:

- `source_type`
- `language`
- `source_ref`

The descriptive fields are stored and returned, but they are not part of the shared scope object and do not define the retrieval partition.

### 3. API-first, UI-second

The frontend is a consumer only, not a privileged client.

### 4. Raw and structured together

The system preserves both raw input and structured chunks. The API exposes both document-level and chunk-level views accordingly.

### 5. Versioned contract

All public endpoints in this slice are under `/api/v1/...`.

### 6. Deterministic envelope

All responses follow a consistent shape so external apps can consume them easily.

---

## Endpoint Reference

### 1. System

```text
GET /api/v1/health
GET /api/v1/capabilities
```

External clients need a quick bootstrap to check whether the service is alive and which backend capabilities exist.

**Example response**

```json
{
  "status": "ok",
  "service": "cfhee",
  "api_version": "v1",
  "capabilities": {
    "document_inspection": true,
    "document_ingest": true,
    "scoped_retrieval": true,
    "grounded_answer": true,
    "query_logs": true,
    "scope_values": true
  }
}
```

`grounded_answer: true` indicates a module capability exists.
It does not imply a versioned `/api/v1/answer/query` endpoint exists in the current slice.

---

### 2. Scope Helpers

```text
GET /api/v1/scopes/values
GET /api/v1/scopes/tree
```

Retrieves existing stored scope values for reuse during ingest.
Useful for autocomplete and conservative value reuse in external tools.

**Query params** (all optional): `workspace`, `domain`, `project`, `client`

**Response**

```json
{
  "workspaces": ["bechtle", "internal"],
  "domains": ["crm", "business-central"],
  "projects": ["rydoo-modernization"],
  "clients": ["contoso"],
  "modules": ["payments", "avizo"]
}
```

Current note:

- the current v1 helper surface exposes value reuse plus stored-hierarchy visibility
- there is no versioned scope-resolution endpoint in the current freeze slice

#### GET /api/v1/scopes/tree

Returns the currently stored scope hierarchy as a structured tree built from the `workspaces`, `domains`, `projects`, `clients`, and `modules` tables.

This is a visibility helper for external callers.
It does not infer scope, resolve scope, or plan retrieval on behalf of the caller.

**Response**

```json
{
  "workspaces": [
    {
      "name": "Internal",
      "domains": [
        {
          "name": "Business Central",
          "projects": [
            {
              "name": "Finance Customization",
              "clients": [
                {
                  "name": "CustomerA",
                  "modules": [
                    { "name": "Avizo" }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Behavior in the current slice:

- only stored scope combinations are returned
- no synthetic nodes are created
- naming is returned exactly as stored
- the endpoint is a visibility helper only and must not be treated as query-scope inference

---

### 3. Documents

```text
POST /api/v1/documents
GET  /api/v1/documents
GET  /api/v1/documents/{document_id}
GET  /api/v1/documents/{document_id}/chunks
```

These routes expose the current public ingest and inspection slice.

#### POST /api/v1/documents

The primary ingest endpoint.

**Request**

```json
{
  "source_type": "jira_ticket",
  "title": "Rydoo refund avizo logic extension",
  "raw_text": "....",
  "language": "en",
  "source_ref": "JIRA-123",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "metadata": {
    "author": "Zoltan",
    "tags": ["refund", "payment-journal"]
  }
}
```

`metadata` is optional and loosely structured.
In the current v1 slice, it is accepted by the public request model but not persisted by the backend translation layer.

#### GET /api/v1/documents

Filterable list endpoint.
Document listing is scoped by default.

**Query params**: `workspace`, `domain`, `project`, `client`, `module`, `source_type`, `title_contains`, `limit`, `offset`

In v1, at least `workspace` and `domain` are required.

---

### 4. Retrieval

```text
POST /api/v1/retrieval/query
```

This is the main external retrieval endpoint.

**Request**

```json
{
  "query": "Where is refund handling described in avizo logic?",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "top_k": 5,
  "include_chunks": true,
  "include_diagnostics": false
}
```

**Response**

```json
{
  "status": "ok",
  "query": "Where is refund handling described in avizo logic?",
  "active_scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "results": [
    {
      "document_id": 142,
      "chunk_id": 991,
      "chunk_index": 0,
      "title": "Rydoo refund avizo logic extension",
      "source_type": "jira_ticket",
      "similarity_score": 0.88,
      "distance": 0.12,
      "text": "...."
    }
  ],
  "result_count": 3
}
```

Current retrieval stance:

- retrieval is explicit-scope-driven
- CfHEE executes retrieval within caller-provided scope
- missing query scope is not inferred from the user question inside CfHEE
- the system does not silently widen across scope boundaries
- the current model is strongest for exact or intentionally chosen scopes
- partial-scope and wider-scope handling remain future design areas

Diagnostics note:

- retrieval diagnostics are omitted unless `include_diagnostics=true`
- diagnostics already exist in stored query logs for inspection

---

### 5. Context Build

```text
POST /api/v1/context/build
```

This endpoint prepares provider-free, retrieval-derived context for external consumers.
It does not generate an answer and does not add prompt instructions.
It also does not determine or infer scope on behalf of the caller.

Behavior in the current slice:

- reuses scoped retrieval and current reranking behavior
- reuses the current deterministic context-selection and dedupe logic from the answer flow
- applies a chunk-count limit through `max_context_chunks`
- omits diagnostics unless `include_diagnostics=true`
- does not support `max_context_chars` yet
- does not log a separate context-build trace yet

---

### 6. Query Logs / Traces

```text
GET /api/v1/query-logs
```

This endpoint is explicitly developer-oriented and intended for inspectability rather than end-user output.

**Query params**: `limit`, `type` (`retrieval` | `answer`), `workspace`, `domain`, `project`, `client`, `module`

When scope filtering is used, `workspace` and `domain` must be provided together.

Current note:

- there is no versioned query-log detail endpoint in the current freeze slice

---

## Shared Request Models

All scope-bearing endpoints use the same scope shape.

### ScopeRef

```json
{
  "workspace": "string",
  "domain": "string",
  "project": "string|null",
  "client": "string|null",
  "module": "string|null"
}
```

Hierarchy validation in the current slice:

- `client` requires `project`
- `module` requires `client`

### ApiError

```json
{
  "error": {
    "code": "missing_scope",
    "message": "workspace and domain are required",
    "details": {}
  }
}
```

### PagedResponse

```json
{
  "items": [],
  "paging": {
    "limit": 50,
    "offset": 0,
    "returned": 12
  }
}
```

---

## Standard Status Values

| Status | Meaning |
|--------|---------|
| `ok` | Success |
| `no_results` | Query returned no matches |
| `validation_error` | Request was malformed or missing required fields |

Note:
`no_evidence` and `provider_failure` remain relevant to the built-in answer capability, but they are not currently part of the versioned v1 route surface.

---

## Authentication Stance (v1)

The system is currently local-first and developer-heavy.
Complex auth is not introduced in v1.

v1 position:

- no complex auth by default
- optional API key layer may be added later
- auth hardening belongs to later runtime and deployment work

---

## Sync vs Async

Everything in v1 is synchronous.

Why:

- the current core is a synchronous flow
- simpler for external clients
- easier to stabilize on a smaller surface area

Explicitly not in v1:

- `POST /jobs`
- polling
- callbacks
- event queues

Async patterns are a concern for higher-level workflow layers, not the core module.
