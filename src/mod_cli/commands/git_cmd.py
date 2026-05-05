"""commands/git_cmd.py — Git workflow helpers."""
from __future__ import annotations

import subprocess

import typer
from rich import print as rprint
from rich.table import Table

from mod_cli.core import runner

app = typer.Typer(help="Git workflow helpers.")


@app.command("clean-branches")
def clean_branches(
    base: str = typer.Option("main", "--base", "-b", help="Base branch to compare against."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="List branches without deleting."),
) -> None:
    """Delete local branches already merged into *base*."""
    runner.check_tool("git")

    result = runner.run(
        ["git", "branch", "--merged", base],
        capture=True,
    )
    merged = [
        b.strip()
        for b in result.stdout.splitlines()
        if b.strip() and b.strip() not in {base, "main", "master", f"* {base}"}
        and not b.strip().startswith("*")
    ]

    if not merged:
        rprint("[green]No merged branches to clean up.[/green]")
        return

    table = Table(title="Merged branches", show_header=True)
    table.add_column("Branch", style="cyan")
    table.add_column("Action", style="yellow")
    for branch in merged:
        table.add_column  # noqa
        action = "[dim]would delete[/dim]" if dry_run else "[red]deleted[/red]"
        table.add_row(branch, action)
    rprint(table)

    if not dry_run:
        for branch in merged:
            runner.run(["git", "branch", "-d", branch])


@app.command("log-pretty")
def log_pretty(
    n: int = typer.Option(20, "--n", "-n", help="Number of commits to show."),
    author: str = typer.Option("", "--author", help="Filter by author name/email."),
) -> None:
    """Pretty one-line git log with relative dates."""
    runner.check_tool("git")

    cmd = [
        "git", "log",
        f"-{n}",
        "--pretty=format:%C(yellow)%h%Creset %C(cyan)%<(12,trunc)%ar%Creset %C(green)%<(20,trunc)%an%Creset %s",
    ]
    if author:
        cmd += [f"--author={author}"]

    runner.run(cmd)


@app.command("open")
def open_repo() -> None:
    """Open the current repository in the browser via ``gh browse``."""
    runner.check_tool("gh")
    runner.run(["gh", "browse"])
