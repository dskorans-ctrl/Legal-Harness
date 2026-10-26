"""Keep all test configuration and writes inside temporary directories."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from casefile import config


ROOT = Path(__file__).resolve().parents[1]


def _toml_value(value):
    if isinstance(value, Path):
        value = str(value)
    if isinstance(value, (str, bool, int, float, list)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    raise TypeError(f"unsupported TOML fixture value: {type(value).__name__}")


def write_config(tmp_path, **overrides):
    """Write a complete invented config; overrides merge by table or key."""
    tmp_path = Path(tmp_path).resolve()
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir(parents=True, exist_ok=True)
    for name in ("matters", "state", "playbook"):
        (tmp_path / name).mkdir(exist_ok=True)
    values = {
        "paths": {
            "matters": tmp_path / "matters",
            "state": tmp_path / "state",
            "playbook": tmp_path / "playbook",
        },
        "model": {
            "host": "http://127.0.0.1:11434",
            "name": "qwen3.8:27b",
            "num_ctx": 65536,
            "temperature": 0.1,
            "timeout_s": 600,
        },
        "ocr": {"tesseract": "tesseract", "ocrmypdf": "ocrmypdf"},
    }
    for name, value in overrides.items():
        if isinstance(value, dict):
            values.setdefault(name, {}).update(value)
        else:
            table = next(
                (table for table in values.values() if isinstance(table, dict) and name in table),
                None,
            )
            if table is None:
                values[name] = value
            else:
                table[name] = value
    lines = []
    for name, value in values.items():
        if not isinstance(value, dict):
            lines.append(f"{json.dumps(name)} = {_toml_value(value)}")
    for name, table in values.items():
        if isinstance(table, dict):
            lines.append(f"\n[{json.dumps(name)}]")
            for key, value in table.items():
                lines.append(f"{json.dumps(key)} = {_toml_value(value)}")
    path = settings_dir / "config.toml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _production_snapshot():
    """Read metadata only; never open a production file's contents."""
    snapshot = {}
    for name in ("state", "Cases", "Bench"):
        directory = ROOT / name
        snapshot[name] = directory.exists()
        if directory.exists():
            for parent, _, filenames in os.walk(directory, followlinks=False):
                for filename in filenames:
                    path = Path(parent) / filename
                    stat = path.lstat()
                    snapshot[str(path.relative_to(ROOT))] = (
                        stat.st_size,
                        stat.st_mtime_ns,
                    )
    return snapshot


@pytest.fixture(scope="session", autouse=True)
def production_dirs_untouched():
    before = _production_snapshot()
    yield
    assert _production_snapshot() == before, "production directories changed during tests"


@pytest.fixture(scope="session", autouse=True)
def isolated_config(tmp_path_factory, production_dirs_untouched):
    tmp_root = tmp_path_factory.mktemp("casefile-isolated").resolve()
    path = write_config(tmp_root)
    source = ROOT / "playbook"
    if source.exists():
        shutil.copytree(source, tmp_root / "playbook", dirs_exist_ok=True)
    old_config = os.environ.get("CASEFILE_CONFIG")
    os.environ["CASEFILE_CONFIG"] = str(path)
    try:
        try:
            loaded = config.load(path)
            paths = {name: getattr(loaded.paths, name) for name in ("matters", "state", "playbook")}
            for name in ("matters", "state", "playbook"):
                target = Path(paths[name]).expanduser()
                if not target.is_absolute():
                    target = path.parent / target
                if not target.resolve().is_relative_to(tmp_root):
                    raise ValueError(str(target))
            if os.environ.get("CASEFILE_CONFIG") != str(path):
                raise ValueError("CASEFILE_CONFIG changed")
        except Exception as exc:
            pytest.exit(f"test isolation failed: {path}: {exc}", returncode=3)
        yield path
    finally:
        if old_config is None:
            os.environ.pop("CASEFILE_CONFIG", None)
        else:
            os.environ["CASEFILE_CONFIG"] = old_config


def ocr_expected_fail() -> bool:
    tesseract = shutil.which("tesseract")
    ocrmypdf = shutil.which("ocrmypdf")
    if tesseract is None or ocrmypdf is None:
        return True
    try:
        result = subprocess.run(
            [tesseract, "--version"], capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return True
    return result.returncode != 0
