from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
from zipfile import ZipFile

from kit.modules.raid_dens.schema import BossSchema
from kit.modules.util.csv_io import write_csv


@dataclass
class DumpStats:
    total: int = 0
    ok: int = 0
    failed: int = 0
    mismatched: int = 0


def list_boss_jsons(jar_path: Path, boss_root: str) -> List[str]:
    with ZipFile(jar_path) as z:
        return sorted([n for n in z.namelist() if n.startswith(boss_root) and n.endswith(".json")])


def dump_bosses_to_csv(
    jar_path: Path,
    schema: BossSchema,
    mod_version: str,
    out_csv: Path,
    out_errors_csv: Path,
    fail_on_mismatch: bool = False,
) -> DumpStats:
    boss_paths = list_boss_jsons(jar_path, schema.boss_root)
    stats = DumpStats(total=len(boss_paths))

    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    with ZipFile(jar_path) as z:
        for internal in boss_paths:
            filename = Path(internal).name
            try:
                obj = json.loads(z.read(internal).decode("utf-8"))
                row = schema.flatten(obj, source_file=filename, mod_version=mod_version)
                rows.append(row)
                stats.ok += 1
                if not row.get("id_matches_species"):
                    stats.mismatched += 1
            except Exception as ex:
                stats.failed += 1
                errors.append({"source_file": filename, "error": f"{type(ex).__name__}: {ex}"})

    write_csv(rows, out_csv)
    if errors:
        write_csv(errors, out_errors_csv)

    if fail_on_mismatch and stats.mismatched > 0:
        raise RuntimeError(f"{stats.mismatched} entries have filename/species mismatches (see CSV column id_matches_species).")

    return stats