"""The stage 2 answer key loader and its thirteen refusals."""

import copy
import json

import pytest

from casefile import matter as matters
from casefile.benchkey import BenchKeyError, load
from test_matter import make

PAGES = {"medical": [("ER visit.\nPain 7/10 in the low back, no radiation.", "MED0001"),
                     ("He said “no prior injury” at intake.", "MED0002")]}

KEY = {
    "facts": [
        {"id": "F1", "cite": "MED0001", "quote": "Pain 7/10 in the low back, no radiation.",
         "text": "Pain was 7/10 in the low back."},
        {"id": "F2", "cite": "MED0002", "quote": 'He said "no prior   injury"',
         "text": "He reported no prior injury."},
    ],
    "flags": [{"id": "G1", "kind": "gap", "cites": ["MED0001"], "about": "An x-ray report is missing."}],
}


def write(tmp_path, data):
    path = tmp_path / "key.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# --- Helper functions for test_key_refusals ---

def case_top_level_keys_wrong():
    data = {"facts": KEY["facts"]}
    return data

def case_empty_facts():
    data = copy.deepcopy(KEY)
    data["facts"] = []
    return data

def case_fact_missing_text():
    data = copy.deepcopy(KEY)
    del data["facts"][0]["text"]
    return data

def case_duplicate_fact_id():
    data = copy.deepcopy(KEY)
    data["facts"][1]["id"] = "F1"
    return data

def case_cite_not_a_page():
    data = copy.deepcopy(KEY)
    data["facts"][0]["cite"] = "MED0099"
    return data

def case_quote_not_on_page():
    data = copy.deepcopy(KEY)
    data["facts"][0]["quote"] = "Pain 8/10 in the low back, no radiation."
    return data

def case_flag_kind():
    data = copy.deepcopy(KEY)
    data["flags"][0]["kind"] = "note"
    return data

def case_flag_cites_empty():
    data = copy.deepcopy(KEY)
    data["flags"][0]["cites"] = []
    return data

def case_flag_cite_not_a_page():
    data = copy.deepcopy(KEY)
    data["flags"][0]["cites"] = ["MED0099"]
    return data

def case_duplicate_fact_quote():
    data = copy.deepcopy(KEY)
    data["facts"].append({"id": "F3", "cite": "MED0002", "quote": "he said “no prior injury”",
                          "text": "He reported no prior injury."})
    return data

def case_duplicate_flag():
    data = copy.deepcopy(KEY)
    data["flags"][0]["cites"] = ["MED0001", "MED0002"]
    data["flags"].append({"id": "G2", "kind": "gap", "cites": ["MED0002", "MED0001"],
                          "about": "A referral letter is missing."})
    return data


# --- Tests ---

def test_key_loads(tmp_path):
    matter = matters.load(make(tmp_path, PAGES))
    key = load(write(tmp_path, KEY), matter)
    assert len(key.facts) == 2
    assert len(key.flags) == 1
    assert key.facts[1].id == "F2"
    assert key.flags[0].cites == ("MED0001",)


def test_key_refusals(tmp_path, capsys):
    matter = matters.load(make(tmp_path, PAGES))
    ok = 0

    # Define cases: (data_generator_function, match_text)
    cases = [
        (case_top_level_keys_wrong, "expected object with keys facts and flags"), # Case 2
        (case_empty_facts, "facts must be a nonempty list"), # Case 3
        (case_fact_missing_text, "fact 1: expected keys id, cite, quote, text"), # Case 4
        (case_duplicate_fact_id, "fact F1: duplicate id"), # Case 5
        (case_cite_not_a_page, "fact F1: cite MED0099 is not a page of matter 9001.001"), # Case 6
        (case_quote_not_on_page, "fact F1: quote not found on page MED0001"), # Case 7
        (case_flag_kind, "flag G1: kind must be conflict or gap"), # Case 8
        (case_flag_cites_empty, "flag G1: cites must be a nonempty list of Bates stamps"), # Case 9
        (case_flag_cite_not_a_page, "flag G1: cite MED0099 is not a page of matter 9001.001"), # Case 10
        (case_duplicate_fact_quote, "fact F3: same cite and quote as fact F2"), # Case 11
        (case_duplicate_flag, "flag G2: same kind and cites as flag G1"), # Case 12
    ]

    # Case 1: not JSON (raw text)
    path_1 = tmp_path / "bad.json"
    path_1.write_text("{not json", encoding="utf-8")

    try:
        load(path_1, matter)
    except BenchKeyError as exc:
        if "Expecting" in str(exc):
            ok += 1

    # Cases 2 through 12
    for i, (data_gen, match_text) in enumerate(cases):
        case_num = i + 2
        path = tmp_path / f"key{case_num}.json"
        path.write_text(json.dumps(data_gen()), encoding="utf-8")

        try:
            load(path, matter)
        except BenchKeyError as exc:
            if match_text in str(exc):
                ok += 1
        # Any other exception fails the test

    collision_matter = matters.load(make(tmp_path / "collision", {
        "medical": [("The exam-\nination and examination were normal.", "MED0001")],
    }))
    collision = {"facts": [
        {"id": "F1", "cite": "MED0001", "quote": "exam-\nination", "text": "The report."},
        {"id": "F2", "cite": "MED0001", "quote": "examination", "text": "The report."},
    ], "flags": []}
    try:
        load(write(tmp_path / "collision", collision), collision_matter)
    except BenchKeyError as exc:
        if "fact F2: same cite and quote as fact F1" in str(exc):
            ok += 1

    with capsys.disabled():
        print(f"key_refusals={ok} of 13")
    assert ok == 13


def test_key_spellings_load_as_the_normalised_stamp(tmp_path):
    matter = matters.load(make(tmp_path, PAGES))
    data = copy.deepcopy(KEY)
    data["facts"][0]["cite"] = "MED-0001"
    data["flags"][0]["cites"] = ["MED 0001"]
    key = load(write(tmp_path, data), matter)
    assert key.facts[0].cite == "MED0001"
    assert key.flags[0].cites == ("MED0001",)


def test_whitespace_only_text_and_about_are_refused(tmp_path):
    matter = matters.load(make(tmp_path, PAGES))
    blank_text = copy.deepcopy(KEY)
    blank_text["facts"][0]["text"] = "   \n"
    blank_about = copy.deepcopy(KEY)
    blank_about["flags"][0]["about"] = "  "
    with pytest.raises(BenchKeyError, match="fact 1: expected keys id, cite, quote, text"):
        load(write(tmp_path, blank_text), matter)
    with pytest.raises(BenchKeyError, match="flag G1: about must be a nonempty string"):
        load(write(tmp_path, blank_about), matter)
