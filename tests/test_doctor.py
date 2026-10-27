"""Doctor verdicts over invented, in-process model replies."""

from io import StringIO
import json
import os
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


VERSIONS = {"ocrmypdf": "17.13.0", "tesseract": "5.5.3"}


def passing_smoke(config):
    """An injected smoke result: a text-free page before, the smoke line read after (Codex 13)."""
    return "", "CASEFILE OCR SMOKE 7342\n", VERSIONS


def invoke(config, *, fake=None, lsof=None, smoke=passing_smoke):
    """Unit tests inject a passing smoke; pass smoke=doctor.REAL to run the real tools."""
    fake = FakeModel() if fake is None else fake
    out = StringIO()
    code = doctor.run(config, out=out, opener=FakeTransport(fake),
                      lsof_runner=lambda *a, **k: lsof_result() if lsof is None else lsof,
                      ocr_smoke=smoke)
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
def test_bad_context(tmp_path, mode, reason, context_status_only):
    code, output = invoke(setup_config(tmp_path), fake=FakeModel(mode=mode))
    assert code == 1, output
    assert f"doctor context FAIL {reason}" in output, output


def test_short_context_fails(tmp_path, capsys, context_status_only):
    code, output = invoke(setup_config(tmp_path), fake=FakeModel(mode="short_context"))
    assert code == 1, output
    report(capsys, next(line for line in output.splitlines() if line.startswith("doctor context ")))
    assert "doctor context FAIL context_length=8192 want 65536" in output, output


def test_truncated_fails(tmp_path, context_status_only):
    code, output = invoke(setup_config(tmp_path), fake=FakeModel(mode="truncated"))
    assert code == 1, output
    assert "doctor context FAIL done_reason=length" in output, output


def test_empty_answer_fails(tmp_path, context_status_only):
    config = setup_config(tmp_path)
    code, output = invoke(config, fake=FakeModel(mode="empty"))
    assert code == 1, output
    assert "doctor context FAIL status=200 empty" in output, output
    with runlog.open_db(config.paths.state / "runlog.sqlite") as log:
        assert log.count_test_jobs() == 0
        assert log.connection.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 0
        assert log.connection.execute("SELECT gate FROM failures").fetchone()[0] == "doctor.context"


def test_wrong_word_fails(tmp_path, capsys, context_status_only):
    fake = FakeModel(recordings=[{"messages": doctor.MESSAGES, "answer": "READY."}])
    code, output = invoke(setup_config(tmp_path), fake=fake)
    assert code == 1, output
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
        assert doctor.run(config, out=out, ocr_smoke=passing_smoke) == 1
        assert f"doctor ollama_loopback FAIL listening on *:{server.server_port}" in out.getvalue()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class ReplyFields(FakeModel):
    def __init__(self, **fields):
        super().__init__()
        self.fields = fields

    def handle(self, method, path, body=b""):
        status, payload = super().handle(method, path, body)
        if path == "/api/chat" and status == 200:
            payload.update(self.fields)
            for key, value in self.fields.items():
                if value is None:
                    payload.pop(key)
        return status, payload


@pytest.mark.parametrize("field", ["prompt_eval_count", "eval_count"])
@pytest.mark.parametrize("count", [None, 0, -1, True, "20", 1.5])
def test_context_requires_positive_token_counts(tmp_path, monkeypatch, field, count, context_status_only):
    from dataclasses import replace

    native_chat = doctor.ModelClient.chat

    def chat(client, *args, **kwargs):
        return replace(native_chat(client, *args, **kwargs), **{field: count})

    monkeypatch.setattr(doctor.ModelClient, "chat", chat)
    config = setup_config(tmp_path)
    code, output = invoke(config)
    assert code == 1, output
    assert "doctor context FAIL" in output, output
    with runlog.open_db(config.paths.state / "runlog.sqlite") as log:
        assert log.count_test_jobs() == 0


def ocr_line(output):
    return next(line for line in output.splitlines() if line.startswith("doctor ocr "))


def test_ocr_unit_cases(tmp_path, capsys, monkeypatch):
    """Six verdicts from injected smokes; each guard fails alone (#R01-CX-10)."""
    from casefile.intake import IntakeError

    def smoke(before, after):
        return lambda config: (before, after, VERSIONS)

    def raises(message):
        def run(config):
            raise IntakeError(message)
        return run

    cases = [
        ("pass", smoke("", "CASEFILE OCR SMOKE 7342\n"), True,
         "smoke=ok stamps=SMOKE7342 ocrmypdf=17.13.0 tesseract=5.5.3 ms="),
        ("input had text", smoke("already text", "CASEFILE OCR SMOKE 7342"), False, "smoke input had text"),
        ("text wrong, stamp right", smoke("", "SMOKE 7342 and nothing else"), False,
         "smoke text not read: SMOKE 7342 and nothing else"),
        ("stamp wrong, text right", smoke("", "CASEFILE OCR SMOKE"), False, "smoke stamp not found"),
        ("ocrmypdf exit", raises("ocrmypdf exit=7: gs: no fonts"), False, "ocrmypdf exit=7: gs: no fonts"),
        ("tool missing", smoke("", "CASEFILE OCR SMOKE 7342"), False, "not found: tesseract"),
    ]
    good = 0
    for index, (name, injected, want_ok, text) in enumerate(cases):
        config = setup_config(tmp_path / f"c{index}")
        with monkeypatch.context() as patch:
            if name == "tool missing":
                patch.setattr(doctor.shutil, "which", lambda tool: None)
            ok, reason = doctor.check_ocr(doctor.State(config, config=config, ocr_smoke=injected))
        assert ok is want_ok and text in reason, (name, ok, reason)
        code, output = invoke(config, smoke=injected) if name != "tool missing" else (None, "")
        if name != "tool missing":
            line = ocr_line(output)
            assert ("PASS" in line) is want_ok and text in line, (name, line)
            assert code == (0 if want_ok else 1), (name, code, output)
        good += 1
    with capsys.disabled():
        print(f"ocr_unit={good} of 6")
    assert good == 6


def test_ocr_next_step_names_the_fix(tmp_path):
    config = setup_config(tmp_path)
    state = doctor.State(config, config=config)
    assert "brew install ocrmypdf" in doctor.next_step("ocr", "not found: ocrmypdf", state)
    assert "ocrmypdf stderr" in doctor.next_step("ocr", "ocrmypdf exit=7: x", state)


def write_stub_tools(folder, ocrmypdf_body):
    folder.mkdir(parents=True, exist_ok=True)
    tools = {}
    for name, body in (("tesseract", '#!/bin/sh\n[ "$1" = "--version" ] && echo "tesseract 5.5.3"\nexit 0\n'),
                       ("ocrmypdf", ocrmypdf_body)):
        stub = folder / name
        stub.write_text(body)
        stub.chmod(0o755)
        tools[name] = str(stub)
    return tools


def test_ocr_copying_stub_cannot_pass(tmp_path):
    """A tool that copies input to output with an empty sidecar read nothing (Codex 16)."""
    body = ('#!/bin/bash\n[ "$1" = "--version" ] && { echo 17.13.0; exit 0; }\n'
            'args=("$@"); n=${#args[@]}; cp "${args[$((n-2))]}" "${args[$((n-1))]}"\n'
            'for ((i=0;i<n;i++)); do [ "${args[$i]}" = "--sidecar" ] && : > "${args[$((i+1))]}"; done\nexit 0\n')
    config = setup_config(tmp_path, ocr=write_stub_tools(tmp_path / "stubs", body))
    ok, reason = doctor.check_ocr(doctor.State(config, config=config))
    assert ok is False and reason == "smoke text not read: "


def test_ocr_no_op_stub_is_exit_zero_but_not_a_pass(tmp_path):
    body = '#!/bin/bash\n[ "$1" = "--version" ] && echo 17.13.0\nexit 0\n'
    config = setup_config(tmp_path, ocr=write_stub_tools(tmp_path / "stubs", body))
    ok, reason = doctor.check_ocr(doctor.State(config, config=config))
    assert ok is False and "smoke=ok" not in reason, reason


@pytest.mark.ocr
def test_run_sh_appends_homebrew_to_path(tmp_path):
    """The wrapper finds the OCR tools even when launchd or the sandbox omit Homebrew's folder."""
    result = subprocess.run(
        ["scripts/run.sh", "python", "-c",
         "import shutil; print(shutil.which('ocrmypdf')); print(shutil.which('tesseract'))"],
        cwd=ROOT, env={"PATH": "/usr/bin:/bin", "HOME": os.environ["HOME"], "TMPDIR": os.environ.get("TMPDIR", "/tmp")},
        capture_output=True, text=True, timeout=60)
    ocrmypdf, tesseract = result.stdout.split()
    assert ocrmypdf in ("/opt/homebrew/bin/ocrmypdf", "/usr/local/bin/ocrmypdf"), result
    assert tesseract in ("/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"), result


@pytest.mark.ocr
def test_ocr_real_tools(tmp_path, capsys):
    code, output = invoke(setup_config(tmp_path), smoke=doctor.REAL)
    line = ocr_line(output)
    with capsys.disabled():
        print(line)
        print("ocr_real=" + ("PASS" if line.startswith("doctor ocr PASS") else "FAIL"))
    assert line.startswith("doctor ocr PASS smoke=ok stamps=SMOKE7342 ocrmypdf="), output
    assert " tesseract=" in line and " ms=" in line
    assert verdicts(output) == set()


@pytest.mark.parametrize("fields,reason", [
    ({"done_reason": "length"}, "done_reason=length"),
    ({"done": False}, "done must be true"),
])
def test_ready_requires_completion(tmp_path, fields, reason, context_status_only):
    code, output = invoke(setup_config(tmp_path), fake=ReplyFields(**fields))
    assert code == 1, output
    assert "doctor context FAIL" in output, output
    assert reason in next(line for line in output.splitlines() if line.startswith("doctor context "))


@pytest.fixture
def context_status_only(monkeypatch):
    # Keep unrelated and downstream failures from masking the context exit status.
    monkeypatch.setattr(doctor, "check_ocr", lambda state: (True, "isolated version check"))
    monkeypatch.setattr(doctor, "check_runlog_job", lambda state: (True, "isolated downstream check"))


def test_runlog_job_fails_when_answer_not_recorded(tmp_path, monkeypatch):
    config = setup_config(tmp_path)
    monkeypatch.setattr(runlog.RunLog, "record_answer", lambda *args, **kwargs: None)
    monkeypatch.setattr(doctor, "check_ocr", lambda state: (True, "isolated OCR check"))
    code, output = invoke(config)
    assert "doctor context PASS context_length=65536" in output, output
    assert "doctor runlog_job FAIL test_jobs=+0" in output, output
    assert verdicts(output) == {"runlog_job"}, output
    assert code == 1, output
    with runlog.open_db(config.paths.state / "runlog.sqlite") as log:
        assert log.count_test_jobs() == 0
