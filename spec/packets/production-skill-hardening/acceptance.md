---
id: PSH-ACCEPTANCE
title: Strict Spec Agent Skill Behavior Acceptance
status: approved
related_spec: spec.md
created: 2026-07-17
---

# Strict Spec Agent Skill Behavior Acceptance

## Acceptance scope

Validate discovery, requirements friction, product-only outputs, handoff, drift, and history.

## Behavior acceptance

- AC-PSH-001: A vague feature request triggers request flow and reaches no file writing
  before blocking questions and product approval. Covers PSH-001 through PSH-004.
- AC-PSH-002: Completion leaves `spec.md` and `acceptance.md`, both approved and free of
  implementation content. Covers PSH-005 and PSH-007.
- AC-PSH-003: The final response contains the required Code Agent prompt with the real
  specification path and no planning advice. Covers PSH-006.
- AC-PSH-004: Drift observation changes no spec, code, test, or backlink and may replace
  only derived traceability data. Covers PSH-008 and PSH-009.
- AC-PSH-005: Evolution events contain product decisions and exclude engineering
  execution fields. Covers PSH-010.
- AC-PSH-006: A later product change reuses the packet and repeats both approvals.
  Covers PSH-011.
- AC-PSH-007: Validation rejects a plan template, plan artifact, implementation prompt,
  repair workflow, or engineering event field. Covers PSH-012.

## Alternative and failure acceptance

Blocking uncertainty, ambiguous approval, or a semantic conflict stops progression and
names the next product decision required.

## Edge cases

Small changes still pass the gates; the presented product decision may be brief.

## Exception policy

No request urgency or user phrase such as “just implement it” bypasses approval gates.

## Permissions and privacy acceptance

Only explicit product-authority approval changes normative status or meaning.

## Acceptance dependencies

Compatible agents honor `AGENTS.md` and Agent Skills discovery conventions.

## Unresolved acceptance decisions

None.
