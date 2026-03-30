# Domain Model

## Hierarchy

The hard scope hierarchy is:

```text
Workspace
  -> Domain
    -> Project
      -> Client
        -> Module
```

Documents and chunks are stored under that hierarchy.

## Scope field classes

### Hard scope / retrieval partitioning fields

These fields define where knowledge lives and how retrieval is partitioned:

- `workspace`
- `domain`
- `project`
- `client`
- `module`

These fields are the active scope used for ingest validation, persistence, and scoped retrieval filters.

### Descriptive metadata fields

These fields describe the document but do not define the retrieval partition:

- `source_type`
- `language`
- `source_ref`
- document-level `metadata`

They are stored and returned with document and retrieval results, but they are not a substitute for hard scope.

## Minimum required on document ingest

- `workspace`
- `domain`
- `source_type`
- `title`
- `raw_text`

## Optional on document ingest

- `project`
- `client`
- `module`
- `language`
- `source_ref`
- `metadata`

## Field meanings and operational usage

### `workspace`

Meaning:
A stable top-level knowledge space.
In practice this is usually an organization, internal knowledge boundary, or another durable top-level partition.

Usage rule:
Do not use ad hoc labels such as temporary initiatives, sprint names, or one-off import buckets as `workspace`.

### `domain`

Meaning:
A broad technical, product, or business area within a workspace.

Usage rule:
Use a stable area name that can hold many related documents over time.
Do not use narrow ticket-level or document-level labels as `domain`.

### `project`

Meaning:
A concrete initiative, solution area, implementation stream, or bounded body of work inside a workspace and domain.

Usage rule:
Use `project` when documents belong to a specific implementation or program that should remain retrievable as a coherent subset.
Leave it empty when the material is domain-wide and not tied to one concrete initiative.

### `client`

Meaning:
A specific customer, tenant, or comparable external party within a project.

Usage rule:
Use `client` only when the distinction is operationally meaningful for retrieval isolation.
Do not force a fake client value for generic internal or shared knowledge.

### `module`

Meaning:
The narrowest functional, technical, or business subsystem that is still useful as a retrieval boundary.

Usage rule:
Use `module` for a real subsystem, feature area, integration surface, or bounded operational unit.
Do not use per-document labels, filenames, or issue identifiers as `module`.

### `source_type`

Meaning:
The kind of source material being ingested, such as `jira_ticket`, `wiki_page`, `meeting_note`, `code_snippet`, or `manual_note`.

Usage rule:
Choose a small stable vocabulary and reuse it consistently.
`source_type` is descriptive metadata only and must not be used as a replacement for missing hard scope.

### `language`

Meaning:
The language of the stored source text when it is useful to capture explicitly.

Usage rule:
Populate it when the document language is known or obvious.
For multilingual or mixed-content documents, use the dominant language if one is clear; otherwise leave it empty rather than guessing.
`language` is descriptive metadata only.

### `source_ref`

Meaning:
An external identifier or human-meaningful reference back to the source system or artifact.

Examples:
- ticket ID
- wiki page slug
- repository path
- document number
- URL-like source handle

Usage rule:
Use `source_ref` when it improves traceability.
It is not part of hard scope and should not be overloaded as a project, client, or module identifier.

### document-level `metadata`

Meaning:
Caller-provided descriptive document data preserved together with the stored document.

Current implementation:

- persisted as document-level JSON / JSONB
- preserved as provided by the caller
- returned on current document inspection surfaces

Usage rule:

- treat `metadata` as descriptive document-associated data, not as hard scope
- do not use `metadata` as a substitute for `workspace`, `domain`, `project`, `client`, or `module`
- do not assume `metadata` currently affects retrieval, ranking, filtering, or scope isolation
- `metadata` is preserved for traceability and external-consumer use, not yet as a first-class retrieval/query surface

## Deterministic ingest policy

Use the smallest stable scope that matches how the document should later be found.

Operational policy:

- `workspace` should be a durable top-level knowledge space, not an ad hoc import label.
- `domain` should be a broad technical or business area inside that workspace.
- `project` should identify a concrete initiative or solution area only when that distinction matters for retrieval.
- `client` should identify a real customer or tenant only when that distinction matters for retrieval.
- `module` should identify the narrowest meaningful subsystem, not an individual document topic.
- `source_type`, `language`, and `source_ref` should be recorded as descriptive metadata and must not be treated as equivalent to hard scope.
- document-level `metadata` may be recorded as preserved descriptive JSON but must not be treated as equivalent to hard scope.
- if a narrower hard-scope field is not truly known or not operationally useful, leave it empty instead of inventing a value
- reuse existing scope values where possible to avoid fragmentation caused by near-duplicate labels
- conservative normalization currently trims and collapses whitespace and matches existing scope rows case-insensitively; this reduces accidental duplicates but does not replace deliberate scope selection

## Retrieval stance in the current implementation

Current verified behavior:

- retrieval is explicit-scope-driven
- retrieval is scoped by default
- the system does not silently widen across workspace, domain, project, client, or module boundaries
- CfHEE executes retrieval within an explicit scope
- CfHEE does not perform query-scope inference
- the strongest current behavior is for exact scopes or intentionally chosen scopes at query time
- user-provided top-level scope remains authoritative

Current limitation:

Partial-scope, uncertain-scope, and wider-scope query handling is not a solved capability in the current slice.
If ingest scope and query scope do not align, relevant knowledge may be missed rather than silently found through wider search.

## Scope-resolution boundary

Scope determination is the responsibility of the caller or an external orchestration layer.
CfHEE is a scoped execution engine, not a discovery engine.

Operational implication:

- if a higher-level app wants to handle partial-scope questions, it must decide how to choose or propose scope outside CfHEE
- if a higher-level app wants to handle cross-scope questions, that orchestration must happen outside CfHEE
- future helper surfaces may support external scope planning, but that would not make CfHEE itself a discovery engine

## Future direction

Future work may add:

- explicit query-scope resolution
- explicit wider-scope retrieval options
- higher-level external consumers that orchestrate multiple scoped retrieval calls

Those are future design areas.
They are not part of the current retrieval behavior and should not be assumed by users or downstream systems today.

## Rules

- User-provided top-level scope is authoritative.
- Model-generated tags are advisory only.
- Enrichment must not override hard scope.
- Cross-scope retrieval must be explicit, never silent.
