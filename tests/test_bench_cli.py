import json
import shutil
import os
from pathlib import Path
import pytest

# Assuming ROOT and write_config are available via conftest
from conftest import ROOT, write_config

# Constants defined in background
MATTERS = ROOT / "tests" / "fixtures" / "matters"
MATTER = MATTERS / "9001.001"
FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
PERFECT = ("bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")
FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 "
               "flags_extra=1 rules=1 pages_failed=0 of 14")

# Mock bench function based on background description
def bench(config, *args):
    env = dict(os.environ, CASEFILE_CONFIG=str(config))
    # In a real test environment, this would call the actual CLI runner.
    # We rely on the provided implementation structure for testing purposes.
    import subprocess
    return subprocess.run(["casefile", "bench", *args], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=60)


def test_bench_exits(tmp_path, capsys):
    # 1. Setup configuration
    config = write_config(tmp_path / "a", playbook=ROOT / "playbook", host="http://127.0.0.1:9")

    # 2. Perfect run
    r1 = bench(config, "--matters", str(MATTERS), "--candidate", str(MATTER / "ideal.json"))
    lines1 = r1.stdout.splitlines()

    # 3. Flawed run
    r2 = bench(config, "--matters", str(MATTERS), "--candidate", str(FLAWED))
    lines2 = r2.stdout.splitlines()

    # 4. Bad key run
    bad_matter_dir = tmp_path / "bad" / "9001.001"
    shutil.copytree(MATTER, bad_matter_dir)
    
    key_path = bad_matter_dir / "key.json"
    
    # Load, modify, and write back the key file
    with open(key_path, 'r') as f:
        data = json.load(f)
    
    # Modify the first fact's quote
    if data and 'facts' in data and data['facts']:
        data['facts'][0]['quote'] = "Pain 9/10 in the low back, no radiation."
        
    with open(key_path, 'w') as f:
        json.dump(data, f)

    r3 = bench(config, "--matters", str(tmp_path / "bad"), "--candidate", str(MATTER / "ideal.json"))

    # 5. No config run
    r4 = bench(config, "--matters", str(MATTERS), "--candidate", str(MATTER / "ideal.json"), "--config", str(tmp_path / "missing.toml"))

    # 6. No run log run
    blocker_file = tmp_path / "blocker"
    blocker_file.write_text("a file, not a folder", encoding="utf-8")
    
    # Note: state must point to a directory, but we pass the blocker file path 
    # which is not a directory, simulating an invalid state setup for the run log check.
    # We rely on write_config handling this or the subsequent bench call failing.
    config5 = write_config(tmp_path / "e", playbook=ROOT / "playbook", host="http://127.0.0.1:9", state=str(blocker_file / "state"))
    
    r5 = bench(config5, "--matters", str(MATTERS))

    # 7. Print results
    summary = (f"bench_exit_perfect={r1.returncode} bench_exit_flawed={r2.returncode} "
               f"bench_exit_badkey={r3.returncode} bench_exit_noconfig={r4.returncode} "
               f"bench_exit_nolog={r5.returncode}")
    
    with capsys.disabled():
        print(summary)

    # 8. Assertions
    
    # r1 assertions (Perfect)
    assert r1.returncode == 0
    assert lines1[0] == PERFECT
    assert lines1[-1] == "bench matters=1 imperfect=0"

    # r2 assertions (Flawed)
    assert r2.returncode == 1
    assert lines2[0] == FLAWED_LINE
    assert lines2[-1] == "bench matters=1 imperfect=1"

    # r3 assertions (Bad Key)
    assert r3.returncode == 2
    assert r3.stdout == ""
    assert r3.stderr.startswith("BenchKeyError:")

    # r4 assertions (No Config)
    assert r4.returncode == 2
    assert r4.stderr.startswith("ConfigError: no config file")

    # r5 assertions (No Run Log)
    assert r5.returncode == 2
    assert r5.stdout == ""
    assert r5.stderr.startswith("bench: cannot open run log")

    # Final check: no run log was created by the candidate runs
    # We check the state directory created in step 1 (tmp_path / "a")
    runlog_path = tmp_path / "a" / "state" / "runlog.sqlite"
    assert not runlog_path.exists()


def run_runner_mode(tmp_path, opener=None, host="http://127.0.0.1:9"):
    """casefile bench in runner mode, in process, with the stand-in's recordings or no server at all."""
    import io
    from casefile import bench
    config = write_config(tmp_path, playbook=ROOT / "playbook", host=host)
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(MATTERS, config, out=out, err=err, opener=opener)
    return code, out.getvalue().splitlines(), err.getvalue()


def test_bench_no_reply_exit2(tmp_path, capsys):
    """No server at the host: nothing was received, so the run cannot be scored (Q26, D25): exit 2."""
    code, lines, err = run_runner_mode(tmp_path)
    with capsys.disabled():
        print(f"no_reply_exit={code}")
    assert code == 2
    assert lines and lines[0].startswith("bench 9001.001 failure bench.model: ")
    assert "bench matters=" not in "\n".join(lines)
    assert err.startswith("bench: cannot run: no reply from the model server at http://127.0.0.1:9: ")
    assert err.count("\n") == 1


def test_bench_received_404_stays_exit1(tmp_path, capsys):
    """A 404 for an unknown model tag is a received reply: scored found=0, exit 1 (D25)."""
    from fakemodel.bench import recordings_for
    from fakemodel.core import FakeModel, FakeTransport
    opener = FakeTransport(FakeModel(recordings=recordings_for(MATTER), model="other:model"))
    code, lines, err = run_runner_mode(tmp_path, opener)
    with capsys.disabled():
        print(f"received_404_exit={code}")
    assert code == 1
    assert err == ""
    assert lines[0].startswith("bench 9001.001 failure bench.model: status=404")
    assert lines[1].startswith("bench 9001.001 model=qwen3.8:27b found=0 of 29 ")
    assert lines[1].endswith("pages_failed=14 of 14")
    assert lines[-1] == "bench matters=1 imperfect=1"


def test_candidate_lines_name_the_model_candidate(tmp_path):
    r = bench(write_config(tmp_path, playbook=ROOT / "playbook", host="http://127.0.0.1:9"),
              "--matters", str(MATTERS), "--candidate", str(FLAWED))
    assert r.stdout.splitlines()[0].startswith("bench 9001.001 model=candidate found=")


def test_bench_received_bad_answer_stays_exit1(tmp_path, capsys):
    """A truncated answer reached us: scored with every page failed, exit 1, not exit 2 (D25)."""
    from fakemodel.bench import recordings_for
    from fakemodel.core import FakeModel, FakeTransport
    opener = FakeTransport(FakeModel(recordings=recordings_for(MATTER), mode="truncated"))
    code, lines, err = run_runner_mode(tmp_path, opener)
    with capsys.disabled():
        print(f"received_truncated_exit={code}")
    assert (code, err) == (1, "")
    assert lines[0].startswith("bench 9001.001 failure bench.truncation")
    assert lines[1].endswith("pages_failed=14 of 14")
