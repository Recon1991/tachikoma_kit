from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

def _state_path() -> Path:
    # Cross-platform-ish default (good enough; refine later if you want)
    home = Path.home()
    return home / ".mayview-kit" / "state.json"

@dataclass
class State:
    working_instance: Optional[str] = None  # path string

def load_state() -> State:
    p = _state_path()
    if not p.exists():
        return State()
    data = json.loads(p.read_text(encoding="utf-8"))
    return State(working_instance=data.get("working_instance"))

def save_state(state: State) -> None:
    p = _state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"working_instance": state.working_instance}, indent=2), encoding="utf-8")