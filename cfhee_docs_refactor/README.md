# CfHEE

CfHEE is a local-first, scoped knowledge storage and retrieval module.

It is designed to ingest heterogeneous technical and enterprise material, preserve strict scope isolation, persist raw inputs and derived chunks, and provide fast, reliable scoped retrieval over stored knowledge.

CfHEE is not defined as an end-user copilot application, workflow engine, or orchestration platform. It is a reusable backend module that higher-level workflows, agents, scripts, and applications can build on top of.

The built-in answer functionality is a thin convenience consumer of retrieval. It exists to support local querying, validation, and developer ergonomics. It is not the primary system responsibility.

## Core responsibilities

- scoped ingest of raw source material
- persistent storage of source data, metadata, and chunks
- strict hierarchical scope isolation
- scoped retrieval over stored knowledge
- source traceability and inspectable query history
- optional built-in grounded answer access as a convenience layer

## What CfHEE is not

CfHEE is not:

- a general-purpose copilot product
- an agent framework
- a workflow engine
- a business automation platform
- a domain-specific execution runtime

Those capabilities should be implemented in separate systems that communicate with CfHEE through stable APIs.

## System shape

```text
External workflows / tools / apps
            ↓
        CfHEE API
            ↓
  Scoped knowledge core
  - ingest
  - storage
  - chunking
  - retrieval
  - traceability
            ↓
Persistence
- Postgres
- Vector index
- Raw storage
```

## Built-in UI role

The current frontend should be understood as a lightweight developer workbench for:

- manual ingest
- document browsing
- chunk inspection
- scoped query testing
- grounded-answer validation

It is useful, but it is not the architectural center of the system.

## Near-term direction

The next architectural step is to expose CfHEE as a cleaner API-first module so that other scripts, services, and applications can use it without modifying the core codebase.

## Longer-term direction

After the module boundary and API surface are stable, the system should become easier to run outside the current Windows-heavy localhost development setup. The intended long-term direction is a production-buildable, containerized deployment shape that can run consistently on Linux and other environments.
