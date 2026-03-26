# TASKS

## Now
- Validate rescored retrieval on real developer documentation
  - Goal: confirm chunk-level precision is acceptable for MVP
  - Status: mostly validated
  - Notes: exact identifiers and explicit technical terms now rank better

## Next
- Add a small repeatable retrieval check set
  - Goal: avoid future regressions in ranking quality
  - Status: planned
  - Notes: use a few real BC/AL document queries as a lightweight regression pack

## Later
- Improve retrieval quality further if justified
  - Goal: reduce remaining cross-document noise in top results
  - Status: deferred
  - Notes: only if observed on real usage

- Revisit embedding quality
  - Goal: improve base semantic separation
  - Status: deferred
  - Notes: not necessary for current MVP

## Frozen
- Hybrid retrieval
- Full BM25 integration
- Second-model reranking
- Retrieval UI dashboards