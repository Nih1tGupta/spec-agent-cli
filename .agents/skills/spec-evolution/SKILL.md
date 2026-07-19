---
name: spec-evolution
description: Use when an approved specification change, product authority decision, correction, terminal spec outcome, timeline, or UI history must be preserved as durable product evolution.
---

# Spec Evolution

Preserve meaningful product decisions and contract transitions in one append-only, UI-ready log.
Current specifications own present truth; evolution owns why that truth changed.

## Event boundaries

Append one event only at these boundaries:

| Boundary | Record when |
|---|---|
| approved specification change | Product authority explicitly approves new or revised `spec.md` and `acceptance.md`. |
| product authority decision | A drift conflict or open product question receives an authoritative decision. |
| correction | A historical product record is wrong and a replacement names it in `supersedes`. |
| terminal spec outcome | Specification work completes or is explicitly stopped, blocked, or abandoned with a meaningful product state. |

Routine reads, tool calls, unanswered clarification, unchanged drift observations, and
engineering execution do not create product evolution events.

## Record the event

1. Run `scripts/record.py --help`, then append to `spec/evolution/events.jsonl` with a
   unique ID and ISO-8601 timestamp.
2. Include summarized user intent, task type, behavior IDs, both spec files, assumptions,
   approved product decision, rationale, normative spec delta, follow-ups, and
   `supersedes` when correcting history.
3. Exclude implementation plans, code locations or deltas, engineering evidence, test
   outcomes, verification status, commands, full prompts, secrets, credentials, copied
   file contents, and unnecessary private data.
4. Never rewrite, reorder, or delete completed lines. Correct by appending a replacement.

## Regenerate and verify

1. Run `scripts/timeline.py --log spec/evolution/events.jsonl --output spec/evolution/timeline.md`.
2. Verify the event ID appears in both the JSONL source and generated timeline.
3. Report exact validation or line errors; never reconstruct missing product evidence.

UI consumers read `events.jsonl` for structured history. `timeline.md` is generated
Markdown/Mermaid presentation and is never normative.

## Ownership boundaries

- Root and feature product specs own current approved behavior.
- `events.jsonl` owns product intent, decisions, rationale, deltas, and supersession.
- Git and external engineering systems own code diffs, plans, tests, and verification.
- `timeline.md` owns no source data.

## Gotchas

- Do not append one event per prompt; record defined product boundaries only.
- Later prompts reuse the same feature and stable behavior IDs.
- Missing information remains missing rather than being inferred.
