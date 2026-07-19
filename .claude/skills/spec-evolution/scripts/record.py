#!/usr/bin/env python3
"""Append one validated, product-only specification evolution event."""

# spec: ELOG-001, ELOG-002, ELOG-003, ELOG-004

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


LIST_FIELDS = ("behavior_ids", "spec_files")
TEXT_DEFAULTS = {
    "actor": "agent",
    "status": "completed",
    "assumptions": "",
    "decision": "",
    "rationale": "",
    "spec_delta": "",
    "follow_ups": "",
    "supersedes": "",
}
REQUIRED_TEXT = ("id", "timestamp", "title", "task_type", "user_intent")
ENGINEERING_FIELDS = {
    "code_files",
    "evidence_refs",
    "implementation_delta",
    "drift_status",
    "drift_summary",
    "verification_result",
    "verification_summary",
}


def append_event(log: Path, event: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_event(event)
    existing_ids: set[str] = set()
    if log.exists():
        for line_number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"existing log has invalid JSON at line {line_number}") from error
            if not isinstance(value, dict):
                raise ValueError(f"existing log line {line_number} is not an object")
            event_id = value.get("id")
            if isinstance(event_id, str):
                existing_ids.add(event_id)
    if normalized["id"] in existing_ids:
        raise ValueError(f"duplicate event id: {normalized['id']}")

    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(normalized, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
    return normalized


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    forbidden = sorted(ENGINEERING_FIELDS.intersection(event))
    if forbidden:
        raise ValueError(f"engineering field is not allowed: {', '.join(forbidden)}")

    normalized: dict[str, Any] = {"schema_version": 2}
    for field in REQUIRED_TEXT:
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"missing required field: {field}")
        normalized[field] = value.strip()
    try:
        datetime.fromisoformat(normalized["timestamp"].replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("timestamp must be ISO-8601") from error
    for field, default in TEXT_DEFAULTS.items():
        value = event.get(field, default)
        if not isinstance(value, str):
            raise ValueError(f"field must be text: {field}")
        normalized[field] = value.strip()
    for field in LIST_FIELDS:
        value = event.get(field, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"field must be a string list: {field}")
        normalized[field] = [item.strip() for item in value if item.strip()]
    return normalized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=Path("spec/evolution/events.jsonl"))
    parser.add_argument("--id", required=True)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--user-intent", required=True)
    parser.add_argument("--actor", default="agent")
    parser.add_argument("--status", default="completed")
    parser.add_argument("--behavior-id", action="append", default=[])
    parser.add_argument("--spec-file", action="append", default=[])
    parser.add_argument("--assumptions", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--rationale", default="")
    parser.add_argument("--spec-delta", default="")
    parser.add_argument("--follow-ups", default="")
    parser.add_argument("--supersedes", default="")
    args = parser.parse_args(argv)
    event = vars(args)
    log = event.pop("log")
    event["task_type"] = event.pop("task_type")
    event["user_intent"] = event.pop("user_intent")
    event["behavior_ids"] = event.pop("behavior_id")
    event["spec_files"] = event.pop("spec_file")
    try:
        append_event(log, event)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
