"""Find prohibited prose dash characters in the round's authored surfaces."""

from pathlib import Path


PATTERNS = ("*.md", "docs/**/*.md", ".workflow/LEDGER.md", "playbook/**/*.toml",
            "src/**/*.py", "tests/**/*.py", "tests/fixtures/**/*.txt", "tests/fixtures/**/*.json",
            "tests/fixtures/**/*.toml", "scripts/*", "config.example.toml", "pyproject.toml")


def files(root):
    root = Path(root)
    return sorted({path for pattern in PATTERNS for path in root.glob(pattern) if path.is_file()})


def scan(root):
    hits = []
    for path in files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            hits.extend((path.relative_to(root).as_posix(), number)
                        for char in line if char in (chr(0x2013), chr(0x2014)))
    return hits
