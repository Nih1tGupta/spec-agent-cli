#!/usr/bin/env python3
"""Create a non-overwriting two-file feature specification packet."""

# spec: FSP-001, FSP-002, FSP-003, TRACE-001

from __future__ import annotations

import argparse
import re
from datetime import UTC, datetime
from pathlib import Path


SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEMPLATES = {
    "spec.md": "packet-spec.template.md",
    "acceptance.md": "packet-acceptance.template.md",
}


def create_packet(repo: Path, slug: str, title: str | None = None) -> Path:
    if not SLUG.fullmatch(slug):
        raise ValueError("feature slug must use lowercase kebab-case")

    feature_title = title or slug.replace("-", " ").title()
    behavior_prefix = slug.upper()
    created = datetime.now(UTC).date().isoformat()
    assets = Path(__file__).resolve().parent.parent / "assets"
    replacements = {
        "{{FEATURE_TITLE}}": feature_title,
        "{{BEHAVIOR_PREFIX}}": behavior_prefix,
        "{{DATE}}": created,
    }
    rendered: dict[str, str] = {}
    for output_name, template_name in TEMPLATES.items():
        text = (assets / template_name).read_text(encoding="utf-8")
        for token, value in replacements.items():
            text = text.replace(token, value)
        rendered[output_name] = text

    target = repo.resolve() / "spec/packets" / slug
    target.mkdir(parents=True, exist_ok=False)
    for output_name, text in rendered.items():
        (target / output_name).write_text(text, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--title")
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        target = create_packet(args.repo, args.slug, args.title)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
