---
id: CLAUDE-CODE-DISCOVERY-ACCEPTANCE
title: Claude Code Skill Discovery Acceptance
status: approved
version: 1.0.0
---

# Claude Code Skill Discovery Acceptance

## Acceptance scenarios

AC-CCD-001: Given a clean repository, when Spec Agent is initialized, then each of the
three skills is available through both the open-agent and Claude Code discovery
locations.

AC-CCD-002: Given an initialized repository, when Claude Code evaluates a feature,
drift, or evolution request, then its native project instructions route it to the same
corresponding skill behavior as another compatible agent.

AC-CCD-003: Given the two discovery trees, when their content is normalized for the
agent-specific discovery path, then their files and instructions are equivalent.

AC-CCD-004: Given user-authored text in either project instruction file, when
initialization runs repeatedly, then that text remains unchanged and exactly one
managed Spec Agent block is present.

AC-CCD-005: Given a locally modified skill in either discovery tree, when normal
initialization runs, then the modification remains; when forced initialization runs,
then both trees return to the packaged content.

AC-CCD-006: Given a missing or divergent Claude Code mirror file, when package tests
run, then validation fails with the affected skill file identified.

AC-CCD-007: Given an existing project specification, feature packet, evolution log, or
traceability baseline, when the CLI is upgraded and forced initialization runs, then
those project-owned artifacts remain unchanged.

AC-CCD-008: Given a built distribution installed in a clean environment, when a project
is initialized, then the installed Claude Code skills and router are present and the
read-only initialization check succeeds.
