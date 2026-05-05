"""commands/git_cmd.py — Git workflow helpers."""
from __future__ import annotations

import typer
from rich import print as rprint

from mod_cli.core import output, runner
from mod_cli.core.output import OutputFormat

app = typer.Typer(help="Git workflow helpers.")

REQUIRED_TOOLS = ["git", "gh"]


@app.command("clean-branches")
def clean_branches(
    base: str = typer.Option("main", "--base", "-b", help="Base branch to compare against."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="List branches without deleting."),
    fmt: OutputFormat = output.output_option(),
) -> None:
    """Delete local branches already merged into *base*."""
    runner.check_tool("git")

    result = runner.run(["git", "branch", "--merged", base], capture=True)
    merged = [
        b.strip()
        for b in result.stdout.splitlines()
        if b.strip() and b.strip() not in {base, "main", "master", f"* {base}"}
        and not b.strip().startswith("*")
    ]

    if not merged:
        if fmt == OutputFormat.table:
            rprint("[green]No merged branches to clean up.[/green]")
        else:
            output.print_output([], fmt=fmt, columns=["branch", "action"])
        return

    action_label = "would delete" if dry_run else "deleted"
    rows = [{"branch": b, "action": action_label} for b in merged]
    output.print_output(rows, fmt=fmt, columns=["branch", "action"], title="Merged branches")

    if not dry_run:
        for branch in merged:
            runner.run(["git", "branch", "-d", branch])


@app.command("log-pretty")
def log_pretty(
    n: int = typer.Option(20, "--n", "-n", help="Number of commits to show."),
    author: str = typer.Option("", "--author", help="Filter by author name/email."),
    fmt: OutputFormat = output.output_option(),
) -> None:
    """Pretty one-line git log with relative dates."""
    runner.check_tool("git")

    if fmt != OutputFormat.table:
        cmd = ["git", "log", f"-{n}", "--pretty=format:%H\t%ar\t%an\t%s"]
        if author:
            cmd += [f"--author={author}"]
        result = runner.run(cmd, capture=True)
        rows = []
        for line in result.stdout.splitlines():
            parts = line.split("\t", 3)
            if len(parts) == 4:
                rows.append({"hash": parts[0][:12], "date": parts[1], "author": parts[2], "subject": parts[3]})
        output.print_output(rows, fmt=fmt, columns=["hash", "date", "author", "subject"])
    else:
        cmd = [
            "git", "log", f"-{n}",
            "--pretty=format:%C(yellow)%h%Creset %C(cyan)%<(12,trunc)%ar%Creset "
            "%C(green)%<(20,trunc)%an%Creset %s",
        ]
        if author:
            cmd += [f"--author={author}"]
        runner.run(cmd)


@app.command("open")
def open_repo() -> None:
    """Open the current repository in the browser via ``gh browse``."""
    runner.check_tool("gh")
    runner.run(["gh", "browse"])
