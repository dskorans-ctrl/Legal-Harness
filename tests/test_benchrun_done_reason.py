"""A reply with no done_reason fails gate.truncation after the one retry."""

from casefile import pipeline, config as config_mod, matter as matters, runlog
from conftest import ROOT, write_config
from fakemodel.bench import recordings_for
from fakemodel.core import FakeModel, FakeTransport

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"


def test_missing_done_reason_is_truncation(tmp_path):
    config = config_mod.load(write_config(tmp_path, playbook=ROOT / "playbook"))
    log = runlog.open_db(tmp_path / "runlog.sqlite")
    fake = FakeModel(recordings=recordings_for(MATTER))
    original = fake.handle

    def handle(method, path, body=b""):
        status, payload = original(method, path, body)
        if path == "/api/chat":
            payload.pop("done_reason", None)
        return status, payload

    fake.handle = handle
    try:
        r = pipeline.bench_run(matters.load(MATTER), config, log, "pb-test", FakeTransport(fake))
        assert r.failure == ("gate.truncation: the answer stopped before it finished (done_reason=None); "
                             "not retried: the one retry was used"), r.failure
        assert r.pages_failed == 14
        assert r.candidate.facts == ()
        rows = [tuple(row) for row in log.connection.execute("SELECT status, done_reason FROM answers ORDER BY id")]
        assert rows == [("failed", None)] * 2
        gates = [row[0] for row in log.connection.execute("SELECT gate FROM failures ORDER BY id")]
        assert gates == ["gate.truncation"] * 2
    finally:
        log.close()
