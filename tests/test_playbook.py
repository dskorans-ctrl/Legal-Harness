"""Load invented SAMPLE entries and refuse each deliberately malformed fixture."""

from dataclasses import FrozenInstanceError
import hashlib
from pathlib import Path
import re
import shutil

import pytest

from casefile.playbook import Entry, PlaybookError, load


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "playbook"
FIXTURES = ROOT / "tests" / "fixtures" / "playbook"


def copy_playbook(tmp_path):
    return Path(shutil.copytree(SOURCE, tmp_path / "playbook"))


def test_malformed_fail_closed(tmp_path, capsys):
    directory = copy_playbook(tmp_path)
    refused = []
    for name, field in (("malformed-missing-why.toml", "why"),
                        ("unmarked.toml", "sample"), ("bad-date.toml", "added")):
        target = directory / name
        shutil.copyfile(FIXTURES / name, target)
        try:
            load(directory)
        except PlaybookError as exc:
            refused.append(name in str(exc) and field in str(exc))
        else:
            refused.append(False)
        finally:
            target.unlink()
    with capsys.disabled():
        print(f"refused={sum(refused)} of 3", flush=True)
    assert all(refused), refused


def test_version_moves(tmp_path, capsys):
    directory = copy_playbook(tmp_path)
    before = load(directory)
    sample = directory / "samples" / "depo-goals.toml"
    sample.write_bytes(sample.read_bytes() + b"\n")
    after = load(directory)
    changed = before.version != after.version
    with capsys.disabled():
        print(f"version_changed={int(changed)}", flush=True)
    assert changed
    assert re.fullmatch(r"pb-[0-9a-f]{12}", after.version)
    # Independent byte construction checks the prescribed digest, including separators.
    raw = b"".join(path.relative_to(directory).as_posix().encode() + b"\0" + path.read_bytes() + b"\0"
                   for path in sorted(directory.rglob("*.toml"),
                                      key=lambda p: p.relative_to(directory).as_posix()))
    assert after.version == "pb-" + hashlib.sha256(raw).hexdigest()[:12]
    sample.rename(sample.with_name("renamed.toml"))
    assert load(directory).version != after.version


def test_rules_file_entries_not_sample():
    playbook = load(SOURCE)
    firm = [entry for entry in playbook.entries if not isinstance(entry, Entry)]
    entries = [entry for entry in playbook.entries if isinstance(entry, Entry)]
    samples = [entry for entry in entries if entry.sample]
    assert sum(not entry.sample for entry in entries) == 13
    print("playbook_entries practice=13 samples=3")
    assert {entry.id for entry in firm} == {
        "no-dme-ime", "no-hired-paid-retained", "treatment-and-bills-apart", "bates-cites"}
    assert all(not hasattr(entry, "sample") for entry in firm)
    assert len(samples) == 3
    assert all(entry.sample is True and entry.rule.startswith("SAMPLE:") for entry in samples)
    assert playbook.rules.rules == tuple(firm)


@pytest.mark.parametrize(("old", "new", "field"), [
    ('sample = true', 'sample = "true"', "sample"),
    ('sample = true', 'sample = false', "sample"),
    ('rule = "SAMPLE:', 'rule = "Invented:', "sample"),
    ('kind = "question"', 'kind = "other"', "kind"),
    ('kind = "question"', 'kind = "question"\nunexpected = 1', "unexpected"),
    ('id = "sample-question"', 'id = "sample-depo-goal"', "duplicate id"),
    ('id = "sample-question"', 'id = "no-dme-ime"', "duplicate id"),
    ('deponent = "SAMPLE: invented defense doctor Dr. Example"', 'deponent = 1', "deponent"),
])
def test_invalid_entries(tmp_path, old, new, field):
    directory = copy_playbook(tmp_path)
    sample = directory / "samples" / "depo-goals.toml"
    sample.write_text(sample.read_text().replace(old, new, 1))
    with pytest.raises(PlaybookError, match=field):
        load(directory)


def test_no_stale_result_after_failure(tmp_path):
    directory = copy_playbook(tmp_path)
    first = load(directory)
    shutil.copyfile(FIXTURES / "bad-date.toml", directory / "bad.toml")
    with pytest.raises(PlaybookError, match="added"):
        load(directory)
    assert len(first.entries) == 20
    with pytest.raises(FrozenInstanceError):
        first.version = "pb-stale"
    (directory / "bad.toml").unlink()
    assert load(directory) == first


def test_missing_and_bad_documents(tmp_path):
    with pytest.raises(PlaybookError, match="directory not found"):
        load(tmp_path / "missing")
    with pytest.raises(PlaybookError, match="rules.toml"):
        load(tmp_path)
    directory = copy_playbook(tmp_path)
    rules = directory / "rules.toml"
    original = rules.read_bytes()
    rules.write_bytes(original.replace(b"version = 1", b"version = 2", 1))
    with pytest.raises(PlaybookError, match="version"):
        load(directory)
    rules.write_bytes(original)
    bad = directory / "bad.toml"
    for data in (b"broken = [", b"\xff", b"entry = []", b"other = 1"):
        bad.write_bytes(data)
        with pytest.raises(PlaybookError, match="bad.toml"):
            load(directory)


def test_practice_marking_both_ways(tmp_path):
    directory = copy_playbook(tmp_path)
    path = directory / 'deposition.toml'
    original = path.read_text(encoding='utf-8')
    for changed in (original.replace('rule = "', 'rule = "SAMPLE:',1),
                    original.replace('learned = "firm skill ', 'learned = "unknown ',1)):
        path.write_text(changed,encoding='utf-8')
        with pytest.raises(PlaybookError,match='sample'):
            load(directory)
    path.write_text(original,encoding='utf-8')
    assert len(load(directory).entries) == 20
