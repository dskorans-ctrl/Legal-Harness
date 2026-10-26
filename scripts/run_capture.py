"""Bound combined output and stop the entire child group on overflow."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys


def capture_failed(reason):
    print(f"run.sh: capture stage failed: {reason}; exit 98", file=sys.stderr)
    return 98


def main():
    if len(sys.argv) < 3 or not sys.argv[2] or not Path(sys.argv[2]).is_dir():
        return capture_failed("capture directory must be a non-empty existing directory")
    cap, directory, *command = sys.argv[1:]
    cap = int(cap)
    child = capture = None
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
        while chunk := os.read(child.stdout.fileno(), min(65536, cap + 1 - total)):
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
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
                print(f"run.sh: output cap {cap} bytes hit (child status {child.returncode}); exit 97",
                      file=sys.stderr)
                return 97
        status = child.wait()
        return status if status >= 0 else 128 - status
    finally:
        if child is not None:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            child.stdout.close()
        if capture is not None:
            capture.close()
        shutil.rmtree(directory)


if __name__ == "__main__":
    raise SystemExit(main())
