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

## ADR-012
The hard scope model is limited to `workspace`, `domain`, `project`, `client`, and `module`; `source_type`, `language`, and `source_ref` are descriptive metadata only.
Reason: retrieval partitioning must stay deterministic and must not drift into mixed use of source descriptors as pseudo-scope.

## ADR-013
Ingest should prefer the smallest stable hard scope that matches how knowledge is expected to be retrieved later, while leaving uncertain narrower fields empty instead of inventing values.
Reason: deterministic ingest reduces fragmentation and makes strict scoped retrieval operationally usable.

## ADR-014
Current retrieval remains explicit-scope-driven and must not silently widen for partial-scope or uncertain-scope queries.
Reason: strict scoped isolation is a deliberate safety property; wider-scope resolution is a future design area that must be made explicit rather than implicit.

## ADR-015
CfHEE does not perform query-scope inference. Scope determination is the responsibility of the caller or an external orchestration layer. CfHEE is a scoped execution engine, not a discovery engine.
Reason: keeping scope planning outside the module preserves deterministic scoped execution, keeps the module boundary clean, and avoids turning CfHEE into a workflow or orchestration system.
