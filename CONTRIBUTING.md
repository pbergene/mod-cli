# Contributing to mod-cli

Thank you for your interest in contributing! This guide explains how to get
set up, what conventions we follow, and how to submit a pull request.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Adding a New Command Group](#adding-a-new-command-group)
- [Adding a Command to an Existing Group](#adding-a-command-to-an-existing-group)
- [Code Style](#code-style)
- [Tests](#tests)
- [Commit Messages](#commit-messages)
- [Opening a Pull Request](#opening-a-pull-request)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating you agree to abide by its terms.

---

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) ≥ 0.11 — the only tool you need to install manually
- Python ≥ 3.11 (managed automatically by uv)
- External tools that commands wrap: `gh`, `git`, `kubectl`/`oc`, `jq`, `yq`
  (only needed when running the relevant commands, not for the test suite)

### Setup

```bash
git clone https://github.com/pbergene/mod-cli.git
cd mod-cli
uv sync          # creates .venv and installs all deps including dev extras
uv run mod --help
```

---

## Development Workflow

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_runner.py -v

# Run the CLI without installing globally
uv run mod git log-pretty

# Install globally for manual testing
uv tool install --reinstall .
```

---

## Adding a New Command Group

1. **Create** `src/mod_cli/commands/<tool>_cmd.py`:

```python
import typer
from mod_cli.core import runner

app = typer.Typer(help="Short description of the tool group.")

@app.command("hello")
def hello(name: str = typer.Argument("world")) -> None:
    """Say hello to NAME."""
    runner.check_tool("echo")
    runner.run(["echo", f"Hello, {name}!"])
```

2. **Register** it in `src/mod_cli/cli.py` (one line):

```python
from mod_cli.commands import mytool_cmd
app.add_typer(mytool_cmd.app, name="mytool")
```

3. **Add a smoke test** in `tests/test_smoke.py`:

```python
def test_mytool_help():
    result = runner.invoke(app, ["mytool", "--help"])
    assert result.exit_code == 0
    assert "hello" in result.output
```

---

## Adding a Command to an Existing Group

Open the relevant file in `src/mod_cli/commands/` and add a new
`@app.command()` function. Follow the patterns already used in that file.

---

## Code Style

- **Type hints** on every function signature
- **Docstrings** on every public function and command (Typer uses them as help text)
- No commented-out code
- Use `runner.run()` / `runner.run_json()` for all subprocess calls — never
  call `subprocess` directly in command modules
- Use `rich` for terminal output; keep plain stdout clean so output can be piped

---

## Tests

- Unit tests live in `tests/` and are run with `uv run pytest`
- Use `typer.testing.CliRunner` for command integration tests
- Mock external tool calls with `unittest.mock` or `monkeypatch`
- All tests must pass before a PR can be merged

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat(kube): add 'exec' command for interactive pod shell
fix(runner): handle jq exit code 3 gracefully
docs: add CONTRIBUTING guide
test(gh): mock gh api calls in clone-org test
```

---

## Opening a Pull Request

1. Fork or branch from `main`
2. Make your changes with tests
3. Ensure `uv run pytest` passes
4. Push your branch and open a PR against `main`
5. Fill in the PR description explaining *what* and *why*
6. A maintainer will review and merge

For larger changes, open an issue first to discuss the design.
