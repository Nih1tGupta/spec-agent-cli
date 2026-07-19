# Strict Spec Agent

Read root `SPEC.md`, then load one discoverable skill from `.agents/skills/`.
Feature packets contain product-only `spec.md` and `acceptance.md` files under
`spec/features/<feature-slug>/`.

| Situation | Load skill |
|---|---|
| Feature, fix, refactor, or behavior request | `spec-request-flow` |
| Possible spec/code/backlink disagreement | `spec-drift-sync` |
| Approved product change, rationale, or timeline | `spec-evolution` |

`spec-request-flow` ends after explicit approval and the Code Agent handoff. It
never writes implementation plans, code, tests, or engineering commands.

Code backlinks use `spec: BEHAVIOR-ID`. `spec-drift-sync` observes them and may
regenerate only non-normative `spec/traceability.json`; it never repairs code or
specifications. Product decision history lives in `spec/evolution/events.jsonl`.
