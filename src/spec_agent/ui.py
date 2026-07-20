"""Read-only local dashboard for specification, evolution, and traceability data."""

# spec: UI-001, UI-002, UI-003, UI-004, UI-006, UI-007, UI-008

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


BEHAVIOR_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}\b")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
MAX_FILE_BYTES = 300_000


def build_snapshot(repo_root: Path | str) -> dict[str, Any]:
    """Build a JSON-serializable, read-only view of a repository."""
    root = Path(repo_root).resolve()
    packets = _load_packets(root)
    events, event_errors = _load_events(root / "spec/evolution/events.jsonl")
    traceability, traceability_error = _load_traceability(root / "spec/traceability.json")
    drift = _load_drift(root)
    changes = _load_changes(root)
    behavior_links = _traceability_links(traceability)

    for packet in packets:
        ids = set(packet["behavior_ids"])
        packet["linked_files"] = sorted(
            {
                path
                for behavior_id in ids
                for path in behavior_links.get(behavior_id, [])
            }
        )
        packet["behavior_links"] = {
            behavior_id: behavior_links.get(behavior_id, [])
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

    linked_files = sorted({path for paths in behavior_links.values() for path in paths})
    return {
        "project": _project_summary(root),
        "packets": packets,
        "events": events,
        "recent_changes": changes,
        "drift": drift,
        "traceability": {
            "available": traceability is not None,
            "error": traceability_error,
            "behavior_count": len(behavior_links),
            "linked_file_count": len(linked_files),
            "links": behavior_links,
        },
        "warnings": event_errors,
    }


def render_dashboard() -> str:
    """Return the bundled dashboard HTML for tests and the HTTP server."""
    asset = Path(__file__).with_name("ui_assets") / "index.html"
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
            if parsed.path == "/":
                self._send_text(render_dashboard(), "text/html; charset=utf-8")
                return
            if parsed.path == "/api/snapshot":
                self._send_json(snapshot())
                return
            if parsed.path == "/api/file":
                self._send_file(parse_qs(parsed.query).get("path", [""])[0])
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
        behavior_ids = sorted(set(BEHAVIOR_ID.findall(spec_text)))
        result.append(
            {
                "slug": directory.name,
                "title": _frontmatter(spec_text).get("title") or _first_heading(spec_text) or directory.name,
                "status": _frontmatter(spec_text).get("status", "draft"),
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
        if isinstance(value, list):
            for backlink in value:
                if isinstance(backlink, dict) and isinstance(backlink.get("path"), str):
                    paths.append(backlink["path"])
        elif isinstance(value, dict):
            events.append(value)
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


def _traceability_links(traceability: dict[str, Any] | None) -> dict[str, list[str]]:
    if not traceability:
        return {}
    result: dict[str, list[str]] = {}
    for behavior_id, value in (traceability.get("behaviors") or {}).items():
        paths: list[str] = []
        if isinstance(value, dict):
            raw = value.get("files", [])
            if isinstance(raw, list):
                paths.extend(item for item in raw if isinstance(item, str))
            for backlink in value.get("backlinks", []):
                if isinstance(backlink, dict) and isinstance(backlink.get("path"), str):
                    paths.append(backlink["path"])
        result[str(behavior_id)] = sorted(set(paths))
    return result


def _load_drift(root: Path) -> dict[str, Any]:
    checker = root / ".agents/skills/spec-drift-sync/scripts/check.py"
    if not checker.is_file():
        return {"status": "unavailable", "issues": []}
    try:
        raw = subprocess.check_output(
            [sys.executable, str(checker), "check", "--repo", str(root), "--json"],
            cwd=root,
            text=True,
            stderr=subprocess.STDOUT,
        )
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


def _load_changes(root: Path) -> list[dict[str, str]]:
    if not (root / ".git").exists():
        return []
    try:
        output = subprocess.check_output(
            ["git", "--no-pager", "log", "-8", "--date=short", "--pretty=format:%h%x09%ad%x09%s"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    changes = []
    for line in output.splitlines():
        short_id, date, subject = (line.split("\t", 2) + ["", "", ""])[:3]
        changes.append({"id": short_id, "date": date, "subject": subject})
    return changes


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
