from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from kit.modules.raid_dens.detect import RaidDensDetection
from kit.modules.raid_dens.schema import BossSchema


@dataclass(frozen=True)
class DoctorReport:
    instance_root: Path
    detection: RaidDensDetection
    schema: BossSchema
    boss_path_exists_in_jar: bool
    boss_file_count: int


def doctor(instance_root: Path, detection: RaidDensDetection, schema: BossSchema) -> DoctorReport:
    from zipfile import ZipFile

    boss_root = schema.boss_root
    boss_count = 0
    exists = False

    with ZipFile(detection.jar_info.jar_path) as z:
        names = z.namelist()
        exists = any(n.startswith(boss_root) for n in names)
        boss_count = sum(1 for n in names if n.startswith(boss_root) and n.endswith(".json"))

    return DoctorReport(
        instance_root=instance_root,
        detection=detection,
        schema=schema,
        boss_path_exists_in_jar=exists,
        boss_file_count=boss_count,
    )