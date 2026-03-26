# CfHEE External API v1

## Goal

The purpose of CfHEE API v1 is to:

- make the module usable without a frontend
- provide a stable entry point for external apps and scripts
- respect the current module boundary
- expose a knowledge service, not a workflow engine

The key statement:

> **CfHEE API v1 = scoped ingest + scoped retrieval + grounded access + inspectability**

---

## What is in v1

Four capabilities only:

- Scope-aware document ingest
- Scope-aware document and chunk inspection
- Scope-aware retrieval
- Scoped grounded answer as a convenience endpoint

Plus one supplementary capability:

- Trace / query log inspection for developer use

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
- no domain-specific business endpoints

---

## API Design Principles

### 1. Scope is mandatory

Retrieval is already scoped by default. The API must enforce this strictly.

### 2. API-first, UI-second

The frontend is a consumer only — not a privileged client.

### 3. Raw and structured together

The system preserves both raw input and structured chunks. The API exposes both document-level and chunk-level views accordingly.

### 4. Versioned contract

All public endpoints are under `/api/v1/...`.

### 5. Deterministic envelope

All responses follow a consistent shape so external apps can consume them easily.

---

## Endpoint Reference

### 1. System

```
GET  /api/v1/health
GET  /api/v1/capabilities
```

External clients need a quick bootstrap to check whether the service is alive, which features are enabled, and whether the answer provider is available.

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

---

### 2. Scope Helpers

```
GET  /api/v1/scopes/values
POST /api/v1/scopes/resolve
```

#### GET /api/v1/scopes/values

Retrieves existing scope values. Useful for autocomplete in external ingest tools.

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

#### POST /api/v1/scopes/resolve

Allows a client to verify how a scope would be normalized — and validate it before ingest.

**Request**

```json
{
  "scope": {
    "workspace": " Bechtle ",
    "domain": "CRM ",
    "project": "Dynamics Rollout",
    "client": "Contoso",
    "module": "Lead Sync"
  }
}
```

**Response**

```json
{
  "normalized_scope": {
    "workspace": "Bechtle",
    "domain": "CRM",
    "project": "Dynamics Rollout",
    "client": "Contoso",
    "module": "Lead Sync"
  },
  "matched_existing": {
    "workspace": true,
    "domain": true,
    "project": false,
    "client": false,
    "module": false
  }
}
```

---

### 3. Documents

```
POST /api/v1/documents
GET  /api/v1/documents
GET  /api/v1/documents/{document_id}
GET  /api/v1/documents/{document_id}/chunks
```

This is close to the current implementation, promoted to a stable public contract.

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

> `metadata` is optional and loosely structured. In the current v1 slice, it is accepted by the public request model but not persisted yet.

**Response**

```json
{
  "document_id": 142,
  "status": "stored",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "chunk_count": 7,
  "indexed": true
}
```

#### GET /api/v1/documents

Filterable list endpoint. **Document listing is scoped by default.**

**Query params**: `workspace`, `domain`, `project`, `client`, `module`, `source_type`, `title_contains`, `limit`, `offset`

In v1, at least `workspace` + `domain` are required (conservative approach).

#### GET /api/v1/documents/{document_id}

Document metadata and raw preview.

**Response**

```json
{
  "document_id": 142,
  "title": "Rydoo refund avizo logic extension",
  "source_type": "jira_ticket",
  "language": "en",
  "source_ref": "JIRA-123",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "raw_text_preview": "First 1000 chars...",
  "chunk_count": 7,
  "created_at": "2026-03-26T18:00:00Z"
}
```

#### GET /api/v1/documents/{document_id}/chunks

**Response**

```json
{
  "document_id": 142,
  "chunks": [
    {
      "chunk_id": 991,
      "chunk_index": 0,
      "text": "...",
      "char_count": 432
    }
  ]
}
```

---

### 4. Retrieval

```
POST /api/v1/retrieval/query
```

The most important external endpoint. Retrieval is the core value path.

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

**Optional diagnostics** (only when `include_diagnostics: true`)

Retrieval diagnostics already exist in the query logs. In v1, they are not part of the default response.

When `include_diagnostics` is `false`, the `diagnostics` field is omitted from the response.

```json
{
  "diagnostics": {
    "candidate_count": 20,
    "top_k_limit_hit": false,
    "reranking_applied": true,
    "original_ranked_chunk_ids": [1, 3, 5],
    "reranked_chunk_ids": [3, 1, 5]
  }
}
```

---

### 5. Answer

```
POST /api/v1/answer/query
```

> **This is a convenience endpoint.** The grounded answer is built on top of retrieval, with provider selection and fallback. External apps should treat this as an optional layer, not the primary integration point.

**Request**

```json
{
  "query": "Summarize the refund handling in avizo logic.",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "top_k": 5,
  "max_context_chunks": 4,
  "language": "en",
  "include_citations": true
}
```

**Response**

```json
{
  "status": "ok",
  "answer": "Refund handling is covered in ...",
  "active_scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "citations": [
    {
      "document_id": 142,
      "chunk_id": 991,
      "chunk_index": 0
    }
  ],
  "provider": {
    "configured": "auto",
    "used": "ollama",
    "fallback_used": false
  },
  "evidence": {
    "has_evidence": true,
    "context_used_count": 3,
    "grounded_flag": true
  }
}
```

External apps can choose between using retrieval directly or using this built-in convenience layer.

---

### 6. Query Logs / Traces

```
GET /api/v1/query-logs
GET /api/v1/query-logs/{query_log_id}
```

Useful for regression checks, debugging, workflow audit trails, and answering "why did it return this?".

#### GET /api/v1/query-logs

**Query params**: `type` (`retrieval` | `answer`), `workspace`, `domain`, `project`, `client`, `module`, `limit`

**Response**

```json
{
  "items": [
    {
      "query_log_id": 88,
      "type": "answer",
      "query": "Summarize refund handling",
      "created_at": "2026-03-26T19:00:00Z",
      "active_scope": {
        "workspace": "Internal",
        "domain": "Business Central"
      },
      "result_count": 4,
      "provider_used": "ollama",
      "fallback_used": false
    }
  ]
}
```

#### GET /api/v1/query-logs/{query_log_id}

Returns a detailed trace for the given log entry.

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
| `no_evidence` | Answer had no grounding context |
| `validation_error` | Request was malformed or missing required fields |
| `provider_failure` | Answer provider was unavailable or failed |

---

## Authentication Stance (v1)

The system is currently local-first and developer-heavy. Complex auth is not introduced in v1.

**v1 position:**

- no complex auth by default
- optional API key layer to be added later
- can be tightened during the containerization / runtime phase

A future-ready header placeholder is reserved:

```
X-CFHEE-API-Key: ...
```

This is a no-op or disabled by default in v1.

---

## Sync vs Async

Everything in v1 is synchronous.

**Why:**

- the current core is a sync flow
- simpler for external clients
- easier to stabilize on a smaller surface area

**Explicitly not in v1:**

- `POST /jobs`
- polling
- callbacks
- event queues

Async patterns are a concern for the workflow layer, not the core.
