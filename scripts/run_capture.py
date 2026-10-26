"""Bound combined output and stop the entire child group on overflow."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys


def main():
    cap, directory, *command = sys.argv[1:]
    cap = int(cap)
    child = None
    try:
        with (Path(directory) / "out").open("wb") as capture:
            child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     start_new_session=True)
            total = 0
            while chunk := os.read(child.stdout.fileno(), min(65536, cap + 1 - total)):
                capture.write(chunk)
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
    except OSError as exc:
        print(f"run.sh: capture stage failed: {exc}; exit 98", file=sys.stderr)
        return 98
    finally:
        if child is not None:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            child.stdout.close()
        shutil.rmtree(directory)


if __name__ == "__main__":
    raise SystemExit(main())
