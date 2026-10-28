"""Legacy quote normalisation and the stage 4 quote ladder."""

from casefile.quotes import fold, found_in, match, normalize, same

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


LADDER = [
    ("exact", "Pain 7/10.", "Vitals stable.\nPain 7/10.\nPlan: rest.", "exact"),
    ("whitespace", "Pain 7/10   in the\nlow back.", "Pain 7/10 in the low back.", "whitespace"),
    ("curly", 'He said "no prior injury".', 'He said “no prior injury”.', "curly"),
    ("casefold", "DIAGNOSIS: STRAIN.", "Diagnosis: strain.", "curly"),
    ("ligature", "finding", "ﬁnding", "curly"),
    ("hyphen", "examination", "exam-\nination", "ocr"),
    ("stamp line", "Pain 7/10.\nNo weakness.", "Pain 7/10.\nMED0001\nNo weakness.", "ocr"),
    ("page line", "Pain 7/10.\nNo weakness.", "Pain 7/10.\nPage 2 of 5\nNo weakness.", "ocr"),
    ("changed digit", "Pain 8/10.", "Pain 7/10.", None),
    ("dropped no", "There was weakness.", "There was no weakness.", None),
    ("dropped word", "Acute strain.", "Acute lumbar strain.", None),
    ("skipped ordinary line", "Pain 7/10.\nNo weakness.",
     "Pain 7/10.\nHarrowgate Clinic\nNo weakness.", None),
    ("skipped bare page line", "Pain 7/10.\nNo weakness.",
     "Pain 7/10.\nPage 2\nNo weakness.", None),
    ("empty", "", "Pain 7/10.", None),
]


def test_ladder(capsys):
    results = [match(quote, page) for _, quote, page, _ in LADDER]
    rungs = [result.rung if result else None for result in results]
    passed = sum(rung == case[3] for rung, case in zip(rungs, LADDER))
    with capsys.disabled():
        print(f"ladder_ok={passed} of {len(LADDER)}", flush=True)
    assert passed == len(LADDER), f"ladder_ok={passed} of {len(LADDER)}"
    for (name, quote, _, expected), result in zip(LADDER, results):
        assert (result.rung if result else None) == expected, name
        if result:
            expected_text = {"exact": quote, "whitespace": " ".join(quote.split()),
                             "curly": normalize(quote), "ocr": fold(quote)}[expected]
            assert result.text == expected_text, name


def test_same_and_legacy_boundary():
    assert same("Today’s exam", "today's   exam") is True
    assert same("exam-\nination", "examination") is True
    assert same("7/10", "8/10") is False
    assert same("Pain.\nMED0001\nRest.", "Pain. Rest.") is False
    assert fold("exam-\r\n  ination") == "examination"
    assert found_in("finding", "ﬁnding") is True
    assert found_in("examination", "exam-\nination") is False
    assert found_in("Pain. Rest.", "Pain.\nMED0001\nRest.") is False


def test_ocr_drops_only_whole_allowed_lines():
    for line in ("MED0001A", "MED0001-A", "MED0001.2", "AB-MED0001", "xMED0001",
                 "MED0001.", "(MED0001)", "MED0001 MED0002", "See MED0001", "CONFIDENTIAL",
                 "2026-10-27", "Page 2 of 5 extra"):
        assert match("Pain. Rest.", f"Pain.\n{line}\nRest.") is None, line
    for line in ("MED0001", " MED 0001 ", "MED-0001", " pAgE 2 of 5 "):
        result = match("Pain. Rest.", f"Pain.\n{line}\nRest.")
        assert result is not None and result.rung == "ocr", line
    assert match("Pain. MED0001 Rest.", "Pain.\nMED0002\nRest.") is None
    assert match(" \n\t", "Pain.") is None
