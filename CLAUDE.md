# Strict Spec Agent

Read root `SPEC.md`, then load one discoverable skill from `.claude/skills/`.
Feature packets contain product-only `spec.md` and `acceptance.md` files under
`spec/packets/<feature-slug>/`.

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

## Code Agent contract

When implementing an approved handoff, the Code Agent MUST:

1. Read the feature `spec.md` and `acceptance.md`.
2. Add `spec: BEHAVIOR-ID` backlinks to relevant production code and tests for every
   implemented rule.
3. Run `spec-agent traceability-sync --repo .` after the approved implementation.
4. Run `spec-agent validate --repo .` and resolve or report every finding.

The Code Agent MUST NOT claim completion unless validation reports `CLEAN`. It MUST NOT
edit product specifications merely to match code; changed product intent returns to
`spec-request-flow` for clarification and approval.
