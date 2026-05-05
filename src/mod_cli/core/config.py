"""core/config.py — configuration loader.

Reads ``~/.mod-cli/config.toml`` (or the path in ``$MOD_CLI_CONFIG``).
All values are optional; sensible defaults are used when absent.

Example config file:

    [kube]
    namespace = "default"
    context   = "my-cluster"

    [github]
    owner = "my-org"

    [output]
    format = "table"   # table | json | yaml
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

_DEFAULT_PATH = Path.home() / ".mod-cli" / "config.toml"

_DEFAULTS: dict[str, Any] = {
    "kube": {
        "namespace": "default",
        "context": "",
    },
    "github": {
        "owner": "",
    },
    "output": {
        "format": "table",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load() -> dict[str, Any]:
    """Return the merged configuration (defaults + file)."""
    config_path = Path(os.environ.get("MOD_CLI_CONFIG", _DEFAULT_PATH))

    if not config_path.exists():
        return _DEFAULTS.copy()

    if tomllib is None:
        # Python < 3.11 and tomli not installed — return defaults with a warning
        import typer
        typer.echo(
            "[warning] tomllib/tomli not available; ignoring config file", err=True
        )
        return _DEFAULTS.copy()

    with config_path.open("rb") as fh:
        raw = tomllib.load(fh)

    return _deep_merge(_DEFAULTS, raw)


_config: dict[str, Any] | None = None


def get() -> dict[str, Any]:
    """Return cached config (loaded once per process)."""
    global _config
    if _config is None:
        _config = load()
    return _config
