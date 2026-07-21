---
id: PSH
title: Strict Spec Agent Skill Behavior
status: approved
created: 2026-07-17
---

# Strict Spec Agent Skill Behavior

## Problem and desired outcome

Ensure compatible agents consistently gather complete product requirements, produce
approved specifications, stop before Plan Mode, preserve product evolution, and observe
drift without repairing implementation.

## Users and actors

Requesting users provide intent; product authorities approve decisions; Spec Agents
author contracts; Code Agents independently plan and implement; auditors inspect drift.

## Scope and non-goals

This feature governs the three skills, their discovery, approval gates, product-only
artifacts, handoff message, drift observation, and evolution history. It excludes
implementation planning, code generation, test execution, debugging, and repair.

## Approved product decisions

Keep exactly three focused skills. Request flow stops after approval; drift is a
read-only observer with a derived traceability output; evolution records product
decisions only.

## Conceptual data model

A request moves through context, clarification, completeness, product approval,
two-file specification, written approval, evolution recording, and handoff.

## Business rules

PSH-001: Skill frontmatter MUST contain only matching `name` and trigger-focused
`description` fields within Agent Skills limits.

PSH-002: Request flow MUST explore context and scope before proposing product behavior.

PSH-003: Request flow MUST ask one blocking question at a time and present two or three
approaches for every material product decision, using the Spec Agent signature
(`Question N:`, `Option 1 (Recommended)` / `Option 2` / `Option 3`, and
`Please select one of the following options (1, 2, or 3):`).

PSH-004: Specification writing MUST wait for product-decision approval and MUST evaluate
all categories in the requirements-completeness gate.

PSH-005: Request flow MUST write and self-review both product specification files and
obtain explicit written-spec approval.

PSH-006: Request flow MUST then emit the exact Code Agent prompt with the actual
`spec.md` path and stop.

PSH-007: Request flow MUST NOT create plans, select implementation details, write code
or tests, dispatch implementation, or run engineering verification.

PSH-008: Drift flow MUST preserve specifications, code, tests, and backlinks unchanged;
only its derived traceability index may be regenerated.

PSH-009: Drift flow MUST distinguish structural findings from semantic conflicts and
hand authority decisions to the appropriate agent.

PSH-010: Evolution MUST record approved product transitions and corrections without
engineering execution fields.

PSH-011: Later requests MUST update the same packet, preserve stable behavior IDs, and
repeat clarification and approval for changed product meaning.

PSH-012: Package validation MUST enforce strict Spec/Plan separation, two product-only
spec files, handoff wording, read-only drift, and product-only evolution.

## Preconditions and postconditions

The workflow begins with a product-affecting request and ends only with approved product
specifications or an explicit blocked outcome; it never ends with implementation work.

## Primary user flows

The agent clarifies, presents choices, obtains approval, writes both files, self-reviews,
obtains written approval, records evolution, emits the handoff, and stops.

## Alternative and failure flows

Ambiguous approval, blocking unknowns, scope spanning independent features, or conflicting
accepted behavior returns to clarification rather than progressing.

## States and transitions

Request state advances only through explicit gates; later product changes re-enter the
same state machine.

## Permissions, privacy, and compliance

Only product authority may approve normative behavior; history excludes full prompts,
secrets, and unnecessary personal data.

## Constraints and defaults

The architecture remains three skills, one skill tree, two product files per feature,
one product event log, one generated timeline, and one derived traceability index.

## Assumptions and unresolved decisions

None.
