# Next Steps

## Recommended next development step

Run the small retrieval regression pack after future retrieval changes, then add only the next highest-signal failing case if needed.

Why this is next:

- the project now has a real local Ollama-backed provider behind the answer abstraction
- retrieval and answer traceability are now persisted through `query_logs`
- simple deterministic evaluation signals are now persisted through `query_logs`
- grounded answer language is now more explicitly tied to the query language
- a small lexical reranking step now sits on top of vector candidates, so the next gap is measuring where it helps and where it still misses
- the current slice is functional but intentionally minimal
- the repo now has a tiny regression guardrail for a few real developer-document queries, but coverage is still intentionally narrow

## Suggested narrow scope

1. Run `apps/backend/scripts/retrieval_regression_check.py` after retrieval changes.
2. Inspect original vs. reranked chunk order in `GET /query-logs` when a regression case fails or looks noisy.
3. Add only a few more high-signal cases if a real failure mode is observed again.
4. Keep the current no-evidence behavior when retrieval is empty.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration
