from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/spec-evolution/scripts/timeline.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_timeline", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TimelineTests(unittest.TestCase):
    def test_renders_events_in_timestamp_order_and_labels_missing_data(self) -> None:
        renderer = load_renderer()
        with tempfile.TemporaryDirectory() as tmp:
            events = Path(tmp) / "events.jsonl"
            rows = [
                {
                    "id": "EV-2",
                    "timestamp": "2026-07-18T10:00:00Z",
                    "title": "Second",
                    "task_type": "drift-review",
                    "user_intent": "Reconcile retry behavior.",
                    "behavior_ids": ["AUTH-002"],
                    "decision": "Require bounded retries.",
                    "rationale": "Prevents indefinite waiting.",
                },
                {
                    "id": "EV-1",
                    "timestamp": "2026-07-17T09:00:00Z",
                    "title": "First",
                    "task_type": "spec-change",
                    "user_intent": "",
                    "behavior_ids": [],
                    "decision": "",
                    "rationale": "",
                },
            ]
            events.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )

            parsed = renderer.read_events(events)
            output = renderer.render_markdown(parsed)

        self.assertLess(output.index("First"), output.index("Second"))
        self.assertIn("EV-1", output)
        self.assertIn("EV-2", output)
        self.assertIn("AUTH-002", output)
        self.assertIn("missing", output)
        self.assertIn("```mermaid", output)

    def test_reports_invalid_jsonl_line(self) -> None:
        renderer = load_renderer()
        with tempfile.TemporaryDirectory() as tmp:
            events = Path(tmp) / "events.jsonl"
            events.write_text('{"id":"EV-1"}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2"):
                renderer.read_events(events)


if __name__ == "__main__":
    unittest.main()
