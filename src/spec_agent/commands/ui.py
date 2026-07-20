"""Implementation of the local read-only Spec Agent dashboard."""

from __future__ import annotations

from pathlib import Path

from spec_agent.ui import serve_dashboard


def cmd_ui(
    repo_root: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    open_browser: bool = True,
) -> int:
    return serve_dashboard(
        repo_root,
        host=host,
        port=port,
        open_browser=open_browser,
    )
