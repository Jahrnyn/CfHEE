# CfHEE

CfHEE is a local-first, scoped knowledge infrastructure module for document ingest, scoped storage, retrieval, and retrieval-derived context building.

Its core responsibility is: storing heterogeneous technical or enterprise knowledge so it can be retrieved later within an explicit scope, with traceability back to stored source material.

CfHEE acts as a:

- Knowledge Infrastructure Module

## What This System Is

- A reusable backend module for scoped knowledge ingest and retrieval
- A developer workbench for inspection, debugging, and validation of stored knowledge, and grounded answers
- A source-grounded retrieval system with explicit scope boundaries

## What This System Is Not

- Not an AI assistant product
- Not a workflow engine
- Not an orchestration layer
- Not a discovery or search engine across unknown scopes

CfHEE is a scoped execution engine, not a discovery engine.

CfHEE does not perform query-scope inference.

## Core Capability

- Retrieval-derived context building

External systems are expected to retrieve scoped context from CfHEE and use it downstream in LLM calls, workflows, or other higher-level consumers.

## Core Concepts

- Scope: `workspace -> domain -> project -> client -> module`
- Ingest: document plus explicit scope is stored, chunked, and indexed
- Retrieval: queries execute inside caller-provided scope
- Chunking: normal text uses paragraph-first chunking; `code_snippet` uses fixed 40-line windows with 10-line overlap
- Embeddings: normal operation uses Ollama-backed `bge-m3` semantic vectors
- Metadata: caller-provided document `metadata` is persisted as descriptive JSON, not as hard scope
- Answer: grounded only in retrieved context
- Context: deterministic selection of retrieved chunks

## Mental Model

- The caller must provide scope.
- CfHEE does not hide scope planning behavior.
- Retrieval does not silently widen across scopes.
- If scope is wrong or incomplete, results may be empty or partial.
- Behavior is intended to stay explicit and deterministic.

## Scope Guide

- `workspace`: stable top-level knowledge space, usually an organization or other durable top boundary
- `domain`: broad technical, product, or business area inside that workspace
- `project`: concrete initiative or solution area when that distinction matters for retrieval
- `client`: specific customer or tenant when that distinction is operationally meaningful
- `module`: narrowest functional or business subsystem that is still useful as a retrieval boundary

Practical rules:

- the caller provides scope
- CfHEE does not infer scope
- retrieval stays inside the caller-provided scope
- incorrect or overly narrow scope can produce empty or partial results
- hard scope is not the same as descriptive metadata such as `source_type`, `language`, `source_ref`, or document `metadata`

For external apps, scripts, and future orchestration layers:

- use stable scope values
- reuse existing stored scope values when possible
- treat scope as an explicit contract with CfHEE
- do not expect hidden scope widening, discovery behavior, or scope repair from CfHEE

Example:

workspace: "Internal"
domain: "Business Central"
project: "Finance Customization"
client: "CustomerA"
module: "Avizo"

At minimum, `workspace` and `domain` must always be provided.

## Minimal Usage Flow

1. Ingest a document with explicit scope.
2. Query with explicit scope.
3. Build deterministic scoped context through `POST /api/v1/context/build` when an external system needs provider-free context assembly.
4. Use scoped retrieval results directly, or call the built-in unversioned grounded-answer convenience route if you need local answer validation.

## Example

### Ingest

```json
POST /api/v1/documents
{
  "source_type": "manual_note",
  "title": "Refund handling notes",
  "raw_text": "Refund logic for Avizo lives in the payment journal extension.",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  }
}
```

### Retrieval

```json
POST /api/v1/retrieval/query
{
  "query": "Where is refund handling described?",
  "scope": {
    "workspace": "Internal",
    "domain": "Business Central",
    "project": "Finance Customization",
    "client": "CustomerA",
    "module": "Avizo"
  },
  "top_k": 5
}
```

## API Overview

Main versioned endpoints:

- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `GET /api/v1/documents/{document_id}/chunks`
- `DELETE /api/v1/documents/{document_id}`
- `POST /api/v1/retrieval/query`
- `POST /api/v1/context/build`
- `GET /api/v1/scopes/values`
- `GET /api/v1/scopes/tree`
- `GET /api/v1/query-logs`

For the current public contract, use [docs/API_V1.md](docs/API_V1.md).

External-consumer note:

- the stable public v1 surface is centered on ingest, retrieval, context building, inspection, and traces
- the built-in grounded-answer capability exists, but it is a convenience consumer and not part of the current frozen `/api/v1` route surface

## Current Capabilities

- Document ingestion with explicit scope
- Scoped retrieval
- Grounded answers from retrieved context
- Scope-tree visibility through `GET /api/v1/scopes/tree`
- Deterministic single-document deletion through `DELETE /api/v1/documents/{document_id}`

## Limitations

- No query-scope inference
- No discovery-engine behavior across unknown scopes
- No automatic reasoning over scopes
- No silent cross-scope retrieval widening

## Embedding Runtime

- Default semantic path: `EMBEDDING_PROVIDER=ollama`
- Default embedding model: `EMBEDDING_MODEL=bge-m3`
- Embedding Ollama URL: `EMBEDDING_OLLAMA_BASE_URL` or fallback `OLLAMA_BASE_URL`
- Explicit placeholder fallback only: `EMBEDDING_PROVIDER=hash`
- If semantic embeddings are configured but Ollama or `bge-m3` is unavailable, ingest and retrieval fail clearly

## Running CfHEE

- DEV: source-based workbench on `http://127.0.0.1:4200` with backend on `http://127.0.0.1:8000`
- Use the current `scripts/dev-up.ps1` workflow for source-based local development
- RUNTIME: portable containerized instance on `http://127.0.0.1:4210` with backend on `http://127.0.0.1:8010`
- Portable runtime now includes a runtime-local Ollama service for semantic embeddings
- On first runtime start, Compose lazily pulls `bge-m3` into `runtime-data/ollama` if it is not already present
- Readiness is inspectable through `docker compose ps`, `docker compose logs ollama-model-init`, and `docker compose logs ollama`
- For full runtime details, use [docs/RUNTIME_OPERATIONS.md](docs/RUNTIME_OPERATIONS.md)

## Full Documentation

The `/docs/` directory is the source of truth.

Start here:

- [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md)
- [docs/API_V1.md](docs/API_V1.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DECISIONS.md](docs/DECISIONS.md)
- [docs/DOMAIN_MODEL.md](docs/DOMAIN_MODEL.md)
- [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)
- [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md)
