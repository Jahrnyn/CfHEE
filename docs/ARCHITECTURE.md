# Architecture

## Purpose

Copilot for hostile enterprise environment is a local-first, multi-workspace, domain-aware knowledge copilot.

Its purpose is to:

* build a scoped knowledge base from heterogeneous enterprise and technical inputs
* enable fast scoped retrieval across that knowledge
* provide source-grounded answers from retrieved context
* prevent cross-contamination across companies, clients, projects, and modules
* establish a clean foundation for later enrichment and agent-style workflows

This document describes the **intended system architecture and long-term structure**.

It is **not** the authoritative source for current implementation status.

For verified current state, use:

* `docs/PROJECT_STATE.md`
* `docs/NEXT_STEPS.md`

---

## Design Principles

### 1. Local-first by default

The system should work on the developer's local machine without requiring cloud infrastructure.

### 2. Retrieval-first

The core value of the system comes from finding and scoping the right information before attempting higher-level reasoning.

### 3. Scoped isolation by default

Knowledge must remain partitioned by workspace/domain/project/client/module unless broader access is explicitly requested.

### 4. Source-grounded answers

Answers must be generated only from retrieved context and remain traceable back to source chunks and documents.

### 5. User-defined top-level metadata is authoritative

The user provides the primary scope at ingest time.
Model-generated tags and classifications are advisory only.

### 6. Raw inputs are preserved

Original source material must remain available for inspection and reprocessing.

### 7. Provider abstraction

LLM providers and vector backends should remain replaceable.

### 8. Thin vertical slices over speculative frameworks

The system should grow incrementally through verifiable slices, not broad unvalidated scaffolding.

---

## Target System Shape

```text
Frontend (Angular)
    ↓
API / Orchestrator (FastAPI)
    ↓
+--------------------------------------------------+
| Scope Layer                                      |
| Ingestion Pipeline                               |
| Retrieval Pipeline                               |
| Answer Layer                                     |
| Optional Enrichment / Background Processing      |
+--------------------------------------------------+
    ↓
Persistence Layer
- Postgres
- Vector Index
- Raw File Storage
```

---

## Core Domain and Scope Model

The system is built around hierarchical scope.

### Scope hierarchy

```text
Workspace > Domain > Project > Client > Module
```

### Meaning

* **Workspace**: highest-level separation, usually company or major knowledge space
* **Domain**: large technical or business area inside a workspace
* **Project**: concrete project or solution area
* **Client**: customer or sub-tenant inside a project/domain
* **Module**: narrow feature, subsystem, or operational context

### Rule

Every document and chunk must remain traceable to its scope.

Minimum ingest scope:

* workspace
* domain
* source_type
* title
* raw_text

Optional:

* project
* client
* module
* language
* source_ref

---

## Target Layers

## 1. Frontend Layer

The frontend is the user-facing workbench.

### Target responsibilities

* manual ingest UI
* document browsing
* chunk inspection
* retrieval UI
* grounded answer UI
* scope selection
* later: scope management and settings
* later: admin/debug tooling

### Intended views

* Overview
* Inbox / Capture
* Documents
* Ask Copilot
* Scope Manager
* Settings

---

## 2. API / Orchestrator Layer

The backend coordinates all workflows.

### Target responsibilities

* document ingest
* scope validation and enforcement
* chunk generation
* indexing orchestration
* retrieval
* grounded answer generation
* error handling
* configuration handling
* later: enrichment/background jobs

---

## 3. Scope Layer

This layer protects isolation and keeps the knowledge base partitioned correctly.

### Intended components

* Scope Registry
* Scope Policy Engine
* Query Scope Resolver

### Core rules

* retrieval is scoped by default
* cross-workspace access is forbidden unless explicitly enabled
* global search is opt-in only
* answer generation must preserve active scope
* user-provided top-level scope is never silently overridden

---

## 4. Ingestion Pipeline

The ingestion pipeline turns raw input into structured, indexable knowledge.

### Target flow

```text
Input → Scope metadata → Normalize → Chunk → Embed → Store → Optional enrichment
```

### Intended input types

* pasted text
* wiki text
* ticket text
* technical notes
* code snippets
* later: PDF, HTML, Markdown, DOCX

### Intended components

* Document Normalizer
* Chunking Service
* Embedding Service
* Vector Store Adapter
* Optional enrichment services

### Target outcomes

* original input preserved
* document metadata persisted
* chunks persisted
* vectors indexed
* scope preserved at every layer

---

## 5. Retrieval Pipeline

This is the core value path of the system.

### Target flow

```text
Query → Scope resolve → Embed → Scoped retrieval → Rank/select → Build context
```

### Intended components

* Scoped Retriever
* Vector search backend
* Metadata filtering
* Context Builder
* later: Context Budget Manager
* later: better ranking/reranking options if needed

### Retrieval rules

* retrieval must never silently cross scopes
* empty retrieval must be explicit
* retrieved results must remain inspectable
* retrieved chunks must preserve source traceability

---

## 6. Answer Layer

The answer layer sits on top of retrieval.

### Target flow

```text
Scoped query → Retrieval → Context assembly → Answer provider → Grounded response
```

### Intended components

* Answer Service
* Answer Provider Abstraction
* Local LLM Provider
* later: provider routing if needed
* later: improved citation formatting and prompting

### Answer rules

* answers must only use retrieved context
* no free-form unsupported answering
* if there is not enough evidence, the system should say so explicitly
* cited source chunks must remain visible and traceable

### Intended response shape

```json
{
  "answer": "...",
  "active_scope": { "...": "..." },
  "citations": [
    {
      "document_id": 0,
      "chunk_id": 0,
      "chunk_index": 0
    }
  ],
  "status": "ok | no_evidence | provider_failure"
}
```

---

## 7. Persistence Layer

## Postgres

Postgres is the inspectable system of record for metadata and stored content.

### Intended responsibilities

* scope entities
* documents
* chunks
* glossary/enrichment metadata later
* query logs later
* job metadata later

### Core tables

* workspaces
* domains
* projects
* clients
* modules
* documents
* chunks

### Later tables

* glossary_entries
* ingestion_jobs
* query_logs
* answer_logs
* enrichment metadata

## Vector Index

The vector backend supports retrieval.

### MVP backend

* Chroma

### Later option

* Qdrant

## Raw File Storage

Local filesystem stores original imported artifacts when needed.

---

## 8. Optional Enrichment and Background Processing

These are planned capabilities, not core MVP dependencies.

### Intended future capabilities

* translation
* summary generation
* entity extraction
* glossary candidate extraction
* tag suggestion
* reindex jobs
* document reprocessing

### Future background jobs

* ingestion jobs
* enrichment jobs
* reindex jobs
* maintenance jobs

---

## End-to-End Target Flows

## A. Ingest flow

```text
User input
→ scope assignment
→ normalization
→ document persistence
→ chunk generation
→ chunk persistence
→ embedding generation
→ vector indexing
→ optional enrichment
```

## B. Retrieval flow

```text
User query
→ explicit scope
→ retrieval
→ scoped chunk results
→ source metadata
```

## C. Answer flow

```text
User query
→ explicit scope
→ retrieval
→ grounded answer generation
→ answer + citations + active scope
```

---

## Planned Capability Map

## Already aligned in direction

* scoped ingest
* chunk persistence
* vector indexing
* scoped retrieval
* grounded answer path

## Planned but not necessarily implemented yet

* real local LLM-backed answer provider
* enrichment pipeline
* glossary extraction
* background jobs
* scope management UI
* settings UI
* stronger provider selection/routing
* later agent workflows built on top of this foundation

---

## Current Implementation Snapshot

This section is intentionally short.
For detailed verified status, use `docs/PROJECT_STATE.md`.

### Implemented now

* Angular shell and core pages
* manual ingest flow
* document listing
* chunk inspection
* Postgres persistence for scope/documents/chunks
* paragraph-based chunking
* local hash embedding
* Chroma indexing
* scoped retrieval
* retrieval hardening
* grounded answer flow using a deterministic local provider
* Windows-first dev bootstrap scripts

### Not yet implemented

* real Ollama-backed answer provider
* enrichment pipeline
* real scope management UI
* settings UI beyond placeholders
* background job system
* glossary pipeline
* agent workflows

---

## Non-goals for the Current MVP

The current MVP is not trying to provide:

* autonomous agent workflows
* external enterprise connectors
* advanced auth / multi-user deployment
* production-grade cloud runtime
* large orchestration framework
* broad automation beyond scoped knowledge ingest/retrieval/answering

---

## Technology Stack

### Current direction

* Frontend: Angular
* Backend: Python + FastAPI
* Metadata DB: Postgres
* Vector backend: Chroma
* Local file storage: filesystem

### LLM direction

* local provider first
* Ollama intended as the primary real local answer provider path
* deterministic provider acceptable as temporary fallback during development

---

## Final Architectural Intent

The intended end state is:

A multi-workspace, domain-aware, local-first knowledge copilot that can ingest heterogeneous enterprise and technical material, preserve strict scope isolation, retrieve relevant evidence quickly, and generate grounded answers with traceable citations — while remaining extensible toward enrichment and later agent-style workflows.
