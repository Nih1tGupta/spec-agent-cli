"""Read canonical Spec Agent assets in source checkouts and built wheels."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any


# spec: CCD-003, CCD-004, CCD-008, SA-025, SA-027
CLAUDE_ADAPTATIONS = {
    "spec-request-flow/SKILL.md": ((b"AGENTS.md", b"CLAUDE.md"),),
}


def _development_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _embedded_root() -> Any:
    return files("spec_agent").joinpath("resources")


def skill_root() -> Any:
    embedded = _embedded_root().joinpath("skills")
    if embedded.is_dir():
        return embedded
    return _development_root() / ".agents/skills"


def rules_text() -> str:
    embedded = _embedded_root().joinpath("project-rules.md")
    if embedded.is_file():
        return embedded.read_text(encoding="utf-8")
    return (_development_root() / "AGENTS.md").read_text(encoding="utf-8")


def claude_rules_text() -> str:
    """Return the canonical router adapted to Claude Code discovery."""
    return rules_text().replace(".agents/skills", ".claude/skills")


def project_spec_template() -> str:
    return (
        skill_root()
        .joinpath("spec-request-flow")
        .joinpath("assets")
        .joinpath("SPEC.template.md")
        .read_text(encoding="utf-8")
    )


def skill_files() -> dict[str, bytes]:
    result: dict[str, bytes] = {}

    def visit(directory: Any, prefix: PurePosixPath) -> None:
        for entry in sorted(directory.iterdir(), key=lambda item: item.name):
            if entry.name == "__pycache__" or entry.name.endswith((".pyc", ".pyo")):
                continue
            relative = prefix / entry.name
            if entry.is_dir():
                visit(entry, relative)
            elif entry.is_file():
                result[str(relative)] = entry.read_bytes()

    visit(skill_root(), PurePosixPath())
    return result


def claude_skill_files() -> dict[str, bytes]:
    """Generate Claude Code skills from the canonical open-agent tree."""
    result = skill_files()
    for relative, replacements in CLAUDE_ADAPTATIONS.items():
        content = result[relative]
        for original, replacement in replacements:
            content = content.replace(original, replacement)
        result[relative] = content
    return result
