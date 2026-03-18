# Architectural Decisions

## ADR-001
Backend is Python + FastAPI.
Reason: better ecosystem fit for AI/RAG workflows.

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
Reason: prevent accidental mixing across companies/clients/projects.

## ADR-007
LLM provider must remain replaceable.
Reason: local-first now, stronger model routing later.