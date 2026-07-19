from __future__ import annotations

import sys
from pathlib import Path

# spec: CLI-001, CLI-007


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
