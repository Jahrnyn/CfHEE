# MVP Tasks

## Phase 1 - Foundation
- [ ] Initialize repo structure
- [ ] Create Angular frontend app
- [ ] Create FastAPI backend app
- [ ] Add Postgres via docker compose
- [ ] Create initial DB schema
- [ ] Add AGENTS.md
- [ ] Add architecture docs

## Phase 2 - Ingestion vertical slice
- [ ] Build manual ingest form
- [ ] Create POST /documents endpoint
- [ ] Persist documents with scope metadata
- [ ] Build documents list endpoint
- [ ] Build documents list page

## Phase 3 - Retrieval foundation
- [ ] Add chunking service
- [ ] Add embedding service abstraction
- [ ] Add vector store abstraction
- [ ] Add Chroma adapter
- [ ] Index chunks on ingest

## Phase 4 - Query
- [ ] Build scoped search endpoint
- [ ] Build Ask Copilot page
- [ ] Return source-grounded answers