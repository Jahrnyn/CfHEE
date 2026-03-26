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

Keep the API surface stable and shift the next development focus away from new public endpoint work.

Why this is next:

- the core scoped knowledge module is already functional in a narrow local form
- manual ingest, chunk persistence, scoped retrieval, grounded answer access, and query logging already exist
- the built-in frontend is useful as a developer workbench, but it should not become the main expansion surface
- the newly clarified architectural direction treats higher-level workflows and automation as external consumers
- the first public versioned routing shell now exists and is frozen for contract stabilization
- the next leverage comes from using that stable surface, not expanding it further right now

## Suggested narrow scope

1. Improve the frontend against the frozen API surface.
2. Containerize and harden runtime setup without changing the public contract.
3. Build or validate first external consumer integrations against the frozen API.
4. Keep workflow-specific logic outside CfHEE.

## Keep out of scope for that step

- workflow orchestration inside CfHEE
- agent loops inside CfHEE
- proposal-generation logic inside CfHEE
- pentest automation logic inside CfHEE
- expanding the `/api/v1` API surface during the freeze
- broad connector ecosystems
- complex file-import subsystems unless an immediate integration need forces it
- cross-environment packaging work before the API boundary is stable

## After that step

Once the frozen API surface has been exercised by real consumers, the next long-term infrastructure target is deployment portability:

- containerize the system
- reduce dependence on the current Windows-heavy localhost development setup
- make the module easier to run on Linux and other environments
- prepare for production-buildable packaging without changing the core architectural boundary
