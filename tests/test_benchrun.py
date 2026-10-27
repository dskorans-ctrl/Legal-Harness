"""The stage 2 runner: seven probes, each with exactly one thing wrong, and the run-log rows."""

import json

import pytest

from casefile import benchrun, config as config_mod, matter as matters, runlog
from conftest import ROOT, write_config
from fakemodel.bench import recordings_for
from fakemodel.core import FakeModel, FakeTransport

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"


def patched(fake, field, value):
    """Wrap fake.handle so /api/chat payloads get payload[field] = value; returns the original."""
    original = fake.handle

    def handle(method, path, body=b""):
        status, payload = original(method, path, body)
        if path == "/api/chat":
            payload[field] = value
        return status, payload

    fake.handle = handle
    return original


def test_benchrun_modes(tmp_path, capsys):
    # Setup
    config = config_mod.load(write_config(tmp_path))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    fake = FakeModel(recordings=recordings_for(MATTER))
    opener = FakeTransport(fake)
    matter = matters.load(MATTER)

    checks = []

    def go():
        return benchrun.run(matter, config, log, "pb-test", opener)

    try:
        # Replay (default mode)
        r = go()
        check1 = r.pages_failed == 0 and r.failure is None and len(r.candidate.facts) == 31

        # Request shape check
        sent = json.loads(fake.requests[-1]["body"])
        req_shape_ok = (
            sent["options"] == {"num_ctx": 65536, "temperature": 0.1} and
            sent["stream"] is False and
            sent["messages"][1]["content"].startswith("Matter 9001.001\n=== PAGE medical/001 BATES MED0001 ===")
        )
        checks.append(check1 and req_shape_ok)

        # Truncated
        fake.mode = "truncated"
        r = go()
        check2 = r.failure.startswith("bench.truncation") and r.pages_failed == 14
        checks.append(check2)

        # Malformed
        fake.mode = "malformed"
        r = go()
        check3 = r.failure.startswith("bench.answer: not JSON")
        checks.append(check3)

        # Forbidden
        fake.mode = "forbidden"
        r = go()
        check4 = r.failure.startswith("bench.answer")
        checks.append(check4)

        # Truncation only (full valid JSON, done_reason "length")
        fake.mode = "replay"
        original = patched(fake, "done_reason", "length")
        r = go()
        fake.handle = original
        check5 = r.failure.startswith("bench.truncation") and r.pages_failed == 14
        checks.append(check5)

        # Incomplete
        fake.mode = "incomplete"
        r = go()
        newest = log.connection.execute("SELECT status, raw_answer FROM answers ORDER BY id DESC LIMIT 1").fetchone()
        check6 = (
            r.failure.startswith("bench.model: status=200 done must be true") and
            newest[0] == "failed" and
            '"done": false' in newest[1]
        )
        checks.append(check6)

        # Counts only
        fake.mode = "replay"
        original = patched(fake, "eval_count", None)
        r = go()
        fake.handle = original
        check7 = r.failure.startswith("bench.counts") and r.pages_failed == 14
        checks.append(check7)

        # Read run log
        db = log.connection
        runs = [tuple(row) for row in db.execute("SELECT job, matter, pages_in FROM runs ORDER BY id")]
        ok_answers = db.execute("SELECT COUNT(*) FROM answers WHERE status = 'ok'").fetchone()[0]
        failed_answers = db.execute("SELECT COUNT(*) FROM answers WHERE status = 'failed'").fetchone()[0]
        gates = [row[0] for row in db.execute("SELECT gate FROM failures ORDER BY id")]

        ok = sum(checks)

        with capsys.disabled():
            print(f"benchrun_modes={ok} of 7 answers_ok={ok_answers} answers_failed={failed_answers} failures={len(gates)}")

        assert checks == [True] * 7
        assert runs == [("bench", "9001.001", 14)] * 7
        assert (ok_answers, failed_answers) == (1, 6)
        assert gates == ["bench.truncation", "bench.answer", "bench.answer", "bench.truncation", "bench.model", "bench.counts"]

    finally:
        log.close()


def test_benchrun_zero_counts(tmp_path):
    """A zero token count is not proof the model read or wrote anything: bench.counts must fire."""
    config = config_mod.load(write_config(tmp_path))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    fake = FakeModel(recordings=recordings_for(MATTER))
    opener = FakeTransport(fake)
    matter = matters.load(MATTER)
    try:
        failures = []
        for field in ("eval_count", "prompt_eval_count"):
            original = patched(fake, field, 0)
            r = benchrun.run(matter, config, log, "pb-test", opener)
            fake.handle = original
            failures.append(r.failure)
            assert r.failure is not None and r.failure.startswith("bench.counts"), (field, r.failure)
            assert r.pages_failed == 14
        gates = [row[0] for row in log.connection.execute("SELECT gate FROM failures ORDER BY id")]
        assert gates == ["bench.counts", "bench.counts"]
    finally:
        log.close()


def test_benchrun_unparsed_reply(tmp_path):
    """A 200 reply that is not a JSON object is still stored as a failed answer row (D25)."""
    from io import BytesIO

    class OneReply:
        def __init__(self, body):
            self.body = body

        def open(self, request, timeout=None):
            response = BytesIO(self.body)
            response.getcode = lambda: 200
            return response

    config = config_mod.load(write_config(tmp_path))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    matter = matters.load(MATTER)
    try:
        for text in ("invented reply that is not JSON", '["invented", "array"]'):
            r = benchrun.run(matter, config, log, "pb-test", OneReply(text.encode("utf-8")))
            assert r.failure is not None and r.failure.startswith("bench.model"), r.failure
            assert r.pages_failed == 14
            row = log.connection.execute(
                "SELECT status, raw_answer FROM answers ORDER BY id DESC LIMIT 1").fetchone()
            assert row is not None, text
            assert (row[0], row[1]) == ("failed", text)
        count = log.connection.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
        assert count == 2
    finally:
        log.close()


def test_benchrun_non200_reply(tmp_path):
    """A received non-200 reply is stored as a failed answer row holding the whole body (D25, V2-F1)."""
    from io import BytesIO

    class OneReply:
        def __init__(self, status, body):
            self.status = status
            self.body = body

        def open(self, request, timeout=None):
            response = BytesIO(self.body)
            response.getcode = lambda: self.status
            return response

    config = config_mod.load(write_config(tmp_path))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    matter = matters.load(MATTER)
    long_body = "invented server busy reply " * 20
    try:
        # HTTPError path: the stand-in serves another model tag and answers 404
        fake = FakeModel(recordings=recordings_for(MATTER), model="other:model")
        r = benchrun.run(matter, config, log, "pb-test", FakeTransport(fake))
        assert r.failure is not None and r.failure.startswith("bench.model: status=404"), r.failure
        assert r.pages_failed == 14
        rows = [tuple(row) for row in log.connection.execute("SELECT status, raw_answer FROM answers ORDER BY id")]
        assert rows == [("failed", '{"error": "fakemodel: unknown model"}')]
        gates = [row[0] for row in log.connection.execute("SELECT gate FROM failures ORDER BY id")]
        assert gates == ["bench.model"]

        # Status path: a 503 reply returned without an exception, body longer than 200 bytes
        r = benchrun.run(matter, config, log, "pb-test", OneReply(503, long_body.encode("utf-8")))
        assert r.failure is not None and r.failure.startswith("bench.model: status=503"), r.failure
        assert r.pages_failed == 14
        rows = [tuple(row) for row in log.connection.execute("SELECT status, raw_answer FROM answers ORDER BY id")]
        assert rows == [("failed", '{"error": "fakemodel: unknown model"}'), ("failed", long_body)]
        gates = [row[0] for row in log.connection.execute("SELECT gate FROM failures ORDER BY id")]
        assert gates == ["bench.model", "bench.model"]
    finally:
        log.close()


@pytest.mark.socket
def test_benchrun_redirect_reply(tmp_path):
    """A received 3xx reply is stored as a failed answer row holding the body, on all three paths (D25, OR-8, V2b-F1)."""
    from http.client import HTTPMessage
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from io import BytesIO
    from threading import Thread
    from urllib.error import HTTPError

    class Located:
        def __init__(self, response):
            self.response = response

        def open(self, request, timeout=None):
            return self.response()

    def status_response():
        response = BytesIO(b"invented status redirect body")
        response.getcode = lambda: 302
        response.headers = {"Location": "http://127.0.0.1:1/status"}
        return response

    def error_response():
        headers = HTTPMessage()
        headers["Location"] = "http://127.0.0.1:1/error"
        raise HTTPError("http://127.0.0.1:1/api/chat", 307, "Temporary Redirect", headers,
                        BytesIO(b"invented error redirect body"))

    class Redirecting(BaseHTTPRequestHandler):
        def do_POST(self):
            body = b"invented opener redirect body"
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.1:1/opener")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Redirecting)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    matter = matters.load(MATTER)
    try:
        config = config_mod.load(write_config(tmp_path))
        live = config_mod.load(write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}"))
        cases = [
            (config, Located(status_response), "invented status redirect body"),
            (config, Located(error_response), "invented error redirect body"),
            (live, None, "invented opener redirect body"),
        ]
        for cfg, opener, body in cases:
            r = benchrun.run(matter, cfg, log, "pb-test", opener)
            assert r.failure is not None and r.failure.startswith("bench.model: redirect refused"), (body, r.failure)
            assert r.pages_failed == 14
            row = log.connection.execute(
                "SELECT status, raw_answer FROM answers ORDER BY id DESC LIMIT 1").fetchone()
            assert row is not None, body
            assert (row[0], row[1]) == ("failed", body)
        assert log.connection.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 3
    finally:
        log.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _run_with(tmp_path, opener):
    config = config_mod.load(write_config(tmp_path))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    try:
        result = benchrun.run(matters.load(MATTER), config, log, "pb-test", opener)
        rows = [tuple(row) for row in log.connection.execute("SELECT status, raw_answer FROM answers ORDER BY id")]
    finally:
        log.close()
    return result, rows


def test_benchrun_no_stream_http_error_stores_an_empty_row(tmp_path, capsys):
    """A 503 whose HTTPError has no body stream still stores one failed row with an empty body (D25, OR-8)."""
    from urllib.error import HTTPError

    class Refuses:
        def open(self, request, timeout=None):
            raise HTTPError(request.full_url, 503, "x", {}, None)

    r, rows = _run_with(tmp_path, Refuses())
    ok = int(rows == [("failed", "")] and r.reply_received is True)
    with capsys.disabled():
        print(f"no_stream_row={ok}")
    assert r.failure.startswith("bench.model: status=503"), r.failure
    assert (rows, r.reply_received) == ([("failed", "")], True)


def test_benchrun_empty_body_redirect_stores_an_empty_row(tmp_path, capsys):
    """A 302 whose body is empty is a received reply: one failed row holding "" (verifier 3 S5)."""
    from io import BytesIO

    class Redirects:
        def open(self, request, timeout=None):
            response = BytesIO(b"")
            response.getcode = lambda: 302
            response.headers = {"Location": "http://127.0.0.1:1/"}
            return response

    r, rows = _run_with(tmp_path, Redirects())
    ok = int(rows == [("failed", "")])
    with capsys.disabled():
        print(f"empty_302_row={ok}")
    assert r.failure.startswith("bench.model: redirect refused"), r.failure
    assert (rows, r.reply_received) == ([("failed", "")], True)


def test_benchrun_read_timeout_is_a_received_failed_row(tmp_path, capsys):
    """The status line arrived and the body read timed out: received, one failed row holding ""."""
    import socket
    from io import BytesIO

    class Stalls:
        def open(self, request, timeout=None):
            class Body(BytesIO):
                def getcode(self):
                    return 200

                def read(self, *args):
                    raise socket.timeout("timed out")
            return Body()

    r, rows = _run_with(tmp_path, Stalls())
    ok = int(rows == [("failed", "")] and r.reply_received is True)
    with capsys.disabled():
        print(f"read_timeout_row={ok}")
    assert (rows, r.reply_received) == ([("failed", "")], True)
    assert r.pages_failed == 14


def test_benchrun_no_reply_stores_no_row_and_is_not_received(tmp_path):
    class Dead:
        def open(self, request, timeout=None):
            raise ConnectionRefusedError("refused")

    r, rows = _run_with(tmp_path, Dead())
    assert rows == []
    assert (r.reply_received, r.pages_failed) == (False, 14)
    assert r.failure == "bench.model: refused"


def test_benchrun_reply_received_on_success_and_on_a_failed_gate(tmp_path):
    config = config_mod.load(write_config(tmp_path))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    fake = FakeModel(recordings=recordings_for(MATTER))
    matter = matters.load(MATTER)
    try:
        ok = benchrun.run(matter, config, log, "pb-test", FakeTransport(fake))
        fake.mode = "truncated"
        truncated = benchrun.run(matter, config, log, "pb-test", FakeTransport(fake))
    finally:
        log.close()
    assert (ok.failure, ok.reply_received) == (None, True)
    assert truncated.failure.startswith("bench.truncation") and truncated.reply_received is True
