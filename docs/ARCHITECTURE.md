# Architecture

## Purpose

CfHEE is a local-first, scoped knowledge storage, retrieval, and retrieval-derived context-building module.

Its purpose is to:

- build a scoped knowledge base from heterogeneous enterprise and technical inputs
- preserve raw source material and structured metadata
- enforce strict isolation across workspace, domain, project, client, and module boundaries
- provide fast, inspectable, scoped retrieval over stored knowledge
- provide retrieval-derived context building for higher-level systems
- expose that knowledge through stable APIs for higher-level systems
- provide a small built-in query and grounded-answer interface as a convenience consumer

This document describes the intended system architecture and long-term structure.

It is not the authoritative source for current implementation status.

For verified current state, use:

- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`

---

## Design Principles

### 1. Local-first by default

The system should work on the developer's local machine without requiring cloud infrastructure.

### 2. Retrieval-first

The main value of the system comes from storing, scoping, and retrieving the right information before any higher-level reasoning occurs.

### 3. Scoped isolation by default

Knowledge must remain partitioned by workspace, domain, project, client, and module unless broader access is explicitly requested.

### 4. Source traceability

Stored documents, chunks, and retrieval results must remain inspectable and traceable back to their sources.

### 5. User-defined top-level metadata is authoritative

The user provides the primary scope at ingest time.
Model-generated tags and classifications are advisory only.

### 6. Raw inputs are preserved

Original source material must remain available for inspection and reprocessing.

### 7. API-first module boundary

CfHEE should be usable as a backend module even when its frontend is absent.

### 8. Thin vertical slices over speculative frameworks

The system should grow incrementally through verifiable slices, not broad unvalidated scaffolding.

### 9. Higher-level workflows live outside the core

Workflow engines, automation pipelines, agents, and domain-specific business logic should be built as separate consumers of the module, not folded into the core system.

---

## Target System Shape

```text
External workflows / tools / apps
            ↓
        CfHEE API
            ↓
+--------------------------------------------------+
| CfHEE Knowledge Core                             |
| - Scope Layer                                    |
| - Ingestion Pipeline                             |
| - Retrieval Pipeline                             |
| - Context Builder                                |
| - Traceability / Query Logging                   |
| - Built-in Answer Consumer                       |
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

- **Workspace**: highest-level separation, usually company or major knowledge space
- **Domain**: large technical or business area inside a workspace
- **Project**: concrete project or solution area
- **Client**: customer or sub-tenant inside a project or domain
- **Module**: narrow feature, subsystem, or operational context

### Rule

Every document and chunk must remain traceable to its scope.

Minimum ingest scope:

- workspace
- domain
- source_type
- title
- raw_text

Optional:

- project
- client
- module
- language
- source_ref

---

## Target Layers

## 1. API Layer

The API layer is the primary boundary of the module.

### Responsibilities

- document ingest
- scope validation and enforcement
- document and chunk inspection
- retrieval queries
- retrieval-derived context building
- grounded-answer access as a convenience endpoint
- traceability and query-log access
- later: stable integration surface for external automation and workflow systems

### Boundary rule

External systems should interact with CfHEE through API contracts rather than direct code coupling.

---

## 2. Frontend Layer

The frontend is a lightweight developer workbench.

### Responsibilities

- manual ingest UI
- document browsing
- chunk inspection
- retrieval UI
- grounded-answer testing
- scope selection
- debugging and validation support

### Non-goal

The frontend is not the primary product identity of CfHEE.

---

## 3. Scope Layer

This layer protects isolation and keeps the knowledge base partitioned correctly.

### Intended components

- Scope Registry
- Scope Policy Engine
- Query Scope Resolver

### Core rules

- retrieval is scoped by default
- cross-workspace access is forbidden unless explicitly enabled
- global search is opt-in only
- user-provided top-level scope is never silently overridden

---

## 4. Ingestion Pipeline

The ingestion pipeline turns raw input into structured, indexable knowledge.

### Target flow

```text
Input → Scope metadata → Normalize → Chunk → Embed → Store
```

### Intended input types

- pasted text
- wiki text
- ticket text
- technical notes
- code snippets
- later: file-based imports such as PDF, HTML, Markdown, DOCX

### Intended components

- Document Normalizer
- Chunking Service
- Embedding Service
- Vector Store Adapter

### Target outcomes

- original input preserved
- document metadata persisted
- chunks persisted
- vectors indexed
- scope preserved at every layer

---

## 5. Retrieval Pipeline

This is the core value path of the system.

### Target flow

```text
Query → Scope resolve → Embed → Scoped retrieval → Rank/select → Build context
```

### Intended components

- Scoped Retriever
- Vector search backend
- Metadata filtering
- Context Builder
- later: Context Budget Manager
- later: better ranking and reranking options if needed

### Retrieval rules

- retrieval must never silently cross scopes
- empty retrieval must be explicit
- retrieved results must remain inspectable
- retrieved chunks must preserve source traceability

---

## 6. Built-in Answer Consumer

The built-in answer capability sits on top of retrieval.

### Purpose

- quick local querying
- validation of stored knowledge quality
- convenient grounded access during development

### Rule

This is a convenience consumer, not the architectural center of the system.

### Flow

```text
Scoped query → Retrieval → Context assembly → Answer provider → Grounded response
```

### Rules

- answers must only use retrieved context
- no free-form unsupported answering
- if there is not enough evidence, the system should say so explicitly
- cited chunks must remain visible and traceable

---

## 7. Traceability Layer

The system should preserve inspectable evidence about what happened during retrieval and grounded answering.

### Intended responsibilities

- query logs
- selected and dropped context tracking
- retrieval diagnostics
- provider and fallback visibility
- later: integration-facing observability

---

## 8. Persistence Layer

## Postgres

Postgres is the inspectable system of record for metadata and stored content.

### Intended responsibilities

- scope entities
- documents
- chunks
- query logs
- later: job and integration metadata

### Core tables

- workspaces
- domains
- projects
- clients
- modules
- documents
- chunks
- query_logs

## Vector Index

The vector backend supports retrieval.

### Current backend direction

- Chroma

### Later option

- Qdrant

## Raw File Storage

Local filesystem stores original imported artifacts when needed.

---

## End-to-End Target Flows

## A. Ingest flow

```text
User or external system input
→ scope assignment
→ normalization
→ document persistence
→ chunk generation
→ chunk persistence
→ embedding generation
→ vector indexing
```

## B. Retrieval flow

```text
User or external system query
→ explicit scope
→ retrieval
→ scoped chunk results
→ source metadata
```

## C. Grounded answer flow

```text
Scoped query
→ retrieval
→ grounded answer generation
→ answer + citations + active scope
```

---

## Current architectural boundary

CfHEE ends at:

- scoped knowledge ingest
- storage
- chunking and indexing
- scoped retrieval
- retrieval-derived context building
- traceable grounded access to stored knowledge

CfHEE does not include:

- workflow orchestration
- multi-step autonomous agents
- business-domain automation logic
- proposal-generation pipelines
- pentest decision engines
- external connector ecosystems as a core identity

Those should be implemented outside the module and communicate with it through stable APIs.

---

## Long-term deployment direction

The current active development path is local.

The first portable runtime slice now exists.

Long-term, after the module boundary and API surface are stable, CfHEE should continue moving toward a more production-buildable and containerized deployment shape so it can run consistently on Linux and other environments without depending on the current development setup alone.
