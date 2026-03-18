# AGENTS.md

## Project
Copilot for Hostile Enterprise Environment

Local-first, multi-workspace, domain-aware knowledge retrieval and reasoning platform.

## Mission
Build a personal AI workbench that ingests heterogeneous technical and enterprise documents,
stores them with explicit scope metadata, indexes them, and answers questions with source-grounded responses.

## Core principles
- Local-first by default
- Retrieval-first, not agent-first
- Source-grounded answers only
- Scoped isolation by default
- User-defined top-level metadata is authoritative
- Keep implementation simple and modular
- Favor thin vertical slices over broad unfinished scaffolding

## Tech stack
- Frontend: Angular
- Backend: Python + FastAPI
- Database: Postgres
- Vector store: Chroma first, abstracted behind adapter
- LLM runtime: Ollama local
- Raw file storage: local filesystem

## Domain model
Hierarchy:
- Workspace
- Domain
- Project
- Client
- Module
- Source
- Document
- Chunk

Every document must belong to a workspace and domain at minimum.
The system must avoid cross-contamination across scopes.

## Architectural rules
- Never couple business logic directly to a specific vector DB implementation.
- Never couple business logic directly to a specific LLM provider.
- Preserve raw source input.
- Enrichment must not overwrite user-provided top-level scope.
- Prefer async enrichment where possible.
- Default retrieval must be scoped.
- Global search must be explicit, never implicit.

## MVP target
The first usable MVP must support:
1. Manual document ingestion
2. Explicit scope metadata assignment
3. Persistence in Postgres
4. Document listing
5. Basic chunking
6. Embedding + vector indexing
7. Scoped retrieval
8. Source-grounded answers

## Coding rules
- Prefer readable, boring code over clever abstractions
- Strong typing where practical
- Small services with explicit responsibilities
- Avoid framework magic when simple code is enough
- Keep functions short and names literal
- Add docstrings/comments only where they clarify intent

## Backend structure
Expected modules:
- api
- scope_registry
- ingestion
- normalization
- chunking
- enrichment
- embeddings
- vector_store
- retrieval
- llm
- answers
- persistence

## Frontend structure
Expected views:
- Inbox / Capture
- Documents
- Ask Copilot
- Scope Manager
- Settings

## Working style for Codex
When implementing:
1. Read docs/ARCHITECTURE.md and docs/MVP.md first
2. Propose the smallest viable change
3. Implement incrementally
4. Keep diffs narrow
5. Explain tradeoffs briefly
6. Do not introduce speculative complexity unless required

## Do not do yet
- No autonomous ticket solving
- No multi-agent orchestration
- No external connectors
- No complex auth system
- No cloud model dependency by default