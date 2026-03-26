# Next Steps

## Recommended next development step

Run a few more real-document retrieval checks before considering any larger search changes.

Why this is next:

- the project now has a real local Ollama-backed provider behind the answer abstraction
- retrieval and answer traceability are now persisted through `query_logs`
- simple deterministic evaluation signals are now persisted through `query_logs`
- grounded answer language is now more explicitly tied to the query language
- a small lexical reranking step now sits on top of vector candidates, so the next gap is measuring where it helps and where it still misses
- the current slice is functional but intentionally minimal

## Suggested narrow scope

1. Run a few real identifier and table/template-name queries against the Hungarian Business Central material.
2. Inspect original vs. reranked chunk order in `GET /query-logs` to see where lexical boosting helped.
3. Keep the current no-evidence behavior when retrieval is empty.
4. Keep the deterministic provider available as a fallback for local setup issues.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once answer formatting is steadier, improve manual verification coverage for the full Ask page flow.
