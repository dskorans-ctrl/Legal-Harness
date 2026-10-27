"""A reply with no done_reason is not a stop: bench.truncation fires (D25, verifier seed V2-S4)."""

from casefile import benchrun, config as config_mod, matter as matters, runlog
from conftest import ROOT, write_config
from fakemodel.bench import recordings_for
from fakemodel.core import FakeModel, FakeTransport

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"


def test_missing_done_reason_is_truncation(tmp_path):
    config = config_mod.load(write_config(tmp_path))
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
        r = benchrun.run(matters.load(MATTER), config, log, "pb-test", FakeTransport(fake))
        assert r.failure == "bench.truncation: done_reason=None", r.failure
        assert r.pages_failed == 14
        assert r.candidate.facts == ()
        rows = [tuple(row) for row in log.connection.execute("SELECT status, done_reason FROM answers ORDER BY id")]
        assert rows == [("failed", None)]
        gates = [row[0] for row in log.connection.execute("SELECT gate FROM failures ORDER BY id")]
        assert gates == ["bench.truncation"]
    finally:
        log.close()
