"""Build and reopen a memo from a private copy of the invented scanned intake."""

from io import StringIO
import json
import shutil

from docx import Document

from casefile import config, extract, facts, memo_job, pages, status
from conftest import ROOT, write_config
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for


def test_memo_intake(tmp_path, scanned_intake):
    intake_result, _, shared = scanned_intake
    assert intake_result.returncode == 1
    original = {str(path.relative_to(shared)): path.read_bytes()
                for path in shared.rglob("*") if path.is_file()}
    settings = config.load(write_config(tmp_path))
    shutil.copytree(ROOT / "playbook", settings.paths.playbook, dirs_exist_ok=True)
    folder = settings.paths.matters / "9002.001"
    shutil.copytree(shared, folder)
    loaded = pages.load(settings.paths.matters, "9002.001", settings.ocr.stamp_pattern)
    expected = json.loads((ROOT / "tests/fixtures/scanned/scanned.json").read_text(encoding="utf-8"))
    spans = {item["page"]: item["must_contain"][0] for item in expected["pages"] if item["must_contain"]}
    answer = {"facts": [{"cite": page.stamps[0], "quote": spans[page.number], "text": spans[page.number]}
                         for page in loaded.pages],
              "flags": [{"kind": "gap", "cites": ["KMR2345"],
                         "about": "The therapy completion record has not been provided."}]}
    transport = FakeTransport(FakeModel(recordings=[recording_for(extract.card(), loaded.pages, "9002.001", answer)]))
    out, err = StringIO(), StringIO()
    code = memo_job.run(settings, "9002.001", out=out, err=err, opener=transport)
    assert code == 1, f"memo_intake must exit=1: {err.getvalue()}"
    assert err.getvalue() == ""
    result = status.matter_status(settings, "9002.001")
    assert result["read"] == 5, "empty intake page reached the model: read=0"
    assert (result["open"], result["facts"], result["gaps"]) == (1, 5, 1)
    assert len(transport.requests) == 1
    request = json.loads(transport.requests[0][0].data)
    assert "scan/004" not in request["messages"][1]["content"]
    assert out.getvalue().splitlines() == [
        "memo 9002.001 chunks=1 runs=+1 read=5 open=1 facts=5 conflicts=0 gaps=1 "
        f"new_facts=5 new_flags=1 memo={folder / 'outputs/memo.docx'}",
        "  open: scan/004: empty: no text after OCR"]
    document = Document(folder / "outputs/memo.docx")
    texts = [paragraph.text for paragraph in document.paragraphs]
    label_ok = int("Scan page KMR2344 TWP7731 (scan/003)" in texts)
    assert label_ok == 1
    quotes = [paragraph for paragraph in document.paragraphs if paragraph.text.startswith('"')]
    assert len(quotes) == 5
    for paragraph, page in zip(quotes, loaded.pages):
        assert paragraph.text == f'"{spans[page.number]}" [cite {page.stamps[0]}]'
        assert [run.text for run in paragraph.runs] == [f'"{spans[page.number]}"', f' [cite {page.stamps[0]}]']
    assert len(facts.load(folder / "casefile.jsonl").facts) == 5
    assert not (folder / "outputs/memo.docx.tmp").exists()
    assert {str(path.relative_to(shared)): path.read_bytes()
            for path in shared.rglob("*") if path.is_file()} == original
    assert {path.name for path in shared.iterdir()} == {"records", "pages"}
    print(f"memo_intake 9002.001 chunks=1 read=5 open=1 facts=5 gaps=1 label_ok={label_ok} exit={code}", flush=True)
    print(f"scanned_intake {shared}: records pages", flush=True)
