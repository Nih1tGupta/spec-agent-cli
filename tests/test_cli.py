from __future__ import annotations

import sys
from pathlib import Path

# spec: CLI-001, CLI-007, TRACE-003, TRACE-008, TRACE-012, CCD-001, CCD-005


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spec_agent.cli import main


def test_cli_version(capsys) -> None:
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.startswith("spec-agent ")


def test_cli_init_and_check(tmp_path: Path) -> None:
    assert main(["init", "--repo", str(tmp_path)]) == 0
    assert main(["init", "--repo", str(tmp_path), "--check"]) == 0
    assert (tmp_path / ".agents/skills/spec-request-flow/SKILL.md").is_file()
    assert (tmp_path / ".claude/skills/spec-request-flow/SKILL.md").is_file()
    assert (tmp_path / "CLAUDE.md").is_file()


def test_cli_traceability_sync_and_validate_detect_later_code_change(tmp_path: Path) -> None:
    assert main(["init", "--repo", str(tmp_path)]) == 0
    (tmp_path / "SPEC.md").write_text(
        "---\nstatus: approved\n---\n\nFEATURE-001: Feature works.\n",
        encoding="utf-8",
    )
    code = tmp_path / "service.py"
    code.write_text("# spec: FEATURE-001\nvalue = 1\n", encoding="utf-8")

    assert main(["traceability-sync", "--repo", str(tmp_path)]) == 0
    before_validation = {
        str(path.relative_to(tmp_path)): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert main(["validate", "--repo", str(tmp_path)]) == 0
    after_validation = {
        str(path.relative_to(tmp_path)): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after_validation == before_validation

    code.write_text("# spec: FEATURE-001\nvalue = 2\n", encoding="utf-8")
    assert main(["validate", "--repo", str(tmp_path)]) == 1
