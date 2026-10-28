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


def case_token_end():
    # A match must end at a token boundary: a truncated prefix is never recorded (CX-7).
    refused = ("MED0001A and MED0001B", "MED0001a", "MED00012A", "KMR2344x", "MED 0001B")
    kept = {"MED 0001": ["MED0001"], "MED-0001, next": ["MED0001"], "see KMR2344.": ["KMR2344"],
            "end MED0001": ["MED0001"], "(TWP7731)": ["TWP7731"], "KMR2344\nTWP7731": ["KMR2344", "TWP7731"]}
    return (all(stamps(text) == [] for text in refused)
            and all(stamps(text) == want for text, want in kept.items()))


def case_joined_tokens():
    # A match never continues into a joined token at either end (H1): ids, suffixes, prefixes.
    refused = ("QRL-2025-0418", "MED0001-A", "MED0001.2", "MED0001/3", "xMED0001", "AB-MED0001",
               "MED0001A", "a.MED0001", "7/MED0001", "x-MED0001")
    kept = {"MED 0001": ["MED0001"], "MED-0001": ["MED0001"], "MED0001,": ["MED0001"],
            "Ends at MED0001.": ["MED0001"], "(MED0001)": ["MED0001"], "MED0001": ["MED0001"],
            "KMR23441": ["KMR23441"], "XKMR2344": ["XKMR2344"], "MED 0001 Page 3": ["MED0001"],
            "see MED0001. Next": ["MED0001"], "MED0001 - A": ["MED0001"]}
    mixed = stamps("Claim Number: QRL-2025-0418  MED0001-A  MED 0001") == ["MED0001"]
    return (all(stamps(text) == [] for text in refused)
            and all(stamps(text) == want for text, want in kept.items()) and mixed)


def case_normalize_punctuation():
    return normalize("MED.0001") == "MED0001" and normalize("med_0001") == "MED0001"


CASES = [case_main, case_whole_tokens, case_nothing, case_normalize, case_first_raw, case_token_end,
         case_joined_tokens, case_normalize_punctuation]


def test_stamps(capsys):
    passed = sum(1 for case in CASES if case())
    with capsys.disabled():
        print(f"stamps_cases={passed} of {len(CASES)}")
    assert passed == len(CASES), [c.__name__ for c in CASES if not c()]
