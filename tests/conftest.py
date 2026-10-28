"""Keep all test configuration and writes inside temporary directories."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import unicodedata

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
            "host": "http://127.0.0.1:9",
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


@pytest.fixture(scope="session")
def scanned_intake(tmp_path_factory, isolated_config):
    """Run the real scanned binder command once in a fresh folder for this session."""
    base = tmp_path_factory.mktemp("scanned-intake").resolve()
    path = write_config(base)
    loaded = config.load(path)
    root = loaded.paths.matters / "9002.001"
    assert not root.exists(), f"scanned intake must use a fresh matter folder: {root}"
    root.mkdir()
    command = ["scripts/run.sh", "casefile", "intake", "--matter", "9002.001", "--binder", "scan",
               "tests/fixtures/scanned/scanned.pdf"]
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, CASEFILE_CONFIG=str(path)),
                            capture_output=True, text=True, timeout=180)
    yield result, loaded, root


@contextmanager
def alias_table(base, root, firmlink=True):
    """Yield the 19 path rows (id, path, expected) every guard caller must agree on.

    Links are made under `base` (a tmp_path) against `root` (the checkout under test).
    The unreadable folder is restored on exit. A disk that cannot build a row fails the
    row (samefile asserts), it is never skipped.
    """
    base, root = Path(base), Path(root)
    swapped = root.with_name(root.name.swapcase())
    assert os.path.samefile(swapped, root), "this disk must treat a case-swapped checkout as the same folder"
    (root / "tests" / "fixtures").mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(exist_ok=True)

    def link(name, target):
        (base / name).symlink_to(target, target_is_directory=True)
        return base / name

    link("lroot", root)
    link("lsub", swapped / "tests" / "fixtures")
    link("c1", base / "lsub")
    link("c2", base / "c1")
    (base / "loopA").symlink_to(base / "loopB")
    (base / "loopB").symlink_to(base / "loopA")
    link("dang", swapped / "no-such" / "x")
    link("lsrc", root / "src")
    nfc = link("Caf\u00e9", root)
    nfd = base / unicodedata.normalize("NFD", "Caf\u00e9")
    assert nfd.name != nfc.name and os.path.samefile(nfd, root), "NFD spelling must reach the same folder"
    # hop leads two levels down, so `hop/..` lands in base/deep while its text says base.
    (base / "deep" / "sub").mkdir(parents=True)
    link("hop", base / "deep" / "sub")
    (base / "out" / "ok").mkdir(parents=True)
    blocked = base / "blocked"
    blocked.mkdir()
    if firmlink:
        firm = "/System/Volumes/Data" + str(root)
        assert os.path.samefile(firm, root), "firmlink spelling must reach the same folder"
    else:
        firm = str(link("lroot2", root))
    rows = [
        ("case-swapped-root", f"{swapped}/m", "inside"),
        ("symlink-root", f"{base}/lroot/m", "inside"),
        ("symlink-root-bare", f"{base}/lroot", "inside"),
        ("symlink-subfolder-case", f"{base}/lsub/m", "inside"),
        ("symlink-subfolder-bare", f"{base}/lsub", "inside"),
        ("chain", f"{base}/c2/m", "inside"),
        ("loop", f"{base}/loopA/m", "cannot-verify"),
        ("dotdot-after-missing", f"{base}/nope" + "/.." * (len(base.parts) + 1) + f"{root}/tc", "inside"),
        ("dangling-into-checkout", f"{base}/dang/m", "inside"),
        ("dotdot-after-symlink", f"{base}/lsrc/../m", "inside"),
        ("relative", "relchk", "relative"),
        ("unreadable-ancestor", f"{blocked}/m", "cannot-verify"),
        ("checkout-itself", str(root), "inside"),
        ("trailing-slash", f"{root}/", "inside"),
        ("nfd-alias", f"{nfd}/m", "inside"),
        ("firmlink", f"{firm}/m", "inside"),
        # normpath would read this as base/lroot/m (inside); the kernel lands in base/deep (outside).
        ("hop-dotdot-through-link", f"{base}/hop/../lroot/m", "outside"),
        ("outside-existing", f"{base}/out/ok", "outside"),
        ("outside-new", f"{base}/out/new/deeper", "outside"),
    ]
    assert len(rows) == 19 and len({row[0] for row in rows}) == 19
    blocked.chmod(0o000)
    try:
        yield rows
    finally:
        blocked.chmod(0o700)


def ocr_expected_fail() -> bool:
    """The doctor's OCR check runs a real smoke page (stage 3); no check is expected to fail."""
    return False
