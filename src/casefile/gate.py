"""Run all five measured rows and return the failed-row count."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

from . import playbook, privacy, prose, rules


@dataclass(frozen=True)
class Row:
    name: str
    check: object


def pytest_row(root):
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, check=False)
    return result.returncode == 0, f"exit={result.returncode}"


def privacy_row(root):
    offenders = privacy.scan(root)
    for path in offenders:
        print(f"privacy offender {path}")
    return not offenders, f"offenders={len(offenders)} scanned={len(privacy.paths(root))}"


def rules_selftest_row(root):
    loaded = rules.load(root / "playbook" / "rules.toml")
    misses = false_hits = 0
    for rule in loaded.rules:
        bad = loaded.check(rule.bad, stamped=True, unit=rule.unit)
        good = loaded.check(rule.good, stamped=True, unit=rule.unit)
        misses += not any(f.rule_id == rule.id for f in bad)
        false_hits += any(f.rule_id == rule.id for f in good)
    return misses == 0 and false_hits == 0, f"misses={misses} false_hits={false_hits}"


def playbook_row(root):
    try:
        book = playbook.load(root / "playbook")
    except playbook.PlaybookError as exc:
        return False, f"invalid=1 unmarked=0 version=unavailable {exc}"
    unmarked = sum(not entry.sample or not entry.rule.startswith("SAMPLE:")
                   for entry in book.entries if isinstance(entry, playbook.Entry))
    return unmarked == 0, f"invalid=0 unmarked={unmarked} version={book.version}"


def prose_row(root):
    hits = prose.scan(root)
    for path, number in hits:
        print(f"prose {path}:{number}")
    return not hits, f"dashes={len(hits)} files={len(prose.files(root))}"


ROWS_WITHOUT_PYTEST = (Row("privacy", privacy_row), Row("rules_selftest", rules_selftest_row),
                       Row("playbook", playbook_row), Row("prose", prose_row))
ROWS = (Row("pytest", pytest_row), *ROWS_WITHOUT_PYTEST)


def main(rows=None, root=None) -> int:
    root = Path(__file__).resolve().parents[2] if root is None else Path(root)
    rows = ROWS if rows is None else rows
    failed = 0
    for row in rows:
        try:
            ok, number = row.check(root)
        except Exception as exc:
            ok, number = False, f"error={exc}"
        failed += not ok
        number = " ".join(str(number).splitlines())
        print(f"gate {row.name} {'PASS' if ok else 'FAIL'} {number}")
    print(failed)
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
