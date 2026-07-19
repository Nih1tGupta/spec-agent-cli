---
name: spec-request-flow
description: Use when a user asks to add, change, fix, refactor, design, or implement repository behavior under spec-driven development, including vague requests and follow-ups that modify an existing feature even when specifications are not mentioned.
---

# Spec Request Flow

Produce an approved, implementation-independent product specification, then stop with
a discoverable Code Agent handoff.

<HARD-GATE>
Do not scaffold or write specification files before the user approves the presented
product decisions. Do not create an implementation plan, choose repository files,
write code or tests, dispatch implementation, or perform engineering verification at
any point in this skill.
</HARD-GATE>

## Explore context

1. Read applicable `AGENTS.md`, root `SPEC.md`, the existing feature packet, relevant
   product behavior, and related `spec/evolution/events.jsonl` entries.
2. Separate evidence, outcomes, conflicts, assumptions, and unknowns.
3. If the request contains independent subsystems, propose decomposition and process
   one independently valuable feature at a time.

## Clarify product behavior

1. Ask one blocking question at a time. Do not ask what repository evidence answers.
2. For each material product decision, present 2-3 approaches, trade-offs, and a
   recommendation. Keep choices about observable behavior, not technical solutions.
3. Cover actors, rules, conceptual data, primary and alternate flows, failures,
   recovery, states, edges, permissions, privacy, defaults, constraints, non-goals,
   and measurable outcomes.
4. Label every unresolved item `blocking` or `non-blocking`. Never turn an assumption
   into an accepted requirement.

## Requirements-completeness gate

Verify every category above before presenting the product decision. Continue while any
blocking item remains. Defer one only when the user approves a stated default.

## Product-decision approval gate

Present the proposed product behavior and ask the user to approve or revise it. Do not
scaffold or write either specification file while approval is absent or ambiguous.

## Write and self-review the specification

1. Reuse `spec/features/<feature-slug>/` when present; otherwise run
   `scripts/create_feature.py <feature-slug> --title "Feature Title"`.
2. Read [references/spec-format.md](references/spec-format.md). Write both `spec.md`
   and `acceptance.md`; add both paths to root `SPEC.md`.
3. Keep both files strictly product-facing. Do not include code paths, symbols,
   frameworks, storage choices, ordered engineering steps, test files, commands,
   deployment instructions, or code backlinks.
4. Run the complete self-review on both files and fix every finding.

## Written-spec approval gate

Show both paths and summarize their delta. Ask for explicit written-spec approval. If
revised, update both files, rerun self-review, and ask again.

## Completion and Code Agent handoff

After approval, mark both files `approved`, use `spec-evolution` to record the approved
product decision, and stop. `spec-drift-sync` is used later as a read-only observer;
it is not implementation work for this skill.

Output exactly the following, replacing `[SPEC_PATH]` with the actual `spec.md` path:

Spec complete. To implement this, give your Code Agent the following prompt: 'Read the specification at [SPEC_PATH] and generate an implementation plan.'

Do not append planning advice, implementation steps, or an offer to write code.

## Later changes

A later prompt updates the same two-file packet and preserves stable behavior IDs.
Return to clarification and both approval gates for every normative product change.
