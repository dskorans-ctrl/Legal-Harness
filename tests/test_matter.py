"""The stage 2 matter loader: pages, stamps and its fifteen refusals."""

import pytest
from pathlib import Path
from casefile.matter import MatterError, load

def make(tmp_path, pages):
    """pages: {binder: [(text, stamp), ...]} in binder order. Returns the matter root."""
    root = tmp_path / "matter"
    binders = ", ".join(f'"{b}"' for b in pages)
    (root / "records").mkdir(parents=True)
    (root / "matter.toml").write_text(f'number = "9001.001"\nbinders = [{binders}]\n', encoding="utf-8")
    for binder, items in pages.items():
        folder = root / "records" / binder
        folder.mkdir()
        for index, (text, stamp) in enumerate(items, start=1):
            (folder / f"{index:03d}.txt").write_text(f"{text}\n{stamp}\n", encoding="utf-8")
    return root

GOOD = {"medical": [("ER visit, low back pain.", "MED0001"), ("Diagnosis: acute lumbar strain.", "MED0002")], "employer": [("Incident report.", "EMP0001")]}

def test_load_happy(tmp_path):
    root = make(tmp_path, GOOD)
    matter = load(root)
    assert len(matter.pages) == 3
    assert matter.pages[0].page_id == "medical/001"
    assert matter.pages[0].stamps == ("MED0001",)
    assert matter.page("MED0002").text == "Diagnosis: acute lumbar strain."
    assert matter.page("NOPE0001") is None
    assert matter.number == "9001.001"

    # Check that only expected files exist (filenames only)
    actual_files = sorted(p.name for p in root.rglob("*") if p.is_file())
    assert actual_files == ["001.txt", "001.txt", "002.txt", "matter.toml"]

# --- Refusal Setup Functions ---

def setup_missing_toml(base):
    root = make(base, GOOD)
    (root / "matter.toml").unlink()
    return root

def setup_unknown_key(base):
    root = make(base, GOOD)
    content = 'number = "9001.001"\nbinders = ["medical", "employer"]\nextra = 1\n'
    (root / "matter.toml").write_text(content, encoding="utf-8")
    return root

def setup_bad_number(base):
    root = make(base, GOOD)
    content = 'number = "9001"\nbinders = ["medical", "employer"]\n'
    (root / "matter.toml").write_text(content, encoding="utf-8")
    return root

def setup_empty_binders(base):
    root = make(base, GOOD)
    content = 'number = "9001.001"\nbinders = []\n'
    (root / "matter.toml").write_text(content, encoding="utf-8")
    return root

def setup_binder_folder_missing(base):
    root = make(base, GOOD)
    content = 'number = "9001.001"\nbinders = ["medical", "employer", "defense"]\n'
    (root / "matter.toml").write_text(content, encoding="utf-8")
    return root

def setup_numbering_gap(base):
    root = make(base, GOOD)
    (root / "records/medical/002.txt").rename(root / "records/medical/003.txt")
    return root

def setup_stray_file(base):
    root = make(base, GOOD)
    (root / "records/medical/notes.txt").write_text("x\nMED0009\n", encoding="utf-8")
    return root

def setup_trailing_text(base):
    root = make(base, GOOD)
    content = "ER visit.\nMED0001 page 1\n"
    (root / "records/medical/001.txt").write_text(content, encoding="utf-8")
    return root

def setup_duplicate_stamp(base):
    root = make(base, GOOD)
    content = "Incident report.\nMED0001\n"
    (root / "records/employer/001.txt").write_text(content, encoding="utf-8")
    return root

def setup_page_is_folder(base):
    root = make(base, GOOD)
    (root / "records/medical/002.txt").unlink()
    (root / "records/medical/002.txt").mkdir()
    return root

def setup_page_not_utf8(base):
    root = make(base, GOOD)
    (root / "records/medical/002.txt").write_bytes(b"\xff\xfe text\nMED0002\n")
    return root

def setup_toml_not_utf8(base):
    root = make(base, GOOD)
    with (root / "matter.toml").open("ab") as stream:
        stream.write(b"\xff")
    return root

def setup_binders_repeated(base):
    root = make(base, GOOD)
    content = 'number = "9001.001"\nbinders = ["medical", "employer", "medical"]\n'
    (root / "matter.toml").write_text(content, encoding="utf-8")
    return root

def setup_stray_file_named_before_unreadable_page(base):
    """The first binder holds a page that is not UTF-8; the second holds a stray file. Names are
    checked for every binder before any page is read, so the stray file is the refusal named."""
    root = make(base, GOOD)
    (root / "records/medical/002.txt").write_bytes(b"\xff\xfe text\nMED0002\n")
    (root / "records/employer/notes.txt").write_text("x\nEMP0009\n", encoding="utf-8")
    return root

def setup_unlisted_binder(base):
    root = make(base, GOOD)
    (root / "records/xray").mkdir()
    return root

def test_refusals(tmp_path, capsys):
    CASES = [
        (setup_missing_toml, "matter.toml not found"),
        (setup_unknown_key, "expected keys number and binders"),
        (setup_bad_number, "number must look like 9001.001"),
        (setup_empty_binders, "binders must be a nonempty list of names"),
        (setup_binder_folder_missing, "binder folder not found"),
        (setup_numbering_gap, "found 003.txt"),
        (setup_stray_file, "found notes.txt"),
        (setup_trailing_text, "last line is not a Bates stamp"),
        (setup_duplicate_stamp, "duplicate Bates stamp MED0001"),
        (setup_page_is_folder, "002.txt"),
        (setup_page_not_utf8, "002.txt"),
        (setup_toml_not_utf8, "can't decode byte 0xff"),
        (setup_binders_repeated, "binders must be distinct"),
        (setup_stray_file_named_before_unreadable_page, "found notes.txt"),
        (setup_unlisted_binder, "unlisted binder folder xray"),
    ]

    ok = 0
    for i, (setup, match_text) in enumerate(CASES):
        base = tmp_path / f"case{i}"
        base.mkdir()
        root = setup(base)
        try:
            load(root)
        except MatterError as exc:
            if match_text in str(exc):
                ok += 1

    with capsys.disabled():
        # Create a fresh happy path directory for the final check
        happy_root = tmp_path / "happy"
        happy_root.mkdir()
        happy_root = make(happy_root, GOOD)
        matter = load(happy_root)
        print(f"matter_pages={len(matter.pages)} refusals={ok} of 15")
    assert ok == 15


def test_dotfiles_are_ignored(tmp_path, capsys):
    ignored = 0
    for where in ("records", "records/medical"):
        base = tmp_path / where.replace("/", "_")
        base.mkdir()
        root = make(base, GOOD)
        (root / where / ".DS_Store").write_bytes(b"\x00\x00 finder bytes")
        try:
            matter = load(root)
        except MatterError:
            continue
        if [p.page_id for p in matter.pages] == ["medical/001", "medical/002", "employer/001"]:
            ignored += 1
    with capsys.disabled():
        print(f"dotfiles_ignored={ignored}")
    assert ignored == 2


def test_dotfile_is_the_only_ignore_rule(tmp_path):
    root = make(tmp_path, GOOD)
    (root / "records" / "medical" / "Thumbs.db").write_bytes(b"x")
    with pytest.raises(MatterError, match="found Thumbs.db"):
        load(root)


def test_stamp_spellings_are_one_stamp(tmp_path, capsys):
    matter = load(make(tmp_path, GOOD))
    hits = [matter.page(c) for c in ("MED0001", "MED 0001", "MED-0001")]
    ok = sum(1 for h in hits if h is not None and h.page_id == "medical/001")
    with capsys.disabled():
        print(f"cite_spellings={ok} of 3")
    assert ok == 3
    assert matter.page("MED 0003") is None


def test_authored_stamp_with_a_space_collides_with_the_plain_one(tmp_path):
    pages = {"medical": [("First page.", "MED0001"), ("Second page.", "MED 0001")]}
    with pytest.raises(MatterError, match="duplicate Bates stamp MED 0001"):
        load(make(tmp_path, pages))
