"""Run the installed read-only drift checker and traceability refresh."""

# spec: SA-020, SA-022, TRACE-003, TRACE-008, TRACE-009, TRACE-012

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _checker(repo_root: Path) -> Path:
    return repo_root / ".agents/skills/spec-drift-sync/scripts/check.py"


def _run(repo_root: Path, command: str) -> int:
    root = repo_root.resolve()
    checker = _checker(root)
    if not checker.is_file():
        print("Spec Agent drift checker is missing. Run 'spec-agent init' first.")
        return 2
    arguments = [sys.executable, str(checker), command, "--repo", str(root)]
    if command == "sync":
        arguments.extend(["--output", "spec/traceability.json"])
    return subprocess.run(arguments, check=False).returncode


def cmd_validate(repo_root: Path) -> int:
    """Validate current specs, backlinks, and traceability without writes."""
    return _run(repo_root, "check")


def cmd_traceability_sync(repo_root: Path) -> int:
    """Accept current approved backlink evidence as the derived baseline."""
    return _run(repo_root, "sync")
