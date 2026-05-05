"""Smoke tests for command groups using Typer's test runner."""
from __future__ import annotations

from typer.testing import CliRunner

from mod_cli.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "git" in result.output
    assert "gh" in result.output
    assert "kube" in result.output


def test_git_help():
    result = runner.invoke(app, ["git", "--help"])
    assert result.exit_code == 0
    assert "clean-branches" in result.output


def test_gh_help():
    result = runner.invoke(app, ["gh", "--help"])
    assert result.exit_code == 0
    assert "prs" in result.output
    assert "issues" in result.output
    assert "clone-org" in result.output


def test_kube_help():
    result = runner.invoke(app, ["kube", "--help"])
    assert result.exit_code == 0
    assert "pods" in result.output
    assert "logs" in result.output
    assert "ctx" in result.output
