# Next Steps

## Recommended next development step

Extend the new `/api/v1` shell beyond the initial ingest helpers into a small but usable external integration surface for CfHEE so that external scripts, services, and applications can use the module without modifying the core codebase.

Why this is next:

- the core scoped knowledge module is already functional in a narrow local form
- manual ingest, chunk persistence, scoped retrieval, grounded answer access, and query logging already exist
- the built-in frontend is useful as a developer workbench, but it should not become the main expansion surface
- the newly clarified architectural direction treats higher-level workflows and automation as external consumers
- the first public versioned routing shell now includes basic system, scope-values, document-ingest, retrieval, document-inspection, and query-log list endpoints, so the next leverage comes from extending that shell carefully rather than adding more internal UI or copilot-style behavior

## Suggested narrow scope

1. Extend the first stable integration-oriented API surface from the existing `/api/v1` shell:
   - grounded answer access as a convenience endpoint
   - query-log detail where useful
2. Tighten the new public ingest-retrieval-inspection contract where useful:
   - keep the nested scope shape consistent across later `/api/v1` endpoints
   - decide when metadata persistence should become real instead of request-only acceptance
   - keep optional retrieval diagnostics developer-oriented and explicit
   - keep document-list scope requirements conservative and explicit
3. Make the API contract clearer for external callers:
   - request and response shapes
   - explicit scope expectations
   - validation behavior
   - empty-result behavior
   - keeping optional fields omitted unless explicitly requested
   - keeping translation-layer validation failures at the request boundary
   - keeping query-log inspection explicitly developer-oriented and conservative
4. Keep the current frontend working as a lightweight local workbench, but do not expand it into a richer product layer.
5. Document the module boundary clearly in README and docs so future development does not drift back into an app-centric model.

## Keep out of scope for that step

- workflow orchestration inside CfHEE
- agent loops inside CfHEE
- proposal-generation logic inside CfHEE
- pentest automation logic inside CfHEE
- broad connector ecosystems
- complex file-import subsystems unless an immediate integration need forces it
- cross-environment packaging work before the API boundary is stable

## After that step

Once the API boundary is stable and the module feels reusable, the next long-term infrastructure target is deployment portability:

- containerize the system
- reduce dependence on the current Windows-heavy localhost development setup
- make the module easier to run on Linux and other environments
- prepare for production-buildable packaging without changing the core architectural boundary
