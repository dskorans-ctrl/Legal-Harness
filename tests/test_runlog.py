"""Only invented run records are used, always inside pytest temporary paths."""

from datetime import datetime, timezone
import sqlite3

import pytest

from casefile import runlog
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
        triggers = _trigger_count(log.connection)
        with capsys.disabled():
            print(f"triggers={triggers}")
        assert triggers == 21
        log.record_gate(run, attempt=1, gate="coverage", verdict="pass", message="invented pass")
        log.record_coverage(run, matter="9003.001", page_id="probe/001", card="invented",
                            status="read", reason="invented pass")
        blocked = 0
        for table in ("runs", "answers", "failures", "approvals", "coverage", "gates"):
            for statement in (f"UPDATE {table} SET id=id", f"DELETE FROM {table}"):
                try:
                    with log.connection:
                        log.connection.execute(statement)
                except sqlite3.DatabaseError as exc:
                    assert "append-only" in str(exc)
                    blocked += 1
        with capsys.disabled():
            print(f"blocked_writes={blocked} of 12")
        assert blocked == 12
        for table in ("runs", "answers", "failures", "approvals", "coverage", "gates"):
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
        assert reopened.schema_version == 2
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
                              done_reason="length", prompt_eval_count=23, eval_count=5,
                              prompt_eval_cached_count=None)
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


@pytest.mark.parametrize("table", ["schema_meta", "runs", "answers", "failures", "approvals", "coverage", "gates"])
def test_replace_rejected_with_recursive_triggers_off(tmp_path, table):
    with open_db(tmp_path / "runlog.sqlite") as log:
        run = _start(log)
        log.record_answer(run, raw_answer="READY", status="ok")
        log.record_failure(run, "invented", "invented refusal")
        log.record_approval(run, item="invented", decision="approved", by_whom="test actor")
        log.record_gate(run, attempt=1, gate="coverage", verdict="pass", message="invented pass")
        log.record_coverage(run, matter="9003.001", page_id="probe/001", card="invented",
                            status="read", reason="invented pass")
        connection = log.connection
        connection.execute("PRAGMA recursive_triggers=OFF")
        assert connection.execute("PRAGMA recursive_triggers").fetchone()[0] == 0
        before = [tuple(row) for row in connection.execute(f"SELECT * FROM {table}")]
        columns = [row[1] for row in connection.execute(f"PRAGMA table_info({table})")]
        values = list(before[0])
        values[-1] = "changed" if table != "answers" else "failed"
        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            connection.execute(f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) "
                               f"VALUES ({','.join('?' for _ in values)})", values)
        assert [tuple(row) for row in connection.execute(f"SELECT * FROM {table}")] == before


V1_SCHEMA = """
BEGIN;
CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO schema_meta VALUES ('schema_version', '1');
CREATE TABLE runs(id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL,
  job TEXT NOT NULL, matter TEXT, card TEXT NOT NULL, card_version TEXT NOT NULL,
  playbook_version TEXT NOT NULL, model TEXT NOT NULL, pages_in INTEGER NOT NULL,
  prompt_sha256 TEXT NOT NULL);
CREATE TABLE answers(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  finished_at TEXT NOT NULL, raw_answer TEXT NOT NULL, done_reason TEXT,
  prompt_eval_count INTEGER, eval_count INTEGER,
  status TEXT NOT NULL CHECK(status IN ('ok','failed')));
CREATE TABLE failures(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  at TEXT NOT NULL, gate TEXT NOT NULL, message TEXT NOT NULL);
CREATE TABLE approvals(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  at TEXT NOT NULL, item TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('approved','rejected','edited')), by_whom TEXT NOT NULL);
CREATE TRIGGER runs_no_update BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER runs_no_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER answers_no_update BEFORE UPDATE ON answers BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER answers_no_delete BEFORE DELETE ON answers BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER failures_no_update BEFORE UPDATE ON failures BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER failures_no_delete BEFORE DELETE ON failures BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER approvals_no_update BEFORE UPDATE ON approvals BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER approvals_no_delete BEFORE DELETE ON approvals BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
COMMIT;
"""
V1_EXTRA_TRIGGERS = (
    "CREATE TRIGGER IF NOT EXISTS schema_meta_no_replace BEFORE INSERT ON schema_meta WHEN EXISTS (SELECT 1 FROM schema_meta WHERE key=NEW.key) BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS runs_no_replace BEFORE INSERT ON runs WHEN EXISTS (SELECT 1 FROM runs WHERE id=NEW.id) BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS answers_no_replace BEFORE INSERT ON answers WHEN EXISTS (SELECT 1 FROM answers WHERE id=NEW.id) BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS failures_no_replace BEFORE INSERT ON failures WHEN EXISTS (SELECT 1 FROM failures WHERE id=NEW.id) BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS approvals_no_replace BEFORE INSERT ON approvals WHEN EXISTS (SELECT 1 FROM approvals WHERE id=NEW.id) BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS schema_meta_no_update BEFORE UPDATE ON schema_meta BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS schema_meta_no_delete BEFORE DELETE ON schema_meta BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END",
)


def _trigger_count(connection):
    return connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]


def _snapshot(connection):
    return {table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table}")]
            for table in ("schema_meta", "runs", "answers", "failures", "approvals")}


def _make_v1(path):
    with sqlite3.connect(path) as connection:
        connection.executescript(V1_SCHEMA)
        for statement in V1_EXTRA_TRIGGERS:
            connection.execute(statement)
        connection.execute("INSERT INTO runs VALUES (1, 'later', 'doctor', '9003.001', "
                           "'invented', 'v1', 'pb-invented', 'invented-model', 1, 'sha-invented')")
        connection.execute("INSERT INTO answers VALUES (1, 1, 'later', 'READY', 'stop', 12, 1, 'ok')")
        connection.execute("INSERT INTO failures VALUES (1, 1, 'later', 'invented', 'invented failure')")
        connection.execute("INSERT INTO approvals VALUES (1, 1, 'later', 'invented', 'approved', 'test actor')")
        assert connection.execute("SELECT value FROM schema_meta").fetchone()[0] == '1'
        assert _trigger_count(connection) == 15
        return _snapshot(connection)


def _upgraded_rows(connection):
    rows = _snapshot(connection)
    rows['schema_meta'] = [('schema_version', '1')]
    rows['answers'] = [row[:-1] for row in rows['answers']]
    return rows


def test_upgrade_v1(tmp_path, capsys):
    path = tmp_path / 'runlog.sqlite'
    before = _make_v1(path)
    for _ in range(2):
        with open_db(path) as log:
            count = _trigger_count(log.connection)
            with capsys.disabled():
                print(f'triggers={count}')
            assert count == 21
            assert log.schema_version == 2
            assert _upgraded_rows(log.connection) == before
            assert log.connection.execute('SELECT prompt_eval_cached_count FROM answers').fetchone()[0] is None
            assert log.connection.execute('SELECT COUNT(*) FROM coverage').fetchone()[0] == 0
            assert log.connection.execute('SELECT COUNT(*) FROM gates').fetchone()[0] == 0
    with capsys.disabled():
        print('upgrade_v1=1')


def test_upgrade_atomic(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'runlog.sqlite'
    before = _make_v1(path)
    with monkeypatch.context() as patch:
        steps = runlog.UPGRADE_V1_V2
        patch.setattr(runlog, 'UPGRADE_V1_V2', steps[:2] + ('INSERT INTO no_such_table VALUES (1)',) + steps[2:])
        with pytest.raises(sqlite3.Error, match='no such table: no_such_table'):
            open_db(path)
    with sqlite3.connect(path) as connection:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        columns = {row[1] for row in connection.execute('PRAGMA table_info(answers)')}
        atomic = (_snapshot(connection) == before and _trigger_count(connection) == 15
                  and not {'coverage', 'gates'} & names and 'prompt_eval_cached_count' not in columns)
        with capsys.disabled():
            print(f'upgrade_atomic={int(atomic)}')
        assert atomic, 'upgrade_atomic=0'
    with open_db(path) as log:
        assert log.schema_version == 2
        assert _trigger_count(log.connection) == 21
        assert _upgraded_rows(log.connection) == before


def test_coverage_latest_and_open_items(tmp_path, monkeypatch, capsys):
    with open_db(tmp_path / 'runlog.sqlite') as log:
        first = _start(log, matter='9003.001')
        second = _start(log, matter='9003.001')
        for page in ('probe/001', 'probe/002', 'probe/003'):
            monkeypatch.setattr(runlog, '_now', lambda: '2026-10-28T00:00:00Z')
            log.record_coverage(first, matter='9003.001', page_id=page, card='invented',
                                status='read', reason='first read')
        monkeypatch.setattr(runlog, '_now', lambda: '2026-10-27T00:00:00Z')
        log.record_coverage(second, matter='9003.001', page_id='probe/001', card='invented',
                            status='failed', reason='gate.quotes: invented failure')
        log.record_coverage(second, matter='9003.001', page_id='probe/002', card='invented',
                            status='uncited', reason='no fact or flag cites probe/002')
        expected = {('probe/001', 'invented'): ('failed', 'gate.quotes: invented failure', second),
                    ('probe/002', 'invented'): ('uncited', 'no fact or flag cites probe/002', second),
                    ('probe/003', 'invented'): ('read', 'first read', first)}
        latest = log.coverage('9003.001') == expected
        with capsys.disabled():
            print(f'coverage_latest={int(latest)}')
        assert latest, 'coverage_latest=0'
        opened = log.open_items('9003.001')
        with capsys.disabled():
            print(f'open_items={len(opened)} of 3')
        assert opened == {key: value for key, value in expected.items() if value[0] != 'read'}
        assert log.coverage('9003.002') == {}
        assert log.open_items('9003.002') == {}
        log.record_coverage(second, matter='9003.002', page_id='probe/001', card='invented',
                            status='read', reason='another matter')
        log.record_coverage(second, matter='9003.001', page_id='probe/001', card='other-card',
                            status='read', reason='another card')
        assert log.coverage('9003.001') == {**expected, ('probe/001', 'other-card'): ('read', 'another card', second)}
        assert log.open_items('9003.001') == opened


def test_coverage_statuses_and_gate_fields(tmp_path, capsys):
    with open_db(tmp_path / 'runlog.sqlite') as log:
        run = _start(log)
        for status in ('read', 'uncited', 'failed'):
            log.record_coverage(run, matter='9003.001', page_id='probe/001', card='invented',
                                status=status, reason=f'invented {status}')
        with pytest.raises(sqlite3.IntegrityError, match='CHECK constraint failed'):
            log.record_coverage(run, matter='9003.001', page_id='probe/001', card='invented',
                                status='done', reason='invented invalid')
        assert [row[0] for row in log.connection.execute('SELECT status FROM coverage ORDER BY id')] == [
            'read', 'uncited', 'failed']
        for attempt, verdict in enumerate(('pass', 'fail', 'repaired'), 1):
            log.record_gate(run, attempt=attempt, gate='repair', verdict=verdict, message=f'invented {verdict}')
        rows = [dict(row) for row in log.connection.execute('SELECT * FROM gates ORDER BY id')]
        for attempt, row in enumerate(rows, 1):
            assert row.pop('at').endswith('Z')
            verdict = ('pass', 'fail', 'repaired')[attempt - 1]
            assert row == dict(id=attempt, run_id=run, attempt=attempt, gate='repair',
                               verdict=verdict, message=f'invented {verdict}')
        with pytest.raises(sqlite3.IntegrityError, match='CHECK constraint failed'):
            log.record_gate(run, attempt=1, gate='repair', verdict='done', message='invented invalid')
        with pytest.raises(sqlite3.IntegrityError, match='FOREIGN KEY constraint failed'):
            log.record_gate(run + 1, attempt=1, gate='repair', verdict='pass', message='invented orphan')
        with pytest.raises(sqlite3.IntegrityError, match='FOREIGN KEY constraint failed'):
            log.record_coverage(run + 1, matter='9003.001', page_id='probe/001', card='invented',
                                status='read', reason='invented orphan')
        log.record_answer(run, raw_answer='invented', status='ok', prompt_eval_cached_count=7)
        assert log.connection.execute('SELECT prompt_eval_cached_count FROM answers').fetchone()[0] == 7
    with capsys.disabled():
        print('coverage_statuses=3 of 3')


def test_version_3_refused(tmp_path, capsys):
    path = tmp_path / 'runlog.sqlite'
    with sqlite3.connect(path) as connection:
        connection.executescript(runlog.SCHEMA.replace("('schema_version', '2')", "('schema_version', '3')"))
    with pytest.raises(sqlite3.DatabaseError, match='unsupported runlog schema version 3'):
        open_db(path)
    with capsys.disabled():
        print('version_3_refused=1')
