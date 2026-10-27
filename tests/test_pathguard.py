"""The one identity guard (D24): an alias table, the CLI, and what the module may import."""

import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys


from casefile.pathguard import classify
from conftest import ROOT, alias_table

SOURCE = ROOT / "src" / "casefile" / "pathguard.py"
EXIT = {"outside": 0, "inside": 10, "cannot-verify": 11, "relative": 12}


def make_root(tmp_path):
    root = tmp_path / "Checkout"
    root.mkdir()
    return root


def interpreters():
    found = {}
    for candidate in (sys.executable, "/usr/bin/python3", shutil.which("python3")):
        if candidate and os.path.exists(candidate):
            found.setdefault(os.path.realpath(candidate), candidate)
    return list(found.values())


def cli(interpreter, root, *paths):
    return subprocess.run([interpreter, "-I", str(SOURCE), str(root), *paths],
                          capture_output=True, text=True, timeout=30)


def test_alias_table(tmp_path):
    root = make_root(tmp_path)
    wrong, names = set(), interpreters()
    with alias_table(tmp_path, root, firmlink=False) as rows:
        for row_id, path, expected in rows:
            if classify(path, root)[0] != expected:
                wrong.add(row_id)
            for interpreter in names:
                result = cli(interpreter, root, path)
                lines = result.stdout.splitlines()
                if (result.returncode != EXIT[expected] or len(lines) != 1
                        or not lines[0].startswith(f"pathguard {expected}")):
                    wrong.add(f"{row_id}@{interpreter}")
                if interpreter == sys.executable and result.stderr:
                    wrong.add(f"{row_id}@stderr")
        total = len(rows)
    print(f"\nalias_wrong={len({name.split('@')[0] for name in wrong})} of {total} interpreters={len(names)}")
    assert not wrong, sorted(wrong)
    assert total == 19 and names


def test_outside_detail_is_the_walked_realpath(tmp_path):
    root = make_root(tmp_path)
    (tmp_path / "out").mkdir()
    (tmp_path / "lout").symlink_to(tmp_path / "out", target_is_directory=True)
    assert classify(tmp_path / "lout" / "new", root) == ("outside", str(tmp_path / "out" / "new"))


def test_root_argument_aliases(tmp_path):
    root = make_root(tmp_path)
    assert str(root).startswith("/private/"), "tmp root must have a /private spelling"
    with alias_table(tmp_path, root, firmlink=False) as rows:
        spellings = {"symlink": tmp_path / "lroot", "case": root.with_name(root.name.swapcase()),
                     "private": Path(str(root)[len("/private"):])}
        assert all(os.path.samefile(spelling, root) for spelling in spellings.values())
        wrong = [f"{row_id}@{kind}" for kind, spelling in spellings.items()
                 for row_id, path, expected in rows if classify(path, spelling)[0] != expected]
    assert not wrong, wrong


def test_link_inside_checkout_pointing_out(tmp_path):
    root = make_root(tmp_path)
    (tmp_path / "out").mkdir()
    (root / "lout").symlink_to(tmp_path / "out", target_is_directory=True)
    assert classify(root / "lout" / "m", root)[0] == "inside"


def test_cli_many_paths(tmp_path):
    root = make_root(tmp_path)
    (tmp_path / "out").mkdir()
    (tmp_path / "lroot").symlink_to(root, target_is_directory=True)
    outside, inside = str(tmp_path / "out"), str(tmp_path / "lroot" / "m")
    for paths, verdict in (((outside, inside), "inside"), ((inside, outside), "inside"),
                           ((outside, "relchk"), "relative"), ((outside, outside + "/x"), "outside")):
        result = cli(sys.executable, root, *paths)
        assert (result.returncode, result.stderr) == (EXIT[verdict], ""), paths
        assert result.stdout.startswith(f"pathguard {verdict}"), (paths, result.stdout)
    assert cli(sys.executable, root).returncode == 11


def test_stdlib_only_and_python39_syntax():
    source = SOURCE.read_text()
    ast.parse(source, feature_version=(3, 9))
    print("\npy39_syntax=ok")
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module)
    print("\nimports=" + (",".join(("os", "sys", "errno")) if names == {"os", "sys", "errno"}
                        else ",".join(sorted(map(str, names)))))
    assert names == {"os", "sys", "errno"}
