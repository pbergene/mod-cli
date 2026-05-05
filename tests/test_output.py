"""Tests for core/output.py — CLI-friendly output module."""
from __future__ import annotations

import json
from io import StringIO
from unittest import mock

import pytest

from mod_cli.core.output import (
    OutputFormat,
    _print_json,
    _print_tsv,
    print_output,
    print_record,
)

SAMPLE = [
    {"name": "pod-a", "status": "Running", "restarts": "0"},
    {"name": "pod-b", "status": "Failed",  "restarts": "3"},
]


# ── print_output — json ─────────────────────────────────────────────────────

def test_print_output_json(capsys):
    print_output(SAMPLE, fmt=OutputFormat.json, columns=["name", "status"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 2
    assert data[0]["name"] == "pod-a"
    # columns filter applied — restarts not requested
    assert "restarts" not in data[0]


def test_print_output_json_empty(capsys):
    print_output([], fmt=OutputFormat.json, columns=["name"])
    captured = capsys.readouterr()
    # empty list produces no output (early return)
    assert captured.out == ""


# ── print_output — tsv ──────────────────────────────────────────────────────

def test_print_output_tsv(capsys):
    print_output(SAMPLE, fmt=OutputFormat.tsv, columns=["name", "status"])
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "name\tstatus"
    assert lines[1] == "pod-a\tRunning"
    assert lines[2] == "pod-b\tFailed"


def test_print_output_tsv_missing_column(capsys):
    """Missing keys render as empty string rather than raising."""
    rows = [{"name": "x"}]
    print_output(rows, fmt=OutputFormat.tsv, columns=["name", "status"])
    captured = capsys.readouterr()
    lines = captured.out.splitlines()  # no strip — trailing tab is meaningful
    assert lines[1].startswith("x\t")


# ── print_output — table (TTY path) ────────────────────────────────────────

def test_print_output_table_tty(capsys):
    with mock.patch("mod_cli.core.output._is_tty", return_value=True):
        print_output(SAMPLE, fmt=OutputFormat.table, columns=["name", "status"])
    captured = capsys.readouterr()
    # Rich table output should contain our data
    assert "pod-a" in captured.out
    assert "Running" in captured.out


def test_print_output_table_piped_falls_back_to_tsv(capsys):
    """When stdout is not a TTY, table format should emit TSV."""
    with mock.patch("mod_cli.core.output._is_tty", return_value=False):
        print_output(SAMPLE, fmt=OutputFormat.table, columns=["name", "status"])
    captured = capsys.readouterr()
    assert "name\tstatus" in captured.out


# ── print_output — yaml ─────────────────────────────────────────────────────

def test_print_output_yaml(capsys):
    pytest.importorskip("yaml")
    print_output(SAMPLE, fmt=OutputFormat.yaml, columns=["name", "status"])
    captured = capsys.readouterr()
    assert "pod-a" in captured.out
    assert "Running" in captured.out


# ── print_record ────────────────────────────────────────────────────────────

def test_print_record_json(capsys):
    print_record({"key": "value", "num": 42}, fmt=OutputFormat.json)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    # print_record wraps in a list internally
    assert data[0]["key"] == "value"
    assert data[0]["num"] == 42


def test_print_record_tsv(capsys):
    print_record({"key": "value"}, fmt=OutputFormat.tsv)
    captured = capsys.readouterr()
    assert "key\tvalue" in captured.out


# ── OutputFormat enum ───────────────────────────────────────────────────────

def test_output_format_values():
    assert OutputFormat.table == "table"
    assert OutputFormat.json == "json"
    assert OutputFormat.yaml == "yaml"
    assert OutputFormat.tsv == "tsv"
