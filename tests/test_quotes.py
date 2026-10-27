"""Quote matching for the stage 2 bench: exact after normalisation."""

from casefile.quotes import found_in, normalize

CASES = [
    # (quote, page_text, expected)
    ("Pain 7/10 in the low back.", "Vitals stable.\nPain 7/10 in the low back.\nPlan: rest.", True),
    ("Pain 7/10   in the\nlow back.", "Pain 7/10 in the low back.", True),
    ('He said "no prior injury".', "He said \u201cno prior injury\u201d.", True),
    ("Today's exam was normal.", "Today\u2019s exam was normal.", True),
    ("DIAGNOSIS: ACUTE LUMBAR STRAIN.", "Diagnosis: acute lumbar strain.", True),
    ("Pain 8/10 in the low back.", "Pain 7/10 in the low back.", False),
    ("", "Pain 7/10 in the low back.", False),
    ("Pain 7/10 in the low back. More text here.", "Pain 7/10", False)
]


def test_found_in(capsys):
    passed = sum(1 for quote, page, expected in CASES if found_in(quote, page) is expected)
    with capsys.disabled():
        print(f"quotes_ok={passed} of 8")
    for quote, page, expected in CASES:
        assert found_in(quote, page) is expected, (quote, page)


def test_normalize():
    assert normalize("  A\u201cB\u201d  c ") == 'a"b" c'
