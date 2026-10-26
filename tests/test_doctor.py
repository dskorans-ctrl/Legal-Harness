"""Doctor verdicts over invented, in-process model replies."""

from io import StringIO
import json
import shutil
import subprocess
from threading import Thread

import pytest

from casefile import doctor, runlog
from casefile.config import load
from conftest import ROOT, ocr_expected_fail, write_config
from fakemodel.core import FakeModel, FakeTransport
from fakemodel.server import serve


NAMES = ["config", "folders", "playbook", "runlog_schema", "ollama_loopback",
         "context", "runlog_job", "ocr"]


def lsof_result(address="127.0.0.1:18434", returncode=0, stderr=""):
    return subprocess.CompletedProcess([], returncode,
        "COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME\n"
        f"Python 1 test 3u IPv4 0x0 0t0 TCP {address} (LISTEN)\n" if address else "", stderr)


def setup_config(tmp_path, **overrides):
    config = load(write_config(tmp_path, host="http://127.0.0.1:18434", **overrides))
    shutil.copytree(ROOT / "playbook", config.paths.playbook, dirs_exist_ok=True)
    return config


def invoke(config, *, fake=None, lsof=None):
    fake = FakeModel() if fake is None else fake
    out = StringIO()
    code = doctor.run(config, out=out, opener=FakeTransport(fake),
                      lsof_runner=lambda *a, **k: lsof_result() if lsof is None else lsof)
    return code, out.getvalue()


def verdicts(output):
    lines = [line.split(maxsplit=3) for line in output.splitlines()
             if line.startswith("doctor ") and not line.startswith("doctor failed=")]
    assert [line[1] for line in lines] == NAMES, f"verdicts={len(lines)}\n{output}"
    assert all(line[2] in {"PASS", "FAIL"} for line in lines), output
    return {line[1] for line in lines if line[2] == "FAIL"}


def report(capsys, text):
    with capsys.disabled():
        print(text)


def test_fake_green_except_ocr(tmp_path, capsys):
    code, output = invoke(setup_config(tmp_path))
    expected = {"ocr"} if ocr_expected_fail() else set()
    fails = verdicts(output)
    report(capsys, f"verdicts=8 fails={fails} expected={expected}")
    assert fails == expected, output
    assert code == (1 if expected else 0), output


@pytest.mark.parametrize("mode,reason", [("short_context", "context_length=8192 want 65536"),
                                        ("truncated", "done_reason=length")])
def test_bad_context(tmp_path, mode, reason):
    _, output = invoke(setup_config(tmp_path), fake=FakeModel(mode=mode))
    assert f"doctor context FAIL {reason}" in output, output


def test_short_context_fails(tmp_path, capsys):
    _, output = invoke(setup_config(tmp_path), fake=FakeModel(mode="short_context"))
    report(capsys, next(line for line in output.splitlines() if line.startswith("doctor context ")))
    assert "doctor context FAIL context_length=8192 want 65536" in output, output


def test_truncated_fails(tmp_path):
    _, output = invoke(setup_config(tmp_path), fake=FakeModel(mode="truncated"))
    assert "doctor context FAIL done_reason=length" in output, output


def test_empty_answer_fails(tmp_path):
    config = setup_config(tmp_path)
    _, output = invoke(config, fake=FakeModel(mode="empty"))
    assert "doctor context FAIL status=200 empty" in output, output
    with runlog.open_db(config.paths.state / "runlog.sqlite") as log:
        assert log.count_test_jobs() == 0
        assert log.connection.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 0
        assert log.connection.execute("SELECT gate FROM failures").fetchone()[0] == "doctor.context"


def test_wrong_word_fails(tmp_path, capsys):
    fake = FakeModel(recordings=[{"messages": doctor.MESSAGES, "answer": "READY."}])
    _, output = invoke(setup_config(tmp_path), fake=fake)
    report(capsys, next(line for line in output.splitlines() if line.startswith("doctor context ")))
    assert "doctor context FAIL answer=READY. want READY" in output, output


def test_loopback_star_fails(tmp_path):
    _, output = invoke(setup_config(tmp_path), lsof=lsof_result("*:18434"))
    assert "doctor ollama_loopback FAIL listening on *:18434" in output, output


@pytest.mark.parametrize("result,reason", [
    (lsof_result(None, 1), "no listener visible on 18434"),
    (lsof_result(None, 1, "[Errno 1] Operation not permitted"), "lsof failed: [Errno 1]"),
    (lsof_result("192.0.2.1:18434"), "listening on 192.0.2.1:18434"),
])
def test_loopback_failures(tmp_path, result, reason):
    _, output = invoke(setup_config(tmp_path), lsof=result)
    assert f"doctor ollama_loopback FAIL {reason}" in output, output


def test_nothing_skipped(tmp_path):
    code, output = invoke(tmp_path / "missing.toml")
    assert verdicts(output) == set(NAMES)
    assert output.count("FAIL blocked by config") == 7
    assert code == 1


def test_records_one_job(tmp_path):
    config = setup_config(tmp_path)
    for expected in (1, 2):
        _, output = invoke(config)
        assert "doctor runlog_job PASS test_jobs=+1" in output, output
        with runlog.open_db(config.paths.state / "runlog.sqlite") as log:
            assert log.count_test_jobs() == expected
            row = log.connection.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1").fetchone()
            assert row["pages_in"] == 0 and row["card"] == "doctor.warmup"
            assert len(row["card_version"]) == 12 and row["playbook_version"].startswith("pb-")


def test_uses_config_num_ctx(tmp_path):
    fake = FakeModel(context_length=131072)
    _, output = invoke(setup_config(tmp_path, num_ctx=131072), fake=fake)
    assert "doctor context PASS context_length=131072" in output, output
    chats = [json.loads(r["body"]) for r in fake.requests if r["path"] == "/api/chat"]
    assert len(chats) == 1 and chats[0]["options"]["num_ctx"] == 131072


@pytest.mark.socket
def test_loopback_real_bind_all(tmp_path):
    server = serve(bind="0.0.0.0", port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = load(write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}"))
        shutil.copytree(ROOT / "playbook", config.paths.playbook, dirs_exist_ok=True)
        out = StringIO()
        assert doctor.run(config, out=out) == 1
        assert f"doctor ollama_loopback FAIL listening on *:{server.server_port}" in out.getvalue()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
