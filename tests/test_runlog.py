"""Only invented run records are used, always inside pytest temporary paths."""

from datetime import datetime, timezone
import sqlite3

import pytest

from casefile.runlog import open_db


def _start(log, **overrides):
    values = dict(job="doctor", card="doctor.warmup", card_version="c" * 12,
                  playbook_version="pb-invented", model="invented-model", pages_in=0,
                  prompt_sha256="a" * 64)
    values.update(overrides)
    return log.start_run(**values)


def test_append_only(tmp_path, capsys):
    with open_db(tmp_path / "runlog.sqlite") as log:
        run = _start(log)
        log.record_answer(run, raw_answer="READY", status="ok", done_reason="stop",
                          prompt_eval_count=12, eval_count=1)
        log.record_failure(run, "invented.gate", "invented failure")
        log.record_approval(run, item="invented item", decision="approved", by_whom="test actor")
        assert log.connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0] == 8
        blocked = 0
        for table in ("runs", "answers", "failures", "approvals"):
            for statement in (f"UPDATE {table} SET id=id", f"DELETE FROM {table}"):
                try:
                    with log.connection:
                        log.connection.execute(statement)
                except sqlite3.DatabaseError as exc:
                    assert "append-only" in str(exc)
                    blocked += 1
        with capsys.disabled():
            print(f"blocked_writes={blocked} of 8")
        assert blocked == 8
        for table in ("runs", "answers", "failures", "approvals"):
            assert log.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 1


def test_test_job_count(tmp_path, capsys):
    path = tmp_path / "nested" / "runlog.sqlite"
    with open_db(path) as log:
        assert log.count_test_jobs() == 0
        log.record_answer(_start(log), raw_answer="READY", status="ok")
        log.record_answer(_start(log), raw_answer="unfinished", status="failed")
        log.record_answer(_start(log, job="other"), raw_answer="READY", status="ok")
        log.record_answer(_start(log, card="other.card"), raw_answer="READY", status="ok")
        _start(log)  # A start without an answer does not count.
        count = log.count_test_jobs()
        with capsys.disabled():
            print(f"test_jobs={count}")
        assert count == 1
    with open_db(path) as reopened:
        assert reopened.count_test_jobs() == 1
        assert reopened.schema_version == 1
        assert reopened.connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert reopened.connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_persisted_fields_and_constraints(tmp_path):
    path = tmp_path / "runlog.sqlite"
    with open_db(path) as log:
        run = _start(log, matter="invented-matter", pages_in=3)
        log.record_answer(run, raw_answer="invented raw\nanswer", status="failed",
                          done_reason="length", prompt_eval_count=23, eval_count=5)
        log.record_failure(run, "invented.gate", "invented refusal")
        log.record_approval(run, item="invented item", decision="edited", by_whom="test actor")
    with open_db(path) as log:
        connection = log.connection
        row = dict(connection.execute("SELECT * FROM runs").fetchone())
        timestamp = row.pop("started_at")
        assert timestamp.endswith("Z")
        assert datetime.fromisoformat(timestamp).utcoffset() == timezone.utc.utcoffset(None)
        assert row == dict(id=run, job="doctor", matter="invented-matter", card="doctor.warmup",
                           card_version="c" * 12, playbook_version="pb-invented",
                           model="invented-model", pages_in=3, prompt_sha256="a" * 64)
        answer = dict(connection.execute("SELECT * FROM answers").fetchone())
        assert answer.pop("finished_at").endswith("Z")
        assert answer == dict(id=1, run_id=run, raw_answer="invented raw\nanswer", status="failed",
                              done_reason="length", prompt_eval_count=23, eval_count=5)
        failure = dict(connection.execute("SELECT * FROM failures").fetchone())
        assert failure.pop("at").endswith("Z")
        assert failure == dict(id=1, run_id=run, gate="invented.gate", message="invented refusal")
        approval = dict(connection.execute("SELECT * FROM approvals").fetchone())
        assert approval.pop("at").endswith("Z")
        assert approval == dict(id=1, run_id=run, item="invented item", decision="edited", by_whom="test actor")
        with pytest.raises(sqlite3.IntegrityError):
            log.record_answer(run + 999, raw_answer="orphan", status="ok")
        with pytest.raises(sqlite3.IntegrityError):
            log.record_answer(run, raw_answer="invalid", status="unknown")
        with pytest.raises(sqlite3.IntegrityError):
            log.record_approval(run, item="invalid", decision="unknown", by_whom="test actor")
