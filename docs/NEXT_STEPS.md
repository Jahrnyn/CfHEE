# Next Steps

## Recommended next development step

Implement the first scoped retrieval vertical slice.

Why this is next:

- the project already stores documents, chunks, and Chroma vectors
- `Ask Copilot` is still an explicit placeholder
- retrieval is the next core MVP capability after ingestion and listing

## Suggested narrow scope

1. Add a backend retrieval service that queries Chroma with explicit scope filters.
2. Add a minimal `POST /ask` or `POST /retrieval/query` endpoint.
3. Return matching chunks with source metadata only at first.
4. Wire the `Ask Copilot` page to submit a scoped query and render retrieved chunks.

## Keep out of scope for that step

- free-form answer synthesis
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once scoped retrieval works, add the first source-grounded answer composer on top of retrieved chunks.
