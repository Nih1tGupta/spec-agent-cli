---
id: TRACE
title: Code and Specification Traceability
status: approved
created: 2026-07-19
---

# Code and Specification Traceability

Companion acceptance specification: `acceptance.md`.

## Problem and desired outcome

Approved specifications can become stale when implementation changes are no longer
connected to their product rules. Every implemented behavior needs durable identity so
future agents can detect structural drift and route semantic disagreements for review.

## Users and actors

- Product authority approves intended behavior and specification changes.
- Spec Agent creates product-only rules with stable behavior IDs.
- Code Agent implements approved behavior and maintains implementation evidence.
- Future agents and reviewers inspect drift without silently changing product truth.

## Scope and non-goals

This feature owns the Code Agent traceability contract, derived backlink baseline,
read-only validation, and authority handoff. It does not put code locations inside
normative specifications, prove semantic equivalence automatically, repair code, or
promote observed code to product authority.

## Definitions

- **Backlink:** A `spec: BEHAVIOR-ID` marker in relevant implementation or test code.
- **Traceability baseline:** Derived locations and fingerprints accepted after an
  authorized implementation or reconciliation.
- **Structural drift:** Missing, unknown, moved, unbaselined, or changed evidence.
- **Semantic drift:** Observable behavior that disagrees with approved product meaning.

## Approved product decisions

Keep behavior identity in product specifications and keep code locations only in one
derived traceability index. Make backlinks and validation mandatory in the Code Agent
handoff while the Spec Agent continues to stop before planning or implementation.

## Conceptual data model

An approved behavior has one stable ID and may have multiple implementation or test
backlinks. Each backlink baseline records its location and a deterministic linked-file
fingerprint. Current evidence is compared with that baseline but never becomes product
authority without an approved decision.

## Business rules

TRACE-001: Every approved implementable behavior MUST retain its stable behavior ID
across specification revisions unless it is explicitly superseded.

TRACE-002: The Code Agent handoff MUST require the Code Agent to read both feature
specifications and add `spec: BEHAVIOR-ID` backlinks to relevant production code and
tests for every implemented rule.

TRACE-003: Code Agent completion MUST require a refreshed traceability baseline and a
clean read-only drift validation.

TRACE-004: Traceability MUST remain derived and non-normative; product specifications
MUST NOT contain implementation paths or backlinks.

TRACE-005: The traceability baseline MUST map behavior IDs to backlink locations and
deterministic linked-file fingerprints.

TRACE-006: Validation MUST report approved behavior without backlinks, backlinks
without product authority, current backlinks absent from the baseline, baseline links
that moved or disappeared, and linked files changed since the baseline.

TRACE-007: Draft product rules MUST NOT fail implementation-link validation before
product approval.

TRACE-008: Validation MUST NOT modify specifications, code, tests, backlinks, product
history, or the traceability baseline.

TRACE-009: Baseline refresh MUST occur only after approved implementation or explicit
reconciliation and MUST NOT be used to conceal unexplained drift.

TRACE-010: An intentional product change MUST return through specification
clarification and approval before its implementation baseline is refreshed.

TRACE-011: A semantic disagreement MUST show both product and implementation evidence
and require human product authority; it MUST NOT be resolved automatically.

TRACE-012: The CLI MUST provide simple validation and traceability-refresh commands for
Code Agents and automation while retaining the standalone installed checker.

## Preconditions and postconditions

Traceability starts after written specification approval. Successful Code Agent
completion leaves implemented rules backlinked, a current derived baseline, and a clean
structural report. Product meaning remains owned by the approved specifications.

## Primary user flows

The Spec Agent approves behavior and emits the traceability-aware handoff. The Code
Agent plans and implements it, adds backlinks, refreshes traceability, validates, and
reports completion. Future agents validate before changes and route any finding to the
appropriate product or engineering authority.

## Alternative and failure flows

Missing backlinks block completion. New or moved backlinks require an authorized
baseline refresh. A changed linked file creates a possible-staleness finding. A
semantic conflict returns to human review rather than automatic repair.

## States and transitions

Evidence may be absent, unbaselined, current, changed, moved, or stale. Only approved
implementation or reconciliation may transition current evidence into a new baseline.

## Permissions, privacy, and compliance

Traceability contains repository-relative paths and fingerprints but no source content,
credentials, prompts, or personal data. Only product authority changes normative
meaning; Code Agents maintain derived implementation evidence.

## Constraints and defaults

Use one derived JSON traceability file and the existing three skills. Fingerprint
comparison is conservative evidence requiring review, not proof of semantic drift.

## Assumptions and unresolved decisions

None.
