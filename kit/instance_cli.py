from __future__ import annotations
import typer
from rich.table import Table
from kit.modules.util.console import console
from kit.instances import default_prism_instances_dirs, discover_instances
from kit.state import load_state, save_state

app = typer.Typer(help="Discover and manage Prism instances")

@app.command("list")
def list_instances():
    inst = discover_instances(default_prism_instances_dirs())
    t = Table(title="Prism Instances")
    t.add_column("#", justify="right")
    t.add_column("Name", style="bold")
    t.add_column("Path")
    t.add_column("mods")
    t.add_column("kubejs")
    for i, it in enumerate(inst, start=1):
        t.add_row(str(i), it.name, str(it.path), "yes" if it.has_mods else "no", "yes" if it.has_kubejs else "no")
    console.print(t)

@app.command("use")
def use_instance(name_or_index: str):
    inst = discover_instances(default_prism_instances_dirs())
    chosen = None
    if name_or_index.isdigit():
        idx = int(name_or_index) - 1
        if 0 <= idx < len(inst):
            chosen = inst[idx]
    else:
        for it in inst:
            if it.name.lower() == name_or_index.lower():
                chosen = it
                break

    if not chosen:
        raise typer.BadParameter("Instance not found by name or index. Run `kit instance list`.")

    st = load_state()
    st.working_instance = str(chosen.path)
    save_state(st)
    console.print(f"[bold]Working instance set:[/bold] {chosen.name} → {chosen.path}")

@app.command("show")
def show_instance():
    st = load_state()
    if not st.working_instance:
        console.print("[yellow]No working instance set.[/yellow] Use `kit instance use ...`.")
        return
    console.print(f"[bold]Working instance:[/bold] {st.working_instance}")