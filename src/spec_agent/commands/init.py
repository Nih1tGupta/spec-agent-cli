"""Implementation of ``spec-agent init``."""

from __future__ import annotations

from pathlib import Path

from spec_agent import installer


def _print_rows(rows: list[tuple[str, str]]) -> None:
    width = max((len(path) for path, _ in rows), default=0)
    for path, status in rows:
        print(f"  {path.ljust(width)}  {status}")


def cmd_init(repo_root: Path, *, check: bool = False, force: bool = False) -> int:
    root = repo_root.resolve()
    if check:
        rows = installer.check_status(root)
        _print_rows(rows)
        valid = {"up to date", "present"}
        return 0 if all(status in valid for _, status in rows) else 1

    rows = installer.install(root, force=force)
    print(f"Spec Agent initialized in {root}")
    _print_rows(rows)
    print("")
    print("Next: ask your agent to use spec-request-flow for a feature request.")
    return 0 if all(status != installer.DAMAGED for _, status in rows) else 1
