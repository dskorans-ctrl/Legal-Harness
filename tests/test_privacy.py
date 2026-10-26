"""Zero-byte invented placeholders test path rules in disposable git indexes."""

import subprocess

from casefile import privacy
from conftest import ROOT


def init_repo(root):
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    (root / ".gitignore").write_bytes((ROOT / ".gitignore").read_bytes())
    return root


def touch(root, relative):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_offenders(tmp_path, capsys):
    root = init_repo(tmp_path)
    for path in ("tests/fixtures/a.pdf", "docs/b.PNG", "Cases/c.txt", "Bench/k.md",
                 "docs/tests/fixtures/x.pdf", "notes.md", ".venv/lib/site.py"):
        touch(root, path)
    # These controls must remain visible if ignored untracked files disappear.
    # No commit is needed: --cached reads this disposable index.
    subprocess.run(["git", "add", "-f", "tests/fixtures/a.pdf", "notes.md",
                    "Bench/k.md", "docs/tests/fixtures/x.pdf"], cwd=root, check=True)
    expected = ["Bench/k.md", "Cases/c.txt", "docs/b.PNG", "docs/tests/fixtures/x.pdf"]
    offenders = privacy.scan(root)
    with capsys.disabled():
        print(f"offenders={len(offenders)} expected=4 scanned={len(privacy.paths(root))}")
    assert offenders == expected
    assert len(privacy.paths(root)) == 8  # Seven paths plus the copied .gitignore.


def test_suffixes_and_prefixes(tmp_path):
    root = init_repo(tmp_path)
    assert len(privacy.SUFFIXES) == 9
    for suffix in ("pdf", "doc", "docx", "png", "jpg", "jpeg", "tif", "tiff", "heic"):
        touch(root, f"docs/invented.{suffix.upper()}")
        touch(root, f"tests/fixtures/invented.{suffix}")
    touch(root, "Cases/anything.txt")
    touch(root, "Bench/anything.txt")
    assert len(privacy.scan(root)) == 11
