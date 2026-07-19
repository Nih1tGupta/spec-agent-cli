from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRIFT_SCRIPT = ROOT / ".agents/skills/spec-drift-sync/scripts/check.py"
TIMELINE_SCRIPT = ROOT / ".agents/skills/spec-evolution/scripts/timeline.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SpecDrivenFlowTests(unittest.TestCase):
    def test_spec_backlink_drift_event_and_timeline_flow(self) -> None:
        drift = load_module("spec_agent_drift", DRIFT_SCRIPT)
        timeline = load_module("spec_agent_timeline", TIMELINE_SCRIPT)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_file = root / "SPEC.md"
            code_file = root / "service.py"
            events = root / "spec/evolution/events.jsonl"
            events.parent.mkdir(parents=True)

            spec_file.write_text(
                """# Service

SERVICE-001: The health endpoint returns `ok`.
""",
                encoding="utf-8",
            )
            code_file.write_text(
                """# spec: SERVICE-001
def health():
    return "ok"
""",
                encoding="utf-8",
            )
            events.write_text(
                json.dumps(
                    {
                        "id": "EV-FIXTURE",
                        "timestamp": "2026-07-17T12:00:00Z",
                        "title": "Health Endpoint",
                        "task_type": "feature",
                        "user_intent": "Add a traceable health endpoint.",
                        "behavior_ids": ["SERVICE-001"],
                        "decision": "Expose an observable health outcome.",
                        "rationale": "Operators need a product-visible status.",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            report = drift.analyze_repo(root, spec_root=spec_file)
            rendered = timeline.render_markdown(timeline.read_events(events))

        self.assertTrue(report.clean, report.issues)
        self.assertIn("EV-FIXTURE", rendered)
        self.assertIn("SERVICE-001", rendered)
        self.assertIn("Add a traceable health endpoint.", rendered)


if __name__ == "__main__":
    unittest.main()
