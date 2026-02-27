from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InstancePaths:
    root: Path
    mods: Path
    kubejs: Path
    kubejs_data: Path


def find_instance_root(start: Path, max_up: int = 8) -> InstancePaths:
    """
    Heuristic: walk upward until we find a directory containing mods/.
    """
    p = start.resolve()
    for _ in range(max_up + 1):
        mods = p / "mods"
        if mods.is_dir():
            kubejs = p / "kubejs"
            kubejs_data = kubejs / "data"
            return InstancePaths(root=p, mods=mods, kubejs=kubejs, kubejs_data=kubejs_data)
        if p.parent == p:
            break
        p = p.parent
    raise FileNotFoundError(f"Could not find instance root containing mods/ (starting at {start}).")