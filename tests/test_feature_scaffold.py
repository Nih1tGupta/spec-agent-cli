from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# spec: FSP-001, FSP-002, FSP-003, FSP-005, FSP-006


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/spec-request-flow/scripts/create_packet.py"


class FeatureScaffoldTests(unittest.TestCase):
    def test_creates_complete_feature_packet_without_template_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "feature-x",
                    "--title",
                    "Feature X",
                    "--repo",
                    str(repo),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            packet = repo / "spec/packets/feature-x"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                {path.name for path in packet.glob("*.md")},
                {"spec.md", "acceptance.md"},
            )
            for path in packet.glob("*.md"):
                text = path.read_text(encoding="utf-8")
                self.assertIn("Feature X", text)
                self.assertNotIn("{{", text)
            feature_spec = (packet / "spec.md").read_text(encoding="utf-8")
            acceptance = (packet / "acceptance.md").read_text(encoding="utf-8")
            self.assertIn("## Users and actors", feature_spec)
            self.assertIn("## Business rules", feature_spec)
            self.assertIn("## Primary user flows", feature_spec)
            self.assertIn("## Behavior acceptance", acceptance)
            self.assertIn("## Edge cases", acceptance)
            for text in (feature_spec, acceptance):
                self.assertNotIn("Exact files", text)
                self.assertNotIn("Implementation tasks", text)
                self.assertNotIn("verification commands", text.lower())

    def test_rejects_invalid_slug_and_does_not_overwrite_existing_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            invalid = subprocess.run(
                [sys.executable, str(SCRIPT), "Feature X", "--repo", str(repo)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(invalid.returncode, 0)

            command = [
                sys.executable,
                str(SCRIPT),
                "feature-x",
                "--repo",
                str(repo),
            ]
            self.assertEqual(subprocess.run(command, check=False).returncode, 0)
            spec = repo / "spec/packets/feature-x/spec.md"
            spec.write_text("preserve me\n", encoding="utf-8")

            repeated = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual(spec.read_text(encoding="utf-8"), "preserve me\n")


if __name__ == "__main__":
    unittest.main()
