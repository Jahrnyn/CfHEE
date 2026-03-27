# AGENTS.md

## Project
CfHEE

A local-first, scoped knowledge storage and retrieval module.

## Mission
Build a reusable knowledge infrastructure that:

- ingests heterogeneous technical and enterprise documents
- stores them with explicit hierarchical scope metadata
- preserves raw inputs and traceability
- enables fast, reliable, scoped retrieval

The system is designed to act as a **backend module** for higher-level workflows, agents, and applications.

## Core principles
- Local-first by default
- Retrieval-first, not agent-first
- Source-grounded data access only
- Scoped isolation by default
- User-defined top-level metadata is authoritative
- Preserve raw inputs
- Keep implementation simple and modular
- Favor thin vertical slices over broad unfinished scaffolding

## What this system is

CfHEE is a:

> **Knowledge Infrastructure Module**

It provides:

- ingestion
- structured storage
- scoped retrieval
- retrieval-derived context building
- traceable data access

## What this system is NOT

Do not treat CfHEE as:

- an AI assistant product
- an agent framework
- a workflow engine
- an automation platform
- a business logic container

Higher-level systems must be built **outside** this module.

## Tech stack
- Frontend: Angular (developer workbench)
- Backend: Python + FastAPI
- Database: Postgres
- Vector store: Chroma (abstracted)
- LLM runtime: Ollama (optional, local)
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

Rules:
- Every document must belong to at least a workspace and domain
- Scope isolation must be strictly enforced
- Cross-scope retrieval must be explicit

## Architectural rules
- Never couple business logic to a specific vector DB
- Never couple business logic to a specific LLM provider
- Preserve raw source input
- Enrichment must not override user-defined scope
- Retrieval must be scoped by default
- Global search must be explicit, never implicit

## System boundary

CfHEE ends at:

- ingestion
- storage
- retrieval
- grounded data access

It must NOT contain:

- multi-step workflows
- agent loops
- orchestration logic
- domain-specific automation

## Answer layer

The answer layer is a:

> **built-in convenience consumer**

Purpose:
- quick manual querying
- debugging retrieval
- validating stored knowledge

It is not a core responsibility and should not be expanded into a full assistant system.

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

The frontend acts as a:

> **developer workbench**

Expected views:
- Inbox / Capture (manual ingest)
- Documents (inspection)
- Ask (retrieval + answer convenience)
- Scope Manager (future)
- Settings (future)

## Working style for Codex
When implementing:
1. Read docs/ARCHITECTURE.md first
2. Align with current project definition (knowledge module, not copilot)
3. Propose the smallest viable change
4. Implement incrementally
5. Keep diffs narrow
6. Avoid speculative abstractions

## Do not do
- Do not implement agent workflows inside this module
- Do not embed business-specific logic
- Do not add orchestration layers
- Do not introduce external connectors prematurely
- Do not assume cloud dependencies