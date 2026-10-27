"""Stage 3 exit: the scanned fixture goes through the real command and every page is judged."""

import difflib
import json
import os
import shutil
import subprocess

import pytest

from casefile import quotes, stamps
from conftest import ROOT, write_config

FIXTURE = ROOT / "tests" / "fixtures" / "scanned"
RATIO_FLOOR = 0.95    # T-12; a constant of the test, printed with the measured minimum, never a parameter
PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"


def ratio(expected, got):
    return difflib.SequenceMatcher(None, quotes.normalize(expected), quotes.normalize(got)).ratio()


def ratio_ok(value):
    return value >= RATIO_FLOOR


def read_manifest(tmp_path):
    """The manifest as a temp copy, so a seeded edit never touches the committed file."""
    copy = tmp_path / "scanned.json"
    shutil.copyfile(FIXTURE / "scanned.json", copy)
    return json.loads(copy.read_text(encoding="utf-8"))


def judge(expected_page, record):
    """Per page verdicts: id, stamps, text (ratio floor plus status), must_contain."""
    n = expected_page["page"]
    want_stamps = {stamps.normalize(s) for s in expected_page["stamps"]}
    got_stamps = {s["stamp"] for s in record["stamps"]}
    value = ratio(expected_page["text"], record["text"])
    want_status = "empty" if expected_page["kind"] == "blank" else "ok"
    return {
        "id": record["id"] == f"scan/{n:03d}",
        "stamps": got_stamps == want_stamps and all(set(s) == {"raw", "stamp"} for s in record["stamps"]),
        "text": ratio_ok(value) and record["status"] == want_status,
        "must": all(quotes.found_in(span, record["text"]) for span in expected_page["must_contain"]),
        "ratio": value,
    }


@pytest.mark.ocr
def test_stage3_exit(tmp_path, capsys):
    manifest = read_manifest(tmp_path)
    path = write_config(tmp_path)
    (tmp_path / "matters" / "9002.001").mkdir()
    command = ["scripts/run.sh", "casefile", "intake", "--matter", "9002.001", "--binder", "scan",
               "tests/fixtures/scanned/scanned.pdf"]
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, CASEFILE_CONFIG=str(path)),
                            capture_output=True, text=True, timeout=180)
    pages = sorted((tmp_path / "matters" / "9002.001" / "pages" / "scan").glob("0*.json"))
    records = [json.loads(p.read_text(encoding="utf-8")) for p in pages]
    binder = json.loads((tmp_path / "matters" / "9002.001" / "pages" / "scan" / "binder.json")
                        .read_text(encoding="utf-8"))
    verdicts = [judge(page, record) for page, record in zip(manifest["pages"], records)]
    spans = [v["must"] for page, v in zip(manifest["pages"], verdicts) if page["must_contain"]]
    min_ratio = min(v["ratio"] for v in verdicts)
    with capsys.disabled():
        print(f"stage3 exit={result.returncode} pages={len(records)} "
              f"ids_ok={sum(v['id'] for v in verdicts)} of 6 "
              f"stamps_ok={sum(v['stamps'] for v in verdicts)} of 6 "
              f"text_ok={sum(v['text'] for v in verdicts)} of 6 "
              f"must_ok={sum(spans)} of {len(spans)} empty={binder['empty']} "
              f"failed={binder['failed']} min_ratio={min_ratio:.3f}")
    evidence = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 1, evidence       # the blank page is an open item, by design
    assert len(records) == 6 == len(manifest["pages"])
    assert all(v["id"] for v in verdicts), [r["id"] for r in records]
    assert all(v["stamps"] for v in verdicts), [r["stamps"] for r in records]
    assert all(v["text"] for v in verdicts), [round(v["ratio"], 3) for v in verdicts]
    assert all(spans) and len(spans) == 5
    assert binder["open_ids"] == ["scan/004"] and binder["failed"] == 0
    assert result.stdout.splitlines()[0] == (
        "intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4")


def test_ratio_boundary_is_inclusive():
    expected = "a" * 100
    at_floor = ratio(expected, "a" * 95 + "b" * 5)
    under = ratio(expected, "a" * 94 + "b" * 6)
    assert at_floor == 0.95 and under == 0.94
    assert ratio_ok(at_floor) is True
    assert ratio_ok(under) is False


def test_changed_digit_fails_must_contain_while_ratio_stays_high(tmp_path):
    manifest = read_manifest(tmp_path)
    page = manifest["pages"][0]
    record = {"id": "scan/001", "status": "ok", "text": page["text"].replace("10 pounds", "40 pounds"),
              "stamps": [{"raw": s, "stamp": s} for s in page["stamps"]]}
    verdict = judge(page, record)
    assert verdict["ratio"] >= RATIO_FLOOR and verdict["text"] is True
    assert verdict["must"] is False
    assert judge(page, dict(record, text=page["text"]))["must"] is True
