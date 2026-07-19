---
id: FSP
title: Feature Specification Packets
status: approved
created: 2026-07-17
---

# Feature Specification Packets

## Problem and desired outcome

Give humans, Spec Agents, and downstream Code Agents one predictable, bounded place
to find an approved feature contract without mixing requirements with engineering plans.

## Users and actors

- Product authority clarifies and approves intended behavior.
- Spec Agent writes and maintains the product contract.
- Code Agent consumes the approved contract after handoff.

## Scope and non-goals

This feature owns packet discovery, two-file responsibilities, naming, indexing, and
repeat-request behavior. It does not define implementation planning or code changes.

## Approved product decisions

Use root `SPEC.md` as the index. Use one feature directory containing `spec.md` for
product rules and `acceptance.md` for observable acceptance. This preserves discovery
while keeping each artifact focused.

## Conceptual data model

A feature packet has one slug, one product specification, one acceptance specification,
one lifecycle status, and stable behavior IDs referenced by product history.

## Business rules

FSP-001: Every material feature MUST use `spec/features/<feature-slug>/` containing
exactly `spec.md` and `acceptance.md` as its normative product artifacts.

FSP-002: Feature slugs MUST use lowercase kebab-case, and packet creation MUST NOT
overwrite an existing feature packet.

FSP-003: `spec.md` MUST own product rules and `acceptance.md` MUST own observable
acceptance scenarios without duplicating implementation planning.

FSP-004: Root `SPEC.md` MUST index both files for every feature packet.

FSP-005: A later request for an existing feature MUST update the same packet and
preserve stable behavior IDs rather than create a duplicate folder.

FSP-006: Both packet files MUST remain product-facing and MUST exclude internal code
paths, symbols, technologies, engineering steps, commands, and backlinks.

## Preconditions and postconditions

Creation requires an approved product decision and an unused valid slug. Success leaves
both files discoverable and unapproved until their content passes review and approval.

## Primary user flows

The Spec Agent reuses an existing packet or creates a new packet, writes both files,
self-reviews them, obtains approval, and hands the `spec.md` path to the user.

## Alternative and failure flows

Invalid slugs and existing targets fail without modifying existing content. A later
product change re-enters clarification and updates the same packet.

## States and transitions

Packets move from `draft` to `approved`; a replaced contract may become `superseded`.

## Permissions, privacy, and compliance

Only the designated product authority may approve or supersede product requirements.

## Constraints and defaults

The packet always contains two normative Markdown files; derived traceability and
history remain outside the packet.

## Assumptions and unresolved decisions

None.
