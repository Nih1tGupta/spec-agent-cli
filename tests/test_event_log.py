from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/spec-evolution/scripts/record.py"


def load_recorder():
    spec = importlib.util.spec_from_file_location("record_event", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EventLogTests(unittest.TestCase):
    def test_package_history_uses_product_only_schema(self) -> None:
        rows = [
            json.loads(line)
            for line in (ROOT / "spec/evolution/events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row["schema_version"], 2)
            for forbidden in (
                "code_files",
                "evidence_refs",
                "implementation_delta",
                "drift_status",
                "verification_result",
            ):
                self.assertNotIn(forbidden, row)

    def test_appends_structured_event_for_ui_consumers(self) -> None:
        recorder = load_recorder()
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "spec/evolution/events.jsonl"
            recorder.append_event(
                log,
                {
                    "id": "EV-FEATURE-X",
                    "timestamp": "2026-07-17T12:00:00Z",
                    "title": "Feature X",
                    "task_type": "feature",
                    "user_intent": "Implement Feature X.",
                    "behavior_ids": ["FEATURE-X-001"],
                    "spec_files": [
                        "spec/packets/feature-x/spec.md",
                        "spec/packets/feature-x/acceptance.md",
                    ],
                    "decision": "Use the approved indexed packet.",
                    "rationale": "Keeps product rules separate from acceptance.",
                    "spec_delta": "Approved Feature X behavior.",
                },
            )

            row = json.loads(log.read_text(encoding="utf-8"))

        self.assertEqual(row["schema_version"], 2)
        self.assertEqual(row["behavior_ids"], ["FEATURE-X-001"])
        self.assertEqual(len(row["spec_files"]), 2)
        self.assertEqual(row["rationale"], "Keeps product rules separate from acceptance.")
        for forbidden in (
            "code_files",
            "evidence_refs",
            "implementation_delta",
            "drift_status",
            "verification_result",
        ):
            self.assertNotIn(forbidden, row)

    def test_rejects_engineering_execution_fields(self) -> None:
        recorder = load_recorder()
        event = {
            "id": "EV-ENGINEERING",
            "timestamp": "2026-07-17T12:00:00Z",
            "title": "Engineering data",
            "task_type": "spec-change",
            "user_intent": "Change product behavior.",
            "code_files": ["src/service.py"],
        }
        with self.assertRaisesRegex(ValueError, "engineering field"):
            recorder.normalize_event(event)

    def test_rejects_duplicate_event_id_without_changing_log(self) -> None:
        recorder = load_recorder()
        event = {
            "id": "EV-1",
            "timestamp": "2026-07-17T12:00:00Z",
            "title": "First",
            "task_type": "feature",
            "user_intent": "First event.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "events.jsonl"
            recorder.append_event(log, event)
            before = log.read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate event id"):
                recorder.append_event(log, event)
            self.assertEqual(log.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
