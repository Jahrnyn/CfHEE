# Next Steps

## Recommended next development step

Tighten Ollama prompt/citation behavior and make the grounded answer output more consistent.

Why this is next:

- the project now has a real local Ollama-backed provider behind the answer abstraction
- the next quality gap is answer consistency and citation presentation, not provider plumbing
- the current slice is functional but intentionally minimal

## Suggested narrow scope

1. Tighten the Ollama prompt so answers stay short and citation-friendly.
2. Improve answer response formatting while keeping retrieval as the only context source.
3. Preserve the current no-evidence behavior when retrieval is empty.
4. Keep the deterministic provider available as a fallback for local setup issues.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once answer formatting is steadier, improve manual verification coverage for the full Ask page flow.
