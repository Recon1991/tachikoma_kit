from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass(frozen=True)
class InstanceInfo:
    name: str
    path: Path  # instance root (the folder containing mods/, kubejs/, etc.)
    has_mods: bool
    has_kubejs: bool

def default_prism_instances_dirs() -> List[Path]:
    # best-effort defaults; can be overridden via config later
    dirs: List[Path] = []
    home = Path.home()

    # Windows APPDATA
    appdata = os.environ.get("APPDATA")
    if appdata:
        dirs.append(Path(appdata) / "PrismLauncher" / "instances")
        dirs.append(Path(appdata) / "prismlauncher" / "instances")  # sometimes different casing

    # Linux
    dirs.append(home / ".local" / "share" / "PrismLauncher" / "instances")

    # macOS
    dirs.append(home / "Library" / "Application Support" / "PrismLauncher" / "instances")

    # De-dupe
    out = []
    seen = set()
    for d in dirs:
        dd = d.resolve()
        if str(dd) not in seen:
            seen.add(str(dd))
            out.append(dd)
    return out

def is_instance_dir(p: Path) -> Optional[Path]:
    """
    Prism has an instance folder, and inside is typically 'minecraft/'.
    We want the folder that contains mods/.
    """
    if not p.is_dir():
        return None

    # common: <instance>/minecraft/mods
    mc = p / "minecraft"
    if (mc / "mods").is_dir():
        return mc

    # fallback: maybe directly contains mods/
    if (p / "mods").is_dir():
        return p

    return None

def discover_instances(search_dirs: List[Path]) -> List[InstanceInfo]:
    found: List[InstanceInfo] = []
    for base in search_dirs:
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            mcroot = is_instance_dir(child)
            if not mcroot:
                continue
            found.append(
                InstanceInfo(
                    name=child.name,
                    path=mcroot,
                    has_mods=(mcroot / "mods").is_dir(),
                    has_kubejs=(mcroot / "kubejs").is_dir(),
                )
            )
    return found