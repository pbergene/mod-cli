"""Tests for core/runner.py."""
from __future__ import annotations

import json
import subprocess
from unittest import mock

import pytest
import typer

from mod_cli.core import runner


def test_check_tool_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    runner.check_tool("git")  # should not raise


def test_check_tool_missing(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(typer.Exit):
        runner.check_tool("nonexistent-tool")


def test_run_capture():
    result = runner.run(["echo", "hello"], capture=True)
    assert result.stdout.strip() == "hello"


def test_run_nonzero_raises():
    with pytest.raises(typer.Exit):
        runner.run(["false"])


def test_run_nonzero_no_check():
    result = runner.run(["false"], check=False)
    assert result.returncode != 0


def test_run_json():
    data = runner.run_json(["echo", '{"key": "value"}'])
    assert data == {"key": "value"}


def test_run_json_bad_output():
    with pytest.raises(typer.Exit):
        runner.run_json(["echo", "not-json"])


def test_pipe():
    result = runner.pipe("hello world\n", ["cat"])
    assert result.strip() == "hello world"


@mock.patch("shutil.which", return_value="/usr/bin/jq")
def test_jq(mock_which):
    data = json.dumps({"name": "alice"})
    result = runner.jq(data, ".name")
    assert "alice" in result


@mock.patch("shutil.which", return_value=None)
def test_jq_missing(mock_which):
    with pytest.raises(typer.Exit):
        runner.jq("{}", ".x")
