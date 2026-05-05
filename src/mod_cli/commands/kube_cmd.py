"""commands/kube_cmd.py — kubectl / oc helpers."""
from __future__ import annotations

import json

import typer
from rich import print as rprint

from mod_cli.core import config, output, runner
from mod_cli.core.output import OutputFormat

app = typer.Typer(help="kubectl / oc helpers.")

# oc, jq, yq, grep are optional — only needed for specific subcommands
REQUIRED_TOOLS = ["kubectl"]
OPTIONAL_TOOLS = ["oc", "jq", "yq", "grep"]

_KUBECTL = "kubectl"


def _kubectl(use_oc: bool = False) -> str:
    tool = "oc" if use_oc else _KUBECTL
    runner.check_tool(tool)
    return tool


def _ctx_args(namespace: str, context: str) -> list[str]:
    args: list[str] = []
    cfg = config.get()["kube"]
    ns = namespace or cfg["namespace"]
    ctx = context or cfg["context"]
    if ns:
        args += ["--namespace", ns]
    if ctx:
        args += ["--context", ctx]
    return args


@app.command("pods")
def pods(
    namespace: str = typer.Option("", "--namespace", "-n", help="Kubernetes namespace."),
    context: str = typer.Option("", "--context", "-c", help="kubeconfig context."),
    jq_filter: str = typer.Option("", "--jq", help="jq filter applied to JSON output."),
    yq_filter: str = typer.Option("", "--yq", help="yq filter applied to YAML output."),
    use_oc: bool = typer.Option(False, "--oc", help="Use 'oc' instead of 'kubectl'."),
    fmt: OutputFormat = output.output_option(),
) -> None:
    """List pods in a namespace."""
    tool = _kubectl(use_oc)
    args = _ctx_args(namespace, context)

    if jq_filter or yq_filter:
        fmt_flag = "json" if jq_filter else "yaml"
        result = runner.run([tool, "get", "pods", "-o", fmt_flag] + args, capture=True)
        out = runner.jq(result.stdout, jq_filter) if jq_filter else runner.yq(result.stdout, yq_filter)
        print(out, end="")
        return

    result = runner.run([tool, "get", "pods", "-o", "json"] + args, capture=True)
    data = json.loads(result.stdout)
    items = data.get("items", [])

    rows = []
    for item in items:
        meta = item.get("metadata", {})
        status = item.get("status", {})
        containers = status.get("containerStatuses", [])
        rows.append({
            "name": meta.get("name", ""),
            "status": status.get("phase", "Unknown"),
            "ready": f"{sum(1 for c in containers if c.get('ready'))}/{len(containers)}",
            "restarts": str(sum(c.get("restartCount", 0) for c in containers)),
            "age": meta.get("creationTimestamp", "")[:10],
        })

    output.print_output(
        rows, fmt=fmt,
        columns=["name", "status", "ready", "restarts", "age"],
        title="Pods",
    )


@app.command("top")
def top(
    namespace: str = typer.Option("", "--namespace", "-n", help="Kubernetes namespace."),
    context: str = typer.Option("", "--context", "-c", help="kubeconfig context."),
    use_oc: bool = typer.Option(False, "--oc", help="Use 'oc' instead of 'kubectl'."),
) -> None:
    """Show CPU/memory usage for pods, sorted by CPU descending."""
    tool = _kubectl(use_oc)
    runner.run([tool, "top", "pods", "--sort-by=cpu"] + _ctx_args(namespace, context))


@app.command("ctx")
def ctx(
    name: str = typer.Argument("", help="Context name to switch to. Omit to list available contexts."),
    fmt: OutputFormat = output.output_option(),
) -> None:
    """Switch or list kubectl contexts."""
    runner.check_tool("kubectl")

    if not name:
        runner.run(["kubectl", "config", "get-contexts"])
        return

    runner.run(["kubectl", "config", "use-context", name])
    output.print_record({"context": name, "status": "active"}, fmt=fmt)


@app.command("logs")
def logs(
    pod: str = typer.Argument(..., help="Pod name."),
    container: str = typer.Option("", "--container", "-c", help="Container name."),
    namespace: str = typer.Option("", "--namespace", "-n", help="Kubernetes namespace."),
    context: str = typer.Option("", "--context", help="kubeconfig context."),
    tail: int = typer.Option(100, "--tail", help="Number of lines to tail."),
    follow: bool = typer.Option(False, "--follow", "-f", help="Stream logs."),
    grep: str = typer.Option("", "--grep", "-g", help="Filter log lines (grep pattern)."),
    use_oc: bool = typer.Option(False, "--oc", help="Use 'oc' instead of 'kubectl'."),
) -> None:
    """Tail logs from a pod/container, with optional grep filter."""
    tool = _kubectl(use_oc)
    args = _ctx_args(namespace, context)

    cmd = [tool, "logs", pod, f"--tail={tail}"] + args
    if container:
        cmd += ["--container", container]
    if follow:
        cmd += ["--follow"]

    if grep:
        runner.check_tool("grep")
        result = runner.run(cmd, capture=True)
        runner.run(["grep", grep], input=result.stdout)
    else:
        runner.run(cmd)
