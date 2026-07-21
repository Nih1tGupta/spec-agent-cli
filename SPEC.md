---
id: SPEC-AGENT
title: Strict Spec Agent
status: approved
version: 4.2.0
---

# Strict Spec Agent

## Purpose

Spec Agent turns uncertain feature requests into approved, implementation-independent
product specifications. It creates enough friction to expose ambiguity, then stops and
hands the approved specification to a separate Code Agent.

## Source-of-truth boundaries

- `SPEC.md` owns repository-wide product behavior and indexes every feature packet.
- Each feature packet contains normative `spec.md` and `acceptance.md` files.
- `.agents/skills/` is the canonical authored skill tree.
- `.claude/skills/` is its deterministic Claude Code compatibility mirror.
- `spec/evolution/events.jsonl` owns approved product-decision history.
- `spec/evolution/timeline.md` is a generated view, never a source of truth.
- `spec/traceability.json` is derived from code backlinks and is never normative.

## Feature specifications

- [Feature specification rules](spec/packets/feature-spec-packets/spec.md) and [acceptance](spec/packets/feature-spec-packets/acceptance.md)
- [Evolution event log rules](spec/packets/evolution-event-log/spec.md) and [acceptance](spec/packets/evolution-event-log/acceptance.md)
- [Strict skill behavior](spec/packets/production-skill-hardening/spec.md) and [acceptance](spec/packets/production-skill-hardening/acceptance.md)
- [CLI distribution](spec/packets/cli-distribution/spec.md) and [acceptance](spec/packets/cli-distribution/acceptance.md)
- [Code/spec traceability](spec/packets/code-spec-traceability/spec.md) and [acceptance](spec/packets/code-spec-traceability/acceptance.md)
- [Claude Code discovery](spec/packets/claude-code-discovery/spec.md) and [acceptance](spec/packets/claude-code-discovery/acceptance.md)
- [Local specification workspace](spec/packets/local-dashboard/spec.md) and [acceptance](spec/packets/local-dashboard/acceptance.md)

## Product structure

```text
spec-agent/
├── AGENTS.md
├── CLAUDE.md
├── SPEC.md
├── pyproject.toml
├── src/spec_agent/
├── .agents/skills/
│   ├── spec-request-flow/
│   ├── spec-drift-sync/
│   └── spec-evolution/
├── .claude/skills/              # generated compatibility mirror
│   ├── spec-request-flow/
│   ├── spec-drift-sync/
│   └── spec-evolution/
├── spec/
│   ├── features/<feature-slug>/
│   │   ├── spec.md
│   │   └── acceptance.md
│   ├── evolution/
│   │   ├── events.jsonl
│   │   └── timeline.md
│   └── traceability.json
└── tests/
```

The source `.agents/skills/` tree remains the canonical authored copy. The Claude Code
tree is generated from it with only discovery-path adaptations. The `spec-agent init`
command installs both surfaces without copying this package's self-specifications.

## Agent discovery and boundaries

SA-001: Every responsibility MUST have exactly one owning source.

SA-002: Every skill MUST be discoverable from minimal `name` and trigger-focused
`description` frontmatter before its body or resources are loaded.

SA-003: The package MUST maintain `.agents/skills/` as the canonical authored tree and
MUST generate an equivalent `.claude/skills/` compatibility mirror for Claude Code.

SA-004: `AGENTS.md` MUST remain a concise router to the root contract and applicable
skill rather than duplicate complete workflows.

## Specification request behavior

SA-005: A behavior request MUST trigger context discovery, explicit unknowns, and a
scope check before product decisions are proposed.

SA-006: The agent MUST ask one blocking question at a time and MUST compare two or
three approaches for each material product decision. Clarification MUST use the Spec
Agent signature: `Question N:` for each question; `Option 1 (Recommended)` / `Option 2`
/ `Option 3` for choices; and end choice prompts with
`Please select one of the following options (1, 2, or 3):` (numbers matching the count).

SA-007: The agent MUST evaluate actors, business rules, conceptual data, flows,
failures, states, edge cases, permissions, privacy, defaults, constraints, non-goals,
and measurable outcomes before specification writing.

SA-008: Feature files MUST NOT be scaffolded or written until the user approves the
presented product decisions.

SA-009: Both written specification files MUST be self-reviewed and explicitly approved
before completion.

SA-010: The Spec Agent MUST stop after approval and output: `Spec complete. To
implement this, give your Code Agent the following prompt: 'Read the specification at
[actual spec.md path] and generate an implementation plan.'`

SA-011: The Spec Agent MUST NOT create implementation plans, select code files or
technologies, write code or tests, dispatch implementation, or run engineering repair.

## Traceability and drift

SA-012: Product specifications MUST contain stable behavior IDs but MUST NOT contain
code paths, symbols, technology choices, engineering commands, or code backlinks.

SA-013: Drift observation MUST compare approved product rules with code, backlinks,
tests, interfaces, Git evidence, and verification evidence without modifying them.

SA-014: Traceability refresh MAY replace only derived `spec/traceability.json` with a
mapping from stable behavior IDs to code backlinks that already exist.

SA-015: Semantic disagreement MUST be reported with both normative and implementation
evidence and handed to product authority; observed code is never automatic authority.

## Evolution

SA-016: Evolution history MUST preserve approved user intent, product decisions,
rationale, behavior IDs, normative deltas, supersession, and unresolved product gaps
without storing implementation plans, code deltas, test results, or full prompts.

## CLI distribution

SA-017: Installing the Python distribution MUST NOT modify a project; repository
changes occur only through an explicit `spec-agent init` command.

SA-018: Initialization MUST install the complete canonical `.agents/skills` tree and
its Claude Code compatibility mirror, merge managed router blocks safely, and scaffold
only missing project-owned artifacts.

SA-019: Repeated initialization MUST be safe and idempotent, and forced updates MUST
remain limited to CLI-managed skill assets.

## Code Agent traceability contract

SA-020: The Code Agent handoff MUST require both feature specifications, stable
behavior-ID backlinks in relevant production code and tests, traceability refresh, and
a clean drift validation before implementation completion.

SA-021: Derived traceability MUST preserve a baseline of backlink locations and linked
file fingerprints so later code changes can be reported without placing code paths in
normative specifications.

SA-022: Drift validation MUST be read-only and MUST distinguish missing, unknown,
unbaselined, moved, and changed-code evidence while leaving semantic authority to a
human product decision.

SA-023: Traceability refresh MUST establish a new baseline only after an approved
implementation or reconciliation; it MUST NOT silently make changed code authoritative.

## Claude Code compatibility

SA-024: Initialization MUST make the same three skills discoverable through both the
open-agent and Claude Code project conventions without requiring another package.

SA-025: Claude-specific resources MAY adapt discovery paths and routing language but
MUST preserve all workflow gates, product rules, templates, scripts, and outcomes.

SA-026: Both project instruction files MUST preserve user-authored content outside one
managed Spec Agent block, including across repeated and forced initialization.

SA-027: Package validation MUST detect a missing or semantically divergent Claude Code
mirror before distribution.

## Workflow

```text
request
  -> spec-request-flow
  -> context and clarification
  -> requirements-completeness gate
  -> product-decision approval
  -> spec.md + acceptance.md
  -> self-review and written-spec approval
  -> spec-evolution event
  -> Code Agent prompt
  -> STOP
```

After implementation by another agent, `spec-drift-sync` may observe code/spec drift,
refresh derived traceability, and route a product decision back through request flow.

## Failure handling

- Missing root contract: create it from the root template and obtain product approval.
- Existing feature packet: update the same two files; never create a duplicate folder.
- Blocking uncertainty: continue asking one question at a time; do not draft the spec.
- Invalid metadata or packet shape: report the exact validation failure.
- Semantic conflict: show both sides and request product authority.
- Unavailable evidence: report the gap without invention.

## Acceptance criteria

- AC-SA-001: A compatible agent discovers exactly three independently triggered skills.
- AC-SA-002: A vague request cannot reach specification writing before clarification
  and product-decision approval.
- AC-SA-003: Every feature contains exactly two product-only specification files.
- AC-SA-004: Completion produces the exact Code Agent prompt and no implementation plan.
- AC-SA-005: Drift observation preserves specs, code, tests, and backlinks unchanged.
- AC-SA-006: Approved product evolution remains append-only and UI-readable.
- AC-SA-007: A built wheel installs in a clean environment and initializes a repository
  that passes `spec-agent init --check`.
- AC-SA-008: A Code Agent handoff cannot complete without behavior backlinks, refreshed
  traceability, and clean read-only validation.
- AC-SA-009: Modifying a baselined linked code file produces a drift finding until an
  authorized reconciliation establishes a new baseline.
- AC-SA-010: A clean installation exposes equivalent skills and managed routing to
  both compatible open agents and Claude Code.
