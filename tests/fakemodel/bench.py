"""Build the stand-in's recording for a benchmark matter from its pages and ideal answer (invented
data only)."""

import json
from pathlib import Path

from casefile import benchrun, matter as matters


def recordings_for(matter_root) -> list[dict]:
    root = Path(matter_root)
    loaded = matters.load(root)
    ideal = json.loads((root / "ideal.json").read_text(encoding="utf-8"))
    return [{"name": f"bench-{loaded.number}", "messages": benchrun.messages(loaded),
             "answer": json.dumps(ideal, ensure_ascii=False)}]
