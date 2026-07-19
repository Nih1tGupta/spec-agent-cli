"""Safely install packaged Spec Agent assets into a repository."""

# spec: CLI-002, CLI-003, CLI-004, CLI-005, CLI-006, CLI-007, CLI-008, CLI-009, CLI-010, CLI-011, SA-017, SA-018, SA-019, TRACE-005

from __future__ import annotations

import json
from pathlib import Path

from spec_agent import package_assets


MARKER_START = "<!-- spec-agent:rules:start -->"
MARKER_END = "<!-- spec-agent:rules:end -->"
DAMAGED = "damaged markers — fix or remove the spec-agent:rules markers, then re-run"

EMPTY_TIMELINE = """<!-- Generated from spec/evolution/events.jsonl by .agents/skills/spec-evolution/scripts/timeline.py; do not edit. -->
# Specification Evolution Timeline

## Mermaid

```mermaid
timeline
  title Specification Evolution
```
"""

EMPTY_TRACEABILITY = json.dumps(
    {
        "behaviors": {},
        "baseline_commit": None,
        "schema_version": 2,
        "source": "derived-from-code-backlinks",
    },
    indent=2,
    sort_keys=True,
) + "\n"


def load_skill_files() -> dict[str, bytes]:
    """Return every file from the three canonical skill directories."""
    return package_assets.skill_files()


def render_rules_block(body: str) -> str:
    return f"{MARKER_START}\n{body.strip()}\n{MARKER_END}"


def _find_block(text: str) -> tuple[int, int] | None:
    starts = text.count(MARKER_START)
    ends = text.count(MARKER_END)
    if starts == 0 and ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise ValueError("unbalanced spec-agent rules markers")
    start = text.find(MARKER_START)
    end = text.find(MARKER_END)
    if end < start:
        raise ValueError("spec-agent rules end marker precedes start marker")
    return start, end + len(MARKER_END)


def _managed_file_status(path: Path, expected: bytes) -> str:
    if not path.is_file():
        return "missing"
    return "up to date" if path.read_bytes() == expected else "outdated"


def _rules_status(path: Path, block: str) -> str:
    if not path.is_file():
        return "missing"
    text = path.read_text(encoding="utf-8")
    try:
        span = _find_block(text)
    except ValueError:
        return DAMAGED
    if span is None:
        return "missing"
    return "up to date" if text[span[0] : span[1]] == block else "outdated"


def _apply_managed_file(path: Path, expected: bytes, force: bool) -> str:
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(expected)
        return "installed"
    if path.read_bytes() == expected:
        return "up to date"
    if force:
        path.write_bytes(expected)
        return "updated"
    return "outdated (--force to update)"


def _apply_rules(path: Path, block: str) -> str:
    if not path.is_file():
        path.write_text(block + "\n", encoding="utf-8")
        return "created"
    text = path.read_text(encoding="utf-8")
    try:
        span = _find_block(text)
    except ValueError:
        return DAMAGED
    if span is None:
        updated = text.rstrip("\n") + ("\n\n" if text.strip() else "") + block + "\n"
    else:
        updated = text[: span[0]] + block + text[span[1] :]
    if updated == text:
        return "up to date"
    path.write_text(updated, encoding="utf-8")
    return "rules block added" if span is None else "updated"


def _create_file(path: Path, content: str) -> str:
    if path.exists():
        return "present"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "created"


def _create_directory(path: Path) -> str:
    if path.is_dir():
        return "present"
    path.mkdir(parents=True, exist_ok=True)
    return "created"


def _scaffold_items(repo_root: Path) -> list[tuple[str, str]]:
    return [
        ("SPEC.md", "present" if (repo_root / "SPEC.md").is_file() else "missing"),
        (
            "spec/features/",
            "present" if (repo_root / "spec/features").is_dir() else "missing",
        ),
        (
            "spec/evolution/events.jsonl",
            "present"
            if (repo_root / "spec/evolution/events.jsonl").is_file()
            else "missing",
        ),
        (
            "spec/evolution/timeline.md",
            "present"
            if (repo_root / "spec/evolution/timeline.md").is_file()
            else "missing",
        ),
        (
            "spec/traceability.json",
            "present" if (repo_root / "spec/traceability.json").is_file() else "missing",
        ),
    ]


def check_status(repo_root: Path) -> list[tuple[str, str]]:
    """Report installation state without writing anything."""
    root = repo_root.resolve()
    rows = [
        (
            f".agents/skills/{relative}",
            _managed_file_status(root / ".agents/skills" / relative, content),
        )
        for relative, content in sorted(load_skill_files().items())
    ]
    block = render_rules_block(package_assets.rules_text())
    rows.append(("AGENTS.md", _rules_status(root / "AGENTS.md", block)))
    rows.extend(_scaffold_items(root))
    return rows


def install(repo_root: Path, *, force: bool = False) -> list[tuple[str, str]]:
    """Install agent assets and scaffold missing project-owned spec files."""
    root = repo_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    rows = [
        (
            f".agents/skills/{relative}",
            _apply_managed_file(root / ".agents/skills" / relative, content, force),
        )
        for relative, content in sorted(load_skill_files().items())
    ]
    block = render_rules_block(package_assets.rules_text())
    rows.append(("AGENTS.md", _apply_rules(root / "AGENTS.md", block)))
    rows.extend(
        [
            ("SPEC.md", _create_file(root / "SPEC.md", package_assets.project_spec_template())),
            ("spec/features/", _create_directory(root / "spec/features")),
            (
                "spec/evolution/events.jsonl",
                _create_file(root / "spec/evolution/events.jsonl", ""),
            ),
            (
                "spec/evolution/timeline.md",
                _create_file(root / "spec/evolution/timeline.md", EMPTY_TIMELINE),
            ),
            (
                "spec/traceability.json",
                _create_file(root / "spec/traceability.json", EMPTY_TRACEABILITY),
            ),
        ]
    )
    return rows
