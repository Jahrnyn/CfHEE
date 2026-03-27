# Prompt Template for Codex
Use this template when asking Codex to implement or modify something in this repo.

---
## Standard opening
Read `AGENTS.md` and review the documentation index first:
- `docs/DOCS_INDEX.md`
Then read all relevant documents under `docs/` based on that index.

Before making changes, align with:
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/DOMAIN_MODEL.md`
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/API_V1.md` if the task touches public API behavior or API freeze boundaries
- `docs/PORTABLE_RUNTIME.md` if the task touches portable runtime design
- `docs/RUNTIME_OPERATIONS.md` if the task touches runtime usage or runtime-data ownership
- `docs/PROMPTING_GUIDE.md`
If the task touches recent work, also read:
- `docs/CHANGELOG_DEV.md`
---
## Task statement
Implement the following narrow vertical slice:
[DESCRIBE THE TASK HERE]
---
## Requirements
- keep the implementation small and practical
- do not refactor unrelated parts
- avoid speculative abstractions
- keep business logic readable and easy to debug
- preserve existing working behavior unless a change is required
- stay aligned with the documented architecture and current verified project state
- do not claim something is implemented unless it is actually implemented in code
- do not claim runtime verification unless it was actually verified
- preserve the module boundary: do not turn CfHEE into an orchestration or workflow engine
---
## Explicit in-scope
- [LIST WHAT IS IN SCOPE]
## Explicit out-of-scope
- [LIST WHAT MUST NOT BE DONE]
---
## Implementation guidance
- [OPTIONAL GUIDANCE]
- prefer minimal diffs
- prefer thin vertical slices
- keep local-first behavior by default
- preserve scope isolation rules
- prefer stable API-oriented design for reusable capabilities
- do not expand module responsibility
---
## Deliverables
1. [DELIVERABLE 1]
2. [DELIVERABLE 2]
3. [DELIVERABLE 3]
---
## Verification
Please verify what you can locally and clearly distinguish between:
- implemented in code
- verified by running locally
- not verified due to environment limits
Do not overclaim verification.
---
## Documentation update rules (MANDATORY)
If local setup or run steps changed, update `README.md` briefly.
Update ALWAYS:
- `docs/PROJECT_STATE.md`
- `docs/CHANGELOG_DEV.md`
Update CONDITIONALLY (if affected):
- `docs/NEXT_STEPS.md`
- `docs/API_V1.md` → if API contract or behavior changed
- `docs/PORTABLE_RUNTIME.md` → if runtime model changed
- `docs/RUNTIME_OPERATIONS.md` → if runtime usage changed
- `docs/ARCHITECTURE.md` → if architectural intent changed
- `docs/DOCS_INDEX.md` 
- `docs/BACKUP_AND_RESTORE` 
(or any other .md documentation inside /docs if needed)
- `./README.md` → if usage or positioning changed
Rules for updates:
reflect only what is implemented or verified
do not speculate
keep updates concise and factual
maintain consistency with existing terminology

---
Keep those updates concise, factual, and aligned with the verified current state.
Do not speculate.
