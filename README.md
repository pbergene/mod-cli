# mod-cli

> **⚠️ Note:** This repository is an AI-generated example created to demonstrate a modular Python CLI framework. The commands are illustrative — they wrap real tools (`gh`, `git`, `kubectl`) but the implementations are example stubs and have not been tested in production. Use as a starting point or reference, not as production-ready tooling.

Modular administrative CLI wrapping `gh`, `git`, and `kubectl`/`oc` with `jq`/`yq` filter support.

## Install

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install globally
git clone https://github.com/pbergene/mod-cli.git
cd mod-cli
uv tool install .

# The 'mod' command is now available in your PATH
mod --version
```

## Usage

```
mod --help
mod git --help
mod gh --help
mod kube --help
```

### Git helpers

```bash
mod git log-pretty --n 30              # pretty one-line log
mod git clean-branches                 # delete merged local branches
mod git clean-branches --dry-run       # preview only
mod git open                           # open repo in browser
```

### GitHub CLI helpers

```bash
mod gh prs                             # list open PRs
mod gh prs --author alice --label bug  # filtered
mod gh prs --jq '.[].title'            # raw jq filter on JSON output
mod gh issues --label priority/high
mod gh clone-org my-org --dest ~/src   # clone all org repos
```

### Kubernetes / OpenShift helpers

```bash
mod kube pods --namespace dev
mod kube pods --jq '.items[].metadata.name'   # jq filter
mod kube pods --yq '.items[0]'                # yq filter
mod kube top --namespace production
mod kube ctx                                  # list contexts
mod kube ctx my-cluster                       # switch context
mod kube logs my-pod --tail 200 --grep ERROR
mod kube logs my-pod --follow
mod kube pods --oc                            # use 'oc' instead of 'kubectl'
```

## Configuration

Optional config file at `~/.mod-cli/config.toml` (override with `$MOD_CLI_CONFIG`):

```toml
[kube]
namespace = "dev"
context   = "my-cluster"

[github]
owner = "my-org"

[output]
format = "table"  # table | json | yaml
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Setup and dev workflow (`uv sync`, `uv run pytest`)
- How to add a new command group (one file + one line)
- Code style, test requirements, and commit format
- PR process

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## License

GPL-3.0 — see [LICENSE](LICENSE).
