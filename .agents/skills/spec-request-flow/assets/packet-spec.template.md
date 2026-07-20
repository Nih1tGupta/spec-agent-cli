---
id: {{BEHAVIOR_PREFIX}}
title: {{FEATURE_TITLE}}
status: draft
created: {{DATE}}
---

# {{FEATURE_TITLE}} Specification

Companion acceptance specification: `acceptance.md`.

## Problem and desired outcome

State the user or business problem, the desired observable outcome, and why it matters.

## Users and actors

Identify each human, organization, or external system involved and its product role.

## Scope and non-goals

State included product behavior, boundaries, constraints, and explicit non-goals.

## Definitions

Define product terms that could otherwise have multiple interpretations.

## Approved product decisions

Record the chosen product behavior, alternatives considered, trade-offs, rationale,
and approving authority. Do not prescribe a technical solution.

## Conceptual data model

Describe business entities, relationships, ownership, lifecycle, and invariants without
choosing storage technology or repository structures.

## Business rules

Add current-state normative requirements beginning with `{{BEHAVIOR_PREFIX}}-001`.
Use observable `MUST`, `SHOULD`, or `MAY` language and keep IDs stable.

## Preconditions and postconditions

Define what must be true before each material action and what becomes true afterward.

## Primary user flows

Describe successful actor journeys in business terms.

## Alternative and failure flows

Describe alternate paths, rejected actions, failures, and recovery behavior.

## States and transitions

Define product-visible states, allowed transitions, terminal states, and invariants.

## Permissions, privacy, and compliance

Define who may do what, protected information, retention or disclosure rules, and
applicable compliance constraints. State when a category is not applicable.

## Constraints and defaults

Record product constraints, default behavior, compatibility expectations, and non-goals.

## Assumptions and unresolved decisions

Label each item `blocking` or `non-blocking`. An approved specification contains no
blocking item; deferred non-blocking items include an accepted default.
