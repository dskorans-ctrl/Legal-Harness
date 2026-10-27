"""Re-brief fix cycle 1 (RX-1 to RX-8): each test fails on the defect it names."""

import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time
import types

import pytest

from casefile.config import ConfigError, load
from casefile.pathguard import classify
from conftest import ROOT, write_config

CAPTURE = ROOT / "scripts" / "run_capture.py"
RUN_SH = ROOT / "scripts" / "run.sh"
CAP = 52428800


def run_sh(*argv, timeout=30, **kwargs):
    return subprocess.run([str(RUN_SH), *argv], capture_output=True, timeout=timeout, **kwargs)


def test_stopped_then_continued_child_is_not_an_exit():
    # RX-1: a stop and continue notification must not start the 2 s grace timer.
    command = "(sleep 0.3; kill -CONT $$) & kill -STOP $$; sleep 4; exit 3"
    started = time.monotonic()
    result = run_sh("bash", "-c", command, cwd=ROOT)
    secs = time.monotonic() - started
    print(f"\nstop_continue_exit={result.returncode} secs={secs:.1f}")
    assert result.returncode == 3, result.stderr
    assert secs >= 3.5 and b"pipe stayed open" not in result.stderr


def test_capture_uses_the_guard_interpreter(tmp_path):
    # RX-2: a venv python3 shim that exits 0 must not stand in for the capture stage.
    toolchain = tmp_path / "tc"
    shim = toolchain / ROOT.name / "venv" / "bin" / "python3"
    shim.parent.mkdir(parents=True)
    shim.write_text("#!/bin/sh\nexit 0\n")
    shim.chmod(0o755)
    result = run_sh("false", cwd=tmp_path, env=dict(os.environ, CASEFILE_TOOLCHAIN=str(toolchain),
                                                    TMPDIR=str(tmp_path)))
    assert result.returncode == 1, result
    assert list(tmp_path.glob("casefile-run.*")) == [], "capture directory left behind"


class FakeClock:
    """Each read moves 0.6 s on, so two reads in one pass straddle the 2 s grace deadline."""

    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        self.now += 0.6
        return self.now


def load_main(**replaced):
    # run_path returns a copy of the module globals, so build main afresh over a patched copy.
    namespace = runpy.run_path(str(CAPTURE))
    namespace.update(replaced)
    return types.FunctionType(namespace["main"].__code__, namespace)


def test_remaining_time_never_negative(tmp_path, monkeypatch, capfd):
    # RX-3: the clock is read once per pass and the wait is clamped at 0.
    # Not red-able from outside by timing alone; the fake clock forces the straddle.
    directory = tmp_path / "invented-capture"
    directory.mkdir()
    main = load_main(time=types.SimpleNamespace(monotonic=FakeClock().monotonic))
    monkeypatch.setattr(sys, "argv", ["run_capture.py", str(CAP), str(directory),
                                      "bash", "-c", "sleep 30 & exit 3"])
    assert main() == 3
    assert "ValueError" not in capfd.readouterr().err


class KillpgFails:
    """The real os, but killpg kills the group and then reports EPERM (zombie-only group)."""

    def __getattr__(self, name):
        return getattr(os, name)

    def killpg(self, pgid, sig):
        os.killpg(pgid, sig)
        raise PermissionError(1, "Operation not permitted")


def test_cleanup_killpg_error_keeps_exit_98(tmp_path, monkeypatch):
    # RX-4: the finally-block killpg tolerates OSError like the other two sites.
    directory = tmp_path / "invented-capture"
    directory.mkdir()

    class FailingCapture:
        def write(self, chunk):
            raise OSError("invented write failure")

        def close(self):
            pass

    original_open = Path.open
    monkeypatch.setattr(Path, "open", lambda p, *a, **k: FailingCapture()
                        if p == directory / "out" else original_open(p, *a, **k))
    main = load_main(os=KillpgFails())
    monkeypatch.setattr(sys, "argv", ["run_capture.py", str(CAP), str(directory),
                                      "bash", "-c", "echo invented; sleep 30"])
    assert main() == 98
    assert not directory.exists()


def test_pipe_above_descriptor_1024(tmp_path):
    # RX-5: select.select refuses descriptors at or above FD_SETSIZE; the wrapper must not.
    directory = tmp_path / "invented-capture"
    directory.mkdir()
    launcher = """
import os, resource, runpy, sys
resource.setrlimit(resource.RLIMIT_NOFILE, (4096, resource.getrlimit(resource.RLIMIT_NOFILE)[1]))
held = []
while True:
    fd = os.dup(0)
    held.append(fd)
    if fd > 1100:
        break
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
    result = subprocess.run([sys.executable, "-c", launcher, str(CAPTURE), str(CAP), str(directory),
                             "echo", "invented"], capture_output=True, timeout=30)
    assert (result.returncode, result.stdout) == (0, b"invented\n"), result.stderr
    assert not directory.exists()


def test_realpath_recursion_is_cannot_verify(tmp_path, monkeypatch):
    # RX-6: a RecursionError from realpath is a verdict, never a traceback.
    root = tmp_path / "Checkout"
    root.mkdir()

    def too_deep(path, *args, **kwargs):
        raise RecursionError("maximum recursion depth exceeded")

    monkeypatch.setattr(os.path, "realpath", too_deep)
    verdict, detail = classify(str(tmp_path / "elsewhere"), root)
    assert verdict == "cannot-verify", (verdict, detail)


def test_long_symlink_chain_is_a_verdict(tmp_path):
    # RX-6 end to end: about 2000 acyclic links; any verdict is fine, a traceback is not.
    root = tmp_path / "Checkout"
    root.mkdir()
    previous = root
    for index in range(2000):
        link = tmp_path / f"link{index}"
        link.symlink_to(previous)
        previous = link
    assert classify(str(previous), root)[0] in ("inside", "cannot-verify")


def test_unexpandable_tilde_user_is_config_error(tmp_path):
    # RX-7: "~bad\0/x" makes expanduser raise ValueError.
    path = write_config(tmp_path, matters="~bad\u0000/x")
    with pytest.raises(ConfigError, match="cannot expand ~ in \\[paths\\].matters"):
        load(path)


def test_venv_link_masked_by_venv_bin(tmp_path):
    # RX-8: T/venv -> <root>/sub (inside) while <root>/sub/bin -> elsewhere (outside).
    # Only the $TOOLCHAIN/venv argument of the guard call catches this.
    fake = tmp_path / "fake"
    (fake / "scripts").mkdir(parents=True)
    (fake / "src" / "casefile").mkdir(parents=True)
    shutil.copy(RUN_SH, fake / "scripts" / "run.sh")
    shutil.copy(CAPTURE, fake / "scripts" / "run_capture.py")
    shutil.copy(ROOT / "src" / "casefile" / "pathguard.py", fake / "src" / "casefile" / "pathguard.py")
    (fake / "sub").mkdir()
    (tmp_path / "elsewhere").mkdir()
    (fake / "sub" / "bin").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    toolchain = tmp_path / "tc" / "fake"
    toolchain.mkdir(parents=True)
    (toolchain / "venv").symlink_to(fake / "sub", target_is_directory=True)
    before = sorted(str(p) for p in fake.rglob("*"))
    result = subprocess.run([str(fake / "scripts" / "run.sh"), "true"], cwd=tmp_path, capture_output=True,
                            timeout=30, env=dict(os.environ, CASEFILE_TOOLCHAIN=str(tmp_path / "tc"),
                                                 TMPDIR=str(tmp_path)))
    assert (result.returncode, result.stdout) == (95, b""), result
    assert result.stderr.startswith(b"run.sh: toolchain must be outside the checkout")
    assert sorted(str(p) for p in fake.rglob("*")) == before
    # the module sees the same split: venv alone is inside, venv/bin alone is outside
    assert classify(str(toolchain / "venv"), fake)[0] == "inside"
    assert classify(str(toolchain / "venv" / "bin"), fake)[0] == "outside"
