"""Prose scans the exact authored surfaces, including source and test code."""

from casefile import prose


def test_dashes(tmp_path, capsys):
    (tmp_path / "notes.md").write_text("invented " + chr(0x2014) + " text\n")
    hits = prose.scan(tmp_path)
    with capsys.disabled():
        print(f"dashes={len(hits)}")
    assert hits == [("notes.md", 1)]


def test_surfaces(tmp_path):
    included = ["root.md", "docs/nested/a.md", ".workflow/LEDGER.md", "playbook/a.toml",
                "src/casefile/a.py", "tests/a.py", "scripts/run.sh", "config.example.toml",
                "pyproject.toml"]
    excluded = [".claude/a.md", "cards/a.md", "reference/a.md", "schemas/a.md"]
    for relative in included + excluded:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(chr(0x2013) + chr(0x2014))
    assert len(prose.scan(tmp_path)) == 18
    assert len(prose.files(tmp_path)) == 9
