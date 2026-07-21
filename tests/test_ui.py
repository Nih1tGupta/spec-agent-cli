from __future__ import annotations

# spec: UI-001, UI-002, UI-003, UI-004, UI-005, UI-006

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spec_agent.ui import build_snapshot, render_dashboard  # noqa: E402


def test_snapshot_exposes_packets_events_traceability_and_recent_changes(tmp_path: Path) -> None:
    (tmp_path / "SPEC.md").write_text(
        """---\ntitle: Demo Project\nstatus: approved\n---\n\n# Demo Project\n\nDemo product.\n""",
        encoding="utf-8",
    )
    packet = tmp_path / "spec/packets/payments"
    packet.mkdir(parents=True)
    (packet / "spec.md").write_text(
        """---\nid: PAY\ntitle: Payments\nstatus: approved\n---\n\n# Payments\n\nPAY-001: Payments are authorized before capture.\n""",
        encoding="utf-8",
    )
    (packet / "acceptance.md").write_text(
        """# Payments Acceptance\n\n- AC-PAY-001: Authorization succeeds.\n""",
        encoding="utf-8",
    )
    events = tmp_path / "spec/evolution/events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text(
        json.dumps(
            {
                "id": "EV-1",
                "timestamp": "2026-07-20T10:00:00Z",
                "title": "Approve payments",
                "task_type": "spec-approval",
                "user_intent": "Define payment authorization.",
                "behavior_ids": ["PAY-001"],
                "status": "completed",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "spec/traceability.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "baseline_commit": None,
                "source": "derived-from-code-backlinks",
                "behaviors": {
                    "PAY-001": {
                        "backlinks": [{"path": "src/payments.py", "line": 4}],
                        "files": ["src/payments.py"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    snapshot = build_snapshot(tmp_path)

    assert snapshot["project"]["title"] == "Demo Project"
    assert snapshot["packets"][0]["slug"] == "payments"
    assert snapshot["packets"][0]["behavior_ids"] == ["PAY-001"]
    assert snapshot["events"][0]["id"] == "EV-1"
    assert snapshot["traceability"]["behavior_count"] == 1
    assert snapshot["traceability"]["linked_file_count"] == 1


def test_dashboard_contains_react_shell_and_workspace_markers() -> None:
    html = render_dashboard()

    for marker in (
        'id="root"',
        "/assets/",
        "Spec Agent",
        "Specification workspace",
    ):
        assert marker in html

    assets = Path(__file__).resolve().parents[1] / "src/spec_agent/ui_assets"
    assert (assets / "index.html").is_file()
    assert any(assets.glob("assets/*.js")), "React bundle JS missing"
    assert any(assets.glob("assets/*.css")), "React bundle CSS missing"
    assert (assets / "ui_assets/potpie-logo.jpeg").is_file()
