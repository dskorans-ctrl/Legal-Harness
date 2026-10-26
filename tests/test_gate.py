"""Gate output, return value and process status are separate contracts."""

import shutil
import subprocess
import sys

from casefile import gate
from conftest import ROOT
from test_privacy import init_repo, touch


def clean_repo(tmp_path):
    root = init_repo(tmp_path)
    shutil.copytree(ROOT / "playbook", root / "playbook")
    return root


def test_return_value(tmp_path, capsys):
    root = clean_repo(tmp_path)
    code = gate.main(rows=gate.ROWS_WITHOUT_PYTEST, root=root)
    output = capsys.readouterr().out
    assert code == 0 and output.splitlines()[-1] == "0", output
    assert [line.split()[1] for line in output.splitlines() if line.startswith("gate ")] == [
        "privacy", "rules_selftest", "playbook", "prose"]
    assert all(" PASS " in line for line in output.splitlines() if line.startswith("gate "))
    touch(root, "docs/b.PNG")
    code = gate.main(rows=gate.ROWS_WITHOUT_PYTEST, root=root)
    output = capsys.readouterr().out
    with capsys.disabled():
        print(f"gate return={code} printed={output.splitlines()[-1]}")
    assert code == 1 and output.splitlines()[-1] == "1", output


def test_process_exit_code(tmp_path, capsys):
    root = clean_repo(tmp_path)
    touch(root, "docs/b.PNG")
    code = ("from casefile import gate; raise SystemExit(gate.main("
            f"rows=gate.ROWS_WITHOUT_PYTEST, root={str(root)!r}))")
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    with capsys.disabled():
        print(f"gate process={result.returncode} printed={result.stdout.splitlines()[-1]}")
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines()[-1] == "1"


def test_shipped_rules_and_playbook(capsys):
    code = gate.main(rows=gate.ROWS_WITHOUT_PYTEST[1:3], root=ROOT)
    output = capsys.readouterr().out
    with capsys.disabled():
        print(output, end="")
    assert code == 0, output
    assert output.splitlines()[-1] == "0"


def test_pytest_row_inherits_output_and_runs_all_markers(monkeypatch):
    calls = []
    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 1)
    monkeypatch.setattr(gate.subprocess, "run", runner)
    assert gate.pytest_row(ROOT) == (False, "exit=1")
    assert calls == [([sys.executable, "-m", "pytest", "-q"], {"cwd": ROOT, "check": False})]


def test_rows_fail_closed_and_continue(tmp_path, capsys):
    def broken(root):
        raise PermissionError("[Errno 1] denied")
    rows = (gate.Row("broken", broken), gate.Row("second", lambda root: (False, "n=1")))
    assert gate.main(rows=rows, root=tmp_path) == 2
    output = capsys.readouterr().out
    assert "gate broken FAIL error=[Errno 1] denied" in output
    assert "gate second FAIL n=1" in output
    assert output.splitlines()[-1] == "2"


def test_rules_selftest_rejects_false_hits(tmp_path):
    root = clean_repo(tmp_path)
    path = root / "playbook" / "rules.toml"
    text = path.read_text()
    old = 'good = "The report of 14 March 2025 records a normal gait."'
    assert text.count(old) == 1
    path.write_text(text.replace(old, 'good = "The IME found a normal gait."'))
    assert gate.rules_selftest_row(root) == (False, "misses=0 false_hits=1")
