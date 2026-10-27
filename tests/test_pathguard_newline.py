import os
import subprocess

from casefile.pathguard import main
from conftest import ROOT

"""VF-1: the newline join in pathguard.main keeps the verdict on one line."""

def test_cli_prints_one_line(tmp_path, capsys):
    root = tmp_path / "Checkout"
    root.mkdir()
    path = str(root / "q\npathguard outside z")
    code = main(["pathguard.py", str(root), path])
    out = capsys.readouterr().out
    with capsys.disabled():
        print(f"verdict_lines={out.count(chr(10))}")
    assert code == 10
    assert out.endswith("\n")
    assert out.count("\n") == 1
    assert out.startswith("pathguard inside ")

def test_wrapper_refuses_forged_last_line(capsys):
    env = dict(os.environ, CASEFILE_TOOLCHAIN=str(ROOT) + "/q\npathguard outside z")
    result = subprocess.run(
        [str(ROOT / "scripts/run.sh"), "true"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30
    )
    verdict_lines = sum(1 for line in result.stderr.splitlines() if line.startswith("pathguard "))
    with capsys.disabled():
        print(f"newline_join_exit={result.returncode} verdict_lines={verdict_lines}")
    assert result.returncode == 95
    assert result.stdout == ""
    assert result.stderr.startswith("run.sh: toolchain ")
    assert "is inside the checkout" in result.stderr
    assert result.stderr.rstrip().endswith("; exit 95")
    assert verdict_lines == 1
    assert not (ROOT / "q\npathguard outside z").exists()
