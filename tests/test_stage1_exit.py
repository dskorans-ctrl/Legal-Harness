"""Stage 1 process checks use invented warmup data and the shipped playbook."""

import os
import shlex
import subprocess
import sys
from threading import Thread

import pytest

from casefile import runlog
from casefile.config import load
from conftest import ROOT, ocr_expected_fail, write_config
from fakemodel.server import serve


NAMES = ["config", "folders", "playbook", "runlog_schema", "ollama_loopback",
         "context", "runlog_job", "ocr"]


def assert_exit(result, command, config, capsys, *, label=""):
    expected = {"ocr"} if ocr_expected_fail() else set()
    lines = [line.split(maxsplit=3) for line in result.stdout.splitlines()
             if line.startswith("doctor ") and not line.startswith("doctor failed=")]
    fails = {line[1] for line in lines if len(line) >= 3 and line[2] == "FAIL"}
    with runlog.open_db(config.paths.state / "runlog.sqlite") as log:
        jobs = log.count_test_jobs()
    evidence = (f"command={shlex.join(command)}\n{result.stdout}\n{result.stderr}\n"
                f"exit={result.returncode} verdicts={len(lines)} fails={fails} "
                f"expected={expected} test_jobs={jobs}")
    with capsys.disabled():
        oracle = f"expected={expected} " if label else ""
        print(f"{label}exit={result.returncode} verdicts={len(lines)} fails={fails} "
              f"{oracle}test_jobs={jobs}")
    assert [line[1] for line in lines] == NAMES, evidence
    assert all(len(line) == 4 and line[2] in {"PASS", "FAIL"} for line in lines), evidence
    assert fails == expected, evidence
    assert result.returncode == (1 if expected else 0), evidence
    assert jobs == 1, evidence
    assert result.stdout.splitlines()[-1] == f"doctor failed={len(expected)} of 8", evidence


@pytest.mark.socket
def test_stage1_exit(tmp_path, capsys):
    server = serve(port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        path = write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}",
                            playbook=ROOT / "playbook")
        command = ["scripts/run.sh", "casefile", "doctor"]
        result = subprocess.run(command, cwd=ROOT,
                                env=dict(os.environ, CASEFILE_CONFIG=str(path)),
                                capture_output=True, text=True, timeout=60)
        assert_exit(result, command, load(path), capsys)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


# This companion controls the same process assertions where sockets are denied.
# The socket-marked test above remains the stage exit acceptance test.
INPROCESS_CHILD = '''
import subprocess
from casefile import cli, doctor
from fakemodel.core import FakeModel, FakeTransport
native_client = doctor.ModelClient
fake = FakeModel()
doctor.ModelClient = lambda config, opener=None: native_client(config, FakeTransport(fake))
native_run = doctor.run
def lsof(*args, **kwargs):
    return subprocess.CompletedProcess([], 0,
        "COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME\\n"
        "Python 1 test 3u IPv4 0x0 0t0 TCP 127.0.0.1:18434 (LISTEN)\\n", "")
doctor.run = lambda config: native_run(config, lsof_runner=lsof)
raise SystemExit(cli.main())
'''


def test_stage1_inprocess_control(tmp_path, capsys):
    path = write_config(tmp_path, host="http://127.0.0.1:18434", playbook=ROOT / "playbook")
    env = dict(os.environ, CASEFILE_CONFIG=str(path))
    env["PYTHONPATH"] = str(ROOT / "tests") + os.pathsep + env.get("PYTHONPATH", "")
    command = ["scripts/run.sh", sys.executable, "-c", INPROCESS_CHILD, "doctor"]
    result = subprocess.run(command, cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=60)
    assert_exit(result, command, load(path), capsys, label="stage-control ")
