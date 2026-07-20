---
name: spec-request-flow
description: Use when a user asks to add, change, fix, refactor, design, or implement repository behavior under spec-driven development, including vague requests and follow-ups that modify an existing feature even when specifications are not mentioned.
---

# Spec Request Flow

Produce an approved product specification, then stop with a Code Agent handoff.

<HARD-GATE>
Do not scaffold or write specifications before product-decision approval.
Do not create an implementation plan or choose files or technologies. Do not write
code or tests, dispatch implementation, or perform engineering verification.
</HARD-GATE>

## Explore context

Read `AGENTS.md`, root `SPEC.md`, the existing packet, relevant behavior, and related
evolution events. Separate evidence, outcomes, conflicts, assumptions, and unknowns.
Decompose independent subsystems and process one valuable feature at a time.

## Clarify product behavior

Ask one blocking question at a time. Present 2-3 approaches for each material product
decision, with trade-offs and a recommendation about observable behavior. Cover actors,
rules, conceptual data, flows, failures, recovery, states, edges, permissions, privacy,
defaults, constraints, non-goals, and measurable outcomes. Label every unresolved item
`blocking` or `non-blocking`; never convert an assumption into a requirement.

## Requirements-completeness gate

Verify every category above. Continue while a blocking item remains; defer only with
user approval of a stated default.

## Product-decision approval gate

Present the product behavior for approval or revision. Do not write either file while
approval is absent or ambiguous.

## Write and self-review the specification

1. Reuse `spec/packets/<feature-slug>/` when present; otherwise run
   `scripts/create_packet.py <feature-slug> --title "Feature Title"`.
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

After approval, mark both files `approved`, use `spec-evolution` to record the decision,
emit the contract below, and stop. `spec-drift-sync` is used after implementation.

Output exactly the following, replacing `[SPEC_PATH]` with the actual `spec.md` path:

Spec complete. To implement this, give your Code Agent the following prompt: 'Read the specification at [SPEC_PATH] and its companion acceptance.md, then generate an implementation plan. During implementation, add spec: BEHAVIOR-ID backlinks to relevant production code and tests for every implemented rule. After the approved implementation, run spec-agent traceability-sync --repo ., followed by spec-agent validate --repo . Do not claim completion unless validation reports CLEAN.'

This is a handoff contract, not implementation by the Spec Agent. Do not append other
planning advice, implementation steps, or an offer to write code.

## Later changes

A later prompt updates the same two-file packet and preserves stable behavior IDs.
Return to clarification and both approval gates for every normative product change.
