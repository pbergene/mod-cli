# mod-cli

> **⚠️ Note:** This repository is an AI-generated example created to demonstrate a modular Python CLI framework. The commands are illustrative — they wrap real tools (`gh`, `git`, `kubectl`) but the implementations are example stubs and have not been tested in production. Use as a starting point or reference, not as production-ready tooling.

Modular administrative CLI wrapping `gh`, `git`, and `kubectl`/`oc` with `jq`/`yq` filter support.

## Install

### 1. Dependencies

Install the external tools that `mod` wraps. Choose your distribution and version.

#### Fedora 42, 43, 44

`git`, `jq`, `gh`, `yq`, and `uv` are all in the official Fedora repositories.
`kubectl` is packaged as a versioned RPM (`kubernetesX.Y-client`); Fedora 42+ no longer
ships a generic `kubernetes-client` package. List what's available with
`dnf search kubernetes | grep client` and install the version matching your cluster.

```bash
# Core tools, GitHub CLI, yq, uv — all from official Fedora repos
sudo dnf install -y git jq gh yq uv

# kubectl — skip if using OpenShift
# List available versions: dnf search kubernetes | grep client
# Install the package matching your cluster's minor version, e.g.:
sudo dnf install -y kubernetes1.32-client   # adjust version as needed

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc
```

#### Debian 13 (Trixie)

`git`, `jq`, `gh` (2.46), and `kubectl` (1.32) are all in the official Trixie repositories.
`yq` and `uv` require upstream binaries (the `yq` in apt is `kislyuk/yq`, a different tool).

```bash
# Core tools, GitHub CLI, kubectl — all from official repos
sudo apt-get update && sudo apt-get install -y git jq gh kubectl

# yq — mikefarah/yq upstream binary (apt 'yq' is a different tool)
sudo wget -qO /usr/local/bin/yq \
  https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# uv — upstream binary (not yet in Debian repos)
curl -LO https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-*/uv /usr/local/bin/uv

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc
```

#### Debian 12 (Bookworm)

`gh` (2.23) is available in the official Bookworm repos. `kubectl` is not packaged in
Bookworm; add the Kubernetes APT repo. `yq` and `uv` require upstream binaries.

```bash
# Core tools and GitHub CLI from official repos
sudo apt-get update && sudo apt-get install -y git jq gh curl gpg

# kubectl — skip if using OpenShift — add Kubernetes APT repo
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null
sudo apt-get update && sudo apt-get install -y kubectl

# yq — mikefarah/yq upstream binary (apt 'yq' is a different tool)
sudo wget -qO /usr/local/bin/yq \
  https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# uv — upstream binary (not yet in Debian repos)
curl -LO https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-*/uv /usr/local/bin/uv

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc
```

#### Debian 11 (Bullseye)

Neither `gh` nor `kubectl` is packaged in Bullseye; both require external repos.
`yq` and `uv` require upstream binaries.

```bash
# Core tools
sudo apt-get update && sudo apt-get install -y git jq curl gpg wget

# gh — add GitHub APT repo (not packaged in Bullseye)
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -nv -O /tmp/githubcli.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg
sudo mv /tmp/githubcli.gpg /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] \
  https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update && sudo apt-get install -y gh

# kubectl — skip if using OpenShift — add Kubernetes APT repo
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null
sudo apt-get update && sudo apt-get install -y kubectl

# yq — mikefarah/yq upstream binary (apt 'yq' is a different tool)
sudo wget -qO /usr/local/bin/yq \
  https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# uv — upstream binary (not yet in Debian repos)
curl -LO https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-*/uv /usr/local/bin/uv

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc
```

#### Ubuntu 24.04 (Noble), 22.04 (Jammy), 20.04 (Focal)

`gh` is not current enough in the Ubuntu universe repos; use GitHub's APT repo.
`kubectl` is not packaged in Ubuntu; use the Kubernetes APT repo.
`yq` and `uv` require upstream binaries.

```bash
# Core tools
sudo apt-get update && sudo apt-get install -y git jq curl gpg wget

# gh — add GitHub APT repo
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -nv -O /tmp/githubcli.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg
sudo mv /tmp/githubcli.gpg /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] \
  https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update && sudo apt-get install -y gh

# kubectl — skip if using OpenShift — add Kubernetes APT repo
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null
sudo apt-get update && sudo apt-get install -y kubectl

# yq — mikefarah/yq upstream binary (apt 'yq' is a different tool)
sudo wget -qO /usr/local/bin/yq \
  https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# uv — upstream binary (not yet in Ubuntu repos)
curl -LO https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-*/uv /usr/local/bin/uv

# oc — OpenShift CLI, skip if using plain Kubernetes
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
OCP_VERSION=4.15.0   # replace with your cluster version
curl -LO "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_VERSION}/openshift-client-linux.tar.gz"
tar -xzf openshift-client-linux.tar.gz oc
sudo install -m 0755 oc /usr/local/bin/oc
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
