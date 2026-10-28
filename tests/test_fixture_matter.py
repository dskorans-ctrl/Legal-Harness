from casefile import benchkey, matter as matters, rules
from conftest import ROOT

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
STAMPS = ([f"MED{n:04d}" for n in range(1, 9)] + [f"EMP{n:04d}" for n in range(1, 4)]
          + [f"DEF{n:04d}" for n in range(1, 4)])

def test_fixture_loads(capsys):
    matter = matters.load(MATTER)

    binder_set = {p.binder for p in matter.pages}

    with capsys.disabled():
        print(f"fixture_pages={len(matter.pages)} binders={len(binder_set)}")

    assert len(matter.pages) == 14
    assert len(binder_set) == 3
    assert [p.stamps for p in matter.pages] == [(s,) for s in STAMPS]

def test_key_loads(capsys):
    matter = matters.load(MATTER)
    key = benchkey.load(MATTER / "key.json", matter)
    book = rules.load(ROOT / "playbook" / "rules.toml")

    prose = [f.text for f in key.facts] + [f.about for f in key.flags]

    findings = [finding for text in prose for finding in book.check(text, unit="text", stamped=True)]

    with capsys.disabled():
        print(f"key_facts={len(key.facts)} flags={len(key.flags)} pages={len(matter.pages)}")

    expected_fact_ids = [f"F{n:02d}" for n in range(1, 37)]
    expected_flag_ids = [f"G{n}" for n in range(1, 10)]

    assert (len(key.facts), len(key.flags), len(matter.pages)) == (36, 9, 14)
    assert [f.id for f in key.facts] == expected_fact_ids
    assert [f.id for f in key.flags] == expected_flag_ids
    assert findings == []


G9_ABOUT = ("The defense report says the L4-L5 disc changes are degenerative, while the MRI reports a 4 mm "
            "posterior central disc protrusion at L4-L5 and places the mild degenerative disc disease at L5-S1.")


def test_g9_about_matches_the_pages_in_key_ideal_and_flawed():
    # The MRI (MED0006) puts the mild degenerative disease at L5-S1; the old text implied none (M1).
    import json
    book = rules.load(ROOT / "playbook" / "rules.toml")
    for path in (MATTER / "key.json", MATTER / "ideal.json", ROOT / "tests" / "fixtures" / "bench" / "flawed.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        flags = [f for f in data.get("flags", []) if set(f["cites"]) == {"MED0006", "DEF0002"}]
        assert [f["about"] for f in flags] == [G9_ABOUT], path.name
        assert book.check(G9_ABOUT, unit="text", stamped=True) == []
