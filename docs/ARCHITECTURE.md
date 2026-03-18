## Goal
Local-first personal AI workbench that:
- builds a scoped knowledge base from heterogeneous enterprise inputs
- enables fast retrieval + grounded answers
- avoids cross-contamination between companies/projects
- prepares for future agent workflows

## Core Architecture
```
Frontend (Angular)
    ↓
API / Orchestrator (FastAPI)
    ↓
+-------------------------------+
| Scope Layer                   |
| Ingestion Pipeline            |
| Query / Answer Pipeline       |
+-------------------------------+
    ↓
Persistence (Postgres + Vector DB + Files)
```
## Core Concepts (STRICT)
Hierarchy (ALWAYS applied):
```
Workspace > Domain > Project > Client > Module
```
Each document/chunk MUST include:
- workspace (required)
- domain (recommended)
- optional: project, client, module
- language
- source_type
User-defined top-level metadata is NEVER overridden.

## Isolation Rules (CRITICAL)
- retrieval is ALWAYS scoped by default
- cross-workspace access = forbidden unless explicit
- global search = opt-in only
- every answer includes source attribution
- query session has fixed scope

## Ingestion Pipeline
Flow:
```
Input → Scope metadata → Normalize → Chunk → Embed → Store → (Optional enrichment)
```
Input types:
- pasted text (primary)
- wiki / tickets
- code snippets
- later: files (PDF, HTML, MD)
Key components:
- Document Normalizer
- Chunking Service (heading-aware)
- Embedding Service
- Vector Store Adapter
Optional async:
- translation
- summary
- tagging

## Retrieval Pipeline (CORE VALUE)
Flow:
```
Query → Scope resolve → Embed → Scoped search → Rank → Build context → Answer
```
Components:
- Scoped Retriever (STRICT filtering)
- Hybrid search (vector + metadata)
- Context Budget Manager (token control)
- Context Builder (dedupe + ordering)

## Answer Layer
Components:
- LLM Adapter (Ollama first)
- Model Router (later)
- Answer Composer
Rules:
- MUST be source-grounded
- MUST NOT hallucinate outside context
- response language: EN/HU
Response schema:
```
{
  direct_answer,
  why_this_answer,
  source_snippets,
  confidence,
  follow_up_terms,
  active_scope
}
```
## Persistence
### Postgres (metadata)
Main tables:
- workspaces, domains, projects, clients, modules
- documents, chunks
- glossary_entries
- ingestion_jobs
- query_logs
### Vector DB
- Chroma (MVP)
- Qdrant (later)
### Raw storage
- local filesystem (original inputs)

## Key Layers
### 1. Frontend (Angular)
- ingest UI (with scope selection)
- document browser
- chat interface
- scope selector
- admin tools (reindex, inspect)
### 2. API / Orchestrator (FastAPI)
- ingest workflow
- query workflow
- scope enforcement
### 3. Scope Layer
- Scope Registry (hierarchy)
- Scope Policy Engine (rules)
- Query Scope Resolver
### 4. Background Jobs
- ingestion processing
- enrichment
- reindex

## Modules (Backend)
```
api
scope_registry
scope_policy
ingestion
normalization
chunking
enrichment
embeddings
vector_store
retrieval
llm
answers
persistence
jobs
admin
```

## End-to-End Flows

### A - Ingest
```
User → API → Job → Normalize → Chunk → Embed → Store → Done
```
### B - Query
```
User → API → Scope → Retrieve → Build context → LLM → Response
```

## MVP Scope
Include:
- manual scope input
- ingest + chunk + embed
- scoped retrieval
- chat with sources
- basic summary/translation
Exclude:
- agents
- automation workflows
- external connectors
- complex auth

## 🛠 Tech Stack (MVP)
- Frontend: Angular
- Backend: Python + FastAPI
- DB: Postgres
- Vector: Chroma
- LLM: Ollama (local)
- Storage: local FS

## Key Architectural Principles
1. Retrieval-first
2. Scope isolation by default
3. Raw data always preserved
4. Async enrichment
5. Provider abstraction (LLM + vector DB)
6. User controls top-level metadata

## Build Phases
### Phase 1
- schema + ingest + scope basics
### Phase 2
- embeddings + retrieval + chat
### Phase 3
- enrichment + tagging + glossary
### Phase 4
- admin + tuning + model routing

## Final State
A multi-workspace, domain-aware, local-first knowledge copilot that:
- aggregates enterprise + personal knowledge
- enables fast scoped retrieval
- provides grounded answers
- serves as foundation for future AI agents

