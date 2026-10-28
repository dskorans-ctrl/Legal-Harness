"""The committed scanned fixture: manifest, sha, stamps and the generator's own check."""

import hashlib
import importlib.util
import json

from pypdf import PdfReader

from casefile import stamps
from conftest import ROOT

FIXTURE = ROOT / "tests" / "fixtures" / "scanned"
PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"


def load_generator():
    spec = importlib.util.spec_from_file_location("make_scanned", FIXTURE / "make_scanned.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pdf_bytes(tmp_path):
    """The committed PDF as the test reads it (a temp copy, so a seed can flip a byte)."""
    copy = tmp_path / "scanned.pdf"
    copy.write_bytes((FIXTURE / "scanned.pdf").read_bytes())
    return copy.read_bytes()


def test_scanned_fixture_matches_manifest(tmp_path, capsys):
    data = pdf_bytes(tmp_path)
    manifest = json.loads((FIXTURE / "scanned.json").read_text(encoding="utf-8"))
    sha_ok = hashlib.sha256(data).hexdigest() == manifest["sha256"]
    reader = PdfReader(str(tmp_path / "scanned.pdf"))
    layer = [n for n, page in enumerate(reader.pages, 1) if (page.extract_text() or "").strip()]
    with capsys.disabled():
        print(f"scanned pages={len(reader.pages)} text_layer={layer} sha_ok={int(sha_ok)} "
              f"size_kb={len(data) // 1024}")
    assert sha_ok, "scanned.pdf differs from the sha256 pinned in scanned.json"
    assert (manifest["matter"], manifest["binder"]) == ("9002.001", "scan")
    assert len(reader.pages) == 6 == len(manifest["pages"])
    assert layer == [5, 6]
    assert len(data) < 3 * 1024 * 1024
    assert [p["kind"] for p in manifest["pages"]] == ["image", "image", "image", "blank", "text", "mixed"]
    assert [p["stamps"] for p in manifest["pages"]] == [
        ["KMR2342"], ["KMR2343"], ["KMR2344", "TWP7731"], [], ["KMR2345"], ["KMR2346"]]
    assert [p["page"] for p in manifest["pages"]] == [1, 2, 3, 4, 5, 6]


def test_manifest_is_what_the_generator_describes():
    generator = load_generator()
    manifest = json.loads((FIXTURE / "scanned.json").read_text(encoding="utf-8"))
    assert manifest == generator.manifest(manifest["sha256"])
    # The text each page promises holds exactly its stamps and every must_contain span.
    from casefile import quotes
    for page in manifest["pages"]:
        found = [s.stamp for s in stamps.find(page["text"], PATTERN)]
        assert found == page["stamps"], page["page"]
        for span in page["must_contain"]:
            assert quotes.found_in(span, page["text"]), (page["page"], span)


def test_generator_check_passes_and_names_a_changed_page(capsys, monkeypatch):
    generator = load_generator()
    assert generator.check() == 0
    assert "check bytes_equal=1 content_equal=1" in capsys.readouterr().out
    original = generator.PAGES
    changed = [dict(page) for page in original]
    changed[1] = dict(changed[1], lines=[l.replace("Strength", "Power") for l in changed[1]["lines"]])
    monkeypatch.setattr(generator, "PAGES", changed)
    assert generator.check() == 1
    out = capsys.readouterr().out
    assert "content_equal=0" in out and "check page 2 differs" in out
    changed = [dict(page) for page in original]
    changed[4] = dict(changed[4], lines=[
        line.replace("Frequency: two visits per week for four weeks.",
                     "Frequency: two visits per week for five weeks.")
        for line in changed[4]["lines"]])
    monkeypatch.setattr(generator, "PAGES", changed)
    assert generator.check() == 1
    out = capsys.readouterr().out
    assert "content_equal=0" in out and "check page 5 differs" in out
    assert "check page 2 differs" not in out
    with capsys.disabled():
        print(out.strip())
