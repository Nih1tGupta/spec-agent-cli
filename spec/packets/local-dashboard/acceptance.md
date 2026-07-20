---
id: UI-ACCEPTANCE
title: Local Specification Workspace Acceptance
status: approved
related_spec: spec.md
created: 2026-07-20
---

# Local Specification Workspace Acceptance

## Acceptance scope

Validate local launch, packet inspection, evidence relationships, visualization
signals, read-only behavior, and graceful partial-data handling.

## Behavior acceptance

- AC-UI-001: Launching the UI exposes the local workspace without modifying project
  files. Covers UI-001 and UI-005.
- AC-UI-002: Selecting a packet exposes its specification, acceptance, behavior IDs,
  linked evidence, and related decisions. Covers UI-002 and UI-003.
- AC-UI-003: The workspace renders packet health, drift, evolution, recent changes,
  and a relationship graph as inspectable signal views. Covers UI-006.
- AC-UI-004: Missing or malformed optional evidence produces a visible unavailable or
  warning state while the rest of the workspace remains usable. Covers UI-004.

## Alternative and failure acceptance

Requests for files outside the selected repository are rejected, and repository
content remains unchanged during dashboard use.

## Edge cases

An empty repository, an uninitialized repository, a repository with no packets, a
repository without Git history, and a packet without linked code all render explicit
empty states.

## Exception policy

No remote fallback or inferred evidence is permitted in the local first release.

## Permissions and privacy acceptance

The dashboard serves local content only and does not expose paths outside the selected
repository.

## Unresolved acceptance decisions

None.
