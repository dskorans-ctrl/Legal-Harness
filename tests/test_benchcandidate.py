import json
import copy
import pytest

from casefile.benchcandidate import (
    EMPTY, CandidateError, CandidateFact, CandidateFlag, parse, parse_text
)

GOOD = {
    "facts": [{"cite": "MED0001", "quote": "Pain 7/10 in the low back.", "text": "Pain was 7/10."}],
    "flags": [{"kind": "gap", "cites": ["MED0002"], "about": "The x-ray report is missing."}],
}

def test_parse_good():
    from_dict = parse(GOOD)
    from_text = parse_text(json.dumps(GOOD))
    assert from_dict == from_text
    assert from_dict.facts == (CandidateFact("MED0001", "Pain 7/10 in the low back.", "Pain was 7/10."),)
    assert from_dict.flags == (CandidateFlag("gap", ("MED0002",), "The x-ray report is missing."),)
    assert EMPTY.facts == ()
    assert EMPTY.flags == ()

def case1():
    parse_text("{not json")

def case2():
    parse([GOOD])

def case3():
    data = copy.deepcopy(GOOD)
    del data["flags"]
    parse(data)

def case4():
    data = copy.deepcopy(GOOD)
    data["facts"][0].pop("text")
    parse(data)

def case5():
    data = copy.deepcopy(GOOD)
    data["facts"][0]["page"] = 1
    parse(data)

def case6():
    data = copy.deepcopy(GOOD)
    data["flags"][0]["kind"] = "note"
    parse(data)

def case7():
    data = copy.deepcopy(GOOD)
    data["flags"][0]["cites"] = []
    parse(data)

CASES = [
    (case1, "not JSON: "),
    (case2, "expected a JSON object with keys facts and flags"),
    (case3, "expected a JSON object with keys facts and flags"),
    (case4, "fact 1: expected keys cite, quote, text (strings)"),
    (case5, "fact 1: expected keys cite, quote, text (strings)"),
    (case6, "flag 1: kind must be conflict or gap"),
    (case7, "flag 1: cites must be a nonempty list of strings"),
]

def test_refusals(capsys):
    ok = 0
    for call, expected in CASES:
        try:
            call()
        except CandidateError as exc:
            if expected in str(exc):
                ok += 1
    with capsys.disabled():
        print(f"candidate_refusals={ok} of 7")
    assert ok == 7
