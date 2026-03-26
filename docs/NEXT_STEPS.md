# Next Steps

## Recommended next development step

Run a few targeted manual retrieval diagnostics checks before attempting broader retrieval changes.

Why this is next:

- the project now has a real local Ollama-backed provider behind the answer abstraction
- retrieval and answer traceability are now persisted through `query_logs`
- simple deterministic evaluation signals are now persisted through `query_logs`
- grounded answer language is now more explicitly tied to the query language
- richer retrieval diagnostics are now available in `query_logs`, so the next gap is targeted manual inspection rather than immediate retrieval redesign
- the current slice is functional but intentionally minimal

## Suggested narrow scope

1. Run a few scoped queries against the Hungarian Business Central material and inspect `candidate_count`, `top_k_limit_hit`, and returned distances.
2. Compare retrieval-only output with grounded answers for one Hungarian and one English query.
3. Keep the current no-evidence behavior when retrieval is empty.
4. Keep the deterministic provider available as a fallback for local setup issues.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once answer formatting is steadier, improve manual verification coverage for the full Ask page flow.
