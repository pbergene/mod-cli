"""cli.py — root Typer application.

Register new command groups by importing their module and calling
``app.add_typer()``.  That's the only change required to add a new
top-level subcommand.
"""
from __future__ import annotations

import typer
from rich import print as rprint

from mod_cli import __version__
from mod_cli.commands import gh_cmd, git_cmd, kube_cmd

app = typer.Typer(
    name="mod",
    help="Modular admin CLI — wraps gh, git, kubectl/oc with jq/yq support.",
    no_args_is_help=True,
    rich_markup_mode="markdown",
)

# ── Register command groups ──────────────────────────────────────────────────
app.add_typer(git_cmd.app, name="git")
app.add_typer(gh_cmd.app, name="gh")
app.add_typer(kube_cmd.app, name="kube")


@app.callback(invoke_without_command=True)
def _root(
    version: bool = typer.Option(
        False, "--version", "-V", help="Show version and exit.", is_eager=True
    ),
) -> None:
    if version:
        rprint(f"mod-cli [bold]{__version__}[/bold]")
        raise typer.Exit()


def main() -> None:
    app()
