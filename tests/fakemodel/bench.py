"""Build the stand-in's recording for a benchmark matter from its pages and ideal answer (invented
data only)."""

import json
from pathlib import Path

from casefile import extract, gates, matter as matters


def extraction_card():
    return extract.card()


def recording_for(card, pages, number, answer, *, body=None) -> dict:
    return {"name": f"gates-{number}",
            "messages": gates.messages(card, pages, "__PROMPT_ID__", matter=number, body=body),
            "answer": json.dumps({"prompt_id": "__PROMPT_ID__", **answer,
                                  "end_id": "__PROMPT_ID__"}, ensure_ascii=False)}


def recordings_for(matter_root) -> list[dict]:
    root = Path(matter_root)
    loaded = matters.load(root)
    ideal = json.loads((root / "ideal.json").read_text(encoding="utf-8"))
    card = extraction_card()
    return [recording_for(card, loaded.pages, loaded.number, ideal)]
