"""commands/kube_cmd.py — kubectl / oc helpers."""
from __future__ import annotations

import json

import typer
from rich import print as rprint
from rich.table import Table

from mod_cli.core import config, runner

app = typer.Typer(help="kubectl / oc helpers.")

_KUBECTL = "kubectl"  # override with OC=1 env var or --oc flag


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
) -> None:
    """List pods in a namespace."""
    tool = _kubectl(use_oc)
    args = _ctx_args(namespace, context)

    if jq_filter or yq_filter:
        fmt = "json" if jq_filter else "yaml"
        result = runner.run([tool, "get", "pods", "-o", fmt] + args, capture=True)
        output = runner.jq(result.stdout, jq_filter) if jq_filter else runner.yq(result.stdout, yq_filter)
        rprint(output)
        return

    result = runner.run(
        [tool, "get", "pods", "-o", "json"] + args, capture=True
    )
    data = json.loads(result.stdout)
    items = data.get("items", [])

    if not items:
        rprint("[yellow]No pods found.[/yellow]")
        return

    table = Table(title="Pods", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Status")
    table.add_column("Ready")
    table.add_column("Restarts", style="yellow")
    table.add_column("Age")

    for item in items:
        meta = item.get("metadata", {})
        status = item.get("status", {})
        phase = status.get("phase", "Unknown")
        containers = status.get("containerStatuses", [])
        ready = f"{sum(1 for c in containers if c.get('ready'))}/{len(containers)}"
        restarts = str(sum(c.get("restartCount", 0) for c in containers))
        phase_style = {"Running": "[green]", "Pending": "[yellow]", "Failed": "[red]"}.get(phase, "")
        table.add_row(
            meta.get("name", ""),
            f"{phase_style}{phase}[/]" if phase_style else phase,
            ready,
            restarts,
            meta.get("creationTimestamp", "")[:10],
        )

    rprint(table)


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
) -> None:
    """Switch or list kubectl contexts."""
    runner.check_tool("kubectl")

    if not name:
        runner.run(["kubectl", "config", "get-contexts"])
        return

    runner.run(["kubectl", "config", "use-context", name])
    rprint(f"[green]Switched to context:[/green] {name}")


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
        runner.run(["grep", grep], input=result.stdout)  # type: ignore[call-arg]
    else:
        runner.run(cmd)
