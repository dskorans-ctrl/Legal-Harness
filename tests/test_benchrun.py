"""The stage 2 runner: seven probes, each with exactly one thing wrong, and the run-log rows."""

import json
import sqlite3
from pathlib import Path

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
        # 1. Replay (default mode)
        r = go()
        check1 = r.pages_failed == 0 and r.failure is None and len(r.candidate.facts) == 28
        
        # Request shape check
        sent = json.loads(fake.requests[-1]["body"])
        req_shape_ok = (
            sent["options"] == {"num_ctx": 65536, "temperature": 0.1} and
            sent["stream"] is False and
            sent["messages"][1]["content"].startswith("Matter 9001.001\n=== PAGE medical/001 BATES MED0001 ===")
        )
        checks.append(check1 and req_shape_ok)

        # 2. Truncated
        fake.mode = "truncated"
        r = go()
        check2 = r.failure.startswith("bench.truncation") and r.pages_failed == 14
        checks.append(check2)

        # 3. Malformed
        fake.mode = "malformed"
        r = go()
        check3 = r.failure.startswith("bench.answer: not JSON")
        checks.append(check3)

        # 4. Forbidden
        fake.mode = "forbidden"
        r = go()
        check4 = r.failure.startswith("bench.answer")
        checks.append(check4)

        # 5. Truncation only (full valid JSON, done_reason "length")
        fake.mode = "replay"
        original = patched(fake, "done_reason", "length")
        r = go()
        fake.handle = original
        check5 = r.failure.startswith("bench.truncation") and r.pages_failed == 14
        checks.append(check5)

        # 6. Incomplete
        fake.mode = "incomplete"
        r = go()
        newest = log.connection.execute("SELECT status, raw_answer FROM answers ORDER BY id DESC LIMIT 1").fetchone()
        check6 = (
            r.failure.startswith("bench.model: status=200 done must be true") and
            newest[0] == "failed" and
            '"done": false' in newest[1]
        )
        checks.append(check6)

        # 7. Counts only
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
