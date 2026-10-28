"""Build the stand-in's recording for a benchmark matter from its pages and ideal answer (invented
data only)."""

import json
from pathlib import Path

from casefile import benchrun, gates, matter as matters, schema


def extraction_card():
    text = benchrun.CARD_TEXT + (
        'The first key is "prompt_id" and the last key is "end_id", both holding the value '
        'of the prompt_id line at the top of this message.\n')
    return gates.Card("bench_extract", text, schema.load(
        Path(__file__).resolve().parents[2] / "schemas" / "bench_extract.schema.json"))


def recordings_for(matter_root) -> list[dict]:
    root = Path(matter_root)
    loaded = matters.load(root)
    ideal = json.loads((root / "ideal.json").read_text(encoding="utf-8"))
    card = extraction_card()
    answer = {"prompt_id": "__PROMPT_ID__", **ideal, "end_id": "__PROMPT_ID__"}
    return [{"name": f"bench-{loaded.number}", "messages": benchrun.messages(loaded),
             "answer": json.dumps(ideal, ensure_ascii=False)},
            {"name": f"gates-{loaded.number}",
             "messages": gates.messages(card, loaded.pages, "__PROMPT_ID__", matter=loaded.number),
             "answer": json.dumps(answer, ensure_ascii=False)}]
