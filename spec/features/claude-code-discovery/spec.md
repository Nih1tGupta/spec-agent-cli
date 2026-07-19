---
id: CLAUDE-CODE-DISCOVERY
title: Claude Code Skill Discovery
status: approved
version: 1.0.0
---

# Claude Code Skill Discovery

## Problem and desired outcome

Claude Code discovers project skills through its Claude-specific skill location, while
Spec Agent currently exposes only the open-agent location. A repository initialized by
Spec Agent must therefore expose the same strict specification behavior to Claude Code
without creating a second independently maintained workflow.

## Users and actors

- Repository maintainer: initializes or upgrades Spec Agent in a project.
- Claude Code: discovers and invokes the installed Spec Agent skills.
- Other compatible agents: continue discovering the open-agent skill tree.

## Scope

- Install all three Spec Agent skills for both open-agent and Claude Code discovery.
- Give Claude Code a concise project router equivalent to the open-agent router.
- Preserve the same product behavior, templates, scripts, and strict Spec Agent boundary
  across both discovery surfaces.
- Detect divergence between the two installed skill trees during package validation.

## Non-goals

- Creating Claude-only Spec Agent behavior.
- Adding a fourth skill or changing the two-file feature packet.
- Requiring users to install a separate Claude package or plugin.

## Business rules

CCD-001: Repository initialization MUST make the same three Spec Agent skills
discoverable to compatible open agents and Claude Code.

CCD-002: Claude Code discovery MUST use its native project skill location and native
project instruction file.

CCD-003: The open-agent skill tree MUST remain the canonical authored source; the
Claude Code tree MUST be a deterministic compatibility mirror.

CCD-004: Claude-specific copies MAY adapt discovery paths and agent-facing routing
language but MUST NOT change requirements, gates, templates, scripts, or outcomes.

CCD-005: Initialization and read-only status checks MUST report both discovery trees
and both managed instruction blocks.

CCD-006: A normal initialization MUST preserve local modifications to managed skills;
a forced initialization MAY refresh managed files in both discovery trees.

CCD-007: Initialization MUST preserve user-authored content outside the managed blocks
of both project instruction files.

CCD-008: Package validation MUST fail when a Claude Code skill is missing or differs
semantically from its canonical open-agent counterpart.

CCD-009: Existing specification files, evolution history, and traceability data MUST
retain their current ownership and upgrade behavior.

## Failure behavior

- Missing discovery files are reported as missing and installed on initialization.
- Locally changed managed files are reported as outdated and changed only with force.
- Damaged managed-block markers are reported without rewriting the affected file.
- Mirror divergence blocks package validation until the canonical source and generated
  mirror agree.

## Acceptance outcome

After one initialization, a Claude Code session opened in the repository can discover
and automatically invoke all three Spec Agent skills, while other compatible agents
retain the same behavior and all existing specifications remain untouched.
