"""Inventory tracked and ignored paths without reading their contents."""

from pathlib import Path, PurePosixPath
import subprocess


SUFFIXES = frozenset({".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".heic", ".gif", ".bmp", ".webp", ".heif", ".svg", ".dot", ".dotx", ".docm", ".rtf", ".odt", ".pages", ".avif", ".ico", ".jxl", ".jfif", ".jpe", ".dib", ".eps", ".psd", ".raw", ".dng", ".cr2", ".nef", ".arw", ".rw2", ".raf", ".orf", ".pef", ".ppm", ".pgm", ".pbm", ".pnm", ".tga", ".wmf", ".emf", ".cur", ".apng", ".odg", ".ott", ".dotm", ".svgz", ".jp2", ".j2k", ".hif"})


def paths(repo_root):
    result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others"],
                            cwd=repo_root, capture_output=True, check=True)
    return sorted(set(p.decode("utf-8", errors="surrogateescape")
                      for p in result.stdout.split(b"\0") if p))


def _unsafe_link(root, relative):
    for candidate in (relative, *relative.parents):
        link = root / candidate
        if link.is_symlink():
            try:
                target = link.resolve().relative_to(root)
            except (ValueError, OSError, RuntimeError):
                return True
            if any(part.casefold() in {"cases", "bench"} for part in target.parts):
                return True
    return False


def scan(repo_root) -> list[str]:
    root = Path(repo_root).resolve()
    offenders = []
    for path in paths(repo_root):
        relative = PurePosixPath(path)
        forbidden = bool(relative.parts) and relative.parts[0].casefold() in {"cases", "bench"}
        if (forbidden or _unsafe_link(root, relative) or
                (relative.suffix.lower() in SUFFIXES and not path.startswith("tests/fixtures/"))):
            offenders.append(path)
    return offenders
