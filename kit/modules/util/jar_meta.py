from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from zipfile import ZipFile


@dataclass(frozen=True)
class ModJarInfo:
    jar_path: Path
    mod_id: Optional[str]
    version: Optional[str]
    loader_meta_path: Optional[str]  # which file we found meta in


def parse_version_from_filename(name: str) -> Optional[str]:
    """
    Ex: cobblemonraiddens-neoforge-0.7.6+1.21.1.jar -> 0.7.6+1.21.1
    """
    m = re.search(r"cobblemonraiddens.*?-(\d+\.\d+\.\d+\+\d+\.\d+\.\d+)", name)
    return m.group(1) if m else None


def read_modid_and_version(jar_path: Path) -> ModJarInfo:
    """
    Reads NeoForge/Forge/Fabric metadata if present.
    """
    candidates = [
        "META-INF/neoforge.mods.toml",
        "META-INF/mods.toml",
        "fabric.mod.json",
        "quilt.mod.json",
        "META-INF/MANIFEST.MF",
    ]

    mod_id = None
    version = None
    found = None

    try:
        with ZipFile(jar_path) as z:
            names = set(z.namelist())
            for c in candidates:
                if c not in names:
                    continue
                found = c
                raw = z.read(c).decode("utf-8", errors="replace")

                if c.endswith(".toml"):
                    # lightweight parse
                    m_id = re.search(r'modId\s*=\s*"([^"]+)"', raw)
                    m_v = re.search(r'version\s*=\s*"([^"]+)"', raw)
                    if m_id:
                        mod_id = m_id.group(1)
                    if m_v:
                        version = m_v.group(1)

                elif c.endswith(".json"):
                    # fabric/quilt json
                    # avoid importing json for speed; simple regex ok
                    m_id = re.search(r'"id"\s*:\s*"([^"]+)"', raw)
                    m_v = re.search(r'"version"\s*:\s*"([^"]+)"', raw)
                    if m_id:
                        mod_id = m_id.group(1)
                    if m_v:
                        version = m_v.group(1)

                elif c.endswith("MANIFEST.MF"):
                    # not always helpful
                    m_v = re.search(r"Implementation-Version:\s*(.+)", raw)
                    if m_v:
                        version = (m_v.group(1) or "").strip()

                break
    except Exception:
        pass

    # filename fallback for version
    if not version:
        version = parse_version_from_filename(jar_path.name)

    return ModJarInfo(jar_path=jar_path, mod_id=mod_id, version=version, loader_meta_path=found)