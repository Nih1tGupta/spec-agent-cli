#!/usr/bin/env python3
"""Render deterministic Markdown and Mermaid from an evolution JSONL log."""

# spec: ELOG-005

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple


class EvolutionEvent(NamedTuple):
    event_id: str
    timestamp: str
    source: str
    title: str
    task_type: str
    intent: str
    behavior_ids: tuple[str, ...]
    decision: str
    rationale: str
    spec_delta: str
    supersedes: str


def read_events(events_log: Path) -> list[EvolutionEvent]:
    events: list[EvolutionEvent] = []
    for line_number, line in enumerate(
        events_log.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"invalid JSONL at {events_log}: line {line_number}: {error.msg}"
            ) from error
        if not isinstance(value, dict):
            raise ValueError(
                f"invalid JSONL at {events_log}: line {line_number}: expected object"
            )
        events.append(parse_event(value, f"line {line_number}"))
    return sorted(events, key=lambda event: (_timestamp_key(event.timestamp), event.source))


def parse_event(value: dict[str, Any], source: str) -> EvolutionEvent:
    return EvolutionEvent(
        event_id=_text(value.get("id")),
        timestamp=_text(value.get("timestamp")),
        source=source,
        title=_text(value.get("title")),
        task_type=_text(value.get("task_type")),
        intent=_text(value.get("user_intent")),
        behavior_ids=_string_list(value.get("behavior_ids")),
        decision=_text(value.get("decision")),
        rationale=_text(value.get("rationale")),
        spec_delta=_text(value.get("spec_delta")),
        supersedes=_text(value.get("supersedes")),
    )


def render_markdown(events: list[EvolutionEvent]) -> str:
    lines = [
        "<!-- Generated from spec/evolution/events.jsonl by .agents/skills/spec-evolution/scripts/timeline.py; do not edit. -->",
        "# Specification Evolution Timeline",
        "",
    ]
    for event in events:
        behaviors = ", ".join(event.behavior_ids) or "missing"
        lines.extend(
            [
                f"## {event.timestamp} — {event.title}",
                "",
                f"- Event: {event.event_id}",
                f"- Task type: {event.task_type}",
                f"- User intent: {event.intent}",
                f"- Behavior IDs: {behaviors}",
                f"- Product decision: {event.decision}",
                f"- Rationale: {event.rationale}",
                f"- Specification delta: {event.spec_delta}",
                f"- Supersedes: {event.supersedes}",
                "",
            ]
        )
    lines.extend(
        ["## Mermaid", "", "```mermaid", "timeline", "  title Specification Evolution"]
    )
    for event in events:
        label = _mermaid_text(f"{event.event_id} — {event.title}")
        lines.append(f"  {event.timestamp} : {label}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render specification evolution events.")
    parser.add_argument("--log", "--events", dest="events", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if not args.events.is_file():
        parser.error(f"event log does not exist: {args.events}")
    output = render_markdown(read_events(args.events))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "missing"


def _string_list(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _timestamp_key(value: str) -> tuple[int, str]:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (0, value)
    except ValueError:
        return (1, value)


def _mermaid_text(value: str) -> str:
    return value.replace(":", "-").replace("\n", " ").strip() or "missing"


if __name__ == "__main__":
    raise SystemExit(main())
