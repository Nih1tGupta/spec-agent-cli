from __future__ import annotations

import sys
from pathlib import Path

# spec: CLI-003, CLI-004, CLI-005, CLI-006, CLI-007, CLI-008, CLI-009, CLI-010, CLI-011


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spec_agent import installer
from spec_agent.commands.init import cmd_init


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_fresh_init_installs_complete_open_agent_package(tmp_path: Path) -> None:
    assert cmd_init(tmp_path) == 0

    expected = installer.load_skill_files()
    assert expected
    for relative, content in expected.items():
        assert (tmp_path / ".agents/skills" / relative).read_bytes() == content

    assert (tmp_path / "AGENTS.md").read_text().count(installer.MARKER_START) == 1
    assert (tmp_path / "SPEC.md").is_file()
    assert (tmp_path / "spec/features").is_dir()
    assert (tmp_path / "spec/evolution/events.jsonl").read_text() == ""
    assert (tmp_path / "spec/evolution/timeline.md").is_file()
    assert (tmp_path / "spec/traceability.json").is_file()


def test_init_is_idempotent_and_preserves_project_content(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    spec = tmp_path / "SPEC.md"
    agents.write_text("# My rules\n\nKeep this.\n", encoding="utf-8")
    spec.write_text("# My product spec\n", encoding="utf-8")

    assert cmd_init(tmp_path) == 0
    before = snapshot(tmp_path)
    assert cmd_init(tmp_path) == 0

    assert snapshot(tmp_path) == before
    assert agents.read_text(encoding="utf-8").startswith("# My rules\n\nKeep this.\n")
    assert spec.read_text(encoding="utf-8") == "# My product spec\n"


def test_check_is_read_only_and_force_only_updates_managed_assets(tmp_path: Path) -> None:
    assert cmd_init(tmp_path, check=True) == 1
    assert snapshot(tmp_path) == {}

    assert cmd_init(tmp_path) == 0
    skill_relative = sorted(installer.load_skill_files())[0]
    skill = tmp_path / ".agents/skills" / skill_relative
    skill.write_text("local change\n", encoding="utf-8")
    spec = tmp_path / "SPEC.md"
    spec.write_text("# User-owned spec\n", encoding="utf-8")

    before = snapshot(tmp_path)
    assert cmd_init(tmp_path, check=True) == 1
    assert snapshot(tmp_path) == before
    assert cmd_init(tmp_path) == 0
    assert skill.read_text(encoding="utf-8") == "local change\n"

    assert cmd_init(tmp_path, force=True) == 0
    assert skill.read_bytes() == installer.load_skill_files()[skill_relative]
    assert spec.read_text(encoding="utf-8") == "# User-owned spec\n"


def test_damaged_agent_markers_are_never_rewritten(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    damaged = f"# User rules\n\n{installer.MARKER_START}\nmissing end\n"
    agents.write_text(damaged, encoding="utf-8")

    report = installer.install(tmp_path)

    assert agents.read_text(encoding="utf-8") == damaged
    assert dict(report)["AGENTS.md"] == installer.DAMAGED
    assert cmd_init(tmp_path, check=True) == 1


def test_installer_never_copies_package_self_specs_or_tests(tmp_path: Path) -> None:
    assert cmd_init(tmp_path) == 0

    installed = snapshot(tmp_path)
    assert not any(path.startswith("tests/") for path in installed)
    assert not any(path.startswith("spec/features/") for path in installed)
    assert "spec/evolution/events.jsonl" in installed
    assert "spec/traceability.json" in installed
    assert not any("__pycache__" in path or path.endswith(".pyc") for path in installed)
