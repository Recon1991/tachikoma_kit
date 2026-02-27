from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
MAX_MOVES = 4

@dataclass(frozen=True)
class BossSchema:
    schema_id: str
    boss_root: str  # path inside jar
    supported_major_minor: str  # e.g. "0.7"

    def flatten(self, obj: Dict[str, Any], source_file: str, mod_version: str) -> Dict[str, Any]:
        pokemon = obj.get("pokemon") if isinstance(obj.get("pokemon"), dict) else {}
        moves = pokemon.get("moves") if isinstance(pokemon.get("moves"), list) else []

        species = pokemon.get("species")
        filename_stem = source_file.rsplit(".", 1)[0]

        row = {
            "source_id": filename_stem,
            "source_file": source_file,
            "source_mod_version": mod_version,
            "schema_id": self.schema_id,

            "filename_stem": filename_stem,
            "pokemon_species": species,

            "raid_tier": obj.get("raid_tier"),
            "raid_type": obj.get("raid_type"),
            "weight": obj.get("weight"),

            "id_matches_species": (str(species).lower() == filename_stem.lower()) if species else False,
        }
        
        for i in range(MAX_MOVES):
            row[f"move_{i+1}"] = moves[i] if i < len(moves) else ""
            
        row["moves_count"] = len(moves)
        return row

    def unflatten(self, row: Dict[str, str]) -> Dict[str, Any]:
        moves: List[str] = []

        for i in range(MAX_MOVES):
            v = (row.get(f"move_{i+1}") or "").strip()
            if v:
                moves.append(v)
                
        if not moves:
            moves_str = (row.get("pokemon_moves") or "").strip()
            if moves_str:
                moves = [m.strip() for m in moves_str.split(",") if m.strip()]
                
        
        # weight can be blank in CSV; default 0.0
        w_raw = (row.get("weight") or "").strip()
        try:
            weight = float(w_raw) if w_raw != "" else 0.0
        except ValueError:
            weight = 0.0

        return {
            "pokemon": {"species": row.get("pokemon_species"),"moves": moves,},
            "raid_tier": row.get("raid_tier"),
            "raid_type": row.get("raid_type"),
            "weight": weight,
        }


def pick_schema(mod_version: Optional[str]) -> BossSchema:
    """
    Minimal registry for now:
    - 0.7.x uses boss_root = data/cobblemonraiddens/raid/boss/
    """
    # If version unknown, assume current known layout.
    major_minor = None
    if mod_version and "." in mod_version:
        parts = mod_version.split(".")
        if len(parts) >= 2:
            major_minor = f"{parts[0]}.{parts[1]}"

    if major_minor == "0.7" or major_minor is None:
        return BossSchema(
            schema_id="cobblemonraiddens:boss@0.7.x",
            boss_root="data/cobblemonraiddens/raid/boss/",
            supported_major_minor="0.7",
        )

    # Fallback: treat as 0.7 layout unless later versions diverge
    return BossSchema(
        schema_id=f"cobblemonraiddens:boss@{major_minor}.x",
        boss_root="data/cobblemonraiddens/raid/boss/",
        supported_major_minor=major_minor,
    )