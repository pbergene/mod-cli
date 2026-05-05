"""core/runner.py — subprocess and filter utilities.

All external tool invocations go through this module so that
error handling, output capture, and jq/yq piping are consistent
across every command group.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Any

import typer


def check_tool(name: str) -> None:
    """Exit with a clear error if *name* is not found in PATH."""
    if shutil.which(name) is None:
        typer.echo(
            f"[error] required tool not found in PATH: {name!r}", err=True
        )
        raise typer.Exit(code=1)


def run(
    cmd: list[str] | str,
    *,
    capture: bool = False,
    input: str | None = None,
    check: bool = True,
    shell: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd*, streaming stdout unless *capture=True*.

    Stderr always passes through to the terminal.
    Raises ``typer.Exit(1)`` on non-zero exit when *check=True*.
    """
    kwargs: dict[str, Any] = {
        "text": True,
        "shell": shell,
        "stderr": None,  # inherit
    }
    if capture:
        kwargs["stdout"] = subprocess.PIPE
    if input is not None:
        kwargs["input"] = input

    result = subprocess.run(cmd, **kwargs)  # noqa: S603

    if check and result.returncode != 0:
        typer.echo(
            f"[error] command exited with code {result.returncode}: {cmd}",
            err=True,
        )
        raise typer.Exit(code=result.returncode)

    return result


def run_json(cmd: list[str] | str, *, shell: bool = False) -> Any:
    """Run *cmd* and parse its stdout as JSON."""
    result = run(cmd, capture=True, shell=shell)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        typer.echo(f"[error] failed to parse JSON output: {exc}", err=True)
        raise typer.Exit(code=1) from exc


def pipe(data: str, cmd: list[str] | str, *, shell: bool = False) -> str:
    """Pipe *data* through *cmd* and return stdout."""
    result = run(cmd, capture=True, input=data, shell=shell)
    return result.stdout


def jq(data: str, filter: str) -> str:
    """Pipe *data* (JSON string) through ``jq`` with *filter*."""
    check_tool("jq")
    return pipe(data, ["jq", filter])


def yq(data: str, filter: str) -> str:
    """Pipe *data* (YAML string) through ``yq`` with *filter*."""
    check_tool("yq")
    return pipe(data, ["yq", filter])
