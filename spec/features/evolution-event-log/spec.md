---
id: ELOG
title: Specification Evolution Event Log
status: approved
created: 2026-07-17
---

# Specification Evolution Event Log

## Problem and desired outcome

Preserve an append-only, UI-ready history of how approved product intent changes
without creating one file per prompt or mixing engineering execution into product history.

## Users and actors

Product authorities approve decisions; Spec Agents record them; UI consumers render
the sequence; auditors inspect rationale and supersession.

## Scope and non-goals

The log owns product intent, decisions, behavior IDs, specification deltas, rationale,
supersession, and unresolved product gaps. It excludes code deltas, implementation
plans, test results, commands, and full prompts.

## Approved product decisions

Use one append-only `spec/evolution/events.jsonl` source and generate Markdown/Mermaid
views from it. Corrections append a replacement event linked by `supersedes`.

## Conceptual data model

An event has a unique ID, timestamp, title, task type, actor, status, summarized intent,
behavior IDs, spec files, decision, rationale, spec delta, follow-ups, and optional
supersession link.

## Business rules

ELOG-001: Product evolution MUST use one append-only JSONL source and MUST NOT create
per-event Markdown files.

ELOG-002: Every event MUST contain a unique ID, ISO-8601 timestamp, title, task type,
summarized user intent, and product-decision fields.

ELOG-003: Events MUST exclude implementation deltas, code-file lists, engineering test
results, secrets, credentials, full prompts, and complete file contents.

ELOG-004: Corrections MUST append a new event whose `supersedes` field identifies the
incorrect historical event; completed lines MUST NOT be rewritten or deleted.

ELOG-005: Timeline generation MUST be deterministic, identify malformed input by line,
and render missing optional product data without invention.

ELOG-006: Routine reads, questions without a decision, and unchanged observations MUST
NOT create evolution events.

## Preconditions and postconditions

Recording requires a defined event boundary and required product fields. Success adds
one valid line and permits deterministic timeline regeneration.

## Primary user flows

After written-spec approval, append one decision event and regenerate the timeline.

## Alternative and failure flows

Malformed logs, duplicate IDs, missing required data, and invalid timestamps fail
without modifying history.

## States and transitions

Events are appended once and remain immutable; corrections supersede but never erase.

## Permissions, privacy, and compliance

Store concise product evidence only and omit secrets or unnecessary personal data.

## Constraints and defaults

JSONL is authoritative; generated timeline output is disposable.

## Assumptions and unresolved decisions

None.
