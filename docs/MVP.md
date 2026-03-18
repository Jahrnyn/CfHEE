# MVP

## Goal
Deliver the smallest useful version of the system:
- ingest document with explicit scope
- store in Postgres
- list documents
- prepare for chunking/indexing
- later add scoped retrieval

## In scope
- Angular shell
- FastAPI backend
- Postgres schema
- manual ingest form
- basic document list
- workspace/domain/project/client/module metadata
- raw text storage

## Out of scope
- autonomous workflows
- connectors
- cloud fallback
- OCR
- advanced auth
- production deployment