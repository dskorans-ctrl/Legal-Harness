"""Stage 3 intake: every exit branch, the process lifecycle and the real fixture run."""

from dataclasses import MISSING, fields
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import types

import pytest
from pypdf import PdfReader, PdfWriter

from casefile import intake, matter, pdfsmoke
from casefile.config import load
from conftest import ROOT, write_config

SCANNED = ROOT / "tests" / "fixtures" / "scanned"

TESSERACT_STUB = '#!/bin/bash\n[ "$1" = "--version" ] && { echo "tesseract 5.5.3"; exit 0; }\nexit 9\n'
OCRMYPDF_STUB = r'''#!/bin/bash
D="$(dirname "$0")"
if [ "$1" = "--version" ]; then echo 17.13.0; exit 0; fi
echo "$PATH" > "$D/path.txt"; echo "$TMPDIR" > "$D/tmpdir.txt"; echo "$@" > "$D/args.txt"
args=("$@"); n=${#args[@]}; IN=${args[$((n-2))]}; OUT=${args[$((n-1))]}; SIDE=""
for ((i=0;i<n;i++)); do [ "${args[$i]}" = "--sidecar" ] && SIDE=${args[$((i+1))]}; done
case "$(cat "$D/mode")" in
  fail) echo "boom from the stub" >&2; exit 7;;
  hang) sleep 60 >/dev/null 2>&1 & echo $! > "$D/grandchild.pid"; wait;;
  nooutput) exit 0;;
  leak0|leak7) sleep 60 >/dev/null 2>&1 & echo $! > "$D/grandchild.pid"
     cp "$IN" "$OUT"; cp "$D/sidecar.fixture" "$SIDE"; [ "$(cat "$D/mode")" = leak7 ] && exit 7; exit 0;;
  *) if [ -f "$D/output.fixture" ]; then cp "$D/output.fixture" "$OUT"; else cp "$IN" "$OUT"; fi
     cp "$D/sidecar.fixture" "$SIDE";;
esac
'''


def make_pdf(path: Path, pages: int) -> Path:
    writer = PdfWriter()
    for number in range(pages):
        reader = PdfReader(io.BytesIO(pdfsmoke.text_pdf([f"Invented page {number + 1}", f"KMR{2342 + number}"])))
        writer.add_page(reader.pages[0])
    with path.open("wb") as handle:
        writer.write(handle)
    return path


class Env:
    """A config, a matter folder 9002.001 and stub tools under one temp folder."""

    def __init__(self, base, *, sidecar="", mode="copy", timeout_s=3600, pages=6):
        self.base = Path(base).resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self.stubs = self.base / "stubs"
        self.stubs.mkdir()
        for name, body in (("tesseract", TESSERACT_STUB), ("ocrmypdf", OCRMYPDF_STUB)):
            (self.stubs / name).write_text(body)
            (self.stubs / name).chmod(0o755)
        (self.stubs / "mode").write_text(mode)
        (self.stubs / "sidecar.fixture").write_bytes(sidecar.encode("utf-8"))
        self.config_path = write_config(self.base, ocr={"tesseract": str(self.stubs / "tesseract"),
                                                        "ocrmypdf": str(self.stubs / "ocrmypdf"),
                                                        "timeout_s": timeout_s})
        self.config = load(self.config_path)
        self.matter = self.config.paths.matters / "9002.001"
        self.matter.mkdir()
        self.pdf = make_pdf(self.base / "book.pdf", pages)

    def run(self, *, number="9002.001", binder="scan", file=None):
        out, err = io.StringIO(), io.StringIO()
        code = intake.intake(self.config, number, binder, self.pdf if file is None else file,
                             out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def leftovers(self):
        return sorted(p.name for kind in ("records", "pages") if (self.matter / kind).is_dir()
                      for p in (self.matter / kind).iterdir())


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def wait_dead(pid, seconds=5):
    deadline = time.time() + seconds
    while time.time() < deadline and alive(pid):
        time.sleep(0.05)
    return not alive(pid)


def refusal_cases(base):
    """Each case: name, a function (Env) -> (code, stderr), the expected message part."""
    def plain(**kw):
        def case(env):
            code, _, err = env.run(**kw)
            return code, err
        return case

    def with_setup(setup, **env_kw):
        def case(env):
            setup(env)
            code, _, err = env.run()
            return code, err
        return case

    cases = []
    cases.append(("bad number", {}, plain(number="9002-001"), "matter number"))
    cases.append(("bad binder", {}, plain(binder="Scan One"), "binder name"))

    def missing(env):
        shutil.rmtree(env.matter)
        code, _, err = env.run()
        assert not env.matter.exists(), "intake created the matter folder"
        return code, err
    cases.append(("matter missing", {}, missing, "matter folder not found"))

    def into_checkout(env):
        target = Path(tempfile.mkdtemp(dir=ROOT, prefix=".intake-test-"))
        try:
            env.matter.rmdir()
            env.matter.symlink_to(target, target_is_directory=True)
            code, _, err = env.run()
            assert list(target.iterdir()) == [], "files were written under the checkout"
            return code, err
        finally:
            shutil.rmtree(target, ignore_errors=True)
    cases.append(("symlink into checkout", {}, into_checkout, "resolves outside the matters root"))

    def other_matter(env):
        other = env.config.paths.matters / "9002.002"
        other.mkdir()
        env.matter.rmdir()
        env.matter.symlink_to(other, target_is_directory=True)
        code, _, err = env.run()
        assert list(other.iterdir()) == [], "files were written into another matter"
        return code, err
    cases.append(("symlink to another matter", {}, other_matter, "resolves outside the matters root"))

    def exists(kind, name):
        def setup(env):
            (env.matter / kind / name).mkdir(parents=True)
        return setup
    cases.append(("records exists", {}, with_setup(exists("records", "scan")), "re-intake is refused"))
    cases.append(("pages exists", {}, with_setup(exists("pages", "scan")), "re-intake is refused"))
    cases.append(("pages tmp left over", {}, with_setup(exists("pages", "scan.tmp")), "scan.tmp"))

    def not_pdf(env):
        text = env.base / "notes.pdf"
        text.write_text("not a pdf at all")
        code, _, err = env.run(file=text)
        return code, err
    cases.append(("not a pdf", {}, not_pdf, "not a readable PDF"))

    def no_tool(env):
        env.config = load(write_config(env.base / "c2", ocr={"ocrmypdf": "no-such-ocrmypdf-tool"},
                                       matters=env.config.paths.matters))
        code, _, err = env.run()
        return code, err
    cases.append(("tool not found", {}, no_tool, "tool not found: no-such-ocrmypdf-tool"))
    cases.append(("ocrmypdf exit 7", {"mode": "fail"}, plain(), "ocrmypdf exit=7: boom from the stub"))
    cases.append(("sidecar 5 of 6", {"sidecar": "\f".join(["a"] * 5)}, plain(), "sidecar segments=5 pages=6"))
    cases.append(("skipped range placeholder",
                  {"sidecar": "a\f[OCR skipped on page(s) 2-3]\fb\fc\fd\fe"}, plain(), "skipped placeholder"))

    def short_output(env):
        make_pdf(env.stubs / "output.fixture", 5)
        code, _, err = env.run()
        return code, err
    cases.append(("page count differs", {"sidecar": "\f".join(["a"] * 6)}, short_output, "page count differs"))

    def timeout(env):
        started = time.time()
        code, _, err = env.run()
        pid = int((env.stubs / "grandchild.pid").read_text())
        assert wait_dead(pid), "the OCR process group was not killed"
        assert time.time() - started < 30
        return code, err
    cases.append(("timeout", {"mode": "hang", "timeout_s": 1}, timeout, "ocrmypdf timeout after 1 s"))
    return cases


def test_intake_refusals(tmp_path, capsys):
    cases = refusal_cases(tmp_path)
    assert len(cases) == 15
    passed, group_killed = 0, 0
    for index, (name, env_kw, case, message) in enumerate(cases):
        env = Env(tmp_path / f"case{index}", **env_kw)
        code, err = case(env)
        assert code == 2, (name, code, err)
        assert message in err, (name, err)
        assert env.leftovers() in ([], ["scan.tmp"] if name == "pages tmp left over" else
                                   ["scan"] if name in ("records exists", "pages exists") else []), (name, env.leftovers())
        if name == "ocrmypdf exit 7":
            assert not (env.stubs / "grandchild.pid").exists()
        group_killed += name == "timeout"
        passed += 1
    with capsys.disabled():
        print(f"intake_refusals={passed} of 15 group_killed={group_killed}")


def test_skipped_page_is_failed_and_listed(tmp_path, capsys):
    env = Env(tmp_path, sidecar="text one\f[skipped page]", pages=2)
    code, out, err = env.run()
    page2 = json.loads((env.matter / "pages" / "scan" / "002.json").read_text(encoding="utf-8"))
    binder = json.loads((env.matter / "pages" / "scan" / "binder.json").read_text(encoding="utf-8"))
    with capsys.disabled():
        print(f"skipped_page_exit={code}")
    assert code == 1, err
    assert (page2["status"], page2["reason"], page2["text"], page2["stamps"]) == ("failed", "ocr timeout", "", [])
    assert out.splitlines() == [
        "intake 9002.001 scan pages=2 ok=1 empty=0 failed=1 stamps=1 had_text=2 ocr_added=0",
        "  failed: scan/002 ocr timeout"]
    assert binder["open_ids"] == ["scan/002"] and binder["failed"] == 1


def test_born_digital_page_is_ok(tmp_path, capsys):
    env = Env(tmp_path, sidecar="", pages=1)
    code, out, err = env.run()
    record = json.loads((env.matter / "pages" / "scan" / "001.json").read_text(encoding="utf-8"))
    with capsys.disabled():
        print(f"born_digital_exit={code}")
    assert code == 0, err
    assert (record["had_text_layer"], record["ocr_added"], record["source"], record["status"]) == (
        True, False, "text", "ok")
    assert record["stamps"] == [{"raw": "KMR2342", "stamp": "KMR2342"}]
    assert record["id"] == "scan/001" and record["page"] == 1


def test_stamps_anywhere_on_the_page_raw_and_normalised_once(tmp_path):
    env = Env(tmp_path, sidecar="", pages=1)
    lines = ["Header MED 0001 mid page", "body line", "again MED-0001 and MED0001", "TWP7731", "closing words"]
    env.pdf.write_bytes(pdfsmoke.text_pdf(lines))
    assert env.run()[0] == 0
    record = json.loads((env.matter / "pages" / "scan" / "001.json").read_text(encoding="utf-8"))
    assert record["stamps"] == [{"raw": "MED 0001", "stamp": "MED0001"},
                                {"raw": "TWP7731", "stamp": "TWP7731"}]


def test_child_environment_and_flags(tmp_path):
    env = Env(tmp_path, sidecar="", pages=1)
    assert env.run()[0] == 0
    path = (env.stubs / "path.txt").read_text().strip()
    assert path.split(os.pathsep)[0] == str(env.stubs)
    tmpdir = (env.stubs / "tmpdir.txt").read_text().strip()
    assert tmpdir.startswith(str(env.matter / "records")) and tmpdir.endswith("scan.tmp/work")
    args = (env.stubs / "args.txt").read_text()
    for flag in ("--redo-ocr", "--output-type pdf", "-l eng", "--tesseract-timeout 180", "--sidecar"):
        assert flag in args, args
    assert not (env.matter / "records" / "scan" / "work").exists()
    assert env.leftovers() == ["scan", "scan"]


def test_exit_zero_without_output_is_refused(tmp_path):
    env = Env(tmp_path, mode="nooutput", pages=1)
    code, _, err = env.run()
    assert code == 2 and "wrote no output" in err
    assert env.leftovers() == []


def test_write_failure_is_exit_2_and_leaves_nothing(tmp_path, monkeypatch):
    env = Env(tmp_path, sidecar="", pages=1)

    def refuse(src, dst):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(intake.os, "rename", refuse)
    code, _, err = env.run()
    assert code == 2 and "cannot publish pages" in err
    assert env.leftovers() == []


def test_page_json_write_failure(tmp_path, monkeypatch):
    env = Env(tmp_path, sidecar="", pages=1)

    def refuse(path, data):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(intake, "_write_json", refuse)
    code, _, err = env.run()
    assert code == 2 and "cannot write" in err
    assert env.leftovers() == []


@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT, signal.SIGHUP])
def test_signal_kills_group_and_removes_work(tmp_path, signum):
    env = Env(tmp_path, mode="hang")
    code = ("import sys\nfrom casefile import cli\nsys.argv = ['casefile', 'intake', '--matter', '9002.001',"
            f" '--binder', 'scan', {str(env.pdf)!r}]\nraise SystemExit(cli.main())\n")
    proc = subprocess.Popen([sys.executable, "-c", code], cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=dict(os.environ, CASEFILE_CONFIG=str(env.config_path)))
    pidfile = env.stubs / "grandchild.pid"
    deadline = time.time() + 30
    while time.time() < deadline and not pidfile.exists():
        time.sleep(0.05)
    assert pidfile.exists(), "the stub never started"
    time.sleep(0.2)
    proc.send_signal(signum)
    proc.communicate(timeout=30)
    assert proc.returncode == 128 + signum
    assert wait_dead(int(pidfile.read_text())), "the OCR process group survived"
    assert env.leftovers() == [], "client bytes were left in the matter folder"


@pytest.mark.parametrize("kind", ["records", "pages"])
@pytest.mark.parametrize("target", ["other matter", "checkout", "dangling"])
def test_parent_folder_alias_is_refused_and_nothing_is_written(tmp_path, kind, target):
    env = Env(tmp_path, sidecar="", pages=1)
    cleanup = []
    if target == "other matter":
        real = env.config.paths.matters / "9002.002" / kind
        real.mkdir(parents=True)
    elif target == "checkout":
        real = Path(tempfile.mkdtemp(dir=ROOT, prefix=".intake-test-"))
        cleanup.append(real)
    else:
        real = env.base / "no-such-folder"
    try:
        (env.matter / kind).symlink_to(real, target_is_directory=True)
        code, _, err = env.run()
        written = sorted(p.name for p in real.rglob("*")) if real.exists() else []
        assert (code, written) == (2, []), (code, written, err)
        assert "records or pages folder" in err, err
        assert not (real / "scan.tmp").exists() and not (real / "scan").exists()
    finally:
        for folder in cleanup:
            shutil.rmtree(folder, ignore_errors=True)


@pytest.mark.parametrize("theirs", ["records", "pages"])
def test_failed_mkdir_does_not_remove_another_invocations_workspace(tmp_path, monkeypatch, theirs):
    env = Env(tmp_path, sidecar="", pages=1)
    original = intake._check_destination

    def racing(config, number, binder):
        matter_dir = original(config, number, binder)
        other = matter_dir / theirs / f"{binder}.tmp"
        other.mkdir(parents=True)
        (other / "client.txt").write_text("invented bytes of the first invocation")
        return matter_dir

    monkeypatch.setattr(intake, "_check_destination", racing)
    code, _, err = env.run()
    assert code == 2 and "cannot write" in err, (code, err)
    assert (env.matter / theirs / "scan.tmp" / "client.txt").read_text() == "invented bytes of the first invocation"
    mine = "pages" if theirs == "records" else "records"
    assert not (env.matter / mine / "scan.tmp").exists(), "this invocation left its own folder behind"


def test_interrupt_between_the_two_renames_rolls_back(tmp_path, monkeypatch):
    env = Env(tmp_path, sidecar="", pages=1)
    real_rename, calls = os.rename, []

    def interrupting(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            raise KeyboardInterrupt
        return real_rename(src, dst)

    monkeypatch.setattr(intake.os, "rename", interrupting)
    with pytest.raises(KeyboardInterrupt):
        env.run()
    assert len(calls) >= 2 and env.leftovers() == [], env.leftovers()
    monkeypatch.undo()
    assert env.run()[0] == 0, "re-intake is refused after the interrupt"
    assert env.leftovers() == ["scan", "scan"]


@pytest.mark.parametrize("mode", ["leak0", "leak7"])
def test_ocr_group_is_killed_after_a_normal_return(tmp_path, mode):
    env = Env(tmp_path, sidecar="", pages=1, mode=mode)
    code, _, err = env.run()
    assert code == (0 if mode == "leak0" else 2), (code, err)
    pid = int((env.stubs / "grandchild.pid").read_text())
    assert wait_dead(pid), "a detached child of ocrmypdf outlived intake"


@pytest.mark.parametrize("phase", ["page_texts", "write_json"])
def test_term_after_ocr_removes_both_tmp_folders(tmp_path, phase):
    env = Env(tmp_path, sidecar="", pages=1)
    code = ("import os, signal, sys, time\nfrom casefile import cli, intake\n"
            "phase = %r\ncalls = []\n"
            "def hit():\n    os.kill(os.getpid(), signal.SIGTERM)\n    time.sleep(10)\n"
            "orig_texts, orig_write = intake.page_texts, intake._write_json\n"
            "def texts(path):\n    calls.append(1)\n"
            "    if phase == 'page_texts' and len(calls) == 2: hit()\n    return orig_texts(path)\n"
            "def write(path, data):\n    if phase == 'write_json': hit()\n    return orig_write(path, data)\n"
            "intake.page_texts, intake._write_json = texts, write\n"
            "sys.argv = ['casefile', 'intake', '--matter', '9002.001', '--binder', 'scan', %r]\n"
            "raise SystemExit(cli.main())\n") % (phase, str(env.pdf))
    proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, timeout=60,
                          env=dict(os.environ, CASEFILE_CONFIG=str(env.config_path)))
    assert proc.returncode == 128 + signal.SIGTERM, (proc.returncode, proc.stderr[-300:])
    assert env.leftovers() == [], "client bytes were left in the matter folder"


def test_sidecar_outcomes_and_defaults():
    assert intake.sidecar_outcomes("a\f\f[skipped page]\n", 3) == [None, None, "ocr timeout"]
    with pytest.raises(intake.IntakeError):
        intake.sidecar_outcomes("a\fb", 3)
    assert all(f.default is MISSING and f.default_factory is MISSING for f in fields(intake.PageRecord))


def test_page_id_matches_matter_page_id():
    namespace = types.SimpleNamespace(binder="medical", number=3)
    assert matter.Page.page_id.fget(namespace) == "medical/003" == f"{'medical'}/{3:03d}"
    assert intake.PageRecord("9002.001", "medical", 3, "medical/003", [], "", False, False,
                             "none", "empty", "", "x").id == "medical/003"


@pytest.mark.ocr
def test_intake_fixture_with_real_tools(tmp_path, capsys):
    base = tmp_path.resolve()
    path = write_config(base)
    config = load(path)
    (config.paths.matters / "9002.001").mkdir()
    out, err = io.StringIO(), io.StringIO()
    code = intake.intake(config, "9002.001", "scan", SCANNED / "scanned.pdf", out=out, err=err)
    root = config.paths.matters / "9002.001"
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "pages" / "scan").glob("0*.json"))]
    binder = json.loads((root / "pages" / "scan" / "binder.json").read_text(encoding="utf-8"))
    work_removed = not (root / "records" / "scan" / "work").exists()
    tmp_left = len([p for kind in ("records", "pages") for p in (root / kind).iterdir() if p.name.endswith(".tmp")])
    summary = out.getvalue().splitlines()[0]
    stamps = sum(len(r["stamps"]) for r in records)
    with capsys.disabled():
        print(f"intake_fixture exit={code} pages={len(records)} ok={binder['ok']} empty={binder['empty']} "
              f"failed={binder['failed']} stamps={stamps} had_text={sum(r['had_text_layer'] for r in records)} "
              f"ocr_added={sum(r['ocr_added'] for r in records)} work_removed={int(work_removed)} tmp_left={tmp_left}")
        print(summary)
    assert code == 1, err.getvalue()
    assert summary == ("intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4")
    assert out.getvalue().splitlines()[1:] == ["  empty: scan/004"]
    assert [r["id"] for r in records] == [f"scan/{n:03d}" for n in range(1, 7)]
    assert work_removed and tmp_left == 0
    assert hashlib.sha256((root / "records" / "scan" / "source.pdf").read_bytes()).hexdigest() == binder["sha256"]
    assert all(set(s) == {"raw", "stamp"} for r in records for s in r["stamps"])
    assert [r["source"] for r in records] == ["ocr", "ocr", "ocr", "none", "text", "mixed"]
    assert binder["open_ids"] == ["scan/004"]
