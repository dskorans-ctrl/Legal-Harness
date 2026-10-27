"""Stamp finding: the Q21 pattern, both directions, first raw per normalised form."""

from casefile.stamps import find, normalize

PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"


def stamps(text):
    return [s.stamp for s in find(text, PATTERN)]


def case_main():
    text = ("Stamps KMR2344 and TWP7731; not 9KMR2344, kmr2344 or KMR234; "
            "also MED 0001, MED-0001 and MED0001")
    found = find(text, PATTERN)
    return [s.stamp for s in found] == ["KMR2344", "TWP7731", "MED0001"] and found[2].raw == "MED 0001"


def case_whole_tokens():
    # Complete valid stamps under the pattern, so they are recorded whole.
    return stamps("XKMR2344 and KMR23441") == ["XKMR2344", "KMR23441"]


def case_nothing():
    return stamps("9KMR2344, kmr2344, KMR234 and 12345") == [] and stamps("") == []


def case_normalize():
    return normalize("med-0001") == "MED0001" and normalize("a b-c") == "ABC"


def case_first_raw():
    found = find("MED 0001 then MED0001", PATTERN)
    return [(s.raw, s.stamp) for s in found] == [("MED 0001", "MED0001")]


CASES = [case_main, case_whole_tokens, case_nothing, case_normalize, case_first_raw]


def test_stamps(capsys):
    passed = sum(1 for case in CASES if case())
    with capsys.disabled():
        print(f"stamps_cases={passed} of {len(CASES)}")
    assert passed == len(CASES), [c.__name__ for c in CASES if not c()]
