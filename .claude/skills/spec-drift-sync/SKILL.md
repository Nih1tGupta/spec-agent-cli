---
name: spec-drift-sync
description: Use when accepted specifications may disagree with implementations after refactors, merges, hotfixes, or code-only changes, or when backlinks, traceability, tests, or verification evidence may be missing or stale.
---

# Spec Drift Sync

Act as a read-only observer of specification/code disagreement. Product specs
remain normative; code, tests, Git history, and passing verification are evidence.

<HARD-GATE>
Do not edit specifications, code, tests, code backlinks, or verification state. Do not
run an implementation or repair workflow. The only permitted write is regenerating the
non-normative derived traceability index from backlinks that already exist in code.
</HARD-GATE>

## Detection

1. Read root `SPEC.md`, both files in the affected feature packet, current code and
   public behavior, existing `spec: BEHAVIOR-ID` backlinks, relevant Git changes, and
   related product-decision history.
2. Run `spec-agent validate --repo REPOSITORY`; if the CLI is unavailable, run
   `scripts/check.py check --repo REPOSITORY`. Use `--spec-root SPEC_SOURCE` only for
   an intentionally scoped observation.
3. Inspect meaning manually. A clean structural report proves identity consistency,
   not semantic compliance.

## Traceability refresh

After an approved implementation or explicit reconciliation, run `spec-agent
traceability-sync --repo REPOSITORY`; if the CLI is unavailable, run `scripts/check.py
sync --repo REPOSITORY --output spec/traceability.json`. It records behavior IDs,
backlink locations, and linked-file fingerprints in the derived traceability baseline.

Do not refresh traceability to silence unexplained drift. Validate first, understand
existing findings, and refresh only when product intent or implementation authority is
explicit. Never copy traceability into `spec.md` or `acceptance.md` or treat it as
product authority.

## Evidence report

For every finding report:

- behavior ID and drift category;
- normative product evidence with specification path and rule;
- implementation evidence with code, interface, test, or Git location;
- structural identity problem or semantic conflict;
- observable impact and the authority decision required.

Structural findings include `phantom`, `unlinked`, `unbaselined`, `stale-trace`,
`code-changed`, legacy `dead-ref`, `silent-implementation`, and `stale-verification`.
Semantic conflicts include code contradicting accepted behavior, obsolete or ambiguous
product rules, and behavior without product authority.

## Authority handoff

Ask one product decision at a time and present viable outcomes with impact. Never
silently promote observed code to intended behavior.

- If intended product behavior changes, hand the decision to `spec-request-flow` for
  clarification, both spec files, and approval.
- If the approved product behavior remains correct, hand the evidence to a separate
  Code Agent to plan engineering changes.
- Use `spec-evolution` only to preserve an approved product authority decision.

Stop after the evidence report and handoff. Do not apply the selected repair, add
backlinks, execute tests, weaken the checker, or mark verification current.
