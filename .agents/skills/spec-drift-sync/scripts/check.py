#!/usr/bin/env python3
"""Dependency-free structural specification/code drift checker."""

# spec: SA-013, SA-014, SA-015

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


UPPER_ID = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}):\s*(.*)$")
SLUG_ID = re.compile(r"^((?:[CQ]:)?[a-z][a-z0-9]*(?:-[a-z0-9]+)+):\s*(.*)$")
CODE_REF = re.compile(r"^\s*~\s+(.+?)\s*$")
COMMENT = re.compile(r"(?:#|//|/\*|\*)\s*spec:\s*([^#/*\n]*)", re.I)
TOKEN = re.compile(
    r"^(?:(?:[CQ]:)?[a-z][a-z0-9]*(?:-[a-z0-9]+)+|"
    r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3})$"
)
SKIP_DIRS = {
    ".git",
    ".spec",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "evolution",
}
SKIP_FILES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}


@dataclass(frozen=True)
class SpecEntry:
    behavior_id: str
    statement: str
    spec_file: str
    line: int
    planned: bool
    code_status: str | None
    code_refs: tuple[str, ...]
    verified_commit: str | None


@dataclass(frozen=True)
class CodeBacklink:
    behavior_id: str
    code_file: str
    line: int


@dataclass(frozen=True)
class DriftIssue:
    kind: str
    behavior_id: str
    message: str
    spec_file: str | None = None
    code_file: str | None = None
    line: int | None = None
    ref: str | None = None


@dataclass(frozen=True)
class DriftReport:
    repo_root: str
    spec_root: str
    entries: tuple[SpecEntry, ...]
    backlinks: tuple[CodeBacklink, ...]
    issues: tuple[DriftIssue, ...]

    @property
    def clean(self) -> bool:
        return not self.issues


def analyze_repo(
    repo_root: Path | str, spec_root: Path | str | None = None
) -> DriftReport:
    repo = Path(repo_root).resolve()
    specs = _resolve_spec_sources(repo, spec_root)
    entries = tuple(
        entry for source in specs for entry in parse_spec_entries(source, repo)
    )
    backlinks = tuple(scan_code_backlinks(repo))
    known = {entry.behavior_id: entry for entry in entries}
    by_id: dict[str, list[CodeBacklink]] = {}
    for backlink in backlinks:
        by_id.setdefault(backlink.behavior_id, []).append(backlink)

    issues: list[DriftIssue] = []
    for backlink in backlinks:
        if not _entry_exists(backlink.behavior_id, known):
            issues.append(
                DriftIssue(
                    "phantom",
                    backlink.behavior_id,
                    "code backlink has no spec entry",
                    code_file=backlink.code_file,
                    line=backlink.line,
                )
            )
    for entry in entries:
        for ref in entry.code_refs:
            path = ref.split(":", 1)[0]
            if not (repo / path).exists():
                issues.append(
                    DriftIssue(
                        "dead-ref",
                        entry.behavior_id,
                        "spec code reference does not exist",
                        spec_file=entry.spec_file,
                        line=entry.line,
                        ref=ref,
                    )
                )
        if entry.planned and entry.behavior_id in by_id:
            link = by_id[entry.behavior_id][0]
            issues.append(
                DriftIssue(
                    "silent-implementation",
                    entry.behavior_id,
                    "planned behavior already has a code backlink",
                    spec_file=entry.spec_file,
                    code_file=link.code_file,
                    line=link.line,
                )
            )
        if (
            not entry.planned
            and entry.code_status != "not_applicable"
            and not entry.code_refs
            and entry.behavior_id not in by_id
        ):
            issues.append(
                DriftIssue(
                    "unlinked",
                    entry.behavior_id,
                    "accepted behavior has no trace link",
                    spec_file=entry.spec_file,
                    line=entry.line,
                )
            )
        if entry.verified_commit and _is_git_repo(repo):
            for ref in entry.code_refs:
                path = ref.split(":", 1)[0]
                if _git(
                    repo,
                    ["log", "--format=%H", f"{entry.verified_commit}..HEAD", "--", path],
                ):
                    issues.append(
                        DriftIssue(
                            "stale-verification",
                            entry.behavior_id,
                            "linked code changed after verification",
                            spec_file=entry.spec_file,
                            line=entry.line,
                            ref=ref,
                        )
                    )

    return DriftReport(
        str(repo),
        " | ".join(str(source) for source in specs),
        entries,
        backlinks,
        tuple(issues),
    )


def parse_spec_entries(spec_root: Path, repo_root: Path) -> Iterable[SpecEntry]:
    paths = [spec_root] if spec_root.is_file() else sorted(spec_root.rglob("*.md"))
    for path in paths:
        if "evolution" in path.parts:
            continue
        text = _read(path)
        verified = _frontmatter(text, "verified_commit")
        code_status = _frontmatter(text, "code_status")
        lines = text.splitlines()
        index = 0
        while index < len(lines):
            match = UPPER_ID.match(lines[index]) or SLUG_ID.match(lines[index])
            if not match:
                index += 1
                continue
            refs: list[str] = []
            cursor = index + 1
            while cursor < len(lines) and not (
                UPPER_ID.match(lines[cursor]) or SLUG_ID.match(lines[cursor])
            ):
                ref = CODE_REF.match(lines[cursor])
                if ref:
                    refs.append(ref.group(1).strip())
                cursor += 1
            statement = match.group(2).strip()
            yield SpecEntry(
                match.group(1),
                statement,
                _relative(path, repo_root),
                index + 1,
                "[planned]" in statement.lower(),
                code_status,
                tuple(refs),
                verified,
            )
            index = cursor


def scan_code_backlinks(repo_root: Path) -> Iterable[CodeBacklink]:
    for path in sorted(repo_root.rglob("*")):
        if _skip(path):
            continue
        for number, line in enumerate(_read(path).splitlines(), 1):
            visible = _mask_strings(line)
            for match in COMMENT.finditer(visible):
                for raw in match.group(1).replace(",", " ").split():
                    token = raw.strip().strip("`'\"").rstrip(".,;")
                    if TOKEN.match(token):
                        yield CodeBacklink(token, _relative(path, repo_root), number)


def write_traceability(report: DriftReport, output: Path | str) -> dict[str, object]:
    """Write a deterministic, non-normative index derived from code backlinks."""
    target = Path(output)
    behaviors: dict[str, list[dict[str, object]]] = {}
    for backlink in sorted(
        report.backlinks,
        key=lambda item: (item.behavior_id, item.code_file, item.line),
    ):
        behaviors.setdefault(backlink.behavior_id, []).append(
            {"path": backlink.code_file, "line": backlink.line}
        )
    document: dict[str, object] = {
        "schema_version": 1,
        "source": "derived-from-code-backlinks",
        "behaviors": behaviors,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return document


def render_text(report: DriftReport) -> str:
    if report.clean:
        return "=== SPEC-AGENT DRIFT CHECK ===\n\nCLEAN\n  - no structural drift detected"
    lines = [
        "=== SPEC-AGENT DRIFT CHECK ===",
        "",
        f"DRIFT SUMMARY: {len(report.issues)} item(s)",
    ]
    for issue in report.issues:
        location = issue.code_file or issue.spec_file or ""
        lines.append(
            f"  - {issue.kind}: {issue.behavior_id}: {issue.message} {location}".rstrip()
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check structural spec/code drift.")
    sub = parser.add_subparsers(dest="command")
    check = sub.add_parser("check")
    check.add_argument("--repo", default=".")
    check.add_argument("--spec-root")
    check.add_argument("--json", action="store_true")
    sync = sub.add_parser("sync")
    sync.add_argument("--repo", default=".")
    sync.add_argument("--spec-root")
    sync.add_argument("--output", default="spec/traceability.json")
    args = parser.parse_args(argv)
    if args.command not in {"check", "sync"}:
        parser.print_help()
        return 2
    try:
        report = analyze_repo(args.repo, args.spec_root)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"error: {error}")
        return 2
    if args.command == "sync":
        output = Path(args.output)
        if not output.is_absolute():
            output = Path(args.repo).resolve() / output
        try:
            write_traceability(report, output)
        except OSError as error:
            print(f"error: {error}")
            return 2
        print(output)
        return 0
    print(json.dumps(asdict(report), indent=2) if args.json else render_text(report))
    return 0 if report.clean else 1


def _resolve_spec_sources(
    repo: Path, spec_root: Path | str | None
) -> tuple[Path, ...]:
    if spec_root is not None:
        candidate = Path(spec_root)
        candidate = candidate if candidate.is_absolute() else repo / candidate
        if not candidate.exists() or not (candidate.is_file() or candidate.is_dir()):
            raise FileNotFoundError(f"spec source does not exist: {candidate}")
        return (candidate.resolve(),)
    root_spec = repo / "SPEC.md"
    if root_spec.is_file():
        sources = [root_spec.resolve()]
        spec_dir = repo / "spec"
        if spec_dir.is_dir():
            sources.append(spec_dir.resolve())
        return tuple(sources)
    for name in ("spec", "specs"):
        candidate = repo / name
        if candidate.is_dir():
            return (candidate.resolve(),)
    raise FileNotFoundError("No spec source found. Expected SPEC.md, spec/, or specs/.")


def _frontmatter(text: str, key: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    match = re.search(rf"^\s*{re.escape(key)}:\s*([^\s#]+)\s*$", parts[1], re.M)
    if not match:
        return None
    value = match.group(1).strip("'\"")
    return None if value in {"", "null", "None"} else value


def _mask_strings(line: str) -> str:
    output: list[str] = []
    quote: str | None = None
    escaped = False
    for char in line:
        if quote:
            output.append(" ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)


def _skip(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts) or path.name in SKIP_FILES:
        return True
    try:
        return not path.is_file() or path.suffix.lower() == ".md"
    except OSError:
        return True


def _entry_exists(behavior_id: str, entries: dict[str, SpecEntry]) -> bool:
    return (
        behavior_id in entries
        or f"C:{behavior_id}" in entries
        or f"Q:{behavior_id}" in entries
    )


def _is_git_repo(repo: Path) -> bool:
    return _git(repo, ["rev-parse", "--is-inside-work-tree"]) == "true"


def _git(repo: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
