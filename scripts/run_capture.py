"""Bound combined output and stop the entire child group on overflow."""

import os
from pathlib import Path
import shutil
import select
import signal
import subprocess
import sys
import time

GRACE_S = 2.0   # how long the output pipe may stay open after the child has exited


def capture_failed(reason):
    print(f"run.sh: capture stage failed: {reason}; exit 98", file=sys.stderr)
    return 98


def main():
    if len(sys.argv) < 3 or not sys.argv[2] or not Path(sys.argv[2]).is_dir():
        return capture_failed("capture directory must be a non-empty existing directory")
    cap, directory, *command = sys.argv[1:]
    cap = int(cap)
    child = capture = None
    exit_at = None
    queue = select.kqueue()   # macOS: no descriptor-number limit, and an exit is told from a stop
    try:
        try:
            capture = (Path(directory) / "out").open("wb", buffering=0)
        except OSError as exc:
            return capture_failed(exc)
        try:
            child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        except FileNotFoundError:
            print(f"run.sh: command not found: {command[0]}", file=sys.stderr)
            return 127
        except OSError as exc:
            print(f"run.sh: command not executable: {command[0]}: {exc}", file=sys.stderr)
            return 126
        total = 0
        deadline = None
        fd = child.stdout.fileno()
        # Watch the pipe and the child's exit (NOTE_EXIT is not raised by stop or continue, and
        # it does not reap: reaping would free the pid before the group kill).
        queue.control([select.kevent(fd, select.KQ_FILTER_READ, select.KQ_EV_ADD),
                       select.kevent(child.pid, select.KQ_FILTER_PROC, select.KQ_EV_ADD,
                                     select.KQ_NOTE_EXIT)], 0, 0)
        while True:
            now = time.monotonic()
            if exit_at is not None and deadline is None:
                deadline = exit_at + GRACE_S
            if deadline is not None and now >= deadline:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except OSError:   # ESRCH, or EPERM when only a zombie leader is left
                    pass
                status = child.wait()
                code = status if status >= 0 else 128 - status
                print(f"run.sh: child exited {code} but its output pipe stayed open; "
                      f"process group killed after {GRACE_S}s", file=sys.stderr)
                return code
            wait = None if deadline is None else max(0.0, deadline - now)
            readable = False
            for event in queue.control(None, 2, wait):
                if event.filter == select.KQ_FILTER_PROC:
                    if exit_at is None:
                        exit_at = time.monotonic()
                else:
                    readable = True
            if not readable:
                continue
            chunk = os.read(fd, min(65536, cap + 1 - total))
            if not chunk:
                break
            try:
                remaining = memoryview(chunk)
                while remaining:
                    written = capture.write(remaining)
                    if written is None or written <= 0:
                        raise OSError("capture write made no progress")
                    remaining = remaining[written:]
            except OSError as exc:
                return capture_failed(exc)
            sys.stdout.buffer.write(chunk[:max(0, cap - total)])
            sys.stdout.buffer.flush()
            total += len(chunk)
            if total > cap:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except OSError:
                    pass
                child.wait()
                print(f"run.sh: output cap {cap} bytes hit (child status {child.returncode}); exit 97",
                      file=sys.stderr)
                return 97
        status = child.wait()
        return status if status >= 0 else 128 - status
    finally:
        queue.close()
        if child is not None:
            if child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except OSError:
                    pass
                child.wait()
            child.stdout.close()
        if capture is not None:
            capture.close()
        shutil.rmtree(directory)


if __name__ == "__main__":
    raise SystemExit(main())
