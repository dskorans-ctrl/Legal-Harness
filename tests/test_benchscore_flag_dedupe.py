"""The same extra flag sent twice counts once (D25, verifier seed V2-S5)."""

from test_benchscore import run


def add_extra_flag_twice(data):
    for _ in range(2):
        data["flags"].append({"kind": "gap", "cites": ["MED0002"], "about": "A report is missing."})


def test_same_extra_flag_twice_counts_once(tmp_path):
    s = run(tmp_path, add_extra_flag_twice)
    assert s.flags_extra == 1
    assert s.flags_extra_items == (("gap", ("MED0002",)),)
    assert s.flags_found == 1 and s.flags_missed == 0
    assert s.details() == ["  flags_extra: gap MED0002"]
    assert not s.perfect
