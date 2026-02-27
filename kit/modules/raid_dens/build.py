from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from kit.modules.raid_dens.schema import BossSchema
from kit.modules.util.csv_io import read_csv


@dataclass
class BuildStats:
    total_rows: int = 0
    written: int = 0
    skipped: int = 0


def build_kubejs_boss_jsons(
    instance_root: Path,
    schema: BossSchema,
    in_csv: Path,
    clean: bool = False,
    fail_on_mismatch: bool = False,
) -> Tuple[Path, BuildStats]:
    rows = read_csv(in_csv)
    out_dir = instance_root / "kubejs" / "data" / "cobblemonraiddens" / "raid" / "boss"
    out_dir.mkdir(parents=True, exist_ok=True)

    if clean and out_dir.exists():
        for p in out_dir.glob("*.json"):
            p.unlink()

    stats = BuildStats(total_rows=len(rows))

    for row in rows:
        # required: species and tier/type at least
        species = (row.get("pokemon_species") or "").strip()
        if not species:
            stats.skipped += 1
            continue

        source_id = (row.get("source_id") or "").strip()
        if not source_id:
            source_id = species  # fallback

        # optional mismatch check
        filename_stem = (row.get("filename_stem") or source_id).strip()
        if fail_on_mismatch and filename_stem.lower() != species.lower():
            raise RuntimeError(f"Mismatch: filename_stem={filename_stem} vs species={species} (source_id={source_id})")

        obj = schema.unflatten(row)
        out_file = out_dir / f"{source_id}.json"
        out_file.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        stats.written += 1

    return out_dir, stats