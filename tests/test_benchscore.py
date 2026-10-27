"""The bench scorer: one probe per counter, then the two shipped fixtures."""

import copy
import json
from pathlib import Path

from casefile import benchkey, matter as matters, rules as rules_mod
from casefile.benchcandidate import parse, parse_text
from casefile.benchscore import score
from conftest import ROOT
from test_matter import make

RULES = rules_mod.load(ROOT / "playbook" / "rules.toml")
MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")
FLAWED = ("bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 "
          "flags_extra=1 rules=1 pages_failed=0 of 14")

PAGES = {"medical": [("Pain 7/10 in the low back.\nOther real line.", "MED0001"),
                     ("Diagnosis: acute lumbar strain.", "MED0002")]}
KEY = {"facts": [{"id": "F1", "cite": "MED0001", "quote": "Pain 7/10 in the low back.", "text": "Pain was 7/10."},
                 {"id": "F2", "cite": "MED0002", "quote": "Diagnosis: acute lumbar strain.", "text": "A lumbar strain."}],
       "flags": [{"id": "G1", "kind": "conflict", "cites": ["MED0001", "MED0002"], "about": "The pages differ."}]}
GOOD = {"facts": [{"cite": f["cite"], "quote": f["quote"], "text": f["text"]} for f in KEY["facts"]],
        "flags": [{"kind": "conflict", "cites": ["MED0002", "MED0001"], "about": "The pages differ."}]}


def small(tmp_path):
    matter = matters.load(make(tmp_path, PAGES))
    path = tmp_path / "key.json"
    path.write_text(json.dumps(KEY), encoding="utf-8")
    return matter, benchkey.load(path, matter)


def run(tmp_path, change=None, pages_failed=0):
    """Score GOOD after change(data) edits a deep copy of it."""
    data = copy.deepcopy(GOOD)
    if change is not None:
        change(data)
    matter, key = small(tmp_path)
    return score(key, parse(data), matter, RULES, pages_failed)


# --- Change functions for test_score_cases ---

def drop_second_fact(data):
    del data["facts"][1]

def quote_not_on_page(data):
    data["facts"][1]["quote"] = "Diagnosis: chronic lumbar strain."

def cite_not_a_page(data):
    data["facts"][1]["cite"] = "MED0099"

def add_real_fact(data):
    data["facts"].append({"cite": "MED0001", "quote": "Other real line.", "text": "Another line."})

def duplicate_fact(data):
    data["facts"].append(copy.deepcopy(data["facts"][0]))

def swap_flag_kind(data):
    data["flags"][0]["kind"] = "gap"

def fact_rule_word(data):
    data["facts"][0]["text"] = "The IME found nothing."

def flag_rule_word(data):
    data["flags"][0]["about"] = "The IME found nothing."

def add_extra_flag(data):
    data["flags"].append({"kind": "gap", "cites": ["MED0002"], "about": "A report is missing."})


# --- Test Cases Definition ---

# (change_function, pages_failed, check_function)
CASES = [
    # 1. perfect
    (None, 0, lambda s: s.perfect and s.found == 2 and s.extra == 0 and s.line("9001.001", "candidate").startswith("bench 9001.001 model=candidate found=2 of 2 ")),
    # 2. one key fact dropped
    (drop_second_fact, 0, lambda s: s.missed == 1 and s.missed_ids == ("F2",) and not s.perfect),
    # 3. quote not on the page
    (quote_not_on_page, 0, lambda s: s.invented == 1 and s.missed_ids == ("F2",)),
    # 4. cite not a page
    (cite_not_a_page, 0, lambda s: s.invented == 1 and s.missed == 1),
    # 5. a real fact not in the key
    (add_real_fact, 0, lambda s: s.extra == 1 and s.invented == 0 and s.perfect),
    # 6. duplicate candidate fact
    (duplicate_fact, 0, lambda s: s.found == 2 and s.extra == 0 and s.invented == 0 and s.perfect),
    # 7. flag kind swapped
    (swap_flag_kind, 0, lambda s: s.flags_missed == 1 and s.flags_extra == 1 and not s.perfect),
    # 8. fact text with a firm-rule word
    (fact_rule_word, 0, lambda s: s.rules == 1 and not s.perfect),
    # 9. flag about with a firm-rule word
    (flag_rule_word, 0, lambda s: s.rules == 1 and s.flags_found == 1),
    # 10. pages failed
    (None, 2, lambda s: s.pages_failed == 2 and not s.perfect),
    # 11. an added flag not in the key
    (add_extra_flag, 0, lambda s: s.flags_extra == 1 and s.flags_found == 1 and not s.perfect)
]


def test_score_cases(tmp_path, capsys):
    results = []
    for i, (change, failed, check) in enumerate(CASES):
        (tmp_path / f"c{i}").mkdir()
        s = run(tmp_path / f"c{i}", change, failed)
        results.append(s)

    ok = sum(1 for i, (change, failed, check) in enumerate(CASES) if check(results[i]))
    with capsys.disabled():
        print(f"score_cases={ok} of 11")
    assert ok == 11


def test_shipped_fixtures(capsys):
    matter = matters.load(MATTER)
    key = benchkey.load(MATTER / "key.json", matter)
    ideal = score(key, parse_text((MATTER / "ideal.json").read_text(encoding="utf-8")), matter, RULES, 0)
    flawed = score(key, parse_text((ROOT / "tests" / "fixtures" / "bench" / "flawed.json").read_text(encoding="utf-8")),
                   matter, RULES, 0)
    with capsys.disabled():
        print(ideal.line("9001.001", "candidate"))
        print(flawed.line("9001.001", "candidate"))
    assert ideal.line("9001.001", "candidate") == PERFECT
    assert ideal.perfect
    assert flawed.line("9001.001", "candidate") == FLAWED
    assert not flawed.perfect
