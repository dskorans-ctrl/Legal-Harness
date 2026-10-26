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


def test_missing_command_relays_127():
    command = "invented-casefile-command-that-does-not-exist"
    result = subprocess.run([str(ROOT / "scripts/run.sh"), command], cwd=ROOT,
                            capture_output=True, timeout=30)
    assert (result.returncode, result.stdout) == (127, b"")
    assert f"run.sh: command not found: {command}".encode() in result.stderr


def test_nonexecutable_command_relays_126(tmp_path):
    command = tmp_path / "invented-nonexecutable"
    command.write_text("#!/bin/sh\nexit 0\n")
    command.chmod(0o600)
    result = subprocess.run([str(ROOT / "scripts/run.sh"), str(command)], cwd=ROOT,
                            capture_output=True, timeout=30)
    assert (result.returncode, result.stdout) == (126, b"")


def test_python_capture_open_failure(tmp_path):
    directory = tmp_path / "invented-capture"
    (directory / "out").mkdir(parents=True)
    result = subprocess.run([str(ROOT / "scripts/run.sh"), sys.executable,
                             str(ROOT / "scripts/run_capture.py"), "128", str(directory),
                             sys.executable, "-c", "print('invented')"],
                            cwd=tmp_path, capture_output=True, timeout=30)
    assert result.returncode == 98
    assert b"capture stage failed" in result.stdout + result.stderr


@pytest.mark.parametrize("kind", ["missing-argument", "empty", "nonexistent", "file"])
def test_capture_directory_required(tmp_path, kind):
    sentinel = tmp_path / "invented-file"
    sentinel.write_text("preserve invented bytes\n")
    arguments = ["128"]
    if kind != "missing-argument":
        directory = {"empty": "", "nonexistent": str(tmp_path / "absent"),
                     "file": str(sentinel)}[kind]
        arguments += [directory, sys.executable, "-c", "print('invented')"]
    result = subprocess.run([str(ROOT / "scripts/run.sh"), sys.executable,
                             str(ROOT / "scripts/run_capture.py"), *arguments],
                            cwd=tmp_path, capture_output=True, timeout=30)
    assert result.returncode == 98
    assert b"capture directory" in result.stdout + result.stderr
    assert not (tmp_path / "out").exists()
    assert sentinel.read_bytes() == b"preserve invented bytes\n"


@pytest.mark.parametrize("alias", ["literal", "case", "symlink"])
def test_toolchain_inside_checkout_refused(tmp_path, alias):
    base = ROOT
    if alias == "case":
        base = ROOT.with_name(ROOT.name.swapcase())
        assert os.path.samefile(base, ROOT)
    elif alias == "symlink":
        base = tmp_path / "invented-checkout-alias"
        base.symlink_to(ROOT, target_is_directory=True)
    env = dict(os.environ, CASEFILE_TOOLCHAIN=str(base / "invented-toolchain"))
    result = subprocess.run([str(ROOT / "scripts/run.sh"), "true"], cwd=ROOT,
                            env=env, capture_output=True, timeout=30)
    assert (result.returncode, result.stdout) == (95, b"")
    assert result.stderr == b"run.sh: toolchain must be outside the checkout; exit 95\n"
    assert not (ROOT / "invented-toolchain").exists()


@pytest.mark.parametrize("suffix", ["", "invented-toolchain"])
def test_toolchain_symlink_case_swapped_subdirectory_refused(tmp_path, suffix):
    target = ROOT.with_name(ROOT.name.swapcase()) / "tests" / "fixtures"
    assert os.path.samefile(target, ROOT / "tests" / "fixtures")
    alias = tmp_path / "invented-toolchain-alias"
    alias.symlink_to(target, target_is_directory=True)
    env = dict(os.environ, CASEFILE_TOOLCHAIN=str(alias / suffix))
    result = subprocess.run([str(ROOT / "scripts/run.sh"), "true"], cwd=ROOT,
                            env=env, capture_output=True, timeout=30)
    assert (result.returncode, result.stdout) == (95, b"")
    assert result.stderr == b"run.sh: toolchain must be outside the checkout; exit 95\n"
    assert not (target / suffix / ROOT.name).exists()


@pytest.mark.parametrize("size", [4096, 200000], ids=["short-write", "write-error"])
def test_capture_write_failure_exits_98(tmp_path, size):
    directory = tmp_path / "invented-capture"
    directory.mkdir()
    # Limit only the inner capture process so the outer run.sh cannot mask its verdict.
    launcher = """
import resource
import runpy
import signal
import sys

resource.setrlimit(resource.RLIMIT_FSIZE, (1024, 1024))
signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
    child = f"import sys; sys.stdout.buffer.write(b'x' * {size})"
    result = subprocess.run([str(ROOT / "scripts/run.sh"), sys.executable, "-c", launcher,
                             str(ROOT / "scripts/run_capture.py"), str(CAP), str(directory),
                             sys.executable, "-c", child],
                            cwd=tmp_path, capture_output=True, timeout=30)
    assert result.returncode == 98, result.stdout + result.stderr
    assert b"run.sh: capture stage failed:" in result.stdout + result.stderr
    assert b"exit 98" in result.stdout + result.stderr
    assert not directory.exists()


def test_capture_completes_short_writes(tmp_path, monkeypatch, capfdbinary):
    import runpy

    main = runpy.run_path(str(ROOT / "scripts/run_capture.py"))["main"]
    directory = tmp_path / "invented-short-capture"
    directory.mkdir()
    payload = b"invented capture bytes" * 200

    class ShortCapture:
        def __init__(self):
            self.data = bytearray()
            self.calls = 0
            self.closed = False

        def write(self, chunk):
            count = min(7, len(chunk))
            self.data.extend(chunk[:count])
            self.calls += 1
            return count

        def close(self):
            self.closed = True

    capture = ShortCapture()
    original_open = Path.open

    def open_capture(path, *args, **kwargs):
        if path == directory / "out":
            return capture
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", open_capture)
    monkeypatch.setattr(sys, "argv", [str(ROOT / "scripts/run_capture.py"), str(CAP), str(directory),
                                     str(ROOT / "scripts/run.sh"), sys.executable, "-c",
                                     f"import sys; sys.stdout.buffer.write({payload!r})"])
    assert main() == 0
    assert capture.data == payload
    assert capture.calls > 1
    assert capture.closed
    output = capfdbinary.readouterr()
    assert (output.out, output.err) == (payload, b"")
    assert not directory.exists()
