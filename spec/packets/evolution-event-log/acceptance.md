---
id: ELOG-ACCEPTANCE
title: Specification Evolution Event Log Acceptance
status: approved
related_spec: spec.md
created: 2026-07-17
---

# Specification Evolution Event Log Acceptance

## Acceptance scope

Validate product-decision recording, correction, privacy, and timeline rendering.

## Behavior acceptance

- AC-ELOG-001: One product decision appends exactly one independently parseable JSON
  object and creates no event Markdown file. Covers ELOG-001 and ELOG-002.
- AC-ELOG-002: Engineering-only fields and full prompts are rejected or absent from a
  normalized event. Covers ELOG-003.
- AC-ELOG-003: A correction preserves the old line and names it in `supersedes`.
  Covers ELOG-004.
- AC-ELOG-004: The same valid log always produces the same ordered Markdown/Mermaid
  timeline. Covers ELOG-005.
- AC-ELOG-005: A routine read or unanswered clarification creates no event. Covers
  ELOG-006.

## Alternative and failure acceptance

Malformed JSONL, duplicate IDs, invalid timestamps, and absent required fields fail
without appending partial data.

## Edge cases

Missing optional rationale or follow-up values render as `missing`, never invented text.

## Exception policy

Historical lines are never edited; correction by supersession is the only exception path.

## Permissions and privacy acceptance

Stored content contains no secrets, credentials, full prompts, or unnecessary private data.

## Acceptance dependencies

Timeline consumers treat JSONL as authority and Markdown as generated presentation.

## Unresolved acceptance decisions

None.
