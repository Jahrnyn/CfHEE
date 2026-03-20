# Next Steps

## Recommended next development step

Add a real local LLM-backed answer provider behind the current answer abstraction.

Why this is next:

- the project now supports grounded answers backed by retrieved chunks
- the current provider is deterministic and local, but not yet Ollama-backed
- the main remaining gap in the answer layer is real local model generation behind the same grounded flow

## Suggested narrow scope

1. Add an Ollama-backed provider that implements the existing answer-provider interface.
2. Keep retrieval as the only context source.
3. Preserve the current no-evidence behavior when retrieval is empty.
4. Keep the deterministic provider available as a local fallback until Ollama setup is reliable.

## Keep out of scope for that step

- broad answer orchestration beyond a small cited response
- agent workflows
- external connectors
- complex ranking or orchestration

## After that

Once the local LLM provider works, tighten citation formatting and answer prompting.
