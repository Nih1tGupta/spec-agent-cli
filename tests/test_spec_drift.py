from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# spec: SA-021, SA-022, SA-023, TRACE-004, TRACE-005, TRACE-006, TRACE-007, TRACE-008, TRACE-009, TRACE-011


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = (
    PACKAGE_ROOT
    / ".agents/skills/spec-drift-sync/scripts"
)
sys.path.insert(0, str(SCRIPTS_DIR))


class SpecDriftTests(unittest.TestCase):
    def test_sync_writes_only_a_derived_traceability_index(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            spec_file = root / "spec/spec.md"
            spec_file.write_text(
                "FEATURE-X-001: Users can complete Feature X.\n",
                encoding="utf-8",
            )
            (root / "service.py").write_text(
                "# spec: FEATURE-X-001\n",
                encoding="utf-8",
            )
            output = root / "spec/traceability.json"

            spec_drift.write_traceability(spec_drift.analyze_repo(root), output)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 2)
            self.assertEqual(data["source"], "derived-from-code-backlinks")
            link = data["behaviors"]["FEATURE-X-001"][0]
            self.assertEqual(link["path"], "service.py")
            self.assertEqual(link["line"], 1)
            self.assertRegex(link["file_sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("baseline_commit", data)
            self.assertEqual(
                spec_file.read_text(encoding="utf-8"),
                "FEATURE-X-001: Users can complete Feature X.\n",
            )

    def test_default_source_combines_root_and_feature_specifications(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = root / "spec/features/feature-x"
            feature.mkdir(parents=True)
            (root / "SPEC.md").write_text(
                "ROOT-001: Repository behavior is indexed.\n  ~ root.py\n",
                encoding="utf-8",
            )
            (feature / "spec.md").write_text(
                "FEATURE-X-001: Feature X is available.\n  ~ feature.py\n",
                encoding="utf-8",
            )
            (root / "root.py").write_text("# spec: ROOT-001\n", encoding="utf-8")
            (root / "feature.py").write_text(
                "# spec: FEATURE-X-001\n", encoding="utf-8"
            )

            report = spec_drift.analyze_repo(root)

        self.assertTrue(report.clean, report.issues)
        self.assertEqual(
            {entry.behavior_id for entry in report.entries},
            {"ROOT-001", "FEATURE-X-001"},
        )

    def test_accepts_root_spec_file_as_normative_source(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_file = root / "SPEC.md"
            code_file = root / "service.py"
            spec_file.write_text(
                "SA-001: Service returns a health response.\n  ~ service.py\n",
                encoding="utf-8",
            )
            code_file.write_text(
                "# spec: SA-001\ndef health():\n    return 'ok'\n",
                encoding="utf-8",
            )

            report = spec_drift.analyze_repo(root, spec_root=spec_file)

        self.assertTrue(report.clean, report.issues)

    def test_reports_phantom_dead_silent_and_unlinked_drift(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_dir = root / "spec"
            code_dir = root / "src" / "widgets"
            spec_dir.mkdir()
            code_dir.mkdir(parents=True)

            (spec_dir / "widgets.md").write_text(
                """# Widgets

WIDGET-DASHBOARD-001: Users can view widgets in a dashboard. [planned]
  > user: "create widget dashboard"
  ~ src/widgets/dashboard.tsx

WIDGET-DASHBOARD-002: Users can filter widgets.
  > user: "filter widgets"
  ~ src/widgets/missing-filter.tsx

WIDGET-DASHBOARD-003: Users can see widget owners.
  > user: "show owners"
""",
                encoding="utf-8",
            )
            (code_dir / "dashboard.tsx").write_text(
                """// spec: WIDGET-DASHBOARD-001, WIDGET-DASHBOARD-999
export function WidgetDashboard() {
  return null
}
""",
                encoding="utf-8",
            )

            report = spec_drift.analyze_repo(root, spec_root=spec_dir)

        self.assertIssue(report, "phantom", "WIDGET-DASHBOARD-999")
        self.assertIssue(report, "dead-ref", "WIDGET-DASHBOARD-002")
        self.assertIssue(report, "silent-implementation", "WIDGET-DASHBOARD-001")
        self.assertIssue(report, "unlinked", "WIDGET-DASHBOARD-003")

    def test_reports_stale_verification_when_linked_code_changed_after_verified_commit(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Spec Drift Test"],
                cwd=root,
                check=True,
            )

            spec_dir = root / "spec"
            code_dir = root / "src" / "widgets"
            spec_dir.mkdir()
            code_dir.mkdir(parents=True)
            code_file = code_dir / "dashboard.tsx"
            code_file.write_text(
                """// spec: WIDGET-DASHBOARD-001
export const version = 1
""",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial code"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            verified_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

            (spec_dir / "widgets.md").write_text(
                f"""---
verification:
  verified_commit: {verified_commit}
---

# Widgets

WIDGET-DASHBOARD-001: Users can view widgets in a dashboard.
  > user: "create widget dashboard"
  ~ src/widgets/dashboard.tsx
""",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "add spec"], cwd=root, check=True, stdout=subprocess.DEVNULL)

            code_file.write_text(
                """// spec: WIDGET-DASHBOARD-001
export const version = 2
""",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "change linked code"], cwd=root, check=True, stdout=subprocess.DEVNULL)

            report = spec_drift.analyze_repo(root, spec_root=spec_dir)

        self.assertIssue(report, "stale-verification", "WIDGET-DASHBOARD-001")

    def test_does_not_require_code_links_for_not_applicable_spec_files(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_dir = root / "spec"
            spec_dir.mkdir()
            (spec_dir / "process.md").write_text(
                """---
verification:
  code_status: not_applicable
---

# Process

PROCESS-001: Specs describe current intended behavior.
""",
                encoding="utf-8",
            )

            report = spec_drift.analyze_repo(root, spec_root=spec_dir)

        self.assertFalse(
            any(issue.kind == "unlinked" and issue.behavior_id == "PROCESS-001" for issue in report.issues),
            f"Expected no unlinked drift for not_applicable spec, got {report.issues!r}",
        )

    def test_draft_spec_does_not_require_backlinks(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "SPEC.md"
            spec.write_text(
                """---
status: draft
---

DRAFT-001: Product behavior is still being decided.
""",
                encoding="utf-8",
            )

            report = spec_drift.analyze_repo(root)

        self.assertFalse(
            any(issue.kind == "unlinked" for issue in report.issues),
            report.issues,
        )

    def test_reports_unbaselined_backlink_until_traceability_is_synced(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            (root / "SPEC.md").write_text(
                "---\nstatus: approved\n---\n\nFEATURE-001: Feature works.\n",
                encoding="utf-8",
            )
            (root / "service.py").write_text(
                "# spec: FEATURE-001\nvalue = 1\n", encoding="utf-8"
            )
            traceability = root / "spec/traceability.json"
            traceability.write_text(
                '{"schema_version": 2, "source": "derived-from-code-backlinks", "baseline_commit": null, "behaviors": {}}\n',
                encoding="utf-8",
            )

            report = spec_drift.analyze_repo(root)
            self.assertIssue(report, "unbaselined", "FEATURE-001")

            spec_drift.write_traceability(report, traceability)
            clean = spec_drift.analyze_repo(root)

        self.assertTrue(clean.clean, clean.issues)

    def test_reports_linked_code_changed_since_traceability_baseline(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            (root / "SPEC.md").write_text(
                "---\nstatus: approved\n---\n\nFEATURE-001: Feature works.\n",
                encoding="utf-8",
            )
            code = root / "service.py"
            code.write_text("# spec: FEATURE-001\nvalue = 1\n", encoding="utf-8")
            traceability = root / "spec/traceability.json"
            initial = spec_drift.analyze_repo(root)
            spec_drift.write_traceability(initial, traceability)

            code.write_text("# spec: FEATURE-001\nvalue = 2\n", encoding="utf-8")
            changed = spec_drift.analyze_repo(root)

        self.assertIssue(changed, "code-changed", "FEATURE-001")

    def test_reports_baseline_link_that_moved_or_disappeared(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            (root / "SPEC.md").write_text(
                "---\nstatus: approved\n---\n\nFEATURE-001: Feature works.\n",
                encoding="utf-8",
            )
            old = root / "old_service.py"
            old.write_text("# spec: FEATURE-001\nvalue = 1\n", encoding="utf-8")
            traceability = root / "spec/traceability.json"
            spec_drift.write_traceability(spec_drift.analyze_repo(root), traceability)

            old.unlink()
            (root / "new_service.py").write_text(
                "# spec: FEATURE-001\nvalue = 1\n", encoding="utf-8"
            )
            moved = spec_drift.analyze_repo(root)

        self.assertIssue(moved, "stale-trace", "FEATURE-001")
        self.assertIssue(moved, "unbaselined", "FEATURE-001")

    def test_default_spec_root_is_standalone_spec_directory(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_dir = root / "spec"
            spec_dir.mkdir()
            (spec_dir / "process.md").write_text(
                """---
verification:
  code_status: not_applicable
---

# Process

PROCESS-001: Specs describe current intended behavior.
""",
                encoding="utf-8",
            )

            report = spec_drift.analyze_repo(root)

        self.assertEqual(Path(report.spec_root).name, "spec")

    def test_ignores_spec_tokens_inside_string_literals(self) -> None:
        import check as spec_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code_file = root / "example.ts"
            spec_marker = "spe" + "c:"
            code_file.write_text(
                f"""const fixture = "// {spec_marker} WIDGET-DASHBOARD-999"
export const real = true // {spec_marker} WIDGET-DASHBOARD-001
""",
                encoding="utf-8",
            )

            backlinks = tuple(spec_drift.scan_code_backlinks(root))

        ids = {backlink.behavior_id for backlink in backlinks}
        self.assertIn("WIDGET-DASHBOARD-001", ids)
        self.assertNotIn("WIDGET-DASHBOARD-999", ids)

    def assertIssue(self, report: object, kind: str, behavior_id: str) -> None:
        issues = getattr(report, "issues")
        self.assertTrue(
            any(getattr(issue, "kind") == kind and getattr(issue, "behavior_id") == behavior_id for issue in issues),
            f"Expected {kind} for {behavior_id}, got {issues!r}",
        )


if __name__ == "__main__":
    unittest.main()
