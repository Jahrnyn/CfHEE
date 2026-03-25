# Next Steps

## Recommended next development step

Tighten citation presentation and expand manual verification for the Ask Copilot flow.

Why this is next:

- the project now has a real local Ollama-backed provider behind the answer abstraction
- retrieval and answer traceability are now persisted through `query_logs`
- simple deterministic evaluation signals are now persisted through `query_logs`
- answer prompting is now explicit and conservative, so the next quality gap is response presentation and broader manual verification
- the next quality gap is citation clarity and UI inspection, not backend prompt construction
- the current slice is functional but intentionally minimal

## Suggested narrow scope

1. Make citation display clearer in the Ask page without changing the scoped answer contract.
2. Expand manual verification coverage for grounded answers across evidence-present and no-evidence cases.
3. Preserve the current no-evidence behavior when retrieval is empty.
4. Keep the deterministic provider available as a fallback for local setup issues.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once answer formatting is steadier, improve manual verification coverage for the full Ask page flow.
