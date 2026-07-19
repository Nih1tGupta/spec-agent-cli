import unittest
from pathlib import Path

# spec: SA-001, SA-002, SA-003, SA-004, FSP-004, PSH-001, PSH-012, CCD-001, CCD-002, CCD-003, CCD-004, CCD-008, AC-CCD-001, AC-CCD-002, AC-CCD-003, AC-CCD-006


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".agents/skills"
CLAUDE_SKILLS_ROOT = ROOT / ".claude/skills"

EXPECTED_SKILLS = {
    "spec-request-flow",
    "spec-drift-sync",
    "spec-evolution",
}

REQUIRED_RESOURCES = {
    "spec-request-flow": {
        "references/spec-format.md",
        "assets/SPEC.template.md",
        "assets/feature-spec.template.md",
        "assets/feature-acceptance.template.md",
        "scripts/create_feature.py",
    },
    "spec-drift-sync": {"scripts/check.py"},
    "spec-evolution": {"scripts/record.py", "scripts/timeline.py"},
}


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    block = text.split("---\n", 2)[1]
    return {
        key.strip(): value.strip().strip('"')
        for line in block.splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }


class AgentArchitectureTests(unittest.TestCase):
    def test_exactly_three_skills_are_discoverable(self) -> None:
        actual = {
            path.name
            for path in SKILLS_ROOT.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        self.assertEqual(actual, EXPECTED_SKILLS)

    def test_claude_code_discovers_the_same_three_skills(self) -> None:
        actual = {
            path.name
            for path in CLAUDE_SKILLS_ROOT.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        self.assertEqual(actual, EXPECTED_SKILLS)

    def test_claude_skill_mirror_matches_canonical_content(self) -> None:
        canonical = {
            str(path.relative_to(SKILLS_ROOT)): path.read_bytes()
            for path in SKILLS_ROOT.rglob("*")
            if path.is_file()
        }
        claude = {
            str(path.relative_to(CLAUDE_SKILLS_ROOT)): path.read_bytes()
            for path in CLAUDE_SKILLS_ROOT.rglob("*")
            if path.is_file()
        }
        canonical["spec-request-flow/SKILL.md"] = canonical[
            "spec-request-flow/SKILL.md"
        ].replace(b"AGENTS.md", b"CLAUDE.md")
        self.assertEqual(claude, canonical)

    def test_skill_frontmatter_is_minimal_and_trigger_focused(self) -> None:
        for name in sorted(EXPECTED_SKILLS):
            metadata = frontmatter(SKILLS_ROOT / name / "SKILL.md")
            self.assertEqual(set(metadata), {"name", "description"}, name)
            self.assertEqual(metadata["name"], name)
            self.assertTrue(metadata["description"].startswith("Use when"), name)
            self.assertLessEqual(len(metadata["description"]), 500, name)

    def test_each_resource_has_one_skill_owner(self) -> None:
        for name, resources in REQUIRED_RESOURCES.items():
            for resource in resources:
                self.assertTrue(
                    (SKILLS_ROOT / name / resource).is_file(),
                    f"missing {name}/{resource}",
                )

        owned_files: dict[str, str] = {}
        for skill in EXPECTED_SKILLS:
            root = SKILLS_ROOT / skill
            for path in root.rglob("*"):
                if not path.is_file() or path.name == "SKILL.md":
                    continue
                relative = str(path.relative_to(root))
                content = path.read_bytes().hex()
                previous = owned_files.setdefault(content, f"{skill}/{relative}")
                self.assertEqual(
                    previous,
                    f"{skill}/{relative}",
                    f"duplicate resource content: {previous} and {skill}/{relative}",
                )

    def test_request_flow_routes_to_drift_and_evolution(self) -> None:
        text = (SKILLS_ROOT / "spec-request-flow/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("spec-drift-sync", text)
        self.assertIn("spec-evolution", text)
        self.assertIn("SPEC.md", text)
        self.assertIn("spec/features/<feature-slug>", text)
        self.assertIn("scripts/create_feature.py", text)

    def test_agents_file_is_a_concise_router(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("SPEC.md", text)
        for name in EXPECTED_SKILLS:
            self.assertIn(name, text)
        self.assertLessEqual(len(text.split()), 220)

    def test_claude_file_is_an_equivalent_concise_router(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(
            claude,
            agents.replace(".agents/skills", ".claude/skills"),
        )
        self.assertLessEqual(len(claude.split()), 220)

    def test_agents_file_contains_mandatory_code_agent_traceability_contract(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for term in (
            "Code Agent contract",
            "spec: BEHAVIOR-ID",
            "production code and tests",
            "spec-agent traceability-sync",
            "spec-agent validate",
            "MUST NOT claim completion",
        ):
            self.assertIn(term, text)

    def test_spec_md_indexes_feature_spec_packets(self) -> None:
        self.assertTrue((ROOT / "SPEC.md").is_file())
        root_spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        self.assertIn("spec/features/feature-spec-packets/spec.md", root_spec)
        for packet in (ROOT / "spec/features").iterdir():
            if not packet.is_dir():
                continue
            self.assertEqual(
                {path.name for path in packet.glob("*.md")},
                {"spec.md", "acceptance.md"},
                packet.name,
            )
            for artifact in (packet / "spec.md", packet / "acceptance.md"):
                self.assertIn(str(artifact.relative_to(ROOT)), root_spec)
        self.assertFalse(
            (SKILLS_ROOT / "spec-request-flow/assets/feature-design.template.md").exists()
        )
        self.assertFalse(
            (SKILLS_ROOT / "spec-request-flow/assets/feature-plan.template.md").exists()
        )

    def test_evolution_uses_one_jsonl_source(self) -> None:
        self.assertTrue((ROOT / "spec/evolution/events.jsonl").is_file())
        self.assertFalse((ROOT / "spec/evolution/events").exists())
        self.assertFalse((SKILLS_ROOT / "spec-evolution/assets/event.md").exists())

    def test_no_obsolete_sources_remain(self) -> None:
        obsolete = (
            ROOT / "scripts",
            ROOT / "docs",
            ROOT / "evolution",
        )
        self.assertEqual(
            [str(path.relative_to(ROOT)) for path in obsolete if path.exists()],
            [],
        )

    def test_discovery_tree_contains_no_generated_cache(self) -> None:
        artifacts = [
            path.relative_to(ROOT)
            for root in (SKILLS_ROOT, CLAUDE_SKILLS_ROOT)
            for path in root.rglob("*")
            if path.name == "__pycache__" or path.suffix == ".pyc"
        ]
        self.assertEqual(artifacts, [])


if __name__ == "__main__":
    unittest.main()
