"""Chair-ruled cycle 1 regressions on invented pages and in-process model replies."""

import fcntl
import hashlib
import json
from pathlib import Path

from docx import Document
import pytest

from casefile import facts, gates, matter, memo, pages as page_store, playbook, status
from casefile.runlog import open_db
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recordings_for
from test_status import FIXTURE, invoke, setup_matter


PAGES = (matter.Page("medical", 1, "Gait: Normal.", ("MED0001",)),
         matter.Page("medical", 7, "Reflexes: Normal.", ("MED0007",)))


def answer(cite="MED0001", text="Gait is normal."):
    return dict(facts=[dict(cite=cite, quote="Normal.", text=text)], flags=[])


def build(stored, pages=PAGES):
    return memo.build(stored, pages, [], matter="9009.001", playbook_version="invented", model="invented")


def render(tmp_path, stored, pages=PAGES):
    path = tmp_path / "outputs/memo.docx"
    memo.render(build(stored, pages), path,
                rules=playbook.load(Path(__file__).resolve().parents[1] / "playbook").rules)
    return Document(path).paragraphs


def merged(*answers):
    stored = facts.CaseFile()
    for run_id, item in enumerate(answers, 1):
        stored.extend(facts.merge(stored, item, PAGES, run_id))
    return stored


def test_h1_page_id_cite_renders_stamped_memo(tmp_path):
    rules = playbook.load(Path(__file__).resolve().parents[1] / "playbook").rules
    item = answer("medical/001")
    detail, cited = gates._references(item, PAGES, rules)
    assert "fault" not in detail and cited == {"medical/001"}
    stored = merged(item, answer("medical/007"))
    try:
        paragraphs = render(tmp_path, stored)
    except memo.MemoError as exc:
        pytest.fail(f"H1: page-id cite on a stamped page prevents memo: {exc}")
    assert stored.facts[0].cites == ["MED0001", "MED0007"], "H1: fact or added cite kept page id"
    assert '"Normal." [cite MED0001]' in [p.text for p in paragraphs]
    assert "Also cited: [cite MED0007]" in [p.text for p in paragraphs]


def test_h2_append_failure_resends_pages(tmp_path, monkeypatch):
    _, settings, folder = setup_matter(tmp_path)
    transport = FakeTransport(FakeModel(recordings=recordings_for(FIXTURE)))
    append = facts.append

    def fail(path, events):
        raise facts.CaseFileError("invented append failure")

    with monkeypatch.context() as patch:
        patch.setattr(facts, "append", fail)
        code, _, error = invoke(settings, transport)
    assert code == 2 and "invented append failure" in error
    assert len(transport.requests) == 1, "H2: failure was not after the passing chunk"
    with open_db(settings.paths.state / "runlog.sqlite") as log:
        assert sum(row[0] == "read" for row in log.coverage("9001.001", job="memo").values()) == 13
    assert not facts.load(folder / "casefile.jsonl").runs
    assert facts.append is append
    code, line, error = invoke(settings, transport)
    assert len(transport.requests) == 2, "H2: pages with uncommitted facts were not re-sent"
    assert code == 1 and error == "" and "facts=37" in line
    assert len(facts.load(folder / "casefile.jsonl").facts) == 37


def test_h2_status_joins_latest_coverage_to_casefile_runs(tmp_path):
    _, settings, folder = setup_matter(tmp_path)
    transport = FakeTransport(FakeModel(recordings=recordings_for(FIXTURE)))
    assert invoke(settings, transport)[0] == 1
    path = folder / "casefile.jsonl"
    # Remove the complete run and output tail, leaving the verified facts intact.
    lines = path.read_bytes().splitlines(keepends=True)
    path.write_bytes(b"".join(lines[:-2]))
    snapshot = status.matter_status(settings, "9001.001")
    assert snapshot["read"] == 0 and snapshot["open"] == 14, "H2: status trusts coverage without a case-file run"
    assert invoke(settings, transport)[0] == 1
    assert len(transport.requests) == 2, "H2: deleted complete run tail did not re-send pages"
    assert len(facts.load(path).facts) == 37


def test_h2_probe_refuses_before_model(tmp_path, monkeypatch):
    _, settings, folder = setup_matter(tmp_path)
    transport = FakeTransport(FakeModel(recordings=recordings_for(FIXTURE)))
    original = Path.open

    def fail_open(path, mode="r", *args, **kwargs):
        if path == folder / "casefile.jsonl" and mode == "ab":
            raise OSError("invented append open failure")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_open)
    code, line, error = invoke(settings, transport)
    assert code == 2 and line == "" and "invented append open failure" in error
    assert not transport.requests, "H2: append probe happened after the model call"
    assert not (settings.paths.state / "runlog.sqlite").exists(), "H2: append probe happened after run-log writes"


@pytest.mark.parametrize("present", [True, False], ids=["later-page-present", "all-pages-absent"])
def test_m1_absent_first_page_keeps_every_fact(tmp_path, present):
    stored = merged(answer(), answer("MED0007"))
    pages = (PAGES[1],) if present else ()
    paragraphs = render(tmp_path, stored, pages)
    quotes = [p for p in paragraphs if p.text.startswith('"Normal."')]
    loaded = page_store.PageSet("9009.001", pages, ())
    count = status.snapshot(loaded, stored, {})["facts"]
    assert len(quotes) == count == 1, "M1: memo silently dropped a fact with an absent first page"
    expected = '"Normal." [cite MED0007]' if present else '"Normal." [cite MED0001]'
    assert quotes[0].text == expected
    heading = next(p.text for p in reversed(paragraphs[:paragraphs.index(quotes[0])])
                   if p.style.name.startswith("Heading"))
    assert heading == ("Page MED0007 (medical/007), binder medical" if present else "Facts on pages not in this matter")
    if present:
        assert "Also cited: [cite MED0001]" in [p.text for p in paragraphs]


def test_m2_duplicate_fact_id_refused(tmp_path):
    path = tmp_path / "casefile.jsonl"
    first = facts.merge(facts.CaseFile(), answer(), PAGES, 1)
    second = facts.merge(facts.CaseFile(), answer("MED0007", "Reflexes are normal."), PAGES, 2)
    # Distinct quotes make the overwritten view observable.
    second[0].payload["quote"] = "Reflexes: Normal."
    facts.append(path, first)
    before = path.read_bytes()
    try:
        facts.append(path, second)
    except facts.CaseFileError:
        pass
    else:
        pytest.fail("M2: repeated fact id accepted")
    assert path.read_bytes() == before
    # A complete, correctly chained duplicate on disk must also refuse on load.
    raw = json.loads(before)
    raw.update(seq=2, prev=hashlib.sha256(before.rstrip(b"\n")).hexdigest())
    raw["payload"] = second[0].payload
    path.write_bytes(before + json.dumps(raw).encode() + b"\n")
    with pytest.raises(facts.CaseFileError, match="case file chain broken at line 2"):
        facts.load(path)


def test_m2_duplicate_flag_id_refused(tmp_path):
    path = tmp_path / "casefile.jsonl"
    event = facts.Event("flag", dict(id="G1", kind="gap", cites=["MED0001"],
        page_ids=["medical/001"], about="A later record is missing.", run_id=1))
    facts.append(path, [event])
    before = path.read_bytes()
    try:
        facts.append(path, [event])
    except facts.CaseFileError:
        pass
    else:
        pytest.fail("M2: repeated flag id accepted")
    assert path.read_bytes() == before


def test_m2_memo_holds_exclusive_lock_for_every_writer(tmp_path, monkeypatch):
    _, settings, folder = setup_matter(tmp_path)
    transport = FakeTransport(FakeModel(recordings=recordings_for(FIXTURE)))
    from casefile import memo_job

    checked = []

    def locked(name, function):
        def call(*args, **kwargs):
            with (folder / "casefile.jsonl.lock").open("a") as competitor:
                try:
                    fcntl.flock(competitor, fcntl.LOCK_SH | fcntl.LOCK_NB)
                except BlockingIOError:
                    checked.append(name)
                else:
                    pytest.fail(f"M2: {name} ran outside the exclusive matter lock")
            return function(*args, **kwargs)
        return call

    monkeypatch.setattr(facts, "load", locked("load", facts.load))
    monkeypatch.setattr(facts, "merge", locked("merge", facts.merge))
    monkeypatch.setattr(facts, "append", locked("append", facts.append))
    monkeypatch.setattr(memo_job, "ModelClient", locked("model", memo_job.ModelClient))
    monkeypatch.setattr(memo, "render", locked("render", memo.render))
    assert invoke(settings, transport)[0] == 1
    assert checked == ["load", "model", "merge", "append", "render", "append"]
    with (folder / "casefile.jsonl.lock").open("a") as competitor:
        fcntl.flock(competitor, fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_m3_reading_retains_its_page(tmp_path):
    stored = merged(answer(), answer("MED0007", "Reflexes are normal."))
    reading = next(e for e in stored.events if e.kind == "reading")
    assert reading.payload.get("page_id") == "medical/007", "M3: reading has no source page"
    paragraphs = render(tmp_path, stored)
    assert "Model's reading of [cite MED0007]: Reflexes are normal." in [p.text for p in paragraphs], \
        "M3: reading from another page is attributed to the heading"
    assert "Model's reading: Gait is normal." in [p.text for p in paragraphs]
    assert "Model's reading: Reflexes are normal." not in [p.text for p in paragraphs]


def test_m3_same_reading_on_another_page_is_retained(tmp_path):
    stored = merged(answer(), answer("MED0007"))
    readings = [e for e in stored.events if e.kind == "reading"]
    assert len(readings) == 1, "M3: identical wording on another page lost its source"
    assert readings[0].payload.get("page_id") == "medical/007"
    assert "Model's reading of [cite MED0007]: Gait is normal." in [p.text for p in render(tmp_path, stored)]
    assert facts.merge(stored, answer("MED0007"), PAGES, 3) == []


def test_l1_conflict_requires_distinct_pages():
    item = answer()
    item["flags"] = [dict(kind="conflict", cites=["MED0001", "MED 0001"], about="The reports disagree.")]
    rules = playbook.load(Path(__file__).resolve().parents[1] / "playbook").rules
    detail, _ = gates._references(item, PAGES, rules)
    assert detail == "1 fault (faults=1): flags[0]: a conflict must cite two different pages", \
        "L1: gate accepted a one-page conflict"
    item["flags"][0]["cites"].append("MED0007")
    assert "fault" not in gates._references(item, PAGES, rules)[0]


def test_l1_flag_cites_deduplicated_by_page():
    item = answer()
    item["flags"] = [dict(kind="gap", cites=["MED0001", "medical/001", "MED0007"], about="Missing later record.")]
    flag = merged(item).flags[0]
    assert flag.cites == ["MED0001", "MED0007"] and flag.page_ids == ["medical/001", "medical/007"], \
        "L1: flag cites and page ids lost their pairing"


def test_l2_empty_pages_refused(tmp_path):
    _, settings, folder = setup_matter(tmp_path)
    (folder / "matter.toml").unlink()
    (folder / "pages").mkdir()
    transport = FakeTransport(FakeModel(recordings=[]))
    code, line, error = invoke(settings, transport)
    assert code == 2, "L2: empty pages folder produced a successful memo"
    assert line == "" and error == "memo: cannot run: no pages to read in 9001.001\n"
    assert not transport.requests and not (folder / "outputs").exists()
    assert not (settings.paths.state / "runlog.sqlite").exists()


def test_l5_refusal_is_one_line_per_finding(tmp_path):
    built = build(merged(answer()))
    built.sections[-1].paragraphs.append(memo.Paragraph([
        memo.Run('"IME"', exempt="quote"), memo.Run(" [page medical/001]")]))
    built.sections[12].paragraphs.append(memo.Paragraph([memo.Run("IME summary")]))
    rules = playbook.load(Path(__file__).resolve().parents[1] / "playbook").rules
    with pytest.raises(memo.MemoError) as caught:
        memo.render(built, tmp_path / "outputs/memo.docx", rules=rules)
    assert str(caught.value).splitlines() == [
        "no-dme-ime: IME (in Conflicts)",
        "bates-cites: [page medical/001] (in Facts on pages not in this matter)",
    ], "L5: refusal repeats text or loses its section"


def test_ch1_wrong_seq_on_last_line_refused(tmp_path):
    path = tmp_path / "casefile.jsonl"
    facts.append(path, facts.merge(facts.CaseFile(), answer(), PAGES, 1))
    raw = json.loads(path.read_bytes())
    raw["seq"] = 8
    path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    try:
        facts.load(path)
    except facts.CaseFileError as exc:
        assert str(exc) == "case file chain broken at line 1; the file was edited or truncated"
    else:
        pytest.fail("CH-1: wrong seq on last line accepted")
