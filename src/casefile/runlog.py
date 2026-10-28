"""Durable, append-only SQLite run history, schema version 2."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3


SCHEMA = """
BEGIN;
CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO schema_meta VALUES ('schema_version', '2');
CREATE TABLE runs(id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL,
  job TEXT NOT NULL, matter TEXT, card TEXT NOT NULL, card_version TEXT NOT NULL,
  playbook_version TEXT NOT NULL, model TEXT NOT NULL, pages_in INTEGER NOT NULL,
  prompt_sha256 TEXT NOT NULL);
CREATE TABLE answers(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  finished_at TEXT NOT NULL, raw_answer TEXT NOT NULL, done_reason TEXT,
  prompt_eval_count INTEGER, eval_count INTEGER, prompt_eval_cached_count INTEGER,
  status TEXT NOT NULL CHECK(status IN ('ok','failed')));
CREATE TABLE failures(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  at TEXT NOT NULL, gate TEXT NOT NULL, message TEXT NOT NULL);
CREATE TABLE approvals(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  at TEXT NOT NULL, item TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('approved','rejected','edited')), by_whom TEXT NOT NULL);
CREATE TABLE coverage(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  matter TEXT NOT NULL, page_id TEXT NOT NULL, card TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('read','uncited','failed')), reason TEXT NOT NULL, at TEXT NOT NULL);
CREATE TABLE gates(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  attempt INTEGER NOT NULL, gate TEXT NOT NULL,
  verdict TEXT NOT NULL CHECK(verdict IN ('pass','fail','repaired')), message TEXT NOT NULL, at TEXT NOT NULL);
CREATE TRIGGER runs_no_update BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER runs_no_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER answers_no_update BEFORE UPDATE ON answers BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER answers_no_delete BEFORE DELETE ON answers BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER failures_no_update BEFORE UPDATE ON failures BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER failures_no_delete BEFORE DELETE ON failures BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER approvals_no_update BEFORE UPDATE ON approvals BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER approvals_no_delete BEFORE DELETE ON approvals BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER coverage_no_update BEFORE UPDATE ON coverage BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER coverage_no_delete BEFORE DELETE ON coverage BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER gates_no_update BEFORE UPDATE ON gates BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
CREATE TRIGGER gates_no_delete BEFORE DELETE ON gates BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;
COMMIT;
"""


UPGRADE_V1_V2 = (
    'DROP TRIGGER schema_meta_no_update',
    """CREATE TABLE coverage(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  matter TEXT NOT NULL, page_id TEXT NOT NULL, card TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('read','uncited','failed')), reason TEXT NOT NULL, at TEXT NOT NULL);""",
    """CREATE TABLE gates(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  attempt INTEGER NOT NULL, gate TEXT NOT NULL,
  verdict TEXT NOT NULL CHECK(verdict IN ('pass','fail','repaired')), message TEXT NOT NULL, at TEXT NOT NULL);""",
    "CREATE TRIGGER coverage_no_update BEFORE UPDATE ON coverage BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;",
    "CREATE TRIGGER coverage_no_delete BEFORE DELETE ON coverage BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;",
    "CREATE TRIGGER gates_no_update BEFORE UPDATE ON gates BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;",
    "CREATE TRIGGER gates_no_delete BEFORE DELETE ON gates BEGIN SELECT RAISE(ABORT, 'runlog is append-only'); END;",
    'ALTER TABLE answers ADD COLUMN prompt_eval_cached_count INTEGER',
    "UPDATE schema_meta SET value='2' WHERE key='schema_version'",
)


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
                      eval_count: int | None = None,
                      prompt_eval_cached_count: int | None = None) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO answers(run_id, finished_at, raw_answer, done_reason, "
                "prompt_eval_count, eval_count, status, prompt_eval_cached_count) VALUES (?,?,?,?,?,?,?,?)",
                (run_id, _now(), raw_answer, done_reason, prompt_eval_count, eval_count, status,
                 prompt_eval_cached_count),
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

    def record_gate(self, run_id: int, *, attempt: int, gate: str,
                    verdict: str, message: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO gates(run_id, attempt, gate, verdict, message, at) VALUES (?,?,?,?,?,?)",
                (run_id, attempt, gate, verdict, message, _now()),
            )

    def record_coverage(self, run_id: int, *, matter: str, page_id: str, card: str,
                        status: str, reason: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO coverage(run_id, matter, page_id, card, status, reason, at) "
                "VALUES (?,?,?,?,?,?,?)",
                (run_id, matter, page_id, card, status, reason, _now()),
            )

    def coverage(self, matter: str, *, job: str) -> dict[tuple[str, str], tuple[str, str, int]]:
        """Return the latest disposition for each page and card within one job."""
        rows = self.connection.execute(
            "SELECT c.page_id, c.card, c.status, c.reason, c.run_id FROM coverage c "
            "JOIN runs r ON r.id=c.run_id WHERE c.matter=? AND r.job=? ORDER BY c.id",
            (matter, job),
        )
        return {(row["page_id"], row["card"]): (row["status"], row["reason"], row["run_id"])
                for row in rows}

    def open_items(self, matter: str, *, job: str) -> dict[tuple[str, str], tuple[str, str, int]]:
        return {pair: value for pair, value in self.coverage(matter, job=job).items() if value[0] != "read"}

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
        if log.schema_version == 1:
            connection.execute("BEGIN")
            try:
                for statement in UPGRADE_V1_V2:
                    connection.execute(statement)
                connection.commit()
            except BaseException:
                connection.rollback()
                raise
        if log.schema_version != 2:
            raise sqlite3.DatabaseError(f"unsupported runlog schema version {log.schema_version}")
        with connection:
            for table in ("schema_meta", "runs", "answers", "failures", "approvals", "coverage", "gates"):
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
