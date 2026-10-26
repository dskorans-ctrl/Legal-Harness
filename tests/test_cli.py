"""Check the installed console entry point."""

import subprocess


def test_version():
    result = subprocess.run(
        ["casefile", "version"], capture_output=True, text=True, timeout=30
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, "casefile 0.1.0\n", "")


def test_no_args():
    result = subprocess.run(["casefile"], capture_output=True, text=True, timeout=30)
    assert (result.returncode, result.stdout) == (2, "")
    assert "usage: casefile" in result.stderr
