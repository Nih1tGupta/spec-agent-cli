from __future__ import annotations

import unittest
from pathlib import Path

# spec: SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011, SA-012, SA-016, SA-020, ELOG-006, PSH-002, PSH-003, PSH-004, PSH-005, PSH-006, PSH-007, PSH-008, PSH-009, PSH-010, PSH-011, TRACE-002, TRACE-003, TRACE-009, TRACE-010, TRACE-011


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


def skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def description(name: str) -> str:
    text = skill(name)
    block = text.split("---\n", 2)[1]
    for line in block.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"')
    raise AssertionError(f"missing description for {name}")


def assert_in_order(test: unittest.TestCase, text: str, phrases: list[str]) -> None:
    positions = [text.index(phrase) for phrase in phrases]
    test.assertEqual(positions, sorted(positions), phrases)


class SkillWorkflowTests(unittest.TestCase):
    def test_descriptions_cover_user_intent_and_separate_responsibilities(self) -> None:
        request = description("spec-request-flow")
        drift = description("spec-drift-sync")
        evolution = description("spec-evolution")

        for term in ("asks", "add", "change", "fix", "refactor", "implement", "follow-up"):
            self.assertIn(term, request)
        self.assertIn("even when", request)
        for term in ("implementations", "refactors", "merges", "code-only", "backlinks", "verification"):
            self.assertIn(term, drift)
        for term in ("approved specification change", "product authority decision", "correction", "terminal", "timeline"):
            self.assertIn(term, evolution)
        self.assertLessEqual(len(request), 500)
        self.assertLessEqual(len(drift), 500)
        self.assertLessEqual(len(evolution), 500)

    def test_request_flow_stops_at_approved_specification_and_hands_off(self) -> None:
        text = skill("spec-request-flow")
        self.assertIn("<HARD-GATE>", text)
        self.assertIn("one blocking question at a time", text)
        self.assertIn("2-3 approaches", text)
        self.assertIn("Question N:", text)
        self.assertIn("Option 1 (Recommended)", text)
        self.assertIn("Please select one of the following options", text)
        self.assertIn("independent subsystems", text)
        self.assertIn("Do not scaffold", text)
        self.assertIn("Do not create an implementation plan", text)
        assert_in_order(
            self,
            text,
            [
                "## Explore context",
                "## Clarify product behavior",
                "## Requirements-completeness gate",
                "## Product-decision approval gate",
                "## Write and self-review the specification",
                "## Written-spec approval gate",
                "## Completion and Code Agent handoff",
            ],
        )
        self.assertNotIn("## Plan and implementation handoff", text)
        self.assertNotIn("TDD", text)
        self.assertNotIn("debugging", text)
        self.assertIn(
            "Spec complete. To implement this, give your Code Agent the following prompt:",
            text,
        )
        for term in (
            "acceptance.md",
            "spec: BEHAVIOR-ID",
            "production code and tests",
            "spec-agent traceability-sync",
            "spec-agent validate",
            "reports CLEAN",
        ):
            self.assertIn(term, text)
        self.assertIn("spec-drift-sync", text)
        self.assertIn("spec-evolution", text)

    def test_spec_reference_contains_complete_self_review(self) -> None:
        text = (SKILLS / "spec-request-flow/references/spec-format.md").read_text(
            encoding="utf-8"
        )
        for term in (
            "Placeholder scan",
            "Internal consistency",
            "Scope",
            "Ambiguity",
            "Testability",
            "Failure, security, and privacy",
            "Unique ownership",
            "Acceptance coverage",
        ):
            self.assertIn(term, text)
        self.assertIn("product-approved", text)
        self.assertIn("approved", text)

    def test_two_spec_templates_are_product_only(self) -> None:
        feature = (SKILLS / "spec-request-flow/assets/packet-spec.template.md").read_text(
            encoding="utf-8"
        )
        acceptance = (
            SKILLS / "spec-request-flow/assets/packet-acceptance.template.md"
        ).read_text(encoding="utf-8")
        for term in (
            "Users and actors",
            "Conceptual data model",
            "Business rules",
            "Preconditions and postconditions",
            "Primary user flows",
            "Alternative and failure flows",
            "States and transitions",
            "Permissions, privacy, and compliance",
        ):
            self.assertIn(term, feature)
        for term in ("Behavior acceptance", "Edge cases", "Exception policy"):
            self.assertIn(term, acceptance)
        forbidden = (
            "Exact files",
            "Implementation tasks",
            "Failing test",
            "Minimal implementation",
            "verification commands",
            "~ path",
        )
        for text in (feature, acceptance):
            for term in forbidden:
                self.assertNotIn(term, text)
        self.assertFalse(
            (SKILLS / "spec-request-flow/assets/feature-plan.template.md").exists()
        )

    def test_drift_flow_is_a_read_only_observer(self) -> None:
        text = skill("spec-drift-sync")
        assert_in_order(
            self,
            text,
            ["## Detection", "## Traceability refresh", "## Evidence report", "## Authority handoff"],
        )
        self.assertIn("read-only", text)
        self.assertIn("structural identity", text)
        self.assertIn("semantic conflict", text)
        self.assertIn("derived traceability", text)
        self.assertIn("Do not edit specifications, code, tests", text)
        self.assertNotIn("## Repair and validation", text)
        self.assertNotIn("Apply only the approved delta", text)
        self.assertIn("linked-file fingerprints", text)
        self.assertIn("Do not refresh", text)
        self.assertIn("spec-agent validate", text)

    def test_evolution_flow_defines_product_boundaries_and_privacy(self) -> None:
        text = skill("spec-evolution")
        self.assertIn("## Event boundaries", text)
        for term in (
            "approved specification change",
            "product authority decision",
            "correction",
            "terminal spec outcome",
            "Routine reads",
            "supersedes",
            "full prompts",
            "file contents",
        ):
            self.assertIn(term, text)
        self.assertIn("scripts/record.py", text)
        self.assertIn("scripts/timeline.py", text)
        self.assertIn("Verify the event ID appears in both", text)
        self.assertNotIn("| verification result |", text.lower())
        self.assertNotIn("feature `plan.md`", text.lower())
        self.assertIn("product decisions", text.lower())


if __name__ == "__main__":
    unittest.main()
