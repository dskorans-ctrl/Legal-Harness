"""Exercise the wrapper without relying on a project interpreter or model."""

import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
CAP = 52428800


@pytest.mark.parametrize(
    ("command", "tmpdir", "expected_status", "expected_bytes"),
    [
        ('head -c 52428801 /dev/zero | tr "\\0" a', None, 97, CAP),
        ("exit 3", None, 3, 0),
        ('head -c 52428800 /dev/zero | tr "\\0" a', None, 0, CAP),
        ("true", "/nonexistent/dir", 98, 0),
        ('head -c 52428801 /dev/zero | tr "\\0" a >&2', None, 97, CAP),
        ('kill -KILL "$$"', None, 137, 0),
    ],
    ids=["overflow", "child-exit", "exact-cap", "capture-failure", "stderr", "sigkill"],
)
def test_run_sh(command, tmpdir, expected_status, expected_bytes):
    env = os.environ.copy()
    if tmpdir is not None:
        env["TMPDIR"] = tmpdir
    result = subprocess.run(
        [str(ROOT / "scripts/run.sh"), "bash", "-c", command],
        cwd=ROOT,
        env=env,
        capture_output=True,
        timeout=30,
    )
    assert (result.returncode, len(result.stdout)) == (expected_status, expected_bytes)
    if expected_bytes:
        assert result.stdout == b"a" * expected_bytes
    if expected_status == 97:
        assert b"output cap 52428800 bytes hit" in result.stderr
    elif expected_status == 98:
        assert b"cannot create capture dir" in result.stderr
