"""Wrapped loader errors keep their cause (raise ... from exc)."""

import json
import shutil

import pytest

from casefile.benchkey import BenchKeyError, load as load_key
from casefile.matter import MatterError, load as load_matter
from test_matter import GOOD, make


def test_toml_not_utf8_chains(tmp_path):
    root = make(tmp_path, GOOD)
    with (root / "matter.toml").open("ab") as stream:
        stream.write(b"\xff")
    with pytest.raises(MatterError) as info:
        load_matter(root)
    assert isinstance(info.value.__cause__, UnicodeDecodeError)


def test_records_missing_chains(tmp_path):
    root = make(tmp_path, GOOD)
    shutil.rmtree(root / "records")
    with pytest.raises(MatterError) as info:
        load_matter(root)
    assert isinstance(info.value.__cause__, OSError)


def test_binder_unreadable_chains(tmp_path):
    root = make(tmp_path, GOOD)
    folder = root / "records" / "medical"
    folder.chmod(0)
    try:
        with pytest.raises(MatterError) as info:
            load_matter(root)
    finally:
        folder.chmod(0o755)
    assert isinstance(info.value.__cause__, OSError)


def test_page_not_utf8_chains(tmp_path):
    root = make(tmp_path, GOOD)
    (root / "records" / "medical" / "002.txt").write_bytes(b"\xff\xfe text\nMED0002\n")
    with pytest.raises(MatterError) as info:
        load_matter(root)
    assert isinstance(info.value.__cause__, UnicodeDecodeError)


def test_key_not_json_chains(tmp_path):
    matter = load_matter(make(tmp_path, GOOD))
    path = tmp_path / "key.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(BenchKeyError) as info:
        load_key(path, matter)
    assert isinstance(info.value.__cause__, json.JSONDecodeError)
