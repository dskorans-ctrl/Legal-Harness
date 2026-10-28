"""casefile bench over two matters: an imperfect first matter still fails the run (D25, verifier seed V2-S6)."""

import io
import shutil

from casefile import bench
from casefile.benchcandidate import parse_text
from casefile.benchrun import RunResult
from conftest import ROOT, write_config

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
IDEAL = MATTER / "ideal.json"
FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
PERFECT = ("bench 9001.001 model=qwen3.8:27b found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")
FLAWED_LINE = ("bench 9001.001 model=qwen3.8:27b found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 "
               "flags_extra=1 rules=1 pages_failed=0 of 14")


def test_first_imperfect_second_perfect_exits_1(tmp_path):
    matters_dir = tmp_path / "two"
    shutil.copytree(MATTER, matters_dir / "a")
    shutil.copytree(MATTER, matters_dir / "b")
    # Two roots must carry two numbers; the key and pages of b are unchanged (see the next test).
    toml = (matters_dir / "b" / "matter.toml")
    toml.write_text(toml.read_text(encoding="utf-8").replace("9001.001", "9001.002"), encoding="utf-8")
    answers = [parse_text(FLAWED.read_text(encoding="utf-8")), parse_text(IDEAL.read_text(encoding="utf-8"))]
    seen = []

    def runner(matter, config, log, playbook_version, opener):
        seen.append(matter.root.name)
        return RunResult(answers.pop(0), 0, None, True)

    config = write_config(tmp_path / "cfg", playbook=ROOT / "playbook", host="http://127.0.0.1:9")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(matters_dir, config, out=out, err=err, runner=runner)
    lines = out.getvalue().splitlines()
    assert err.getvalue() == ""
    assert seen == ["a", "b"]
    assert lines[0] == FLAWED_LINE
    assert PERFECT.replace("9001.001", "9001.002") in lines
    assert lines[-1] == "bench matters=2 imperfect=1"
    assert code == 1


def test_equal_matter_numbers_in_two_roots_exit_2(tmp_path, capsys):
    matters_dir = tmp_path / "two"
    shutil.copytree(MATTER, matters_dir / "a")
    shutil.copytree(MATTER, matters_dir / "b")
    seen = []

    def runner(matter, config, log, playbook_version, opener):
        seen.append(matter.root.name)
        return RunResult(parse_text(IDEAL.read_text(encoding="utf-8")), 0, None, True)

    config = write_config(tmp_path / "cfg", playbook=ROOT / "playbook", host="http://127.0.0.1:9")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(matters_dir, config, out=out, err=err, runner=runner)
    with capsys.disabled():
        print(f"duplicate_numbers_exit={code}")
    assert err.getvalue() == (f"bench: duplicate matter number 9001.001 in {matters_dir / 'a'} "
                              f"and {matters_dir / 'b'}\n")
    assert seen == []
    assert not (tmp_path / "cfg" / "state" / "runlog.sqlite").exists()
    assert out.getvalue() == ""
    assert "bench matters=" not in out.getvalue()
    assert code == 2


def test_bad_second_key_refused_before_first_run(tmp_path):
    matters_dir = tmp_path / "two"
    shutil.copytree(MATTER, matters_dir / "a")
    shutil.copytree(MATTER, matters_dir / "b")
    toml = matters_dir / "b" / "matter.toml"
    toml.write_text(toml.read_text(encoding="utf-8").replace("9001.001", "9001.002"), encoding="utf-8")
    (matters_dir / "b" / "key.json").write_text("{}", encoding="utf-8")
    seen = []

    def runner(matter, config, log, playbook_version, opener):
        seen.append(matter.root.name)
        return RunResult(parse_text(IDEAL.read_text(encoding="utf-8")), 0, None, True)

    config = write_config(tmp_path / "cfg", playbook=ROOT / "playbook")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(matters_dir, config, out=out, err=err, runner=runner)
    assert code == 2
    assert err.getvalue() == (f"BenchKeyError: {matters_dir / 'b' / 'key.json'}: "
                              "expected object with keys facts and flags\n")
    assert seen == []
    assert not (tmp_path / "cfg" / "state" / "runlog.sqlite").exists()
    assert out.getvalue() == ""
