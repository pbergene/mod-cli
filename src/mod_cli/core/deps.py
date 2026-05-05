"""core/deps.py — external tool registry and dependency detection.

All external binaries used by mod-cli are declared here with their
purpose and install URL.  Commands use check() / check_all() to guard
against missing tools.  Nothing in this module installs anything.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field

import typer
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


@dataclass
class ToolInfo:
    purpose: str
    install_url: str
    optional: bool = False


# Declarative registry — every external binary the CLI may invoke.
REGISTRY: dict[str, ToolInfo] = {
    "git": ToolInfo(
        purpose="version control",
        install_url="https://git-scm.com/downloads",
    ),
    "gh": ToolInfo(
        purpose="GitHub CLI",
        install_url="https://cli.github.com",
    ),
    "kubectl": ToolInfo(
        purpose="Kubernetes CLI",
        install_url="https://kubernetes.io/docs/tasks/tools/",
    ),
    "oc": ToolInfo(
        purpose="OpenShift CLI",
        install_url="https://mirror.openshift.com/pub/openshift-v4/clients/ocp/",
        optional=True,
    ),
    "jq": ToolInfo(
        purpose="JSON stream filter",
        install_url="https://jqlang.github.io/jq/download/",
        optional=True,
    ),
    "yq": ToolInfo(
        purpose="YAML stream filter",
        install_url="https://github.com/mikefarah/yq#install",
        optional=True,
    ),
    "grep": ToolInfo(
        purpose="text line filter",
        install_url="(provided by your OS)",
        optional=True,
    ),
}


def _found(name: str) -> bool:
    return shutil.which(name) is not None


def version(name: str) -> str | None:
    """Return the version string for *name*, or None if not found / unparseable."""
    if not _found(name):
        return None
    for flag in ("--version", "version"):
        try:
            result = subprocess.run(  # noqa: S603
                [name, flag],
                capture_output=True,
                text=True,
                timeout=3,
            )
            line = (result.stdout or result.stderr or "").splitlines()
            if line:
                # Return just the first line, trimmed
                return line[0].strip()
        except Exception:
            pass
    return None


def check(name: str) -> None:
    """Exit with a rich error panel if *name* is not found in PATH.

    Nothing is installed — this is detection only.
    """
    if _found(name):
        return

    info = REGISTRY.get(name)
    purpose = info.purpose if info else "external tool"
    install_url = info.install_url if info else "see your package manager"

    rprint(
        Panel(
            f"[bold red]{name!r}[/bold red] not found in PATH\n\n"
            f"[dim]Purpose:[/dim]  {purpose}\n"
            f"[dim]Install:[/dim]  {install_url}",
            title="[red]Missing dependency[/red]",
            border_style="red",
        ),
        file=__import__("sys").stderr,
    )
    raise typer.Exit(code=1)


def check_all(names: list[str]) -> None:
    """Check multiple tools at once.

    Collects every missing tool and prints a single summary before
    exiting — so users can fix all problems in one go rather than
    discovering them one at a time.
    """
    missing = [n for n in names if not _found(n)]
    if not missing:
        return

    lines: list[str] = []
    for name in missing:
        info = REGISTRY.get(name)
        url = info.install_url if info else "see your package manager"
        lines.append(f"  [bold red]{name}[/bold red]  →  {url}")

    rprint(
        Panel(
            "\n".join(lines),
            title=f"[red]{len(missing)} missing tool(s)[/red]",
            border_style="red",
        ),
        file=__import__("sys").stderr,
    )
    raise typer.Exit(code=1)


def status_table() -> Table:
    """Build and return a Rich table showing the status of all registered tools."""
    table = Table(
        title="Tool Detection",
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column("Tool", style="bold")
    table.add_column("Found", justify="center")
    table.add_column("Purpose")
    table.add_column("Install / Info", style="dim")

    for name, info in REGISTRY.items():
        found = _found(name)
        found_cell = Text("✓", style="green") if found else Text("✗", style="red")
        install_cell = "" if found else info.install_url
        table.add_row(name, found_cell, info.purpose, install_cell)

    return table


def missing_count() -> int:
    """Return the number of required (non-optional) tools that are missing."""
    return sum(
        1
        for name, info in REGISTRY.items()
        if not info.optional and not _found(name)
    )
