---
id: UI
title: Local Specification Workspace
status: approved
created: 2026-07-20
---

# Local Specification Workspace

## Problem and desired outcome

Give people one local, read-only workspace for understanding how approved product
rules relate to acceptance evidence, implementation evidence, drift, and the
history of specification decisions.

## Users and actors

- Product authorities review current rules and their evolution.
- Engineers inspect implementation evidence and drift after an approved handoff.
- Agents consume the same repository-owned evidence through a deterministic view.

## Scope and non-goals

The workspace presents packet navigation, specification and acceptance content,
traceability, drift findings, recent changes, and evolution visualizations. It does
not edit product specifications, code, history, or traceability evidence.

## Approved product decisions

The first release is a local dashboard launched from the CLI. Its visual language
uses a light documentation-style canvas with black typography, lime-green accents,
thin neutral borders, generous spacing, and responsive panels. The default view is
three evidence surfaces only: a specification map, implementation evidence, and
spec-driven evolution/traceability visualization.

## Conceptual data model

A workspace contains one project, zero or more packets, product decisions, evidence
links, drift findings, and recent repository changes. A packet owns product rules and
acceptance scenarios; behavior IDs connect it to derived evidence and decisions.

## Business rules

UI-001: The workspace MUST be read-only with respect to repository content.

UI-002: The workspace MUST expose every packet and allow a person to inspect its
specification, acceptance scenarios, linked evidence, and related decision events.

UI-003: The workspace MUST distinguish current product truth from derived traceability,
drift findings, and historical evolution.

UI-004: The workspace MUST continue rendering when optional evidence is unavailable,
showing an explicit unavailable state instead of inventing data.

UI-005: The workspace MUST be launchable through one CLI command against a selected
repository and MUST work without a hosted service for the first release.

UI-006: Visualizations MUST help explain relationships among packets, behavior IDs,
implementation evidence, drift, decisions, and time; decorative charts without an
inspectable relationship are not sufficient.

UI-007: The default workspace MUST NOT include a generic project overview or empty
dashboard card. Every visible surface MUST explain current specification truth,
what changed and why, or specification-to-code evidence.

UI-008: The traceability visualization MUST show the authored path from project
specification to packet to behavior rule to implementation/backlinks, with drift
checks represented as a distinct relationship.

## Preconditions and postconditions

The selected repository may contain only a root specification, only packets, or
partial derived evidence. Launching the workspace leaves all repository-owned files
unchanged.

## Primary user flows

The user launches the dashboard, reviews project health, selects a packet, reads its
current contract and acceptance, inspects evidence and drift, and follows a decision
event or recent change to understand how the current state emerged.

## Alternative and failure flows

Missing packets show an empty state. Missing evolution or traceability data shows an
explicit unavailable state. Malformed optional history is reported without preventing
the rest of the workspace from rendering. A path outside the repository is never
served as evidence.

## States and transitions

The workspace has loading, ready, partial-evidence, drift, and unavailable-evidence
states. It does not mutate packet or implementation lifecycle states.

## Permissions, privacy, and compliance

The workspace serves only local repository files beneath the selected repository and
does not transmit project content to a remote service.

## Constraints and defaults

The first release uses local files and repository history as its source of truth. A
free local port is selected by default, and opening a browser may be disabled for
headless environments.

## Assumptions and unresolved decisions

None.
