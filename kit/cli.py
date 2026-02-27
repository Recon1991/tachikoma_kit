from __future__ import annotations

import typer
from kit.modules.raid_dens import cli as raid_dens_cli
from kit.instance_cli import app as instance_app

app = typer.Typer(help="Mayview Kit - modular dev utilities")

app.add_typer(raid_dens_cli.app, name="raid-dens")
app.add_typer(instance_app, name="instance")

if __name__ == "__main__":
    app()