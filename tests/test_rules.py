"""Invented outputs exercise each firm rule independently."""

from pathlib import Path

import pytest

from casefile.rules import RulesError, load


RULES_PATH = Path(__file__).resolve().parents[1] / "playbook" / "rules.toml"


CITE_FORMS = (
    ("See page 12.", True),
    ("see p. 12", True),
    ("at page 12 of the report", True),
    ("(Ex. 3 at 12)", True),
    ("a 12 page report", False),
    ("Page 2 of 3", False),
    ("the next page", False),
    ("page count 14", False),
    ("see page MED0012", False),
    ("see page MED 0012", False),
    ("He looked at page after page.", False),
)


def test_cite_forms():
    rules = load(RULES_PATH)
    assert len(CITE_FORMS) == 11
    results = []
    for text, fails in CITE_FORMS:
        findings = rules.check(text, unit="text", stamped=True)
        excerpt = "at page 12" if text == "at page 12 of the report" else text.rstrip(".")
        expected = [("bates-cites", "error", excerpt)] if fails else []
        results.append([(f.rule_id, f.severity, f.excerpt) for f in findings] == expected)
    print(f"cite_forms={sum(results)} of 11", flush=True)
    assert all(results), [text for (text, _), ok in zip(CITE_FORMS, results) if not ok]


def test_each_rule_goes_red(capsys):
    rules = load(RULES_PATH)
    cases = [
        ("no-dme-ime", "the ime report", "text"),
        ("no-dme-ime", "an Independent Medical Examination", "text"),
        ("no-dme-ime", "two defense medical examinations", "text"),
        ("no-hired-paid-retained", "Who retained the doctor?", "text"),
        ("no-hired-paid-retained", "The employer hired Dr. Example. [cite ABC0001]", "text"),
        ("treatment-and-bills-apart", "Describe your treatment and the bills you received", "question"),
        ("bates-cites", "[cite p. 12] gait normal", "text"),
        ("bates-cites", "[cite garbage ABC0001tail]", "text"),
        ("bates-cites", "[cite ABC0001 and ABC0002]", "text"),
    ]
    results = [{f.rule_id for f in rules.check(text, unit=unit)} == {rule_id}
               for rule_id, text, unit in cases]
    with capsys.disabled():
        print(f"rules_red={sum(results)} of 9", flush=True)
    assert all(results), results


def test_bates_accepts_fullmatch():
    rules = load(RULES_PATH)
    for text in ("[cite ABC0001] gait normal", "[cite AB-00012]", "[cite ABCDEFGH 123456]"):
        assert rules.check(text, unit="text") == []


def test_bates_warning_when_unstamped():
    findings = load(RULES_PATH).check("[cite p. 12]", stamped=False, unit="text")
    assert len(findings) == 1
    assert findings[0].rule_id == "bates-cites"
    assert findings[0].severity == "warning"


def test_good_examples_clean(capsys):
    rules = load(RULES_PATH)
    results = [rules.check(rule.good, unit=rule.unit) == [] for rule in rules.rules]
    with capsys.disabled():
        print(f"good_clean={sum(results)} of 4", flush=True)
    assert all(results)


def test_boundary():
    rules = load(RULES_PATH)
    for text in ("time", "Dimension", "the report of 14 March", "an examination"):
        assert rules.check(text, unit="text") == []
    for text in ("DME", "IME", "independent medical examination", "defense medical examination"):
        assert {f.rule_id for f in rules.check(text, unit="text")} == {"no-dme-ime"}


def test_pattern_without_boundary_refused(tmp_path):
    assert len(load(RULES_PATH).rules) == 4
    bad = tmp_path / "rules.toml"
    text = RULES_PATH.read_text()
    bad.write_text(text.replace("'\\bDME\\b'", "'IME'", 1))
    with pytest.raises(RulesError, match="rule no-dme-ime pattern 1: has no word boundary"):
        load(bad)


def test_source_patterns_units_and_spans(tmp_path):
    rules = load(RULES_PATH)
    for text in ("Who pays the examiner?", "You were paid for the doctor", "referred by the defense",
                 "What fees for the exam?", "How many of these exams?", "reports per month", "The employer hires the physician"):
        assert {f.rule_id for f in rules.check(text, unit="text")} == {"no-hired-paid-retained"}
    assert rules.check("Treatment and bills", unit="text") == []
    for text in ("What therapy?", "What bills?"):
        assert rules.check(text, unit="question") == []
    found = rules.check("A dMe report", unit="text")
    assert [(f.start, f.end, f.excerpt) for f in found] == [(2, 5, "dMe")]
    assert rules.check("[cite abc0001]", unit="text")[0].severity == "error"
    path = tmp_path / "rules.toml"
    path.write_text(RULES_PATH.read_text().replace("[A-Z]{1,8}[ -]?\\d{4,}", "X[0-9]{2}"))
    changed = load(path)
    assert changed.check("[cite X12]", unit="text") == []
    assert changed.check("[cite ABC0001]", unit="text")[0].rule_id == "bates-cites"


@pytest.mark.parametrize(("old", "new", "field"), [
    ("version = 1", "version = 2", "version"),
    ('severity = "error"', 'severity = "fatal"', "severity"),
    ('unit = "text"', 'unit = "paragraph"', "unit"),
    ('kind = "forbid"', 'kind = "other"', "kind"),
    ('added = 2026-10-25', 'added = "2026-10-25"', "added"),
    ('why = "The labels', 'unknown = "The labels', "why"),
    ("'\\bDME\\b'", "'\\b('" , "pattern 1"),
    ('id = "bates-cites"', 'id = "no-dme-ime"', "id"),
    ('unit = "text"', 'unit = "text"\nunknown = true', "unknown"),
])
def test_invalid_rules_fail_closed(tmp_path, old, new, field):
    path = tmp_path / "rules.toml"
    path.write_text(RULES_PATH.read_text().replace(old, new, 1))
    with pytest.raises(RulesError, match=field):
        load(path)


@pytest.mark.parametrize("text", [
    "The insurer paid Dr. Example.",
    "Dr. Example was paid by the insurer.",
    "The defense paid the examiner for the report.",
    "Who paid for the exam?",
    "Payment from the carrier went directly to the doctor.",
    "The examiner received payment from the employer.",
    "The insurer pays the consulting doctor.",
    "DR. EXAMPLE WAS COMPENSATED BY THE CARRIER.",
])
def test_doctor_payment_any_order(text):
    assert {f.rule_id for f in load(RULES_PATH).check(text, unit="text")} == {"no-hired-paid-retained"}


@pytest.mark.parametrize("label", ["independent", "defense"])
@pytest.mark.parametrize("space", ["\n", "  ", "\t", "\r\n"])
def test_spelled_out_label_across_whitespace(label, space):
    text = f"The {label}{space}medical{space}examination found normal motion."
    assert {f.rule_id for f in load(RULES_PATH).check(text, unit="text")} == {"no-dme-ime"}


@pytest.mark.parametrize("text", [
    "The carrier paid temporary total disability through March; Dr. Lane released him to light duty in April.",
    "Benefits were paid until the report issued.",
])
def test_benefit_payment_prose_clean(text):
    assert load(RULES_PATH).check(text, unit="text") == []


@pytest.mark.parametrize("text", [
    "independent-medical-examination",
    "defense-medical-exam",
    "defense medical-examination",
    "INDEPENDENT- MEDICAL--EXAMINATIONS",
])
def test_hyphenated_exam_labels_refused(text):
    assert {f.rule_id for f in load(RULES_PATH).check(text, unit="text")} == {"no-dme-ime"}


def test_round6_rule5_forms():
    from pathlib import Path
    from casefile.rules import load
    firm = load(Path(__file__).resolve().parents[1] / 'playbook/rules.toml')
    bad = ('What is your fee for this deposition?', 'Is there a fee for your testimony today?',
           'How often does the carrier retain you?', 'How many times has the carrier retained you this year?')
    good = ('When were you hired by Quarry Ridge Logistics LLC?',
            'You were hired by Quarry Ridge Logistics in August 2021, correct?',
            'Who hired you at the warehouse?', 'Quarry Ridge hired you as a forklift operator, correct?',
            'You have been engaged in warehouse work since 2021, correct?',
            'How many times did your supervisor refer you to the clinic?',
            'How much time did you spend face to face with the claimant?',
            'Do you currently treat patients with low back injuries?',
            'What share of your practice is treating patients?',
            'How often do you see patients with disc protrusions?',
            'Were you paid for the day you missed work?', 'Did the employer hire a replacement while you were out?',
            'You retained a copy of the incident report, correct?', 'How often did you attend physical therapy?')
    hits = [bool(firm.check(text,unit='question')) == want for text,want in
            [*((v,True) for v in bad), *((v,False) for v in good)]]
    print(f'rule5_forms={sum(hits)} of 18')
    assert all(hits), f'rule5_forms={sum(hits)} of 18; failed={[t for t,ok in zip((*bad,*good),hits) if not ok]}'


def test_round6_bills_forms():
    from pathlib import Path
    from casefile.rules import load
    firm = load(Path(__file__).resolve().parents[1] / 'playbook/rules.toml')
    providers = ('Ridgeline Physical Therapy','Lakeshore Orthopedic Associates')
    bills = ('And separately, Doctor, as to the bills themselves, the charges from {providers}, do you have an '
             'opinion whether those bills are reasonable and causally related to that same work incident?')
    every = ('Fennimore County Hospital','Brightwater Family Medicine','Ridgeline Physical Therapy',
             'Lakeshore Imaging','Lakeshore Orthopedic Associates')
    cases = [(bills.format(providers=', '.join(providers)),providers,False),
             (bills.format(providers=', '.join(every)),every,False),
             ('What treatment did you receive at Ridgeline Physical Therapy?',providers,False),
             ('What treatment did you receive and what bills followed?',(),True),
             ('Doctor, what were you paid for the examination?',(),True),
             ('Doctor, you were provided a bill memo listing charges from Ridgeline Physical Therapy. '
              'Do you have an opinion, within a reasonable degree of medical probability, whether all of the '
              'treatment reflected in those records was reasonable, necessary, and causally related to the '
              '03/11/2025 work incident?',providers,True),
             ('Doctor, what did you charge for the report?',(),True)]
    hits = [bool(firm.check(t,unit='question',providers=p,bills_question=True)) == want for t,p,want in cases]
    print(f'bills_forms={sum(hits)} of 7')
    assert all(hits), f'bills_forms={sum(hits)} of 7'
    assert {f.rule_id for f in firm.check('What bills followed at IME Clinic?',unit='question',providers=('IME Clinic',))} == {'no-dme-ime'}, 'provider mask hid IME'
    assert firm.check('The doctor billed the carrier for the report.',unit='text'), 'text pairing lost'
    assert not firm.check('What bills followed at RIDGELINE\nPHYSICAL THERAPY?',unit='question',providers=providers)
