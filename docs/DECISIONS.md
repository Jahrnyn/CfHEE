# Architectural Decisions

## ADR-001
Backend is Python + FastAPI.
Reason: better ecosystem fit for AI, RAG, and service-style backend workflows.

## ADR-002
Frontend is Angular.
Reason: existing familiarity and faster iteration.

## ADR-003
Postgres is the primary relational store.
Reason: robust metadata persistence and future growth.

## ADR-004
Chroma is the first vector store, behind an abstraction layer.
Reason: simple local-first MVP.

## ADR-005
Top-level scope metadata is user-defined.
Reason: reduce cross-contamination risk.

## ADR-006
Retrieval is scoped by default.
Reason: prevent accidental mixing across companies, clients, and projects.

## ADR-007
LLM provider must remain replaceable.
Reason: local-first now, stronger model routing later.

## ADR-008
CfHEE is defined as a scoped knowledge infrastructure module for storage, retrieval, and retrieval-derived context building, not as an end-user copilot application.
Reason: the architectural core of the system is ingest, storage, scope isolation, retrieval, retrieval-derived context building, and traceability. Higher-level workflows, automation, and agents should be implemented as external consumers.

## ADR-009
The built-in answer functionality is a convenience consumer, not the primary system responsibility.
Reason: grounded answering is useful for local querying, validation, and developer ergonomics, but it should not drive the shape of the core module.

## ADR-010
External integrations should prefer stable API access over direct code coupling.
Reason: the module should remain reusable by other tools, scripts, and services without pulling external workflow logic into the core codebase.

## ADR-011
Long-term deployment direction is containerized, cross-environment runtime after API stabilization.
Reason: the current Windows-heavy localhost workflow is acceptable for development, but the module should eventually become easier to run consistently on Linux and other systems.
