"""Found means the same cite and the same quote: a key quote cited to the wrong page is extra (D25, verifier seed V2-S2)."""

import json

from casefile import benchkey, matter as matters, rules as rules_mod
from casefile.benchcandidate import parse
from casefile.benchscore import score
from conftest import ROOT
from test_matter import make

RULES = rules_mod.load(ROOT / "playbook" / "rules.toml")
PAGES = {"medical": [("Pain 7/10 in the low back.", "MED0001"),
                     ("Pain 7/10 in the low back.\nDiagnosis: acute lumbar strain.", "MED0002")]}
KEY = {"facts": [{"date": "", "id": "F1", "cite": "MED0001", "quote": "Pain 7/10 in the low back.", "text": "Pain was 7/10."},
                 {"date": "", "id": "F2", "cite": "MED0002", "quote": "Diagnosis: acute lumbar strain.", "text": "A lumbar strain."}],
       "flags": [{"id": "G1", "kind": "conflict", "cites": ["MED0001", "MED0002"], "about": "The pages differ."}]}
WRONG_PAGE = {"facts": [{"cite": "MED0002", "quote": "Pain 7/10 in the low back.", "text": "Pain was 7/10."},
                        {"cite": "MED0002", "quote": "Diagnosis: acute lumbar strain.", "text": "A lumbar strain."}],
              "flags": [{"kind": "conflict", "cites": ["MED0001", "MED0002"], "about": "The pages differ."}]}


def test_same_quote_wrong_page_is_extra_and_missed(tmp_path):
    matter = matters.load(make(tmp_path, PAGES))
    path = tmp_path / "key.json"
    path.write_text(json.dumps(KEY), encoding="utf-8")
    key = benchkey.load(path, matter)
    s = score(key, parse(WRONG_PAGE), matter, RULES, 0)
    assert (s.found, s.missed, s.extra, s.invented) == (1, 1, 1, 0)
    assert s.missed_ids == ("F1",)
    assert not s.perfect
    assert s.line("9001.001", "candidate") == ("bench 9001.001 model=candidate found=1 of 2 missed=1 invented=0 extra=1 dates_wrong=0 flags=1 of 1 "
                                  "flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 2")


def test_candidate_cite_spellings_match_the_page(tmp_path, capsys):
    matter = matters.load(make(tmp_path, PAGES))
    path = tmp_path / "key.json"
    path.write_text(json.dumps(KEY), encoding="utf-8")
    key = benchkey.load(path, matter)
    answer = {"facts": [{"cite": "MED-0001", "quote": "Pain 7/10 in the low back.", "text": "Pain was 7/10."},
                        {"cite": "med 0002", "quote": "Diagnosis: acute lumbar strain.", "text": "A lumbar strain."}],
              "flags": [{"kind": "conflict", "cites": ["MED 0002", "MED-0001"], "about": "The pages differ."}]}
    s = score(key, parse(answer), matter, RULES, 0)
    with capsys.disabled():
        print(f"candidate_spellings found={s.found} flags_found={s.flags_found}")
    assert (s.found, s.missed, s.extra, s.invented, s.flags_found, s.flags_extra) == (2, 0, 0, 0, 1, 0)
