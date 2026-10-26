"""Exercise the wrapper without relying on a project interpreter or model."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
CAP = 52428800


def test_toolchain_outside_repo(tmp_path):
    env = os.environ.copy()
    env["CASEFILE_TOOLCHAIN"] = str(tmp_path)
    probe = """
import os
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
names = ("UV_PROJECT_ENVIRONMENT", "UV_PYTHON_INSTALL_DIR", "UV_CACHE_DIR")
inside = sum(Path(os.environ[name]).resolve().is_relative_to(root) for name in names)
print(f"toolchain_inside_repo={inside}")
"""
    result = subprocess.run(
        [str(ROOT / "scripts/run.sh"), sys.executable, "-c", probe, str(ROOT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    print(result.stdout, end="")
    assert result.stdout == "toolchain_inside_repo=0\n", result.stdout


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


def test_cap_terminates_sleeping_child(tmp_path):
    import signal
    import time

    pidfile = tmp_path / "invented-child.pid"
    child = ("import os,sys,time; "
             "open(sys.argv[1], 'w').write(str(os.getpid())); "
             f"sys.stdout.buffer.write(b'a' * {CAP + 1}); "
             "sys.stdout.buffer.flush(); time.sleep(30)")
    started = time.monotonic()
    try:
        try:
            result = subprocess.run([str(ROOT / "scripts/run.sh"), sys.executable,
                                     "-c", child, str(pidfile)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=5)
        except subprocess.TimeoutExpired:
            pytest.fail("output cap did not terminate sleeping child within 5 seconds")
        assert result.returncode == 97, result.stderr
        assert time.monotonic() - started < 5
        with pytest.raises(ProcessLookupError):
            os.kill(int(pidfile.read_text()), 0)
    finally:
        if pidfile.exists():
            try:
                os.kill(int(pidfile.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
