"""Decide whether a path is inside the checkout, by filesystem identity (D24).

Stdlib only and python3 >= 3.9, so scripts/run.sh can run it before the venv exists.
A path is inside when any existing ancestor of its typed or real spelling is the
checkout itself (same device and inode), so case, symlinks, chains and `..` all agree.
Only a missing ancestor (ENOENT, ENOTDIR) is skipped; any other error cannot be verified.
CLI: pathguard.py <root> <path> [<path>...]; prints `pathguard <verdict> <detail>`
and exits 0 outside, 10 inside, 11 cannot-verify, 12 relative.
"""

import errno
import os
import sys

MISSING = (errno.ENOENT, errno.ENOTDIR)
EXIT = {"outside": 0, "inside": 10, "cannot-verify": 11, "relative": 12}


def classify(path, root):
    """Return (verdict, detail); for outside the detail is the realpath walked."""
    path = os.fspath(path)
    if not os.path.isabs(path):
        return "relative", path
    try:
        stat = os.stat(root)
        root_id = (stat.st_dev, stat.st_ino)
        real = os.path.realpath(path)
        for spelling in dict.fromkeys((path, real)):
            ancestor = spelling
            while True:
                try:
                    stat = os.stat(ancestor)
                except OSError as exc:
                    if exc.errno not in MISSING:
                        raise
                else:
                    if (stat.st_dev, stat.st_ino) == root_id:
                        return "inside", real
                parent = os.path.dirname(ancestor)
                if parent == ancestor:
                    break
                ancestor = parent
    except (OSError, ValueError) as exc:
        return "cannot-verify", str(exc)
    return "outside", real


def main(argv):
    if len(argv) < 3:
        print("pathguard cannot-verify usage: pathguard.py <root> <path> [<path>...]")
        return EXIT["cannot-verify"]
    root, paths = argv[1], argv[2:]
    results = [classify(path, root) for path in paths]
    verdict, detail = next((r for r in results if r[0] != "outside"), results[0])
    print("pathguard", verdict, " ".join(str(detail).split("\n")))
    return EXIT[verdict]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
