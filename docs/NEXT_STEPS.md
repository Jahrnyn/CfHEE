# Next Steps

## API v1 Code Freeze (Contract Stabilization)

CfHEE external API v1 is now in **API v1 Code Freeze (Contract Stabilization)**.

Frozen now:

- implemented `/api/v1/...` endpoints
- request and response shapes
- shared scope model and scope rules
- retrieval and document contract behavior

Allowed after freeze:

- bugfixes
- internal refactoring without contract change
- non-breaking additions only if strictly necessary

Not allowed after freeze:

- breaking API changes
- silent contract changes
- scope model changes
- changing response semantics

Not frozen:

- frontend
- internal implementation
- performance improvements
- containerization and runtime setup
- developer tooling

## Recommended next development step

Keep the API surface stable and make scope taxonomy plus metadata policy the next narrow conceptual focus.

Why this is next:

- the core scoped knowledge module is already functional in a narrow local form
- manual ingest, scope-value suggestions, conservative normalization, chunk persistence, scoped retrieval, grounded answer access, query logging, and a small retrieval regression pack already exist
- the built-in frontend is useful as a developer workbench, but it should not become the main expansion surface
- the newly clarified architectural direction treats higher-level workflows and automation as external consumers
- the first public versioned routing shell now exists and is frozen for contract stabilization
- future real-world ingest and retrieval use now depends on deterministic scope semantics more than on broader feature expansion
- the next leverage comes from making ingest and query scope usage reliable, not from expanding the public surface right now

## Suggested narrow scope

1. Keep the documented scope taxonomy and ingest metadata policy explicit and consistent across docs and future implementation work.
2. Exercise current scoped retrieval against realistic exact-scope queries and use the regression guardrail when retrieval behavior changes.
3. Reuse the small semantic verification helper when you need an honest fresh-corpus check against the current `bge-m3` lineage instead of relying on older vector data.
4. When checking retrieval after the semantic embedding switch, make sure the checked corpus is actually indexed in the active semantic Chroma collection rather than an older hash-vector collection.
5. Keep the scope-resolution boundary explicit: CfHEE executes retrieval within caller-provided scope and does not infer missing scope from user questions.
6. Build or validate consumers against the frozen API only after the scope semantics they depend on are deterministic.

External-consumer note:

- if a higher-level app wants to answer partial-scope or cross-scope questions, the planning and orchestration for that must happen outside CfHEE
- future helper surfaces may support external scope planning, but CfHEE itself should remain a scoped execution engine rather than a discovery engine

Runtime portability note:

- the first narrow portability slice is now in place through configurable frontend API base URL and configurable backend CORS origins
- the API surface now also includes a narrow provider-free context-build endpoint on top of existing retrieval behavior
- the portable-instance design baseline is now documented in `docs/PORTABLE_RUNTIME.md`
- the first containerized portable runtime slice now exists for frontend, backend, and Postgres
- runtime start/stop/log/update guidance is now documented in `docs/RUNTIME_OPERATIONS.md`
- backup and restore scope and safety rules are documented in `docs/BACKUP_AND_RESTORE.md`
- future app-managed operations scope is now documented in `docs/OPERATIONS_SURFACE.md`
- a first backend-owned read-only ops summary surface now exists
- a first frontend read-only Operations/Admin page now exists
- first conservative stopped-runtime backup and restore helpers now exist
- hot backup, stronger validation, and production hardening are still not implemented

## Keep out of scope for that step

- workflow orchestration inside CfHEE
- agent loops inside CfHEE
- proposal-generation logic inside CfHEE
- pentest automation logic inside CfHEE
- expanding the `/api/v1` API surface during the freeze
- broad connector ecosystems
- complex file-import subsystems unless an immediate integration need forces it
- automatic cross-scope retrieval or silent retrieval widening
- runtime-topology changes before the current portable instance workflow has been exercised

## After that step

Once scope semantics and real consumer usage are better exercised, the next long-term infrastructure target is deployment portability:

- keep the portable-instance model fixed before implementation drift starts
- harden and exercise the first containerized runtime
- separate packaged runtime from persistent instance data
- tighten validation and operational safety around the new conservative backup and restore workflow
- refine the new read-only Operations/Admin view before attempting any in-app maintenance triggers
- reduce dependence on the current Windows-heavy localhost development setup
- make the module easier to run on Linux and other environments
- prepare for production-buildable packaging without changing the core architectural boundary
