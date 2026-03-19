# Next Steps

## Recommended next development step

Implement the first source-grounded answer slice on top of retrieved chunks.

Why this is next:

- the project now supports scoped retrieval from the `Ask Copilot` page
- retrieval behavior is now more explicit and inspectable for downstream answer use
- the next missing MVP capability is turning retrieved context into a source-grounded response
- retrieval-only results are already traceable to chunks and documents

## Suggested narrow scope

1. Add a minimal answer endpoint that accepts query text plus explicit scope.
2. Reuse the current retrieval results as the only answer context.
3. Return a short answer together with cited chunks and active scope.
4. Keep the first answer flow simple and inspectable.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once the first answer flow works, tighten confidence/citation formatting and retrieval quality.
