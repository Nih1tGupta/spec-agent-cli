<!-- Generated from spec/evolution/events.jsonl by .agents/skills/spec-evolution/scripts/timeline.py; do not edit. -->
# Specification Evolution Timeline

## 2026-07-17T00:00:00Z — Spec Agent Bootstrap

- Event: EV-20260717-000000-SPEC-AGENT-BOOTSTRAP
- Task type: spec-change
- User intent: Create a Spec Agent package for spec-driven development, evolving specifications, drift tracking, and a future timeline UI.
- Behavior IDs: SPAGENT-005, SPAGENT-008, EVOL-005, SYSTEM-013
- Product decision: Create a portable Spec Agent with specification and evolution guidance.
- Rationale: Establish a portable baseline for spec-driven product decisions.
- Specification delta: Added the initial Spec Agent, evolution, and system behaviors.
- Supersedes: missing

## 2026-07-17T08:03:21Z — Backlink Drift Checker

- Event: EV-20260717-080321-BACKLINK-DRIFT-CHECKER
- Task type: spec-change
- User intent: Use Provenance-style backlinks to detect stale specs and code, reconcile drift, and capture the result in evolution history.
- Behavior IDs: PROCESS-009, PROCESS-010, SYSTEM-020, SPAGENT-020, EVOL-019
- Product decision: Adopt Provenance-style behavior backlinks for drift observation.
- Rationale: Stable behavior identity enables stale-rule detection without making code authoritative.
- Specification delta: Added product behavior for phantom, dead, silent, unlinked, and stale-verification findings.
- Supersedes: missing

## 2026-07-17T08:41:48Z — Remove Prov CLI Assumption

- Event: EV-20260717-084148-REMOVE-PROV-CLI-ASSUMPTION
- Task type: product-clarification
- User intent: Make the imported Spec Agent folder work without requiring the Provenance CLI.
- Behavior IDs: SPAGENT-020
- Product decision: Remove the external Provenance CLI as a runtime requirement.
- Rationale: The portable package must work without an unavailable external command.
- Specification delta: Clarified the portable checker as the active drift mechanism.
- Supersedes: missing

## 2026-07-17T09:17:08Z — Add Routing Index

- Event: EV-20260717-091708-ADD-ROUTING-INDEX
- Task type: product-clarification
- User intent: Give agents one map showing which package files are related and what to read for each task.
- Behavior IDs: SPAGENT-005
- Product decision: Strengthen the existing specification index with routing and recovery guidance.
- Rationale: One entrypoint reduces discovery ambiguity.
- Specification delta: Added centralized task routing to the existing index.
- Supersedes: missing

## 2026-07-17T10:32:06Z — Approve Production Skill Architecture

- Event: EV-20260717-103206-APPROVE-PRODUCTION-SKILL-ARCHITECTURE
- Task type: spec-approval
- User intent: Adopt production skill discovery conventions while preserving spec-driven workflow, evolution, backlinks, and drift.
- Behavior IDs: PROCESS-004, PROCESS-005, PROCESS-009, PROCESS-010, SPAGENT-005, SPAGENT-008, SPAGENT-010, SPAGENT-012, SPAGENT-020, EVOL-005, EVOL-010, EVOL-011, EVOL-012
- Product decision: Approve canonical skill sources with framework discovery paths.
- Rationale: Canonical sources reduce duplication while preserving agent discovery.
- Specification delta: Approved the production skill architecture for normative adoption.
- Supersedes: missing

## 2026-07-17T10:51:22Z — Refactor To Provenance Skill Layout

- Event: EV-20260717-105122-REFACTOR-PROVENANCE-SKILL-LAYOUT
- Task type: architecture-decision
- User intent: Refactor Spec Agent to Provenance-style discovery and make evolution, backlinks, and drift first-class skills.
- Behavior IDs: PRODUCT-001, PRODUCT-002, PRODUCT-008, PRODUCT-009, SYSTEM-001, SYSTEM-002, SYSTEM-020, SYSTEM-021, SYSTEM-022, SYSTEM-023, SYSTEM-024, SPAGENT-001, SPAGENT-020, EVOL-005, EVOL-019, EVOL-020, EVOL-021
- Product decision: Use canonical skill sources with deterministic agent discovery.
- Rationale: Production-style discovery should not create competing normative sources.
- Specification delta: Revised product and system contracts for the focused-skill architecture.
- Supersedes: missing

## 2026-07-17T11:14:50Z — Consolidate To One Skill Root

- Event: EV-20260717-111450-CONSOLIDATE-SINGLE-SKILL-ROOT
- Task type: architecture-decision
- User intent: Use only .agents/skills, eliminate duplicate sources, and preserve spec-driven development, evolution, timelines, drift, and traceability.
- Behavior IDs: SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011, SA-012, SA-013, SA-014, SA-015, SA-016
- Product decision: Consolidate to spec-request-flow, spec-drift-sync, and spec-evolution under one skill root.
- Rationale: Three independent triggers create clear ownership without parallel structures.
- Specification delta: Adopted the consolidated Spec Agent contract.
- Supersedes: missing

## 2026-07-17T13:08:51Z — Feature Specification Packets

- Event: EV-FEATURE-SPEC-PACKETS
- Task type: architecture-decision
- User intent: Create at most two specification files per feature without losing requirements, approval, drift, evolution, or timeline behavior.
- Behavior IDs: FSP-001, FSP-002, FSP-003, FSP-004, FSP-005, FSP-006
- Product decision: Use indexed two-file feature packets.
- Rationale: Bounded packets preserve discovery while limiting artifact growth.
- Specification delta: Added FSP-001 through FSP-006 and indexed the feature packet.
- Supersedes: missing

## 2026-07-17T13:31:46Z — Consolidate Evolution Into JSONL

- Event: EV-EVOLUTION-JSONL-CONSOLIDATION
- Task type: architecture-decision
- User intent: Replace accumulating per-event Markdown files with one structured evolution log while preserving history, UI data, and generated diagrams.
- Behavior IDs: ELOG-001, ELOG-002, ELOG-003, ELOG-004, ELOG-005, ELOG-006
- Product decision: Use one append-only events.jsonl as the product-history source and generate Markdown/Mermaid views.
- Rationale: One structured stream avoids per-event file growth and supports UI consumers.
- Specification delta: Added ELOG-001 through ELOG-006 and product-history ownership.
- Supersedes: missing

## 2026-07-17T13:59:47Z — Approve Production Skill Hardening Specification

- Event: EV-PRODUCTION-SKILL-HARDENING-SPEC-APPROVED
- Task type: spec-approval
- User intent: Review the three Spec Agent skills against Superpowers brainstorming and official Agent Skills guidance, then harden them for reliable spec-driven development.
- Behavior IDs: PSH-001, PSH-002, PSH-003, PSH-004, PSH-005, PSH-006, PSH-007, PSH-008, PSH-009, PSH-010, PSH-011, PSH-012
- Product decision: Approve standalone specification gates with progressive disclosure.
- Rationale: Reliable spec-driven behavior must not depend on optional external skills.
- Specification delta: Approved PSH-001 through PSH-012 for gated request flow, authority-aware drift, and boundary-based evolution.
- Supersedes: missing

## 2026-07-17T13:59:48Z — Adopt Production Skill Hardening

- Event: EV-PRODUCTION-SKILL-HARDENING-IMPLEMENTED
- Task type: spec-change
- User intent: Adopt the approved production hardening across the three Spec Agent skills and supporting specification workflow assets.
- Behavior IDs: PSH-001, PSH-002, PSH-003, PSH-004, PSH-005, PSH-006, PSH-007, PSH-008, PSH-009, PSH-010, PSH-011, PSH-012
- Product decision: Adopt the approved skill behavior as the current product contract.
- Rationale: The approved skill behavior became current product truth.
- Specification delta: Accepted PSH-001 through PSH-012 and updated the root contract.
- Supersedes: missing

## 2026-07-18T20:15:19Z — Strict Spec Agent Separation

- Event: EV-STRICT-SPEC-AGENT-SEPARATION
- Task type: architecture-decision
- User intent: Refactor Spec Agent to stop after approved product specifications while preserving two spec files, Code Agent discovery, read-only drift, traceability, and evolution history.
- Behavior IDs: SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011, SA-012, SA-013, SA-014, SA-015, SA-016, FSP-001, FSP-003, FSP-006, ELOG-003, PSH-005, PSH-006, PSH-007, PSH-008, PSH-010
- Product decision: Use a strict Spec Agent that outputs product-only spec.md and acceptance.md, emits the exact Code Agent handoff, and delegates all planning and implementation.
- Rationale: Separating product authority from engineering execution satisfies the audited Spec/Plan boundary while derived traceability preserves drift visibility.
- Specification delta: Replaced plan.md with acceptance.md, removed implementation orchestration and drift repair, isolated code links in derived traceability, and narrowed evolution to product decisions.
- Supersedes: missing

## 2026-07-19T05:53:17Z — CLI Distribution Approved

- Event: EV-CLI-DISTRIBUTION-APPROVED
- Task type: architecture-decision
- User intent: Package Spec Agent like Provenance so anyone can install the CLI and explicitly initialize a repository.
- Behavior IDs: CLI-001, CLI-002, CLI-003, CLI-004, CLI-005, CLI-006, CLI-007, CLI-008, CLI-009, CLI-010, CLI-011, CLI-012, SA-017, SA-018, SA-019
- Product decision: Distribute the strict Spec Agent as spec-agent-cli with an explicit, safe, idempotent spec-agent init command.
- Rationale: The Provenance installation pattern makes the skills portable while keeping repository changes explicit and preserving one authored skill source.
- Specification delta: Added CLI distribution rules, acceptance outcomes, safe initialization behavior, and trusted publishing requirements.
- Supersedes: missing

## 2026-07-19T12:01:39Z — Enforce Code and Specification Traceability

- Event: EV-CODE-SPEC-TRACEABILITY-ENFORCED
- Task type: architecture-decision
- User intent: Require every Code Agent implementation to preserve specification-to-code backlinks so future agents can detect stale specifications and code drift.
- Behavior IDs: SA-020, SA-021, SA-022, SA-023, TRACE-001, TRACE-002, TRACE-003, TRACE-004, TRACE-005, TRACE-006, TRACE-007, TRACE-008, TRACE-009, TRACE-010, TRACE-011, TRACE-012
- Product decision: Make backlinks, traceability refresh, and clean validation mandatory in the Code Agent handoff while keeping product specifications implementation-independent.
- Rationale: Drift detection requires durable implementation evidence connected to stable product behavior IDs.
- Specification delta: Added the Code Agent traceability contract, schema-v2 backlink baselines, changed-code findings, approved-only validation, and CLI validation commands.
- Supersedes: missing

## Mermaid

```mermaid
timeline
  title Specification Evolution
  2026-07-17T00:00:00Z : EV-20260717-000000-SPEC-AGENT-BOOTSTRAP — Spec Agent Bootstrap
  2026-07-17T08:03:21Z : EV-20260717-080321-BACKLINK-DRIFT-CHECKER — Backlink Drift Checker
  2026-07-17T08:41:48Z : EV-20260717-084148-REMOVE-PROV-CLI-ASSUMPTION — Remove Prov CLI Assumption
  2026-07-17T09:17:08Z : EV-20260717-091708-ADD-ROUTING-INDEX — Add Routing Index
  2026-07-17T10:32:06Z : EV-20260717-103206-APPROVE-PRODUCTION-SKILL-ARCHITECTURE — Approve Production Skill Architecture
  2026-07-17T10:51:22Z : EV-20260717-105122-REFACTOR-PROVENANCE-SKILL-LAYOUT — Refactor To Provenance Skill Layout
  2026-07-17T11:14:50Z : EV-20260717-111450-CONSOLIDATE-SINGLE-SKILL-ROOT — Consolidate To One Skill Root
  2026-07-17T13:08:51Z : EV-FEATURE-SPEC-PACKETS — Feature Specification Packets
  2026-07-17T13:31:46Z : EV-EVOLUTION-JSONL-CONSOLIDATION — Consolidate Evolution Into JSONL
  2026-07-17T13:59:47Z : EV-PRODUCTION-SKILL-HARDENING-SPEC-APPROVED — Approve Production Skill Hardening Specification
  2026-07-17T13:59:48Z : EV-PRODUCTION-SKILL-HARDENING-IMPLEMENTED — Adopt Production Skill Hardening
  2026-07-18T20:15:19Z : EV-STRICT-SPEC-AGENT-SEPARATION — Strict Spec Agent Separation
  2026-07-19T05:53:17Z : EV-CLI-DISTRIBUTION-APPROVED — CLI Distribution Approved
  2026-07-19T12:01:39Z : EV-CODE-SPEC-TRACEABILITY-ENFORCED — Enforce Code and Specification Traceability
```
