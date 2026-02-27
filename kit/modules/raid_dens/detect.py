from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from kit.modules.util.jar_meta import ModJarInfo, read_modid_and_version


@dataclass(frozen=True)
class RaidDensDetection:
    jar_info: ModJarInfo
    confidence: float
    reason: str


def detect_raiddens_jar(mods_dir: Path) -> RaidDensDetection:
    jars = sorted(mods_dir.glob("*.jar"))
    # Fast: filename
    for jar in jars:
        if "cobblemonraiddens" in jar.name.lower():
            info = read_modid_and_version(jar)
            # if modId confirms, raise confidence
            if info.mod_id == "cobblemonraiddens":
                return RaidDensDetection(info, 0.98, "Matched filename and modId in jar metadata.")
            return RaidDensDetection(info, 0.85, "Matched filename; modId not confirmed (metadata missing/unreadable).")

    # Robust: open jars and check modId
    for jar in jars:
        info = read_modid_and_version(jar)
        if info.mod_id == "cobblemonraiddens":
            return RaidDensDetection(info, 0.92, "Matched modId in jar metadata.")

    raise FileNotFoundError("Cobblemon Raid Dens jar not found in mods/ directory.")