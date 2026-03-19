# Prompt Template for Codex

Use this template when asking Codex to implement or modify something in this repo.

---

## Standard opening

Read `AGENTS.md` and the relevant files under `docs/` first.

Before making changes, align with:
- `docs/ARCHITECTURE.md`
- `docs/MVP.md`
- `docs/DECISIONS.md`
- `docs/DOMAIN_MODEL.md`
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
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

If local setup or run steps changed, update `README.md` briefly.

After the implementation, also update:
- `docs/PROJECT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/CHANGELOG_DEV.md`

Keep those updates concise, factual, and aligned with the verified current state.
Do not speculate.