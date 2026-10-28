"""casefile bench detail lines: which facts, flags and rules failed (critic M1, D25)."""

import io
import json

from casefile import bench
from test_matter import make
from conftest import ROOT, write_config

MATTERS = ROOT / "tests" / "fixtures" / "matters"
IDEAL = MATTERS / "9001.001" / "ideal.json"
FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")
FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 "
               "flags_extra=1 rules=1 pages_failed=0 of 14")
FLAWED_DETAIL = [
    "  missed: F04 F15 F24",
    '  invented: MED0003 "Patient was lifting 80 pounds." (quote not on the page)',
    '  invented: MED0099 "Date of service: 03/11/2025" (no such page)',
    "  flags_missed: G3",
    "  flags_extra: conflict MED0001,MED0004",
    '  rules: no-dme-ime DEF0003 "IME"',
]
LONG_QUOTE = "Patient was given a lumbar brace and told to rest for two full weeks at home."
PROBE_LINE = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=1 extra=2 flags=9 of 9 flags_missed=0 "
              "flags_extra=0 rules=1 pages_failed=0 of 14")
PROBE_DETAIL = [
    '  invented: MED0002 "Patient was given a lumbar brace and told to rest for two fu" (quote not on the page)',
    '  rules: no-dme-ime flag MED0002 "IME"',
]


def run(tmp_path, candidate):
    config = write_config(tmp_path, playbook=ROOT / "playbook", host="http://127.0.0.1:9")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(MATTERS, config, candidate, out=out, err=err)
    return code, out.getvalue().splitlines(), err.getvalue()


def test_flawed_detail_lines(tmp_path, capsys):
    code, lines, err = run(tmp_path, FLAWED)
    with capsys.disabled():
        print("\n".join(lines))
        print(f"bench_detail_flawed exit={code} detail_lines={len(lines) - 2}")
    assert code == 1, err
    assert lines == [FLAWED_LINE, *FLAWED_DETAIL, "bench matters=1 imperfect=1"]


def test_perfect_has_no_detail(tmp_path, capsys):
    code, lines, err = run(tmp_path, IDEAL)
    with capsys.disabled():
        print(f"bench_detail_perfect exit={code} detail_lines={len(lines) - 2}")
    assert code == 0, err
    assert lines == [PERFECT, "bench matters=1 imperfect=0"]


def test_long_quote_and_flag_rule(tmp_path, capsys):
    data = json.loads(IDEAL.read_text(encoding="utf-8"))
    data["facts"].append({"cite": "MED0002", "quote": LONG_QUOTE, "text": "A brace was given."})
    for flag in data["flags"]:
        if flag["cites"] == ["MED0002"]:
            flag["about"] = "The IME x-ray report is not in the records."
    probe = tmp_path / "probe.json"
    probe.write_text(json.dumps(data), encoding="utf-8")
    code, lines, err = run(tmp_path / "cfg", probe)
    with capsys.disabled():
        print(f"bench_detail_probe exit={code} detail_lines={len(lines) - 2}")
    assert code == 1, err
    assert lines == [PROBE_LINE, *PROBE_DETAIL, "bench matters=1 imperfect=1"]


def test_hyphen_rung_detail(tmp_path):
    root = make(tmp_path / "matters", {
        "medical": [("The exam-\nination was normal.", "MED0001")],
    })
    key = {"facts": [{"id": "F1", "cite": "MED0001", "quote": "The exam-\nination was normal.",
                      "text": "The report was normal."}], "flags": []}
    (root / "key.json").write_text(json.dumps(key), encoding="utf-8")
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps({"facts": [{"cite": "MED0001", "quote": "The examination was normal.",
                                               "text": "The report was normal."}], "flags": []}), encoding="utf-8")
    config = write_config(tmp_path / "cfg", playbook=ROOT / "playbook")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(root.parent, config, candidate, out=out, err=err)
    assert code == 0, err.getvalue()
    assert out.getvalue().splitlines() == [
        "bench 9001.001 model=candidate found=1 of 1 missed=0 invented=0 extra=0 flags=0 of 0 "
        "flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 1",
        "  rungs: exact=0 whitespace=0 curly=0 ocr=1",
        "bench matters=1 imperfect=0",
    ]
