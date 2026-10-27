"""Re-brief fix cycle 2 (F1 to F6): each test fails on the defect it names."""

import json
import os
from pathlib import Path
import signal
import subprocess
import time

import pytest

from casefile import doctor
from casefile.config import ConfigError, load
from conftest import ROOT, write_config
from test_doctor import invoke, setup_config

RUN_SH = ROOT / "scripts" / "run.sh"


def alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def wait_for(predicate, seconds=10):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(0.05)
    return predicate()


@pytest.mark.parametrize(("sig", "name"), [(signal.SIGHUP, "SIGHUP"), (signal.SIGTERM, "SIGTERM"),
                                           (signal.SIGINT, "SIGINT")])
def test_f1_signal_stops_job_and_removes_capture(tmp_path, sig, name):
    pids = tmp_path / "pids"
    script = f"echo $$ > {pids}.child; sleep 300 & echo $! > {pids}.grand; echo INVENTED-LINE; wait"
    env = dict(os.environ, TMPDIR=str(tmp_path))
    wrapper = subprocess.Popen([str(RUN_SH), "bash", "-c", script], cwd=ROOT, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    seen = []
    try:
        assert wrapper.stdout.readline() == b"INVENTED-LINE\n"
        seen = [int(Path(f"{pids}.{part}").read_text()) for part in ("child", "grand")]
        assert list(tmp_path.glob("casefile-run.*"))
        os.kill(wrapper.pid, sig)   # run.sh execs the capture stage, so this is the wrapper
        _, err = wrapper.communicate(timeout=20)
        assert wrapper.returncode == 128 + int(sig)
        assert err == f"run.sh: interrupted by {name}; job stopped\n".encode(), err
        assert wait_for(lambda: not any(alive(pid) for pid in seen))
        assert list(tmp_path.glob("casefile-run.*")) == []
    finally:
        for pid in seen:
            try:
                os.killpg(pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        if wrapper.poll() is None:
            wrapper.kill()
        wrapper.communicate()


def test_f2_state_and_playbook_resolve_against_checkout(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    path = home / "config.toml"
    path.write_text(f"[paths]\nmatters = {json.dumps(str(tmp_path / 'matters'))}\n")
    config = load(path)
    assert config.paths.state == ROOT / "state"
    assert config.paths.playbook == ROOT / "playbook"
    ok, reason = doctor.check_playbook(doctor.State(config, config=config))
    assert ok, reason


def test_f2_absolute_values_unchanged(tmp_path):
    config = load(write_config(tmp_path))
    assert config.paths.state == tmp_path / "state"
    assert config.paths.playbook == tmp_path / "playbook"


def run_toolchain(toolchain, tmp_path):
    env = dict(os.environ, CASEFILE_TOOLCHAIN=toolchain, TMPDIR=str(tmp_path))
    return subprocess.run([str(RUN_SH), "true"], cwd=ROOT, env=env, capture_output=True, timeout=30)


def test_f3_refusal_names_path_and_fix(tmp_path):
    result = run_toolchain(str(ROOT), tmp_path)
    assert result.returncode == 95
    expected = (f"run.sh: toolchain {ROOT / ROOT.name} is inside the checkout {ROOT}; set "
                "CASEFILE_TOOLCHAIN to a folder outside it (e.g. ~/.casefile-dev); exit 95\n")
    assert result.stderr.decode() == expected


def test_f3_literal_tilde_hint(tmp_path):
    result = run_toolchain("~/.casefile-dev", tmp_path)
    assert result.returncode == 95
    assert b"~ is not expanded inside quotes; use $HOME" in result.stderr
    assert not (ROOT / "~").exists()


def test_f5_blocked_hint_points_at_root_cause(tmp_path):
    broken = load(write_config(tmp_path / "b", host="http://127.0.0.1:18434", playbook=tmp_path / "nope"))
    code, output = invoke(broken)
    line = next(l for l in output.splitlines() if l.startswith("doctor runlog_job "))
    assert "blocked by context" in line
    assert line.endswith("| do: fix the playbook line above"), line
    assert "reload the model" not in line


def test_f5_model_only_failure_keeps_its_hint(tmp_path):
    from fakemodel.core import FakeModel
    _, output = invoke(setup_config(tmp_path), fake=FakeModel(mode="truncated"))
    line = next(l for l in output.splitlines() if l.startswith("doctor runlog_job "))
    assert "| do: " in line and "playbook" not in line


def test_f6_unknown_user(tmp_path):
    with pytest.raises(ConfigError) as caught:
        load(write_config(tmp_path, matters="~nosuchuserxyz/Cases"))
    assert str(caught.value) == "unknown user in [paths].matters: ~nosuchuserxyz"
