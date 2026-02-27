from __future__ import annotations

import typer
from pathlib import Path
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from kit.modules.util.console import console
from kit.modules.util.mc_instance import find_instance_root
from kit.modules.raid_dens.detect import detect_raiddens_jar
from kit.modules.raid_dens.schema import pick_schema
from kit.modules.raid_dens.dump import dump_bosses_to_csv
from kit.modules.raid_dens.build import build_kubejs_boss_jsons
from kit.modules.raid_dens.doctor import doctor as doctor_scan

app = typer.Typer(help="Cobblemon Raid Dens tools (dump/build/doctor)")


def _boot_banner(title: str) -> None:
    console.print(Panel.fit(Text(title, style="bold"), subtitle="Mayview Kit • Tachikoma online 🕷️"))


@app.command()
def doctor(
    instance: Path = typer.Option(..., "--instance", "-i", help="Path inside your Minecraft instance (any subfolder is okay)."),
):
    _boot_banner("raid-dens • doctor")
    paths = find_instance_root(instance)
    det = detect_raiddens_jar(paths.mods)
    schema = pick_schema(det.jar_info.version)
    report = doctor_scan(paths.root, det, schema)

    t = Table(title="Raid Dens Detection", show_lines=True)
    t.add_column("Field", style="bold")
    t.add_column("Value")

    t.add_row("Instance root", str(report.instance_root))
    t.add_row("Jar", str(report.detection.jar_info.jar_path))
    t.add_row("Detected modId", str(report.detection.jar_info.mod_id))
    t.add_row("Detected version", str(report.detection.jar_info.version))
    t.add_row("Meta file", str(report.detection.jar_info.loader_meta_path))
    t.add_row("Confidence", f"{report.detection.confidence:.2f} — {report.detection.reason}")
    t.add_row("Schema", report.schema.schema_id)
    t.add_row("Boss root", report.schema.boss_root)
    t.add_row("Boss path exists", str(report.boss_path_exists_in_jar))
    t.add_row("Boss JSON count", str(report.boss_file_count))

    console.print(t)


@app.command()
def dump(
    instance: Path = typer.Option(..., "--instance", "-i", help="Path inside your Minecraft instance."),
    out: Path = typer.Option(Path("master_truth/raid_dens_bosses.csv"), "--out", "-o", help="Output CSV path."),
    errors: Path = typer.Option(Path("master_truth/raid_dens_errors.csv"), "--errors", help="Parse error CSV path."),
    fail_on_mismatch: bool = typer.Option(False, "--fail-on-mismatch", help="Fail if filename stem != pokemon.species."),
):
    _boot_banner("raid-dens • dump (jar → master CSV)")
    paths = find_instance_root(instance)
    det = detect_raiddens_jar(paths.mods)
    schema = pick_schema(det.jar_info.version)
    mod_version = det.jar_info.version or "UNKNOWN"

    stats = dump_bosses_to_csv(
        jar_path=det.jar_info.jar_path,
        schema=schema,
        mod_version=mod_version,
        out_csv=out,
        out_errors_csv=errors,
        fail_on_mismatch=fail_on_mismatch,
    )

    console.print(Panel.fit(
        f"[bold]Dump complete[/bold]\n"
        f"Scanned: {stats.total}\n"
        f"OK: {stats.ok}\n"
        f"Failed: {stats.failed}\n"
        f"Mismatched (filename vs species): {stats.mismatched}\n"
        f"CSV: {out}\n"
        f"Errors: {errors if stats.failed else '(none)'}"
    ))


@app.command()
def build(
    instance: Path = typer.Option(..., "--instance", "-i", help="Path inside your Minecraft instance."),
    inp: Path = typer.Option(..., "--in", help="Input master CSV path."),
    clean: bool = typer.Option(False, "--clean", help="Delete existing kubejs boss JSONs before writing."),
    fail_on_mismatch: bool = typer.Option(False, "--fail-on-mismatch", help="Fail if filename stem != pokemon.species."),
):
    _boot_banner("raid-dens • build (master CSV → kubejs/data)")
    paths = find_instance_root(instance)
    det = detect_raiddens_jar(paths.mods)
    schema = pick_schema(det.jar_info.version)

    out_dir, stats = build_kubejs_boss_jsons(
        instance_root=paths.root,
        schema=schema,
        in_csv=inp,
        clean=clean,
        fail_on_mismatch=fail_on_mismatch,
    )

    console.print(Panel.fit(
        f"[bold]Build complete[/bold]\n"
        f"Input rows: {stats.total_rows}\n"
        f"Written: {stats.written}\n"
        f"Skipped: {stats.skipped}\n"
        f"Output dir: {out_dir}"
    ))