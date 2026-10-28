"""Read the generated Word paragraphs and runs for the twenty-two memo checks."""

import copy
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
import pytest

from casefile import facts, matter, matterinfo, memo, rules


PAGES = (
    matter.Page("medical", 1, 'The IME records a normal gait. No prior injury.', ("MED0001",)),
    matter.Page("medical", 2, 'The IME records a normal gait.', ("MED0002",)),
    matter.Page("probe", 1, "Therapy continued.", ()),
)
QUOTE = 'The IME records a normal gait.'
READINGS = ["The report records a normal gait.", "The gait is recorded as normal."]
GAP_ABOUTS = ["The later record is missing.", "The next visit is not documented."]
OPEN = [memo.OpenItem("scan/003", memo.label(matter.Page("scan", 3, "", ("KMR2344", "TWP7731"))),
                      "empty", "no text after OCR"),
        memo.OpenItem("probe/002", "probe/002", "uncited", "no fact or flag cites probe/002")]


def case_file():
    stored = facts.CaseFile()
    stored.extend([
        facts.Event("fact", {"id": "F1", "cite": "MED0001", "page_id": "medical/001",
                              "quote": QUOTE, "text": READINGS[0], "run_id": 1}),
        facts.Event("cite", {"fact": "F1", "cite": "MED0002", "page_id": "medical/002", "run_id": 2}),
        facts.Event("reading", {"fact": "F1", "text": READINGS[1], "page_id": "medical/002", "run_id": 2}),
        facts.Event("fact", {"id": "F4", "cite": "probe/001", "page_id": "probe/001",
                              "quote": "Therapy continued.", "text": "Therapy is recorded.", "run_id": 1}),
        facts.Event("fact", {"id": "F5", "cite": "MED0001", "page_id": "medical/001",
                              "quote": "No prior injury.", "text": "The history denies prior injury.", "run_id": 2}),
        facts.Event("flag", {"id": "G6", "kind": "conflict", "cites": ["MED0001", "DEF0002"],
                              "page_ids": ["medical/001", "defense-report/002"],
                              "about": "The histories disagree.", "run_id": 1}),
        facts.Event("flag", {"id": "G7", "kind": "gap", "cites": ["MED0002"],
                              "page_ids": ["medical/002"], "about": GAP_ABOUTS[0], "run_id": 1}),
        facts.Event("about", {"flag": "G7", "about": GAP_ABOUTS[1], "run_id": 2}),
    ])
    # Two runs read pages; a third run contributes no read coverage rows.
    for run_id, read in [(1, ["medical/001", "probe/001"]), (2, ["medical/002"]), (3, [])]:
        stored.extend([facts.Event("run", {"run_id": run_id, "job": "memo", "card": "medical_memo",
                                           "card_version": "invented", "pages": read or ["probe/002"],
                                           "ok": bool(read), "read": read,
                                           "uncited": [], "failed": [] if read else ["probe/002"]})])
    return stored


def build(stored=None, pages=PAGES, opened=OPEN):
    return memo.build(stored if stored is not None else case_file(), pages, opened,
                      matter="9009.001", playbook_version="invented-playbook", model="invented-model")


def section(document, title):
    paragraphs = document.paragraphs
    start = next(index for index, paragraph in enumerate(paragraphs)
                 if paragraph.style.name == "Heading 1" and paragraph.text == title) + 1
    end = next((index for index in range(start, len(paragraphs))
                if paragraphs[index].style.name == "Heading 1"), len(paragraphs))
    return paragraphs[start:end]


def rendered(tmp_path, stored, pages=PAGES, opened=()):
    path = tmp_path / "memo.docx"
    memo.render(build(stored, pages, opened), path,
                rules=rules.load(Path(__file__).resolve().parents[1] / "playbook/rules.toml"))
    return Document(path)


@pytest.mark.parametrize("other", ["absent", "stale", "current"])
def test_m1_memo_lists_only_other_stale_outputs(tmp_path, other):
    stored = facts.CaseFile()

    def output(name):
        return facts.Event("output", dict(name=name, path=f"/invented/{name}.docx",
            built_from_seq=stored.last_seq, facts=0, conflicts=0, gaps=0, open=0))

    stored.extend([output("memo")])
    if other != "absent":
        stored.extend([output("report")])
    stored.extend([case_file().events[0]])
    if other == "current":
        stored.extend([output("report")])
    document = rendered(tmp_path, stored)
    expected = ["report" if other == "stale" else "none"]
    assert [p.text for p in section(document, "Outputs out of date")] == expected, "M1: stale outputs differ"


@pytest.mark.parametrize("state", ["read", "uncited", "failed", "empty"])
def test_m2_every_unquoted_page_has_an_explanation(tmp_path, state):
    page = matter.Page("medical", 2, "Invented page text." if state != "empty" else "", ("MED0002",))
    opened = [] if state == "read" else [memo.OpenItem(page.page_id, memo.label(page), state, "Invented reason.")]
    stored = facts.CaseFile()
    # A flag can read a page without placing a fact quote beneath its heading.
    stored.extend([facts.Event("flag", dict(id="G1", kind="gap", cites=["MED0002"],
        page_ids=[page.page_id], about="The next visit is missing.", run_id=1))])
    document = rendered(tmp_path, stored, (page,), opened)
    paragraphs = section(document, "Facts without a date, by page")
    expected = "No fact was quoted from this page." if state == "read" else f"Open item: {state} (see Open items)."
    assert [p.text for p in paragraphs[1:]] == [expected], "M2: unquoted page explanation differs"


@pytest.mark.parametrize("additions, expected", [
    ((0, 0, 0, 0, 0), "0 facts added, 0 cites added, 0 readings added, 0 flags added"),
    ((1, 0, 0, 0, 0), "1 fact added, 0 cites added, 1 reading added, 0 flags added"),
    ((0, 1, 1, 1, 1), "0 facts added, 1 cite added, 1 reading added, 1 flag added, 1 flag reading added"),
    ((2, 2, 0, 2, 2), "2 facts added, 2 cites added, 2 readings added, 2 flags added, 2 flag readings added"),
])
def test_l1_changed_counts_and_grammar(tmp_path, additions, expected):
    stored = case_file()
    stored.extend([facts.Event("output", dict(name="memo", path="/invented/memo.docx",
        built_from_seq=stored.last_seq, facts=3, conflicts=1, gaps=1, open=0))])
    for kind, count in zip(facts.CHANGE_KINDS, additions):
        template = next(event for event in case_file().events if event.kind == kind)
        for index in range(count):
            payload = dict(template.payload)
            if "id" in payload:
                payload["id"] = f"new-{kind}-{index}"
            stored.extend([facts.Event(kind, payload)])
    document = rendered(tmp_path, stored)
    assert [p.text for p in section(document, "What changed since the last memo")] == [expected], "L1: change counts differ"


@pytest.mark.parametrize("title, expected", [
    ("Open items", ["none"]),
    ("Conflicts", ["Pages read in 0 runs; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).", "ROLE NEEDED: no binder pair is marked defense and ours in matter.toml; conflicts are in the order found.", "none"]),
    ("Gaps and missing records", ["none"]),
    ("Outputs out of date", ["none"]),
])
def test_l2_empty_sections_say_none(tmp_path, title, expected):
    document = rendered(tmp_path, facts.CaseFile())
    assert [p.text for p in section(document, title)] == expected, f"L2: {title} lacks none"


@pytest.mark.parametrize("has_text", [True, False])
def test_l3_warning_names_only_unstamped_pages_with_text(tmp_path, has_text):
    pages = (matter.Page("probe", 1, "Invented text." if has_text else "", ()),
             matter.Page("probe", 2, " \n\t", ()),
             matter.Page("probe", 3, "More invented text." if has_text else "", ()),
             matter.Page("probe", 4, "Stamped text.", ("MED0004",)),
             matter.Page("probe", 5, "", ()))
    opened = [memo.OpenItem(page.page_id, memo.label(page), "empty", "no text after OCR")
              for page in pages if not page.text.strip()]
    document = rendered(tmp_path, facts.CaseFile(), pages, opened)
    paragraphs = section(document, "Facts without a date, by page")
    first_heading = next(index for index, p in enumerate(paragraphs) if p.style.name == "Heading 2")
    expected = ["These pages carry no Bates stamp and are cited by page id: probe/001, probe/003."] if has_text else []
    assert [p.text for p in paragraphs[:first_heading]] == expected, "L3: unstamped warning differs"


@pytest.mark.parametrize("part", ["built", "headings"])
def test_l4_sentence_and_heading_capitals(tmp_path, monkeypatch, part):
    class FixedDatetime:
        @staticmethod
        def now(tz):
            return datetime(2026, 10, 28, tzinfo=timezone.utc)

    monkeypatch.setattr(memo, "datetime", FixedDatetime)
    stored = case_file()
    pages = (*PAGES, matter.Page("defense-report", 2, "Invented text.", ("DEF0002",)))
    document = rendered(tmp_path, stored, pages)
    if part == "built":
        assert document.paragraphs[1].text == (
            f"Built 2026-10-28 from case file entry {stored.last_seq}; playbook invented-playbook; model invented-model"
        ), "L4: build line differs"
    else:
        assert [p.text for p in section(document, "Facts without a date, by page") if p.style.name == "Heading 2"] == [
            "Page MED0001 (medical/001), binder medical", "Page MED0002 (medical/002), binder medical",
            "Page probe/001, binder probe", "Page DEF0002 (defense-report/002), binder defense-report"
        ], "L4: page headings differ"


def test_memo(tmp_path):
    book_rules = rules.load(Path(__file__).resolve().parents[1] / "playbook" / "rules.toml")
    path = tmp_path / "outputs" / "memo.docx"
    built = build()
    memo.render(built, path, rules=book_rules)
    document = Document(path)
    paragraphs = document.paragraphs
    conflicts = section(document, "Conflicts")
    gaps = section(document, "Gaps and missing records")
    verified = section(document, "Facts without a date, by page")
    fact = next(paragraph for paragraph in verified if paragraph.text.startswith('"' + QUOTE))
    fact_index = next(index for index, paragraph in enumerate(verified) if paragraph.text == fact.text)
    heading_texts = [paragraph.text for paragraph in verified if paragraph.style.name == "Heading 2"]
    expected_quotes = {
        '"' + QUOTE + '" [cite MED0001]': "medical/001",
        '"No prior injury." [cite MED0001]': "medical/001",
        '"Therapy continued." [page probe/001]': "probe/001",
    }
    seen = {}
    current = None
    page_quotes = {}
    for paragraph in verified:
        if paragraph.style.name == "Heading 2":
            current = next((page.page_id for page in PAGES if paragraph.text == f'Page {memo.label(page)}, binder {page.binder}'), None)
            page_quotes[current] = []
        elif paragraph.text.startswith('"'):
            seen[paragraph.text] = current
            page_quotes.setdefault(current, []).append(paragraph.text)
    checks = [
        paragraphs[0].style.name == "Title" and paragraphs[0].text == "Medical memo: matter 9009.001",
        paragraphs[1].text.startswith("Built ") and
        f'from case file entry {case_file().last_seq}; playbook invented-playbook; model invented-model' in paragraphs[1].text,
        [p.text for p in section(document, "What changed since the last memo")] == ["First memo for this matter"],
        [p.text for p in section(document, "Outputs out of date")] == ["none"],
        [p.text for p in section(document, "Open items")] == [
            "KMR2344 TWP7731 (scan/003): empty: no text after OCR",
            "probe/002: uncited: no fact or flag cites probe/002"],
        [p.text for p in conflicts[2:]] == ["Conflict between [cite MED0001] and [cite DEF0002].",
                                             "Model's reading: The histories disagree.",
                                             "From [cite MED0001]:", f'"{QUOTE}"', '"No prior injury."',
                                             "From [cite DEF0002]:"],
        [p.text for p in gaps] == ["Gap at [cite MED0002].", *[f"Model's reading: {s}" for s in GAP_ABOUTS]],
        fact.text == f'"{QUOTE}" [cite MED0001]' and [run.text for run in fact.runs] == [f'"{QUOTE}"', " [cite MED0001]"],
        verified[fact_index + 1].text == "Also cited: [cite MED0002]",
        [p.text for p in verified[fact_index + 2:fact_index + 4]] == [
            f"Model's reading: {READINGS[0]}", f"Model's reading of [cite MED0002]: {READINGS[1]}"],
        heading_texts[0] == "Page MED0001 (medical/001), binder medical",
        verified[0].text == 'These pages carry no Bates stamp and are cited by page id: probe/001.' and
        '"Therapy continued." [page probe/001]' in [p.text for p in verified],
        heading_texts == ["Page MED0001 (medical/001), binder medical", "Page MED0002 (medical/002), binder medical",
                          "Page probe/001, binder probe"] and seen == expected_quotes and page_quotes.get("medical/002") == [],
        conflicts[0].text == "Pages read in 2 runs; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).",
    ]
    checks.extend(round6_checks(tmp_path))
    assert len(checks) == 22
    for number, ok in enumerate(checks, 1):
        assert ok, f'check {number} red'

    refused = 0
    for name in ("title",):
        bad = copy.deepcopy(built)
        if name == "title":
            bad.sections[0].title = "IME summary"
        else:
            bad = build(pages=(matter.Page("ime", 1, "Invented record.", ("MED0001",)),))
        output = tmp_path / "outputs" / f"{name}.docx"
        try:
            memo.render(bad, output, rules=book_rules)
        except memo.MemoError as exc:
            message = str(exc)
            required = (["IME summary"] if name == "title" else
                        ["binder ime", "no-dme-ime", "remove the binder by hand and intake it under another name (question 34)"])
            refused += int(all(part in message for part in required) and not output.exists())
    assert refused == 1, f'memo_refused={refused} of 1'

    stored = facts.CaseFile()
    stored.extend([facts.Event("output", {"name": "memo", "path": "/invented/outputs/memo.docx",
                                          "built_from_seq": 0, "facts": 0, "conflicts": 0, "gaps": 0, "open": 0}),
                   case_file().events[0]])
    changed_path = tmp_path / "changed.docx"
    memo.render(build(stored), changed_path, rules=book_rules)
    changed_doc = Document(changed_path)
    changed = int([p.text for p in section(changed_doc, "What changed since the last memo")] ==
                  ["1 fact added, 0 cites added, 1 reading added, 0 flags added"] and
                  [p.text for p in section(changed_doc, "Outputs out of date")] == ["none"])
    assert changed == 1, f'memo_changed={changed}'

    reason = next(rule.rule for rule in book_rules.rules if rule.id == "no-dme-ime")
    reason_path = tmp_path / "reason.docx"
    reason_ok = 0
    try:
        memo.render(build(opened=[memo.OpenItem("probe/002", "probe/002", "failed", reason)]),
                    reason_path, rules=book_rules)
        reason_paragraphs = section(Document(reason_path), "Open items")
        reason_ok = int(len(reason_paragraphs) == 1 and
                        [run.text for run in reason_paragraphs[0].runs] == ["probe/002", ": failed: ", reason])
    except memo.MemoError:
        pass
    assert reason_ok == 1, f'memo_reason_exempt={reason_ok}'
    print("memo_docx_ok=22 of 22 memo_refused=1 of 1 memo_changed=1 memo_reason_exempt=1")


@pytest.mark.parametrize("count, noun", [(0, "runs"), (1, "run"), (2, "runs")])
def test_conflicts_sentence_counts_read_runs(tmp_path, count, noun):
    stored = facts.CaseFile()
    stored.extend([event for event in case_file().events
                   if event.kind != "run" or event.payload["run_id"] <= count])
    # Repeated coverage from one run and reads by another job do not add memo runs.
    if count:
        stored.extend([facts.Event("run", {"run_id": 1, "job": "memo", "read": ["medical/001"]})])
    stored.extend([facts.Event("run", {"run_id": 99, "job": "bench", "read": ["medical/001"]}),
                   facts.Event("run", {"run_id": 100, "job": "memo", "read": []})])
    path = tmp_path / "memo.docx"
    memo.render(build(stored), path, rules=rules.load(Path(__file__).resolve().parents[1] / "playbook/rules.toml"))
    assert section(Document(path), "Conflicts")[0].text == (
        f"Pages read in {count} {noun}; conflicts and gaps are checked only between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).")


def round6_checks(tmp_path):
    """Eight independent round 6 controls, in addition to the retained fourteen."""
    from dataclasses import replace

    pages = (matter.Page('medical', 1, 'March 11, 2025. First finding.', ('MED0001',)),
             matter.Page('medical', 2, '03/14/2025. Later finding.', ('MED0002',)),
             matter.Page('medical', 3, '03/14/2025. Tied finding.', ('MED0003',)),
             matter.Page('defense-report', 1, 'Other finding.', ('DEF0001',)),
             matter.Page('other', 1, 'Unrelated finding.', ('OTH0001',)))
    stored = facts.CaseFile()
    for index, (page, day, category) in enumerate((
        (pages[1], '03/14/2025', 'diagnosis'), (pages[0], 'March 11, 2025', 'other'),
        (pages[2], '03/14/2025', 'work_status'), (pages[3], '', 'diagnosis'),
        (pages[4], '', 'other')), 1):
        stored.extend([facts.Event('fact', dict(id=f'F{index}', cite=page.stamps[0], page_id=page.page_id,
            quote=page.text, text='A finding is recorded.', date=day, category=category,
            provider='Invented Clinic' if index < 4 else '', run_id=1))])
    for index, pair in enumerate(((0, 1), (3, 4), (3, 0)), 1):
        selected = [pages[i] for i in pair]
        stored.extend([facts.Event('flag', dict(id=f'G{index}', kind='conflict',
            cites=[p.stamps[0] for p in selected], page_ids=[p.page_id for p in selected],
            about=f'The records disagree ({index}).', run_id=1))])
    info = matterinfo.MatterInfo(roles={'medical':'ours', 'defense-report':'defense', 'other':'other'})
    firm = rules.load(Path(__file__).resolve().parents[1] / 'playbook/rules.toml')

    def make(info=info):
        result = memo.build(stored, pages, [], matter='9009.001', playbook_version='invented', model='invented', info=info)
        path = tmp_path / 'round6.docx'
        memo.render(result, path, rules=firm)
        return result, Document(path)

    result, doc = make()
    chronology = [p.text for p in section(doc, 'Treatment chronology') if '"' in p.text]
    assert chronology == [
        f'March 11, 2025, Invented Clinic, other: "{pages[0].text}" [cite MED0001]',
        f'03/14/2025, Invented Clinic, diagnosis: "{pages[1].text}" [cite MED0002]',
        f'03/14/2025, Invented Clinic, work_status: "{pages[2].text}" [cite MED0003]',
    ], 'chronology: parsed date order or stable tie lost'
    conflicts = [p.text for p in section(doc, 'Conflicts')]
    start = conflicts.index('From [cite DEF0001]:',
        conflicts.index('Conflict between [cite DEF0001] and [cite MED0001].'))
    assert conflicts[start + 1:start + 3] == [f'"{pages[3].text}"', 'From [cite MED0001]:'], \
        'conflict_quotes: quote from outside the cited page'
    assert [p for p in conflicts if p.startswith('Conflict between ')] == [
        'Conflict between [cite DEF0001] and [cite MED0001].',
        'Conflict between [cite MED0001] and [cite MED0002].',
        'Conflict between [cite DEF0001] and [cite OTH0001].',
    ], 'defense_first: defense against other was promoted'
    ime = matter.Page('ime', 1, 'Normal gait.', ())
    ime_stored = facts.CaseFile()
    ime_stored.extend(facts.merge(ime_stored, {'facts':[dict(cite=ime.page_id, quote=ime.text, text=ime.text)], 'flags':[]}, (ime,), 1))
    ime_built = memo.build(ime_stored, (ime,), [], matter='9009.001', playbook_version='invented', model='invented', info=info)
    path = tmp_path / 'ime.docx'
    try:
        memo.render(ime_built, path, rules=firm)
    except memo.MemoError as exc:
        pytest.fail(f'binder_shown=0: {exc}')
    assert not [hit for hit in memo.check(ime_built, firm) if hit.severity == 'error'], 'binder_shown=0'
    heading = next(p for p in section(Document(path), 'Facts without a date, by page') if p.style.name == 'Heading 2')
    assert [run.text for run in heading.runs] == ['Page ', 'ime/001', ', binder ', 'ime'], 'binder_shown=0'
    assert any(run.text == 'ime' and run.exempt == 'binder' for sec in ime_built.sections for p in sec.paragraphs for run in p.runs)
    diagnoses = [p.text for p in section(doc, 'Diagnoses')]
    assert f'"{pages[0].text}" [cite MED0001]' not in diagnoses, 'diagnoses: other category included'
    assert f'"{pages[1].text}" [cite MED0002]' in diagnoses
    assert f'"{pages[1].text}" [cite MED0002]' in [p.text for p in section(doc, "Our doctors' opinions")]
    assert [p.text for p in section(doc, 'Providers')] == [
        'Invented Clinic: first March 11, 2025, last 03/14/2025, pages [cite MED0002] and [cite MED0001] and [cite MED0003]']
    _, no_roles = make(replace(info, roles={}, plaintiffs=2))
    assert any(p.text.startswith('ROLE NEEDED:') for p in section(no_roles, 'Conflicts')), 'roles: missing role guessed'
    assert any(p.text.startswith('ROLE NEEDED:') for p in section(no_roles, "Defense doctors' opinions")), 'roles: missing role guessed'
    upgraded_fact_check(tmp_path)
    placed = [p for title in ('Treatment chronology', 'Facts without a date, by page', 'Facts on pages not in this matter')
              for p in section(doc, title) if any(run.text.startswith('"') for run in p.runs)]
    assert len(placed) == len(stored.facts), 'placement: stored fact lost or repeated'
    return [True] * 8


def upgraded_fact_check(tmp_path):
    import json

    page = matter.Page('medical', 1, 'March 11, 2025. First finding.', ('MED0001',))
    pages = (page,)
    info = matterinfo.MatterInfo()
    firm = rules.load(Path(__file__).resolve().parents[1] / 'playbook/rules.toml')
    path = tmp_path / 'upgrade.docx'
    legacy = tmp_path / 'legacy.jsonl'
    old = facts.Event('fact', dict(id='OLD', cite='MED0001', page_id=pages[0].page_id,
        quote=pages[0].text, text='An older finding.', run_id=1))
    # Encode the old shape with a valid chain, then exercise the production upgrader.
    legacy.write_text(json.dumps(dict(seq=1, at='invented', prev='', kind=old.kind, payload=old.payload)) + '\n', encoding='utf-8')
    upgraded = facts.load(legacy)
    upgraded_memo = memo.build(upgraded, pages, [], matter='9009.001', playbook_version='invented', model='invented', info=info)
    memo.render(upgraded_memo, path, rules=firm)
    upgrade_doc = Document(path)
    assert upgraded.upgraded == 1
    assert [p.text for p in section(upgrade_doc, 'Treatment chronology')] == ['none'], 'upgrade: undated fact entered chronology'
    assert f'"{pages[0].text}" [cite MED0001]' in [p.text for p in section(upgrade_doc, 'Facts without a date, by page')], 'upgrade: undated fact lost'


def test_upgraded_fact_is_undated(tmp_path):
    upgraded_fact_check(tmp_path)
