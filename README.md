# mod-cli

> **⚠️ Note:** This repository is an AI-generated example created to demonstrate a modular Python CLI framework. The commands are illustrative — they wrap real tools (`gh`, `git`, `kubectl`) but the implementations are example stubs and have not been tested in production. Use as a starting point or reference, not as production-ready tooling.

Modular administrative CLI wrapping `gh`, `git`, and `kubectl`/`oc` with `jq`/`yq` filter support.

## Install

### 1. Dependencies

Install the external tools that `mod` wraps. Choose your distribution and version.

#### Fedora 42, 43, 44

All three releases ship `git`, `jq`, `yq`, and `uv` in the official Fedora repositories
and use DNF5 as the default package manager.

```bash
# Core tools
sudo dnf install -y git jq yq uv

# GitHub CLI
sudo dnf install -y dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install -y gh --repo gh-cli

# kubectl — skip if using OpenShift
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.30/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.30/rpm/repodata/repomd.xml.key
EOF
sudo dnf install -y kubectl

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc
```

#### Debian 11 (Bullseye), 12 (Bookworm), 13 (Trixie)

`yq` in apt is a different tool (`kislyuk/yq`); install mikefarah/yq from upstream.
`uv` is not yet in the Debian repositories; install from the upstream release.

```bash
# Core tools
sudo apt-get update && sudo apt-get install -y git jq curl gpg wget

# GitHub CLI
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -nv -O /tmp/githubcli.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg
sudo mv /tmp/githubcli.gpg /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] \
  https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update && sudo apt-get install -y gh

# kubectl — skip if using OpenShift
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null
sudo apt-get update && sudo apt-get install -y kubectl

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc

# yq — upstream binary (mikefarah/yq)
sudo wget -qO /usr/local/bin/yq \
  https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# uv — upstream binary
curl -LO https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-*/uv /usr/local/bin/uv
```

#### Ubuntu 20.04 (Focal), 22.04 (Jammy), 24.04 (Noble)

Same `apt-get` commands as Debian above — all tools install identically across these releases.

```bash
# Core tools
sudo apt-get update && sudo apt-get install -y git jq curl gpg wget

# GitHub CLI
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -nv -O /tmp/githubcli.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg
sudo mv /tmp/githubcli.gpg /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] \
  https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update && sudo apt-get install -y gh

# kubectl — skip if using OpenShift
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null
sudo apt-get update && sudo apt-get install -y kubectl

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc

# yq — upstream binary (mikefarah/yq)
sudo wget -qO /usr/local/bin/yq \
  https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# uv — upstream binary
curl -LO https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-*/uv /usr/local/bin/uv
```

### 2. mod-cli itself

```bash
git clone https://github.com/pbergene/mod-cli.git
cd mod-cli
uv tool install .

# Verify
mod --version
mod doctor          # checks all external tools are reachable
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
