"""commands/gh_cmd.py — GitHub CLI helpers."""
from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print as rprint

from mod_cli.core import config, output, runner
from mod_cli.core.output import OutputFormat

app = typer.Typer(help="GitHub CLI helpers.")

REQUIRED_TOOLS = ["gh", "git"]


@app.command("prs")
def prs(
    author: str = typer.Option("", "--author", "-a", help="Filter by PR author."),
    label: str = typer.Option("", "--label", "-l", help="Filter by label."),
    limit: int = typer.Option(30, "--limit", "-L", help="Max PRs to show."),
    jq_filter: str = typer.Option("", "--jq", help="jq filter applied to raw JSON output."),
    fmt: OutputFormat = output.output_option(),
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
        print(runner.jq(raw, jq_filter), end="")
        return

    data: list[dict] = json.loads(raw)

    rows = [
        {
            "number": str(pr["number"]),
            "title": pr["title"],
            "author": pr["author"]["login"],
            "branch": pr["headRefName"],
            "labels": ", ".join(lbl["name"] for lbl in pr.get("labels", [])),
        }
        for pr in data
    ]
    output.print_output(
        rows, fmt=fmt,
        columns=["number", "title", "author", "branch", "labels"],
        title="Open Pull Requests",
    )


@app.command("issues")
def issues(
    label: str = typer.Option("", "--label", "-l", help="Filter by label."),
    assignee: str = typer.Option("", "--assignee", "-a", help="Filter by assignee."),
    limit: int = typer.Option(30, "--limit", "-L", help="Max issues to show."),
    jq_filter: str = typer.Option("", "--jq", help="jq filter applied to raw JSON output."),
    fmt: OutputFormat = output.output_option(),
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
        print(runner.jq(raw, jq_filter), end="")
        return

    data: list[dict] = json.loads(raw)

    rows = [
        {
            "number": str(issue["number"]),
            "title": issue["title"],
            "assignees": ", ".join(a["login"] for a in issue.get("assignees", [])),
            "labels": ", ".join(lbl["name"] for lbl in issue.get("labels", [])),
        }
        for issue in data
    ]
    output.print_output(
        rows, fmt=fmt,
        columns=["number", "title", "assignees", "labels"],
        title="Open Issues",
    )


@app.command("clone-org")
def clone_org(
    org: str = typer.Argument(..., help="GitHub organisation or user to clone from."),
    dest: Path = typer.Option(Path("."), "--dest", "-d", help="Destination directory."),
    limit: int = typer.Option(100, "--limit", "-L", help="Max repos to clone."),
    skip_forks: bool = typer.Option(True, "--skip-forks/--include-forks", help="Skip forked repos."),
    fmt: OutputFormat = output.output_option(),
) -> None:
    """Clone all repositories in a GitHub organisation into *dest*."""
    runner.check_tool("gh")
    runner.check_tool("git")

    dest.mkdir(parents=True, exist_ok=True)

    cmd = ["gh", "repo", "list", org, "--json", "name,sshUrl,isFork", "--limit", str(limit)]
    data: list[dict] = runner.run_json(cmd)
    repos = [r for r in data if not (skip_forks and r.get("isFork"))]

    results = []
    for repo in repos:
        target = dest / repo["name"]
        if target.exists():
            status = "skipped (exists)"
        else:
            rc = runner.run(["git", "clone", repo["sshUrl"], str(target)], check=False)
            status = "cloned" if rc.returncode == 0 else "error"
        results.append({"repo": repo["name"], "status": status})

    output.print_output(
        results, fmt=fmt,
        columns=["repo", "status"],
        title=f"Clone results for {org}",
    )
