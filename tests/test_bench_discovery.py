"""casefile bench discovery: only folders holding matter.toml are matters (D25, verifier seed V2-S1)."""

import io
import shutil

from casefile import bench
from conftest import ROOT, write_config

MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")


def test_non_matter_entries_are_skipped(tmp_path):
    matters_dir = tmp_path / "matters_copy"
    shutil.copytree(MATTER, matters_dir / "9001.001")
    (matters_dir / "notes").mkdir()
    (matters_dir / "notes" / "todo.txt").write_text("Invented note, not a matter.\n", encoding="utf-8")
    (matters_dir / "readme.txt").write_text("Invented readme, not a matter.\n", encoding="utf-8")
    config = write_config(tmp_path / "cfg", playbook=ROOT / "playbook", host="http://127.0.0.1:9")
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(matters_dir, config, MATTER / "ideal.json", out=out, err=err)
    lines = out.getvalue().splitlines()
    assert err.getvalue() == ""
    assert lines == [PERFECT, "bench matters=1 imperfect=0"]
    assert code == 0
