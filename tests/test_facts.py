"""Fourteen case file checks, including each W4 corruption and identity control."""

import copy
import hashlib
import json
from pathlib import Path

from casefile import facts, matter


FIXTURE = Path(__file__).parent / "fixtures" / "matters" / "9001.001"
FIXED_AT = "2026-10-28T00:00:00+00:00"
QUOTE = 'He said "no prior injury".'
PAGES = (
    matter.Page("medical", 1, QUOTE, ("MED0001",)),
    matter.Page("medical", 2, QUOTE, ("MED0002",)),
    matter.Page("probe", 1, QUOTE, ()),
)
ANSWER = {"facts": [{"cite": "MED0001", "quote": QUOTE, "text": "He reported no prior injury."}],
          "flags": [{"kind": "conflict", "cites": ["MED0001", "MED0002"],
                     "about": "The reports disagree."}]}


def fact_event(quote="The record was received."):
    return facts.Event("fact", {"id": "F1", "cite": "MED0001", "page_id": "medical/001",
                                "quote": quote, "text": "The record was received.", "run_id": 1},
                       at=FIXED_AT)


def output_event(seq):
    return facts.Event("output", {"name": "memo", "path": "/invented/outputs/memo.docx",
                                  "built_from_seq": seq, "facts": 1, "conflicts": 0,
                                  "gaps": 0, "open": 0}, at=FIXED_AT)


def three_events(path):
    facts.append(path, [fact_event()])
    prefix = path.read_bytes()
    run = facts.Event("run", {"run_id": 1, "job": "memo", "card": "bench_extract",
                              "card_version": "invented", "pages": ["medical/001"],
                              "ok": True, "read": ["medical/001"], "uncited": [], "failed": []},
                      at=FIXED_AT)
    facts.append(path, [run, output_event(2)])
    return prefix


def refusal(path, line, message):
    try:
        facts.load(path)
    except facts.CaseFileError as exc:
        assert str(exc) == (f"case file chain broken at line {line}; "
                            "the file was edited or truncated"), message
    else:
        raise AssertionError(message)


def round_trip(path):
    assert facts.load(path).last_seq == 0
    prefix = three_events(path)
    loaded = facts.load(path)
    lines = path.read_bytes().splitlines()
    assert len(lines) == 3 and path.read_bytes().startswith(prefix), "W4(d): append overwrote complete events"
    assert [event.seq for event in loaded.events] == [1, 2, 3]
    assert [event.prev for event in loaded.events] == ["", *[hashlib.sha256(line).hexdigest() for line in lines[:2]]]
    assert loaded.facts[0].quote == "The record was received."
    assert loaded.runs[0]["job"] == "memo" and loaded.outputs[0]["built_from_seq"] == 2


def edited_line(path):
    three_events(path)
    raw = path.read_bytes()
    assert raw.count(b"The record was received.") == 2
    path.write_bytes(raw.replace(b"The record was received.", b"The record was altered.", 1))
    refusal(path, 2, "W4(a): edited line accepted")


def removed_middle(path):
    three_events(path)
    lines = path.read_bytes().splitlines(keepends=True)
    path.write_bytes(lines[0] + lines[2])
    refusal(path, 2, "W4: removed middle line accepted")


def cut_middle(path):
    three_events(path)
    lines = path.read_bytes().splitlines(keepends=True)
    path.write_bytes(lines[0] + lines[1][:20] + b"\n" + lines[2])
    refusal(path, 2, "W4(h): cut middle line accepted")


def torn_tail(path):
    three_events(path)
    lines = path.read_bytes().splitlines(keepends=True)
    tail = lines[2][:25]
    prefix = b"".join(lines[:2])
    path.write_bytes(prefix + tail)
    before = path.read_bytes()
    try:
        loaded = facts.load(path)
    except facts.CaseFileError as exc:
        raise AssertionError("W4(f): torn tail refused") from exc
    assert loaded.torn == len(tail) and loaded.last_seq == 2, "W4(f): torn tail counted as an event"
    assert path.read_bytes() == before, "load rewrote the torn file"
    try:
        facts.append(path, [output_event(2)])
        recovered = facts.load(path)
    except facts.CaseFileError as exc:
        raise AssertionError("W4(g): append did not discard the torn tail") from exc
    assert recovered.last_seq == 3 and recovered.torn == 0, "W4(g): append did not discard the torn tail"
    assert path.read_bytes().startswith(prefix)
    assert len(path.read_bytes().splitlines()) == 3


def missing_newline(path):
    three_events(path)
    path.write_bytes(path.read_bytes()[:-1])
    prefix = path.read_bytes()
    loaded = facts.load(path)
    assert loaded.last_seq == 3 and loaded.torn == 0, "complete last object treated as torn"
    facts.append(path, [output_event(3)])
    loaded = facts.load(path)
    assert loaded.last_seq == 4 and path.read_bytes().startswith(prefix + b"\n")


def ideal_merge(path):
    pages = matter.load(FIXTURE).pages
    answer = json.loads((FIXTURE / "ideal.json").read_text(encoding="utf-8"))
    events = facts.merge(facts.CaseFile(), answer, pages, 7)
    assert sum(event.kind == "fact" for event in events) == 31
    assert sum(event.kind == "flag" for event in events) == 9
    stored = facts.append(path, events)
    assert len(stored.facts) == 31 and len(stored.flags) == 9 and stored.last_seq == 40
    assert stored.flags[0].page_ids == ["medical/001", "employer/001"], "G1 pages were not resolved"
    known = {page.page_id for page in pages}
    assert all(set(record.page_ids) <= known for record in [*stored.facts, *stored.flags])
    assert all(event.payload["run_id"] == 7 for event in stored.events)
    assert [event.payload["id"] for event in events] == [
        *[f"F{seq}" for seq in range(1, 32)], *[f"G{seq}" for seq in range(32, 41)]]


def repeat_merge(path):
    pages = matter.load(FIXTURE).pages
    answer = json.loads((FIXTURE / "ideal.json").read_text(encoding="utf-8"))
    stored = facts.append(path, facts.merge(facts.CaseFile(), answer, pages, 1))
    assert facts.merge(stored, answer, pages, 2) == [], "repeat ideal answer added events"
    stored = facts.CaseFile()
    stored.extend(facts.merge(stored, ANSWER, PAGES, 1))
    variant = copy.deepcopy(ANSWER)
    variant["facts"][0]["quote"] = "He said “no prior injury”."
    events = facts.merge(stored, variant, PAGES, 2)
    assert len(events) == 0, f"W4(b): folded repeat added {len(events)} event(s)"
    assert len(stored.events) == 2, "merge mutated the case file"


def new_cite(path):
    stored = facts.append(path, facts.merge(facts.CaseFile(), ANSWER, PAGES, 1))
    answer = copy.deepcopy(ANSWER)
    answer["facts"][0]["cite"] = "MED 0002"
    events = facts.merge(stored, answer, PAGES, 2)
    assert len(events) == 1 and events[0].kind == "cite", "new page did not add exactly one cite"
    assert events[0].payload == {"fact": "F1", "cite": "MED0002", "page_id": "medical/002", "run_id": 2}
    stored = facts.append(path, events)
    assert stored.facts[0].page_ids == ["medical/001", "medical/002"]
    assert stored.facts[0].cites == ["MED0001", "MED0002"]
    assert facts.merge(stored, answer, PAGES, 3) == []
    answer["facts"][0]["cite"] = "probe/001"
    assert facts.merge(stored, answer, PAGES, 3)[0].payload["page_id"] == "probe/001"


def new_reading(path):
    stored = facts.append(path, facts.merge(facts.CaseFile(), ANSWER, PAGES, 1))
    answer = copy.deepcopy(ANSWER)
    answer["facts"][0]["text"] = "The history records a denial of prior injury."
    events = facts.merge(stored, answer, PAGES, 2)
    assert len(events) == 1 and events[0].kind == "reading", "new reading was lost or duplicated"
    assert events[0].payload["fact"] == "F1" and events[0].payload["run_id"] == 2
    stored = facts.append(path, events)
    assert stored.facts[0].readings == [ANSWER["facts"][0]["text"], answer["facts"][0]["text"]]
    assert facts.merge(stored, answer, PAGES, 3) == []


def new_about(path):
    stored = facts.append(path, facts.merge(facts.CaseFile(), ANSWER, PAGES, 1))
    answer = copy.deepcopy(ANSWER)
    answer["flags"][0]["about"] = "The two records give different histories."
    events = facts.merge(stored, answer, PAGES, 2)
    assert len(events) == 1 and events[0].kind == "about", "W4(c): known flag became a new flag"
    assert events[0].payload["flag"] == "G2" and events[0].payload["run_id"] == 2
    stored = facts.append(path, events)
    assert stored.flags[0].abouts == [ANSWER["flags"][0]["about"], answer["flags"][0]["about"]]
    assert facts.merge(stored, answer, PAGES, 3) == []


def reordered_cites(path):
    stored = facts.append(path, facts.merge(facts.CaseFile(), ANSWER, PAGES, 1))
    answer = copy.deepcopy(ANSWER)
    answer["flags"][0]["cites"] = ["medical/002", "MED-0001"]
    assert facts.merge(stored, answer, PAGES, 2) == [], "W4(c): reordered flag cites added events"


def changed_since(path):
    stored = facts.append(path, [fact_event(), output_event(1)])
    before = stored.last_seq
    answer = copy.deepcopy(ANSWER)
    answer["flags"][0]["kind"] = "gap"
    stored = facts.append(path, facts.merge(stored, answer, PAGES, 2))
    answer["facts"][0]["cite"] = "MED0002"
    answer["facts"][0]["text"] = "A second reading."
    answer["flags"][0]["about"] = "A second gap description."
    stored = facts.append(path, facts.merge(stored, answer, PAGES, 3))
    assert stored.changed_since(before) == {"fact": 1, "cite": 1, "reading": 1, "flag": 1, "about": 1}
    assert stored.changed_since(stored.last_seq) == dict.fromkeys(facts.CHANGE_KINDS, 0)


def stale_outputs(path):
    stored = facts.append(path, [fact_event(), output_event(1)])
    assert stored.stale_outputs() == [], "fresh memo marked stale"
    event = fact_event("Another received record.")
    event = facts.Event("fact", {**event.payload, "id": "F3"}, at=FIXED_AT)
    stored = facts.append(path, [event])
    assert {event.at for event in stored.events} == {FIXED_AT}
    assert stored.stale_outputs() == ["memo"], "W4(e): new fact with the same timestamp left memo current"
    stored = facts.append(path, [output_event(stored.last_seq)])
    assert stored.stale_outputs() == [], "rebuilt memo still stale"


CASES = (round_trip, edited_line, removed_middle, cut_middle, torn_tail, missing_newline,
         ideal_merge, repeat_merge, new_cite, new_reading, new_about, reordered_cites,
         changed_since, stale_outputs)


def test_casefile(tmp_path):
    assert len(CASES) == 14
    for case in CASES:
        case(tmp_path / f"{case.__name__}.jsonl")
    print("casefile_ok=14 of 14")
