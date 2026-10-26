"""Durable, append-only SQLite run history, schema version 1."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3


SCHEMA = """
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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class RunLog:
    """Each API write commits independently so a start survives a later failure."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    @property
    def schema_version(self) -> int:
        row = self.connection.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("runlog schema_version is missing")
        return int(row[0])

    def start_run(self, *, job: str, card: str, card_version: str,
                  playbook_version: str, model: str, pages_in: int,
                  prompt_sha256: str, matter: str | None = None) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO runs(started_at, job, matter, card, card_version, "
                "playbook_version, model, pages_in, prompt_sha256) VALUES (?,?,?,?,?,?,?,?,?)",
                (_now(), job, matter, card, card_version, playbook_version, model, pages_in, prompt_sha256),
            )
        return cursor.lastrowid

    def record_answer(self, run_id: int, *, raw_answer: str, status: str,
                      done_reason: str | None = None, prompt_eval_count: int | None = None,
                      eval_count: int | None = None) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO answers(run_id, finished_at, raw_answer, done_reason, "
                "prompt_eval_count, eval_count, status) VALUES (?,?,?,?,?,?,?)",
                (run_id, _now(), raw_answer, done_reason, prompt_eval_count, eval_count, status),
            )

    def record_failure(self, run_id: int, gate: str, message: str) -> None:
        with self.connection:
            self.connection.execute("INSERT INTO failures(run_id, at, gate, message) VALUES (?,?,?,?)",
                                    (run_id, _now(), gate, message))

    def record_approval(self, run_id: int, *, item: str, decision: str, by_whom: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO approvals(run_id, at, item, decision, by_whom) VALUES (?,?,?,?,?)",
                (run_id, _now(), item, decision, by_whom),
            )

    def count_test_jobs(self) -> int:
        return self.connection.execute(
            "SELECT COUNT(*) FROM runs JOIN answers ON answers.run_id=runs.id "
            "WHERE runs.job='doctor' AND runs.card='doctor.warmup' AND answers.status='ok'"
        ).fetchone()[0]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def open_db(path: str | Path) -> RunLog:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        if connection.execute("SELECT 1 FROM sqlite_master WHERE name='schema_meta'").fetchone() is None:
            connection.executescript(SCHEMA)
        log = RunLog(connection)
        if log.schema_version != 1:
            raise sqlite3.DatabaseError(f"unsupported runlog schema version {log.schema_version}")
        with connection:
            for table in ("schema_meta", "runs", "answers", "failures", "approvals"):
                key = "key" if table == "schema_meta" else "id"
                connection.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {table}_no_replace BEFORE INSERT ON {table} "
                    f"WHEN EXISTS (SELECT 1 FROM {table} WHERE {key}=NEW.{key}) "
                    "BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END")
            for operation in ("UPDATE", "DELETE"):
                connection.execute(
                    f"CREATE TRIGGER IF NOT EXISTS schema_meta_no_{operation.lower()} "
                    f"BEFORE {operation} ON schema_meta "
                    "BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END")
        return log
    except BaseException:
        connection.close()
        raise
