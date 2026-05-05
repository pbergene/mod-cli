"""commands/gh_cmd.py — GitHub CLI helpers."""
from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich import print as rprint
from rich.table import Table

from mod_cli.core import config, runner

app = typer.Typer(help="GitHub CLI helpers.")


@app.command("prs")
def prs(
    author: str = typer.Option("", "--author", "-a", help="Filter by PR author."),
    label: str = typer.Option("", "--label", "-l", help="Filter by label."),
    limit: int = typer.Option(30, "--limit", "-L", help="Max PRs to show."),
    jq_filter: str = typer.Option("", "--jq", help="jq filter applied to raw JSON output."),
) -> None:
    """List open pull requests for the current repository."""
    runner.check_tool("gh")

    cmd = ["gh", "pr", "list", "--json",
           "number,title,author,labels,createdAt,headRefName",
           "--limit", str(limit), "--state", "open"]
    if author:
        cmd += ["--author", author]
    if label:
        cmd += ["--label", label]

    result = runner.run(cmd, capture=True)
    raw = result.stdout

    if jq_filter:
        rprint(runner.jq(raw, jq_filter))
        return

    data: list[dict] = json.loads(raw)
    if not data:
        rprint("[yellow]No open pull requests.[/yellow]")
        return

    table = Table(title="Open Pull Requests", show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Author", style="green")
    table.add_column("Branch", style="blue")
    table.add_column("Labels", style="yellow")

    for pr in data:
        labels = ", ".join(lbl["name"] for lbl in pr.get("labels", []))
        table.add_row(
            str(pr["number"]),
            pr["title"],
            pr["author"]["login"],
            pr["headRefName"],
            labels,
        )

    rprint(table)


@app.command("issues")
def issues(
    label: str = typer.Option("", "--label", "-l", help="Filter by label."),
    assignee: str = typer.Option("", "--assignee", "-a", help="Filter by assignee."),
    limit: int = typer.Option(30, "--limit", "-L", help="Max issues to show."),
    jq_filter: str = typer.Option("", "--jq", help="jq filter applied to raw JSON output."),
) -> None:
    """List open issues for the current repository."""
    runner.check_tool("gh")

    cmd = ["gh", "issue", "list", "--json",
           "number,title,assignees,labels,createdAt",
           "--limit", str(limit), "--state", "open"]
    if label:
        cmd += ["--label", label]
    if assignee:
        cmd += ["--assignee", assignee]

    result = runner.run(cmd, capture=True)
    raw = result.stdout

    if jq_filter:
        rprint(runner.jq(raw, jq_filter))
        return

    data: list[dict] = json.loads(raw)
    if not data:
        rprint("[yellow]No open issues.[/yellow]")
        return

    table = Table(title="Open Issues", show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Assignees", style="green")
    table.add_column("Labels", style="yellow")

    for issue in data:
        assignees = ", ".join(a["login"] for a in issue.get("assignees", []))
        labels = ", ".join(lbl["name"] for lbl in issue.get("labels", []))
        table.add_row(str(issue["number"]), issue["title"], assignees, labels)

    rprint(table)


@app.command("clone-org")
def clone_org(
    org: str = typer.Argument(..., help="GitHub organisation or user to clone from."),
    dest: Path = typer.Option(
        Path("."), "--dest", "-d", help="Destination directory."
    ),
    limit: int = typer.Option(100, "--limit", "-L", help="Max repos to clone."),
    skip_forks: bool = typer.Option(True, "--skip-forks/--include-forks", help="Skip forked repos."),
) -> None:
    """Clone all repositories in a GitHub organisation into *dest*."""
    runner.check_tool("gh")
    runner.check_tool("git")

    dest.mkdir(parents=True, exist_ok=True)

    cmd = ["gh", "repo", "list", org, "--json", "name,sshUrl,isFork",
           "--limit", str(limit)]
    data: list[dict] = runner.run_json(cmd)

    repos = [r for r in data if not (skip_forks and r.get("isFork"))]
    rprint(f"[bold]Cloning {len(repos)} repos into {dest}[/bold]")

    for repo in repos:
        target = dest / repo["name"]
        if target.exists():
            rprint(f"  [dim]skip[/dim] {repo['name']} (already exists)")
            continue
        rprint(f"  [cyan]clone[/cyan] {repo['name']}")
        runner.run(["git", "clone", repo["sshUrl"], str(target)], check=False)
