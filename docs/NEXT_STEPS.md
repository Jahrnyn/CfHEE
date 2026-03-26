# Next Steps

## Recommended next development step

Use the improved manual-ingest flow with reused scope values on real developer material, then add only the next smallest ingest or retrieval painkiller that shows up in actual use.

Why this is next:

- the project now has a real local Ollama-backed provider behind the answer abstraction
- retrieval and answer traceability are now persisted through `query_logs`
- simple deterministic evaluation signals are now persisted through `query_logs`
- grounded answer language is now more explicitly tied to the query language
- a small lexical reranking step now sits on top of vector candidates, and a tiny retrieval regression guardrail already exists for rechecking that behavior
- manual ingest now reuses stored scope values and normalizes trivial casing/spacing variants, which removes one immediate usability risk before heavier ingest work
- the current slice is functional but intentionally minimal
- real scope management UI still does not exist
- this is still not file-import work and not connector work

## Suggested narrow scope

1. Use the manual ingest form against more real developer notes and confirm the existing scope suggestions stay convenient without creating noisy variants.
2. Run `apps/backend/scripts/retrieval_regression_check.py` after retrieval changes.
3. Inspect original vs. reranked chunk order in `GET /query-logs` when a regression case fails or looks noisy.
4. Keep the next slice narrow: no bulk file import, no connectors, no scope-management subsystem unless a concrete need appears.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- bulk file import or parser work
- agent workflows
- external connectors
- complex ranking or orchestration
- full scope-management UI
