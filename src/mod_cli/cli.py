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
from mod_cli.core import deps

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


@app.command("doctor")
def doctor() -> None:
    """Check that all required external tools are installed.

    Prints a status table for every tool in the registry.
    Exits with code 1 if any required tool is missing.
    """
    rprint(deps.status_table())

    missing = deps.missing_count()
    if missing:
        rprint(
            f"\n[red bold]{missing} required tool(s) missing.[/red bold] "
            "Install them using the links above, then re-run [bold]mod doctor[/bold]."
        )
        raise typer.Exit(code=1)
    else:
        rprint("\n[green bold]All required tools found. ✓[/green bold]")


def main() -> None:
    app()
