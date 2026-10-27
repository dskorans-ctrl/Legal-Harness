"""Verifier 3 gaps N2 to N5 (round 2), each with the test the verifier would have written."""

import copy
import io

import pytest

from casefile import bench, benchkey, matter as matters
from casefile.benchcandidate import EMPTY, CandidateError, parse
from casefile.benchrun import RunResult
from conftest import ROOT, write_config
from test_benchkey import KEY, PAGES, write
from test_matter import GOOD, make

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
PASSED = []


def test_n2_candidate_flag_about_must_be_a_string():
    data = {"facts": [], "flags": [{"kind": "gap", "cites": ["MED0001"], "about": 7}]}
    with pytest.raises(CandidateError, match="flag 1: about must be a string"):
        parse(data)
    PASSED.append("n2")


def test_n3_unlisted_binder_folder_is_named(tmp_path):
    root = make(tmp_path, GOOD)
    (root / "records" / "xray").mkdir()
    with pytest.raises(matters.MatterError, match="unlisted binder folder xray"):
        matters.load(root)
    PASSED.append("n3")


def test_n4_key_fact_text_must_be_a_string(tmp_path):
    matter = matters.load(make(tmp_path, PAGES))
    data = copy.deepcopy(KEY)
    data["facts"][0]["text"] = 5
    with pytest.raises(benchkey.BenchKeyError, match="fact 1: expected keys id, cite, quote, text"):
        benchkey.load(write(tmp_path, data), matter)
    PASSED.append("n4")


def test_n5_received_truncation_prints_the_failure_line_and_exits_1(tmp_path):
    def runner(matter, config, log, playbook_version, opener):
        return RunResult(EMPTY, 14, "bench.truncation: done_reason=length", True)

    config = write_config(tmp_path, playbook=ROOT / "playbook", host="http://127.0.0.1:9")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(MATTER.parent, config, out=out, err=err, runner=runner)
    lines = out.getvalue().splitlines()
    assert lines[0] == "bench 9001.001 failure bench.truncation: done_reason=length"
    assert lines[1].endswith("pages_failed=14 of 14")
    assert err.getvalue() == ""
    assert code == 1
    PASSED.append("n5")


def test_verifier_gaps_summary(capsys):
    """Runs last in this file: prints how many of the four gap tests above reached their last line."""
    with capsys.disabled():
        print(f"verifier_gaps={len(PASSED)} of 4")
    assert PASSED == ["n2", "n3", "n4", "n5"]
