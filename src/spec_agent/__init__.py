"""Spec Agent CLI package."""

__all__ = ["main"]


def __getattr__(name: str):
    if name == "main":
        from spec_agent.cli import main

        return main
    raise AttributeError(name)
