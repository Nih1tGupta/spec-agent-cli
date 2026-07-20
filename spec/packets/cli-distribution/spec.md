---
id: CLI
title: CLI Distribution
status: approved
created: 2026-07-19
---

# CLI Distribution Specification

Companion acceptance specification: `acceptance.md`.

## Problem and desired outcome

People need to add the strict Spec Agent to an existing repository without manually
copying files. Installation must be predictable, safe, repeatable, and free to use.

## Users and actors

- A project maintainer installs and updates Spec Agent.
- A compatible AI agent discovers the installed rules and skills.
- PyPI and GitHub distribute approved releases.

## Scope and non-goals

This feature packages the existing Spec Agent and initializes one repository. It does
not run an AI model, implement requested features, create implementation plans, or
publish a release without an explicit maintainer action.

## Definitions

- **Managed asset:** A skill file or marked rules block owned by the installed CLI.
- **Project-owned artifact:** A specification, evolution log, timeline, or traceability
  file whose content belongs to the initialized repository.
- **Initialization:** The explicit action that adds Spec Agent assets to a repository.

## Approved product decisions

Use a Python distribution named `spec-agent-cli` with the `spec-agent` command. Follow
Provenance's explicit installation model: package installation adds only the command;
`spec-agent init` performs repository changes. Install the canonical open-agent skills
and a deterministic Claude Code compatibility mirror from the same packaged source.

## Conceptual data model

An installed distribution contains versioned managed assets. A target repository owns
two agent-specific managed rules blocks, a canonical skill tree and deterministic
Claude Code mirror, a root product index, feature packets, an append-only evolution
log, a generated timeline, and derived traceability.

## Business rules

CLI-001: The product MUST be installable as `spec-agent-cli` and expose the
`spec-agent` command.

CLI-002: Installing or upgrading the distribution MUST NOT modify a target repository.

CLI-003: `spec-agent init` MUST install all files belonging to the three canonical
skills and their Claude Code compatibility mirror, including templates, references,
and scripts.

CLI-004: Initialization MUST add managed Spec Agent blocks to both supported project
instruction files while preserving all user content outside those blocks.

CLI-005: Initialization MUST create only missing project-owned artifacts and MUST NOT
replace existing specifications, evolution history, timelines, or traceability data.

CLI-006: Repeated initialization with the same version MUST be idempotent.

CLI-007: `spec-agent init --check` MUST report missing or outdated assets across both
discovery surfaces, write nothing, and return a failing status when action is required.

CLI-008: `spec-agent init --force` MAY replace locally changed managed skill files in
both discovery trees but MUST NOT replace project-owned artifacts.

CLI-009: Initialization MUST refuse to rewrite either project instruction file when
its managed markers are missing, repeated, reversed, or unbalanced.

CLI-010: The authored `.agents/skills` directory MUST remain the single source of
truth; build tooling MUST deterministically derive Claude Code compatibility files
from those canonical files.

CLI-011: The initialized repository MUST contain the root product index, a feature
packet directory, one append-only evolution log, one generated timeline, and one
derived traceability index.

CLI-012: Public releases MUST be buildable and publishable from GitHub using PyPI
Trusted Publishing without storing a long-lived PyPI password in the repository.

## Preconditions and postconditions

Before initialization, the maintainer selects a writable repository. After successful
initialization, compatible agents and Claude Code can discover the installed skills,
and the read-only check reports both discovery surfaces as current.

## Primary user flows

1. The maintainer installs `spec-agent-cli` using a Python tool installer.
2. The maintainer enters a repository and runs `spec-agent init`.
3. The command reports every created, installed, current, or outdated asset.
4. The maintainer asks an AI agent to use `spec-request-flow` for a feature request.

## Alternative and failure flows

- Existing project-owned artifacts are reported as present and remain unchanged.
- Locally changed managed skill files are reported as outdated until force is chosen.
- Damaged rules markers produce a failure and preserve the complete existing file.
- A read-only check reports drift without creating directories or files.

## States and transitions

Managed assets may be missing, current, outdated, or damaged. Initialization moves
missing assets to current. Force may move outdated skill assets to current. Damaged
rules require a human correction before any managed-block update.

## Permissions, privacy, and compliance

The CLI performs local filesystem writes only after explicit initialization. It sends
no project specification, code, history, or traceability content to an external
service. Public distribution uses the MIT license.

## Constraints and defaults

Python 3.11 or newer is required. The default target is the current directory. The
default initialization is non-destructive and does not force managed skill updates.

## Assumptions and unresolved decisions

- non-blocking: An npm wrapper may be considered later; Python is the approved first
  distribution because the existing Spec Agent utilities are Python.
