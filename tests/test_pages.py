"""Page layouts and refusals use invented records under temporary matter roots."""

import json
import shutil

import pytest

from casefile import matter, pages
from conftest import ROOT


FIXTURE = ROOT / "tests/fixtures/matters/9001.001"
CASES = ("bench", "intake", "neither", "both", "matter", "status", "count",
         "binder_link", "matter_link", "number")


def intake_layout(root):
    folder = root / "9002.001" / "pages"
    for binder, records in (("scan", (1, 3)), ("clinic", (1,))):
        target = folder / binder
        target.mkdir(parents=True)
        (target / "binder.json").write_text(json.dumps({"pages": len(records)}), encoding="utf-8")
        for number in records:
            empty = binder == "scan" and number == 3
            record = dict(matter="9002.001", binder=binder, page=number,
                          id=f"{binder}/{number:03d}", text="" if empty else "Seen by Dr. Rafael Soto-Lindgren.",
                          stamps=([{"raw": "KMR 2344", "stamp": "KMR2344"},
                                   {"raw": "TWP7731", "stamp": "TWP7731"}]
                                  if binder == "clinic" else []),
                          status="empty" if empty else "ok", reason="no text after OCR" if empty else "")
            (target / f"{number:03d}.json").write_text(json.dumps(record), encoding="utf-8")
    return folder.parent


@pytest.fixture(scope="module")
def totals():
    passed = []
    yield passed
    print(f"pages_ok={len(passed)} of 10", flush=True)


@pytest.mark.parametrize("case", CASES)
def test_pages(case, tmp_path, totals):
    root = tmp_path / "matters"
    root.mkdir()
    folder = intake_layout(root)
    record = folder / "pages/scan/001.json"
    if case == "bench":
        shutil.copytree(FIXTURE, root / "9001.001")
        loaded = pages.load(root, "9001.001", matter.STAMP_PATTERN)
        assert loaded.pages == matter.load(FIXTURE).pages
        assert len(loaded.pages) == 14 and loaded.open_pages == ()
    elif case == "intake":
        loaded = pages.load(root, "9002.001", matter.STAMP_PATTERN)
        assert [p.page_id for p in loaded.pages] == ["clinic/001", "scan/001"]
        assert loaded.pages[0].stamps == ("KMR2344", "TWP7731")
        assert loaded.open_pages == (("scan/003", (), "empty", "no text after OCR"),)
        for name in ("casefile.jsonl", "outputs"):
            target = folder / name
            target.symlink_to(tmp_path / "missing")
            with pytest.raises(pages.PagesError, match=name):
                pages.load(root, "9002.001", matter.STAMP_PATTERN)
            target.unlink()
    else:
        named = str(folder)
        number = "9002.001"
        if case == "neither":
            shutil.rmtree(folder / "pages")
            named = f"no pages for matter {number} under {root}: run casefile intake first"
        elif case == "both":
            (folder / "matter.toml").write_text("", encoding="utf-8")
        elif case in {"matter", "status"}:
            obj = json.loads(record.read_text(encoding="utf-8"))
            obj[case] = "9002.002" if case == "matter" else "done"
            if case == "status":
                obj["reason"] = "invented invalid status"
            record.write_text(json.dumps(obj), encoding="utf-8")
            named = str(record)
        elif case == "count":
            meta = folder / "pages/scan/binder.json"
            meta.write_text('{"pages":4}', encoding="utf-8")
            named = str(meta)
        elif case == "binder_link":
            old = folder / "pages/scan"
            old.rename(tmp_path / "scan")
            old.symlink_to(tmp_path / "scan", target_is_directory=True)
            named = str(old)
        elif case == "matter_link":
            destination = root / "9002.002"
            folder.rename(destination)
            folder.symlink_to(destination, target_is_directory=True)
            named = str(folder)
        elif case == "number":
            number = "wrong"
            named = str(root / number)
        with pytest.raises(pages.PagesError) as error:
            pages.load(root, number, matter.STAMP_PATTERN)
        assert named in str(error.value)
    totals.append(case)
