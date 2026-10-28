"""Stage 2 exit test: casefile bench scores the invented matter on the stand-in server (D25)."""

import os
import sqlite3
import subprocess
import sys
from threading import Thread

import pytest

from casefile.config import load
from conftest import ROOT, write_config
from fakemodel.bench import recordings_for
from fakemodel.core import FakeModel
from fakemodel.server import serve

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
PERFECT = ("bench 9001.001 model=qwen3.8:27b found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")
COMMAND = ["casefile", "bench", "--matters", "tests/fixtures/matters"]


def counts(config):
    """(runs, ok answers) in the run log; (0, 0) when it does not exist yet."""
    path = config.paths.state / "runlog.sqlite"
    if not path.exists():
        return 0, 0
    db = sqlite3.connect(path)
    try:
        runs = db.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        ok = db.execute("SELECT COUNT(*) FROM answers WHERE status = 'ok'").fetchone()[0]
    finally:
        db.close()
    return runs, ok


INPROCESS_CHILD = '''
from casefile import pipeline, cli
from fakemodel.bench import recordings_for
from fakemodel.core import FakeModel, FakeTransport
from conftest import ROOT
native_client = pipeline.ModelClient
fake = FakeModel(recordings=recordings_for(ROOT / "tests" / "fixtures" / "matters" / "9001.001"))
pipeline.ModelClient = lambda config, opener=None: native_client(config, FakeTransport(fake))
raise SystemExit(cli.main())
'''


@pytest.mark.socket
def test_stage2_exit(tmp_path, capsys):
    server = serve(port=0, model=FakeModel(recordings=recordings_for(MATTER)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        path = write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}", playbook=ROOT / "playbook")
        config = load(path)
        runs0, ok0 = counts(config)
        result = subprocess.run(["scripts/run.sh", *COMMAND], cwd=ROOT,
                                env=dict(os.environ, CASEFILE_CONFIG=str(path)),
                                capture_output=True, text=True, timeout=120)
        runs1, ok1 = counts(config)
    finally:
        server.shutdown()
        thread.join(timeout=5)
        alive = thread.is_alive()
        server.server_close()

    lines = result.stdout.splitlines()
    dr, da = runs1 - runs0, ok1 - ok0
    with capsys.disabled():
        print(f"stage2 exit={result.returncode} runs={dr:+d} answers_ok={da:+d} server_stopped={int(not alive)}")
        print(lines[0] if lines else "")
    evidence = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 0, evidence
    assert lines[0] == PERFECT, evidence
    assert lines[-1] == "bench matters=1 imperfect=0", evidence
    assert dr == 1 and da == 1, evidence
    assert not alive


def test_stage2_inprocess_control(tmp_path, capsys):
    path = write_config(tmp_path, host="http://127.0.0.1:18434", playbook=ROOT / "playbook")
    config = load(path)
    env = dict(os.environ, CASEFILE_CONFIG=str(path))
    env["PYTHONPATH"] = str(ROOT / "tests") + os.pathsep + env.get("PYTHONPATH", "")
    runs0, ok0 = counts(config)
    result = subprocess.run(["scripts/run.sh", sys.executable, "-c", INPROCESS_CHILD, *COMMAND[1:]],
                            cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    runs1, ok1 = counts(config)
    lines = result.stdout.splitlines()
    dr, da = runs1 - runs0, ok1 - ok0
    with capsys.disabled():
        print(f"stage2-control exit={result.returncode} runs={dr:+d} answers_ok={da:+d}")
    evidence = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 0, evidence
    assert lines[0] == PERFECT, evidence
    assert lines[-1] == "bench matters=1 imperfect=0", evidence
    assert dr == 1 and da == 1, evidence
