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
    for suffix in ("pdf", "doc", "docx", "png", "jpg", "jpeg", "tif", "tiff", "heic"):
        touch(root, f"docs/invented.{suffix.upper()}")
        touch(root, f"tests/fixtures/invented.{suffix}")
    touch(root, "Cases/anything.txt")
    touch(root, "Bench/anything.txt")
    assert len(privacy.scan(root)) == 11


def test_common_document_formats_and_ignore(tmp_path, monkeypatch):
    suffixes = "gif bmp webp heif svg dot dotx docm rtf odt pages avif ico jxl jfif jpe dib eps psd raw dng cr2 nef arw rw2 raf orf pef ppm pgm pbm pnm tga wmf emf cur apng odg ott dotm svgz jp2 j2k hif".split()
    inventory = [f"docs/invented.{s.upper()}" for s in suffixes]
    inventory += [f"tests/fixtures/invented.{s}" for s in suffixes]
    monkeypatch.setattr(privacy, "paths", lambda root: inventory)
    assert privacy.scan(tmp_path) == inventory[:len(suffixes)]
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"],
                             cwd=ROOT, input="\n".join(inventory) + "\n",
                             capture_output=True, text=True, check=False)
    assert ignored.returncode == 0
    assert ignored.stdout.splitlines() == inventory[:len(suffixes)]


def test_forbidden_first_component_any_case(tmp_path, monkeypatch):
    inventory = [f"{name}{tail}" for name in ("Cases", "cases", "CASES", "Bench", "bench", "bEnCh")
                 for tail in ("", "/", "/invented.txt")]
    monkeypatch.setattr(privacy, "paths", lambda root: inventory + ["CaseStudy.txt", "benchmarks/a.txt"])
    assert privacy.scan(tmp_path) == inventory


def test_inventory_symlink_targets(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "allowed").mkdir()
    (root / "Cases").mkdir()
    (root / "bEnCh").mkdir()
    links = {"external": tmp_path / "invented-external",
             "nested/to-cases": root / "Cases",
             "to-bench": root / "bEnCh" / "invented.txt",
             "safe": root / "allowed"}
    for name, target in links.items():
        link = root / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)
    monkeypatch.setattr(privacy, "paths", lambda repo: list(links))
    assert privacy.scan(root) == ["external", "nested/to-cases", "to-bench"]
