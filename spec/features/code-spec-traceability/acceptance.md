---
id: TRACE-ACCEPTANCE
title: Code and Specification Traceability Acceptance
status: approved
related_spec: spec.md
created: 2026-07-19
---

# Code and Specification Traceability Acceptance

## Acceptance scope

Validate the mandatory Code Agent handoff, backlink baseline, drift categories,
read-only behavior, CLI access, and product-authority boundary.

## Behavior acceptance

- AC-TRACE-001: An approved handoff names both feature specifications and requires
  backlinks in relevant production code and tests. Covers TRACE-001 and TRACE-002.
- AC-TRACE-002: Code Agent completion instructions require baseline refresh followed
  by clean validation. Covers TRACE-003.
- AC-TRACE-003: A refreshed traceability index contains behavior IDs, repository-
  relative backlink locations, and deterministic linked-file fingerprints while the
  normative specifications contain no code paths. Covers TRACE-004 and TRACE-005.
- AC-TRACE-004: Approved missing, unknown, unbaselined, moved, and changed-code evidence
  produces distinct findings. Covers TRACE-006.
- AC-TRACE-005: A draft rule without a backlink does not fail validation. Covers
  TRACE-007.
- AC-TRACE-006: Validation leaves specifications, code, tests, backlinks, history, and
  traceability byte-for-byte unchanged. Covers TRACE-008.
- AC-TRACE-007: Refresh replaces the derived baseline only after the caller accepts the
  current approved implementation evidence. Covers TRACE-009 and TRACE-010.
- AC-TRACE-008: Semantic disagreement is reported for human authority and is not
  automatically repaired. Covers TRACE-011.
- AC-TRACE-009: The installed CLI exposes validation and traceability-refresh commands,
  and the installed checker remains directly runnable. Covers TRACE-012.

## Alternative and failure acceptance

Validation returns failure for structural findings and explains the behavior ID,
category, and evidence location. Missing installed assets produce actionable guidance
without modifying the repository.

## Edge cases

Multiple backlinks may implement one behavior. An unchanged file remains current.
Moving a backlink is reported until authorized refresh. Legacy traceability without
fingerprints remains readable and is upgraded on refresh.

## Exception policy

No urgency, implementation success, or passing engineering test permits completion
with missing backlinks or failed drift validation.

## Permissions and privacy acceptance

Validation and traceability refresh operate only on local repository evidence and
store no source contents or secrets.

## Acceptance dependencies

The feature packet is approved, relevant code and tests support comment backlinks, and
the initialized Spec Agent assets are present.

## Unresolved acceptance decisions

None.
