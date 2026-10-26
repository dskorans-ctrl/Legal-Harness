"""Inventory tracked and ignored paths without reading their contents."""

from pathlib import PurePosixPath
import subprocess


SUFFIXES = frozenset({".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".heic"})


def paths(repo_root):
    result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others"],
                            cwd=repo_root, capture_output=True, check=True)
    return sorted(set(p.decode("utf-8", errors="surrogateescape")
                      for p in result.stdout.split(b"\0") if p))


def scan(repo_root) -> list[str]:
    return [path for path in paths(repo_root)
            if path.startswith(("Cases/", "Bench/")) or
            (PurePosixPath(path).suffix.lower() in SUFFIXES
             and not path.startswith("tests/fixtures/"))]
