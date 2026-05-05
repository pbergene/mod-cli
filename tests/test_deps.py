"""Tests for core/deps.py — tool registry and dependency detection."""
from __future__ import annotations

from unittest import mock

import pytest
import typer
from rich.table import Table

from mod_cli.core import deps


# ── check() ────────────────────────────────────────────────────────────────

def test_check_passes_when_tool_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    deps.check("git")  # should not raise


def test_check_exits_when_tool_missing(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(typer.Exit) as exc_info:
        deps.check("git")
    assert exc_info.value.exit_code == 1


def test_check_unknown_tool_exits(monkeypatch):
    """Tools not in the registry still produce an exit, just with generic text."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(typer.Exit):
        deps.check("some-nonexistent-tool-xyz")


# ── check_all() ────────────────────────────────────────────────────────────

def test_check_all_passes_when_all_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    deps.check_all(["git", "gh"])  # should not raise


def test_check_all_exits_on_any_missing(monkeypatch):
    present = {"git"}

    def which(name):
        return f"/usr/bin/{name}" if name in present else None

    monkeypatch.setattr("shutil.which", which)
    with pytest.raises(typer.Exit) as exc_info:
        deps.check_all(["git", "gh"])
    assert exc_info.value.exit_code == 1


def test_check_all_empty_list(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    deps.check_all([])  # empty list — nothing to check, should not raise


# ── version() ──────────────────────────────────────────────────────────────

def test_version_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert deps.version("git") is None


def test_version_returns_string_when_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/git")
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(
            stdout="git version 2.44.0\n", stderr="", returncode=0
        )
        result = deps.version("git")
    assert result == "git version 2.44.0"


def test_version_survives_subprocess_error(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/broken")
    with mock.patch("subprocess.run", side_effect=Exception("boom")):
        result = deps.version("broken")
    assert result is None


# ── status_table() ─────────────────────────────────────────────────────────

def test_status_table_returns_rich_table(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/git")
    table = deps.status_table()
    assert isinstance(table, Table)


def test_status_table_contains_all_registry_tools(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    table = deps.status_table()
    # Row count should equal registry size
    assert table.row_count == len(deps.REGISTRY)


# ── missing_count() ────────────────────────────────────────────────────────

def test_missing_count_zero_when_all_found(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    assert deps.missing_count() == 0


def test_missing_count_ignores_optional_tools(monkeypatch):
    # Only required tools (optional=False) should count
    required_names = {n for n, i in deps.REGISTRY.items() if not i.optional}

    def which(name):
        return f"/usr/bin/{name}" if name in required_names else None

    monkeypatch.setattr("shutil.which", which)
    assert deps.missing_count() == 0


def test_missing_count_counts_missing_required(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    required = sum(1 for i in deps.REGISTRY.values() if not i.optional)
    assert deps.missing_count() == required


# ── registry sanity ────────────────────────────────────────────────────────

def test_registry_has_core_tools():
    for tool in ("git", "gh", "kubectl", "jq", "yq"):
        assert tool in deps.REGISTRY


def test_registry_entries_have_non_empty_fields():
    for name, info in deps.REGISTRY.items():
        assert info.purpose, f"{name} has empty purpose"
        assert info.install_url, f"{name} has empty install_url"


# ── runner.check_tool() delegates to deps ──────────────────────────────────

def test_runner_check_tool_delegates(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    from mod_cli.core import runner
    with pytest.raises(typer.Exit):
        runner.check_tool("git")
