---
id: CLI-ACCEPTANCE
title: CLI Distribution Acceptance Specification
status: approved
related_spec: spec.md
created: 2026-07-19
---

# CLI Distribution Acceptance Specification

## Acceptance scope

These outcomes cover package installation, explicit repository initialization,
updates, safety, and release readiness.

## Behavior acceptance

- AC-CLI-001: Given a clean supported Python environment, when the built distribution
  is installed, then `spec-agent --version` reports its installed version.
- AC-CLI-002: Given only package installation, no repository file is created or edited.
- AC-CLI-003: Given a fresh target, initialization installs every canonical skill file,
  its Claude Code compatibility mirror, and all required project scaffolding.
- AC-CLI-004: Given existing content in either supported project instruction file,
  initialization preserves that content and adds exactly one managed rules block.
- AC-CLI-005: Given existing project-owned artifacts, normal and forced initialization
  preserve their content byte for byte.
- AC-CLI-006: Given a current installation, a second initialization produces no file
  content changes.
- AC-CLI-007: Given a missing or outdated managed asset, check mode returns failure and
  leaves the target byte for byte unchanged.
- AC-CLI-008: Given an outdated skill in either discovery tree, normal initialization
  preserves it and forced initialization restores its generated packaged content.
- AC-CLI-009: Given damaged managed markers in either project instruction file,
  initialization reports failure and leaves the complete file unchanged.
- AC-CLI-010: Given a built wheel, its embedded skill resources match every authored
  canonical skill file and contain no generated cache files.
- AC-CLI-011: Given a freshly initialized target, its project scaffolding contains no
  package tests, package self-specifications, or historical development events.
- AC-CLI-012: Given an approved GitHub release and matching PyPI trusted publisher, the
  publishing workflow can authenticate through OIDC and upload the built artifacts.

## Alternative and failure acceptance

Missing assets are listed individually. Outdated assets explain that force is needed.
Damaged markers return failure without partial rules edits. Build or dependency errors
fail CI before publication.

## Edge cases

- Existing empty and non-empty project instruction files both receive one block.
- Existing specification content is preserved even when force is requested.
- Nested skill files are installed recursively.
- Empty evolution history remains a valid single JSONL source.
- Repeated checks and initializations do not duplicate content.

## Exception policy

There is no automatic overwrite exception for project-owned artifacts. A maintainer
who wants to replace them must do so outside the CLI and remains responsible for data
recovery.

## Permissions and privacy acceptance

Initialization requires local write permission. No project content is uploaded during
installation, initialization, checking, or force refresh.

## Acceptance dependencies

Evaluation requires a supported Python runtime and a writable temporary repository.
Publishing acceptance additionally requires a GitHub repository and PyPI account.

## Unresolved acceptance decisions

- non-blocking: npm installation is outside this release and does not block Python
  package acceptance.
