"""Read-only local dashboard for specification, evolution, and traceability data."""

# spec: UI-001, UI-002, UI-003, UI-004, UI-006, UI-007, UI-008

from __future__ import annotations

import hashlib
import html
import json
import mimetypes
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


BEHAVIOR_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}\b")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
PR_REF = re.compile(r"(?:#|!\s*|/\s*pull\s*/)(\d+)\b")
MAX_FILE_BYTES = 300_000
UI_ASSETS = Path(__file__).with_name("ui_assets")


def build_snapshot(repo_root: Path | str) -> dict[str, Any]:
    """Build a JSON-serializable, read-only view of a repository."""
    root = Path(repo_root).resolve()
    git_root = _git_root(root)
    remote = _git_remote(git_root or root)
    web_base = _web_base(remote)
    packets = _load_packets(root)
    events, event_errors = _load_events(root / "spec/evolution/events.jsonl")
    traceability, traceability_error = _load_traceability(root / "spec/traceability.json")
    drift = _load_drift(root)
    changes = _load_changes(root, git_root, web_base)
    backlinks = _traceability_backlinks(traceability, root)
    path_links = {
        behavior_id: sorted({item["path"] for item in items})
        for behavior_id, items in backlinks.items()
    }
    drift_by_behavior = _drift_by_behavior(drift)

    for packet in packets:
        ids = set(packet["behavior_ids"])
        packet["linked_files"] = sorted(
            {path for behavior_id in ids for path in path_links.get(behavior_id, [])}
        )
        packet["behavior_links"] = {
            behavior_id: path_links.get(behavior_id, [])
            for behavior_id in sorted(ids)
        }
        packet["behavior_backlinks"] = {
            behavior_id: backlinks.get(behavior_id, [])
            for behavior_id in sorted(ids)
        }
        packet["events"] = [
            event["id"]
            for event in events
            if ids.intersection(event.get("behavior_ids", []))
        ]
        packet["event_details"] = [
            event
            for event in events
            if ids.intersection(event.get("behavior_ids", []))
        ]
        packet["provenance"] = {
            "spec": _git_file_provenance(
                root, git_root, f"{packet['source_dir']}/spec.md", web_base
            ),
            "acceptance": _git_file_provenance(
                root, git_root, f"{packet['source_dir']}/acceptance.md", web_base
            ),
        }
        packet["coverage"] = _packet_coverage(
            packet, events, drift_by_behavior, backlinks
        )
        packet["open_follow_ups"] = [
            {
                "event_id": event.get("id", ""),
                "follow_ups": event.get("follow_ups", ""),
                "actor": event.get("actor", ""),
                "timestamp": event.get("timestamp", ""),
            }
            for event in packet["event_details"]
            if str(event.get("follow_ups") or "").strip()
        ]

    linked_files = sorted({item["path"] for items in backlinks.values() for item in items})
    baseline = (traceability or {}).get("baseline_commit") if traceability else None
    hash_mismatches = sum(
        1 for items in backlinks.values() for item in items if item.get("hash_ok") is False
    )

    return {
        "project": {
            **_project_summary(root),
            "remote": remote,
            "web_base": web_base,
            "git_root": str(git_root) if git_root else None,
            "head_commit": _git_head(git_root or root),
        },
        "packets": packets,
        "events": events,
        "recent_changes": changes,
        "drift": drift,
        "traceability": {
            "available": traceability is not None,
            "error": traceability_error,
            "behavior_count": len(backlinks),
            "linked_file_count": len(linked_files),
            "baseline_commit": baseline,
            "baseline_url": _commit_url(web_base, str(baseline)) if baseline else None,
            "hash_mismatches": hash_mismatches,
            "links": path_links,
            "backlinks": backlinks,
        },
        "warnings": event_errors,
    }


def render_dashboard() -> str:
    """Return the bundled dashboard HTML for tests and the HTTP server."""
    asset = UI_ASSETS / "index.html"
    return asset.read_text(encoding="utf-8")


def serve_dashboard(
    repo_root: Path | str,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    open_browser: bool = True,
) -> int:
    """Serve the dashboard until interrupted and return the bound port."""
    root = Path(repo_root).resolve()
    snapshot = lambda: build_snapshot(root)

    class DashboardHandler(BaseHTTPRequestHandler):
        server_version = "SpecAgentUI/1.0"

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = unquote(parsed.path)

            if path == "/api/snapshot":
                self._send_json(snapshot())
                return
            if path == "/api/file":
                self._send_file(parse_qs(parsed.query).get("path", [""])[0])
                return
            if path in {"/", "/index.html"}:
                self._send_text(render_dashboard(), "text/html; charset=utf-8")
                return
            if path.startswith("/assets/") or path.startswith("/ui_assets/"):
                self._send_static(path.lstrip("/"))
                return
            self.send_error(404, "Not found")

        def _send_json(self, payload: Any) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_text(self, body: str, content_type: str) -> None:
            encoded = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _send_file(self, relative: str) -> None:
            if not relative:
                self.send_error(400, "Missing path")
                return
            candidate = (root / relative).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                self.send_error(403, "Path is outside the repository")
                return
            if not candidate.is_file() or candidate.stat().st_size > MAX_FILE_BYTES:
                self.send_error(404, "File unavailable")
                return
            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.send_error(404, "File unavailable")
                return
            self._send_text(content, "text/plain; charset=utf-8")

        def _send_static(self, relative: str) -> None:
            asset = (UI_ASSETS / relative).resolve()
            try:
                asset.relative_to(UI_ASSETS.resolve())
            except ValueError:
                self.send_error(403, "Asset unavailable")
                return
            if not asset.is_file():
                self.send_error(404, "Asset unavailable")
                return
            content_type = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
            if asset.suffix == ".js":
                content_type = "text/javascript; charset=utf-8"
            elif asset.suffix == ".css":
                content_type = "text/css; charset=utf-8"
            body = asset.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer((host, port), DashboardHandler)
    address = f"http://{host}:{server.server_port}/"
    print(f"Spec Agent UI: {address}")
    print(f"Repository: {root}")
    print("Read-only dashboard. Press Ctrl-C to stop.")
    if open_browser:
        threading.Timer(0.15, lambda: webbrowser.open(address)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return server.server_port


def _project_summary(root: Path) -> dict[str, Any]:
    text = _read(root / "SPEC.md")
    metadata = _frontmatter(text)
    title = metadata.get("title") or _first_heading(text) or root.name
    return {"title": title, "status": metadata.get("status", "unknown"), "path": str(root)}


def _load_packets(root: Path) -> list[dict[str, Any]]:
    packet_root = root / "spec/packets"
    if not packet_root.is_dir():
        packet_root = root / "spec/features"
    if not packet_root.is_dir():
        return []
    result: list[dict[str, Any]] = []
    for directory in sorted(path for path in packet_root.iterdir() if path.is_dir()):
        spec_text = _read(directory / "spec.md")
        acceptance_text = _read(directory / "acceptance.md")
        meta = _frontmatter(spec_text)
        behavior_ids = sorted(set(BEHAVIOR_ID.findall(spec_text)))
        result.append(
            {
                "slug": directory.name,
                "source_dir": str(directory.relative_to(root)),
                "title": meta.get("title") or _first_heading(spec_text) or directory.name,
                "status": meta.get("status", "draft"),
                "created": meta.get("created", ""),
                "behavior_ids": behavior_ids,
                "spec": spec_text,
                "acceptance": acceptance_text,
                "linked_files": [],
                "events": [],
            }
        )
    return result


def _load_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.is_file():
        return [], []
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"Evolution log line {line_number}: {error.msg}")
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            errors.append(f"Evolution log line {line_number}: expected object, got {type(value).__name__}")
    events.sort(key=lambda event: str(event.get("timestamp", "")), reverse=True)
    return events, errors


def _load_traceability(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, "Traceability index is not present"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, f"Traceability index could not be read: {error}"
    return (value, None) if isinstance(value, dict) else (None, "Traceability index is not an object")


def _traceability_backlinks(
    traceability: dict[str, Any] | None, root: Path
) -> dict[str, list[dict[str, Any]]]:
    if not traceability:
        return {}
    result: dict[str, list[dict[str, Any]]] = {}
    for behavior_id, value in (traceability.get("behaviors") or {}).items():
        entries: list[dict[str, Any]] = []
        raw_items: list[Any] = []
        if isinstance(value, list):
            raw_items = value
        elif isinstance(value, dict):
            raw_items.extend(value.get("backlinks", []) or [])
            for path in value.get("files", []) or []:
                if isinstance(path, str):
                    raw_items.append({"path": path})

        seen: set[tuple[str, int | None]] = set()
        for item in raw_items:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                continue
            path = item["path"]
            line = item.get("line")
            line_number = int(line) if isinstance(line, int) or (isinstance(line, str) and line.isdigit()) else None
            key = (path, line_number)
            if key in seen:
                continue
            seen.add(key)
            indexed_hash = item.get("file_sha256") if isinstance(item.get("file_sha256"), str) else None
            current_hash = _file_sha256(root / path)
            hash_ok = None if not indexed_hash or not current_hash else indexed_hash == current_hash
            entries.append(
                {
                    "path": path,
                    "line": line_number,
                    "file_sha256": indexed_hash,
                    "current_sha256": current_hash,
                    "hash_ok": hash_ok,
                }
            )
        entries.sort(key=lambda entry: (entry["path"], entry["line"] or 0))
        result[str(behavior_id)] = entries
    return result


def _packet_coverage(
    packet: dict[str, Any],
    events: list[dict[str, Any]],
    drift_by_behavior: dict[str, list[dict[str, Any]]],
    backlinks: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for behavior_id in packet["behavior_ids"]:
        links = backlinks.get(behavior_id, [])
        drift_issues = drift_by_behavior.get(behavior_id, [])
        related = [
            event
            for event in events
            if behavior_id in (event.get("behavior_ids") or [])
        ]
        last_event = related[0] if related else None
        mismatches = sum(1 for item in links if item.get("hash_ok") is False)
        if drift_issues:
            status = "drift"
        elif not links:
            status = "unlinked"
        elif mismatches:
            status = "stale"
        else:
            status = "linked"
        rows.append(
            {
                "behavior_id": behavior_id,
                "file_count": len({item["path"] for item in links}),
                "link_count": len(links),
                "hash_mismatches": mismatches,
                "drift_count": len(drift_issues),
                "last_event_id": (last_event or {}).get("id", ""),
                "last_event_at": (last_event or {}).get("timestamp", ""),
                "status": status,
            }
        )
    return rows


def _drift_by_behavior(drift: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for issue in drift.get("issues") or []:
        behavior_id = str(issue.get("behavior_id") or "unknown")
        result.setdefault(behavior_id, []).append(issue)
    return result


def _load_drift(root: Path) -> dict[str, Any]:
    checker = root / ".agents/skills/spec-drift-sync/scripts/check.py"
    if not checker.is_file():
        return {"status": "unavailable", "issues": []}
    try:
        completed = subprocess.run(
            [sys.executable, str(checker), "check", "--repo", str(root), "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        raw = completed.stdout.strip() or completed.stderr.strip()
        if not raw:
            return {
                "status": "error",
                "issues": [],
                "error": f"Drift checker exited {completed.returncode} with no output",
            }
        report = json.loads(raw)
        issues = [
            {
                "kind": issue.get("kind", "unknown"),
                "behavior_id": issue.get("behavior_id", "unknown"),
                "message": issue.get("message", ""),
                "location": issue.get("code_file") or issue.get("spec_file") or "",
            }
            for issue in report.get("issues", [])
        ]
        return {"status": "clean" if not issues else "drift", "issues": issues}
    except Exception as error:  # dashboard must remain usable if optional evidence is broken
        return {"status": "error", "issues": [], "error": str(error)}


def _load_changes(
    root: Path, git_root: Path | None, web_base: str | None
) -> list[dict[str, Any]]:
    if git_root is None:
        return []
    rel_prefix = _path_relative_to(root, git_root)
    spec_paths = [
        f"{rel_prefix}/spec" if rel_prefix else "spec",
        f"{rel_prefix}/SPEC.md" if rel_prefix else "SPEC.md",
        "spec",
        "SPEC.md",
    ]
    # Preserve order while dropping duplicates.
    seen_paths: set[str] = set()
    unique_paths: list[str] = []
    for path in spec_paths:
        if path not in seen_paths:
            seen_paths.add(path)
            unique_paths.append(path)

    try:
        output = subprocess.check_output(
            [
                "git",
                "--no-pager",
                "log",
                "-12",
                "--date=short",
                "--pretty=format:%H%x09%h%x09%ad%x09%an%x09%s",
                "--",
                *unique_paths,
            ],
            cwd=git_root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    if not output.strip():
        try:
            output = subprocess.check_output(
                [
                    "git",
                    "--no-pager",
                    "log",
                    "-8",
                    "--date=short",
                    "--pretty=format:%H%x09%h%x09%ad%x09%an%x09%s",
                ],
                cwd=git_root,
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError):
            return []

    changes: list[dict[str, Any]] = []
    for line in output.splitlines():
        full, short_id, date, author, subject = (line.split("\t", 4) + ["", "", "", "", ""])[:5]
        pr_match = PR_REF.search(subject)
        pr_number = pr_match.group(1) if pr_match else None
        changes.append(
            {
                "id": short_id,
                "full_id": full,
                "date": date,
                "author": author,
                "subject": subject,
                "url": _commit_url(web_base, full),
                "pr_number": pr_number,
                "pr_url": f"{web_base}/pull/{pr_number}" if web_base and pr_number else None,
            }
        )
    return changes


def _git_file_provenance(
    root: Path, git_root: Path | None, relative: str, web_base: str | None
) -> dict[str, Any] | None:
    if git_root is None or not (root / relative).is_file():
        return None
    git_relative = _path_relative_to(root / relative, git_root)
    if git_relative is None:
        return None
    try:
        output = subprocess.check_output(
            [
                "git",
                "--no-pager",
                "log",
                "-1",
                "--date=iso-strict",
                "--pretty=format:%H%x09%h%x09%an%x09%ae%x09%ad%x09%s",
                "--",
                git_relative,
            ],
            cwd=git_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    if not output:
        return None
    full, short_id, author, email, date, subject = (output.split("\t", 5) + [""] * 6)[:6]
    pr_match = PR_REF.search(subject)
    pr_number = pr_match.group(1) if pr_match else None
    return {
        "path": relative,
        "author": author,
        "email": email,
        "date": date,
        "commit": short_id,
        "full_commit": full,
        "subject": subject,
        "url": _commit_url(web_base, full),
        "pr_number": pr_number,
        "pr_url": f"{web_base}/pull/{pr_number}" if web_base and pr_number else None,
    }


def _git_root(start: Path) -> Path | None:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(value).resolve() if value else None


def _path_relative_to(path: Path, base: Path) -> str | None:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return None


def _git_remote(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def _git_head(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def _web_base(remote: str | None) -> str | None:
    if not remote:
        return None
    value = remote.strip()
    if value.startswith("git@"):
        # git@github.com:org/repo.git
        value = value.split(":", 1)[-1]
        value = "https://github.com/" + value
    value = re.sub(r"\.git$", "", value)
    if value.startswith("https://") or value.startswith("http://"):
        return value.rstrip("/")
    return None


def _commit_url(web_base: str | None, commit: str | None) -> str | None:
    if not web_base or not commit:
        return None
    return f"{web_base}/commit/{commit}"


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("'\"")
    return result


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    except OSError:
        return ""


def safe_html(value: Any) -> str:
    """Escape user-controlled repository text for callers rendering HTML."""
    return html.escape(str(value), quote=True)
