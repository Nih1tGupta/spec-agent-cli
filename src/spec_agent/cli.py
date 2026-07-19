"""Command-line interface for installing Spec Agent into repositories."""

# spec: CLI-001, CLI-007, CLI-008

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import typer

from spec_agent.commands.init import cmd_init
from spec_agent.commands.traceability import cmd_traceability_sync, cmd_validate


app = typer.Typer(
    no_args_is_help=True,
    add_completion=True,
    help="Install the strict Spec Agent workflow into a repository.",
)


def _version_callback(value: bool) -> None:
    if not value:
        return
    try:
        current = version("spec-agent-cli")
    except PackageNotFoundError:
        current = "dev"
    print(f"spec-agent {current}")
    raise typer.Exit()


@app.callback()
def root(
    show_version: bool = typer.Option(
        False,
        "--version",
        help="Show the installed version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Install and maintain Spec Agent project assets."""


@app.command("init")
def init_command(
    repo: Path = typer.Option(Path("."), "--repo", help="Repository to initialize."),
    check: bool = typer.Option(False, "--check", help="Report status; write nothing."),
    force: bool = typer.Option(
        False,
        "--force",
        help="Update locally changed managed skill files.",
    ),
) -> None:
    """Install agent and Claude skills, then scaffold missing specification files."""
    raise typer.Exit(cmd_init(repo, check=check, force=force))


@app.command("validate")
def validate_command(
    repo: Path = typer.Option(Path("."), "--repo", help="Repository to validate."),
) -> None:
    """Read-only validation of specifications, backlinks, and traceability."""
    raise typer.Exit(cmd_validate(repo))


@app.command("traceability-sync")
def traceability_sync_command(
    repo: Path = typer.Option(
        Path("."), "--repo", help="Repository whose approved baseline is refreshed."
    ),
) -> None:
    """Refresh derived traceability after approved implementation or reconciliation."""
    raise typer.Exit(cmd_traceability_sync(repo))


def main(argv: list[str] | None = None) -> int:
    try:
        app(args=argv, prog_name="spec-agent")
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
