"""core/output.py — CLI-friendly, pipeable output helpers.

All commands should emit data through this module so that the output
format can be controlled uniformly by the caller.

Supported formats
-----------------
table  (default)
    Rich-rendered table written to the terminal.  When stdout is not a
    TTY (i.e. being piped) the table falls back to TSV so that tools
    like ``grep``, ``awk``, and ``cut`` can process it line-by-line.

json
    Compact JSON written to stdout with no Rich markup.  Suitable for
    piping to ``jq``.

yaml
    YAML written to stdout with no Rich markup.  Suitable for piping
    to ``yq``.

Usage
-----
from mod_cli.core.output import OutputFormat, print_output

@app.command()
def pods(output: OutputFormat = OutputFormat.table) -> None:
    data = [{"name": "my-pod", "status": "Running"}]
    print_output(data, fmt=output, columns=["name", "status"])
"""
from __future__ import annotations

import json
import sys
from enum import Enum
from typing import Any, Sequence

from rich import print as rprint
from rich.console import Console
from rich.table import Table

try:
    import yaml as _yaml
    _YAML_AVAILABLE = True
except ModuleNotFoundError:
    _YAML_AVAILABLE = False


class OutputFormat(str, Enum):
    """Output format choices exposed as a Typer option."""
    table = "table"
    json = "json"
    yaml = "yaml"
    tsv = "tsv"


def _is_tty() -> bool:
    return sys.stdout.isatty()


# ── Public API ───────────────────────────────────────────────────────────────

def print_output(
    data: list[dict[str, Any]],
    *,
    fmt: OutputFormat = OutputFormat.table,
    columns: Sequence[str] | None = None,
    title: str = "",
) -> None:
    """Render *data* in the requested format.

    Parameters
    ----------
    data:
        List of dicts.  Every dict is one row; keys are column names.
    fmt:
        Output format (table / json / yaml / tsv).
    columns:
        Ordered list of column names to include.  ``None`` uses all keys
        from the first row.
    title:
        Optional title shown above Rich tables.
    """
    if not data:
        if fmt == OutputFormat.table and _is_tty():
            rprint("[dim]No results.[/dim]")
        return

    cols = list(columns) if columns else list(data[0].keys())

    if fmt == OutputFormat.json:
        _print_json(data, cols)
    elif fmt == OutputFormat.yaml:
        _print_yaml(data, cols)
    elif fmt == OutputFormat.tsv:
        _print_tsv(data, cols)
    else:
        # table — Rich when TTY, TSV when piped so output stays clean
        if _is_tty():
            _print_rich_table(data, cols, title=title)
        else:
            _print_tsv(data, cols)


def print_record(
    record: dict[str, Any],
    *,
    fmt: OutputFormat = OutputFormat.table,
) -> None:
    """Render a single dict as key-value pairs or serialised data."""
    if fmt == OutputFormat.json:
        _print_json([record], list(record.keys()))
    elif fmt == OutputFormat.yaml:
        _print_yaml([record], list(record.keys()))
    elif fmt in (OutputFormat.table, OutputFormat.tsv):
        if _is_tty():
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Key", style="bold cyan", no_wrap=True)
            table.add_column("Value")
            for k, v in record.items():
                table.add_row(str(k), str(v) if v is not None else "")
            Console().print(table)
        else:
            for k, v in record.items():
                print(f"{k}\t{v if v is not None else ''}")


# ── Format implementations ───────────────────────────────────────────────────

def _filtered(row: dict, cols: list[str]) -> dict:
    return {c: row.get(c) for c in cols}


def _print_json(data: list[dict], cols: list[str]) -> None:
    """Write compact JSON to stdout — no Rich markup, pipeable to jq."""
    filtered = [_filtered(row, cols) for row in data]
    # Use print() not rprint() so stdout stays markup-free
    print(json.dumps(filtered, indent=2, default=str))


def _print_yaml(data: list[dict], cols: list[str]) -> None:
    """Write YAML to stdout — no Rich markup, pipeable to yq."""
    if not _YAML_AVAILABLE:
        import typer
        typer.echo(
            "[error] PyYAML is not installed. Install it with: uv add pyyaml",
            err=True,
        )
        raise typer.Exit(code=1)

    filtered = [_filtered(row, cols) for row in data]
    print(_yaml.dump(filtered, default_flow_style=False, allow_unicode=True), end="")


def _print_tsv(data: list[dict], cols: list[str]) -> None:
    """Write tab-separated values to stdout — pipeable to awk/cut/grep."""
    print("\t".join(cols))
    for row in data:
        print("\t".join(str(row.get(c, "")) for c in cols))


def _print_rich_table(data: list[dict], cols: list[str], title: str = "") -> None:
    """Write a Rich-rendered table to the terminal."""
    table = Table(
        title=title or None,
        show_header=True,
        header_style="bold magenta",
    )
    for col in cols:
        table.add_column(col)
    for row in data:
        table.add_row(*[str(row.get(c, "")) for c in cols])
    Console().print(table)


# ── Typer option helper ──────────────────────────────────────────────────────

def output_option(default: OutputFormat = OutputFormat.table):
    """Return a pre-configured Typer Option for ``--output / -o``."""
    import typer
    return typer.Option(default, "--output", "-o", help="Output format.")
