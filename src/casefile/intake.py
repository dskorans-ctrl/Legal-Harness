"""Stage 3 intake (D27): one scanned or digital PDF becomes page records with page IDs.

ocrmypdf runs once per PDF in its own process group inside the matter folder; page text is read
with pypdf from its output; the sidecar says which pages Tesseract skipped. A page with no text,
and a skipped page, are listed and never counted as read. Nothing is published until every page
record is built, then two folders are renamed into place.
"""

from dataclasses import asdict, dataclass
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess

from pypdf import PdfReader

from . import stamps as stamp_finder
from .matter import NUMBER_PATTERN
from .pathguard import classify

PAGE_TIMEOUT_S = 180            # tesseract per page (T-14); a timeout is reported, never retried
OCR_FLAGS = ["--redo-ocr", "--output-type", "pdf", "-l", "eng"]
BINDER_PATTERN = r"[a-z][a-z0-9-]{0,39}"
SKIPPED_PAGE = "[skipped page]"
SKIPPED_RANGE = "[OCR skipped on page(s)"
OCR_TIMEOUT_REASON = "ocr timeout"


class IntakeError(Exception):
    """Intake cannot run (exit 2); the message says why."""


@dataclass
class PageRecord:
    matter: str
    binder: str
    page: int
    id: str
    stamps: list
    text: str
    had_text_layer: bool
    ocr_added: bool
    source: str
    status: str            # no default: every page states ok, empty or failed (#R01-OC-M2)
    reason: str
    sha256: str


def squash(text: str) -> str:
    return " ".join(text.split())


def page_texts(pdf_path) -> list[str]:
    """The text pypdf extracts from each page, as extracted."""
    reader = PdfReader(str(pdf_path))
    return [page.extract_text() or "" for page in reader.pages]


def sidecar_outcomes(sidecar_text: str, pages: int) -> list:
    """None for a page ocrmypdf read, 'ocr timeout' for a skipped one; refuse anything unclear."""
    if SKIPPED_RANGE in sidecar_text:
        raise IntakeError("sidecar holds an OCR skipped placeholder; ocrmypdf declined pages")
    parts = sidecar_text.split("\f")
    if len(parts) != pages:
        raise IntakeError(f"sidecar segments={len(parts)} pages={pages}")
    return [OCR_TIMEOUT_REASON if part.strip() == SKIPPED_PAGE else None for part in parts]


def ocr_command(ocrmypdf, src, dst, sidecar, extra=()) -> list[str]:
    """The one ocrmypdf command line; the doctor and the probe use it too."""
    return [str(ocrmypdf), *OCR_FLAGS, "--sidecar", str(sidecar),
            "--tesseract-timeout", str(PAGE_TIMEOUT_S), *extra, str(src), str(dst)]


def _kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def popen_runner(command, env, timeout_s):
    """Run in a new session, kill the whole group on timeout, interrupt or hangup."""
    proc = subprocess.Popen(command, env=env, start_new_session=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(number, frame):
        _kill_group(proc)
        raise SystemExit(128 + number)

    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
    previous = {number: signal.signal(number, stop) for number in signals}
    try:
        try:
            _, err = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            proc.wait()
            raise IntakeError(f"ocrmypdf timeout after {timeout_s} s") from None
        except BaseException:
            _kill_group(proc)
            proc.wait()
            raise
        return proc.returncode, err.decode("utf-8", errors="replace")
    finally:
        # A normal return does not end the group: a child with redirected streams may outlive its
        # parent (CX-5). The pid is the group id and was only just reaped, so this is safe to send.
        _kill_group(proc)
        for number, handler in previous.items():
            signal.signal(number, handler)


def _version(executable, env) -> str:
    try:
        result = subprocess.run([executable, "--version"], capture_output=True, text=True,
                                timeout=30, check=False, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise IntakeError(f"{executable} --version failed: {exc}") from exc
    lines = (result.stdout or result.stderr).strip().splitlines()
    if result.returncode != 0 or not lines or not lines[0].split():
        raise IntakeError(f"{executable} --version exit={result.returncode}")
    return lines[0].split()[-1]


def run_ocr(ocr_config, src, dst, sidecar, *, workdir, timeout_s, runner=None, extra=()) -> dict:
    """Run ocrmypdf with intake's flags; return the tool versions. Raises IntakeError."""
    found = {}
    for name in ("tesseract", "ocrmypdf"):
        path = shutil.which(getattr(ocr_config, name))
        if path is None:
            raise IntakeError(f"tool not found: {getattr(ocr_config, name)}")
        found[name] = path
    src, dst, sidecar, workdir = (Path(p).resolve() for p in (src, dst, sidecar, workdir))
    # ocrmypdf finds tesseract by PATH, so the configured tesseract's folder goes first.
    env = dict(os.environ, TMPDIR=str(workdir),
               PATH=str(Path(found["tesseract"]).parent) + os.pathsep + os.environ.get("PATH", ""))
    versions = {name: _version(path, env) for name, path in found.items()}
    command = ocr_command(found["ocrmypdf"], src, dst, sidecar, extra)
    code, err = (runner or popen_runner)(command, env, timeout_s)
    if code != 0:
        raise IntakeError(f"ocrmypdf exit={code}: {err.strip()[-300:]}")
    if not dst.is_file() or not sidecar.is_file():
        raise IntakeError("ocrmypdf exited 0 but wrote no output or no sidecar")
    return versions


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


@contextmanager
def _exit_on_signals():
    """INT, TERM and HUP become SystemExit(128+n) for the whole intake, so cleanup always runs (CX-6)."""
    def stop(number, frame):
        raise SystemExit(128 + number)

    try:
        previous = {n: signal.signal(n, stop) for n in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    except ValueError:                       # not the main thread: the caller owns signals
        yield
        return
    try:
        yield
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


def _publish(tmp_records, tmp_pages, records, pages):
    os.rename(tmp_records, records)
    try:
        os.rename(tmp_pages, pages)
    except BaseException:
        # Any exit between the two renames (an interrupt included) puts records back (CX-3).
        os.rename(records, tmp_records)
        raise


def _check_destination(config, number, binder):
    matters = config.paths.matters
    matter_dir = matters / number
    if not matter_dir.is_dir():
        raise IntakeError(f"matter folder not found: {matter_dir}")
    checkout = Path(__file__).resolve().parents[2]
    verdict, _ = classify(str(matter_dir), str(checkout))
    if verdict != "outside" or matter_dir.resolve() != matters / number:
        raise IntakeError("matter folder resolves outside the matters root")
    matter_dir = matter_dir.resolve()
    for kind in ("records", "pages"):
        parent = matter_dir / kind
        # The parent must be this matter's own plain folder: a link would carry the write into
        # another matter or the checkout, and a dangling one would be written through (CX-1).
        if os.path.lexists(parent) and (parent.is_symlink() or not parent.is_dir()
                                        or parent.resolve() != parent):
            raise IntakeError(f"{parent} is not a plain folder inside the matter; "
                              "the records or pages folder must not be a link")
        for name in (binder, binder + ".tmp"):
            target = matter_dir / kind / name
            if os.path.lexists(target):
                raise IntakeError(f"{target} already exists; re-intake is refused")
    return matter_dir


def intake(config, number, binder, file, *, out, err, runner=None) -> int:
    try:
        return _intake(config, number, binder, file, out, runner)
    except IntakeError as exc:
        print(f"intake: cannot run: {exc}", file=err)
        return 2


def _intake(config, number, binder, file, out, runner) -> int:
    with _exit_on_signals():
        return _intake_body(config, number, binder, file, out, runner)


def _intake_body(config, number, binder, file, out, runner) -> int:
    if not re.fullmatch(NUMBER_PATTERN, number):
        raise IntakeError(f"matter number must look like 9002.001, got {number!r}")
    if not re.fullmatch(BINDER_PATTERN, binder):
        raise IntakeError(f"binder name must match {BINDER_PATTERN}, got {binder!r}")
    source = Path(file)
    try:
        data = source.read_bytes()
        count = len(PdfReader(str(source)).pages)
    except Exception as exc:
        raise IntakeError(f"not a readable PDF: {source}: {exc}") from exc
    if count == 0:
        raise IntakeError(f"not a readable PDF: {source}: no pages")
    matter_dir = _check_destination(config, number, binder)
    sha = hashlib.sha256(data).hexdigest()
    tmp_records, tmp_pages = (matter_dir / "records" / f"{binder}.tmp",
                              matter_dir / "pages" / f"{binder}.tmp")
    final_records, final_pages = matter_dir / "records" / binder, matter_dir / "pages" / binder
    published = False
    created = []          # only the folders this invocation made; another one's are never removed (CX-2)
    try:
        for folder in (tmp_records, tmp_pages):
            folder.parent.mkdir(exist_ok=True)
            folder.mkdir()
            created.append(folder)
        work = tmp_records / "work"
        work.mkdir()
        (tmp_records / "source.pdf").write_bytes(data)
        before = page_texts(tmp_records / "source.pdf")
        try:
            versions = run_ocr(config.ocr, tmp_records / "source.pdf", tmp_records / "ocr.pdf",
                               tmp_records / "sidecar.txt", workdir=work,
                               timeout_s=config.ocr.timeout_s, runner=runner)
        finally:
            shutil.rmtree(work, ignore_errors=True)
        try:
            sidecar = (tmp_records / "sidecar.txt").read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise IntakeError(f"sidecar is not UTF-8: {exc}") from exc
        try:
            after = page_texts(tmp_records / "ocr.pdf")
        except Exception as exc:
            raise IntakeError(f"cannot read ocr output: {exc}") from exc
        if len(after) != count or len(before) != count:
            raise IntakeError(f"page count differs: input {count} output {len(after)}")
        outcomes = sidecar_outcomes(sidecar, count)
        records = []
        for index, (old, new, outcome) in enumerate(zip(before, after, outcomes), start=1):
            had = bool(squash(old))
            added = squash(old) != squash(new)
            if outcome is not None:
                status, reason, text = "failed", outcome, ""
            elif not squash(new):
                status, reason, text = "empty", "", ""
            else:
                status, reason, text = "ok", "", new
            found = [{"raw": s.raw, "stamp": s.stamp}
                     for s in stamp_finder.find(text, config.ocr.stamp_pattern)]
            source_kind = ("mixed" if had and added else "text" if had
                           else "ocr" if added else "none")
            records.append(PageRecord(number, binder, index, f"{binder}/{index:03d}", found, text,
                                      had, added, source_kind, status, reason, sha))
        for record in records:
            _write_json(tmp_pages / f"{record.page:03d}.json", asdict(record))
        counts = {key: sum(r.status == key for r in records) for key in ("ok", "empty", "failed")}
        _write_json(tmp_pages / "binder.json", {
            "matter": number, "binder": binder, "file": source.name, "sha256": sha, "pages": count,
            **counts, "open_ids": [r.id for r in records if r.status != "ok"], "tools": versions,
            "args": [*OCR_FLAGS, "--tesseract-timeout", str(PAGE_TIMEOUT_S)],
            "written": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        try:
            _publish(tmp_records, tmp_pages, final_records, final_pages)
        except OSError as exc:
            raise IntakeError(f"cannot publish pages: {exc}") from exc
        published = True
    except OSError as exc:
        raise IntakeError(f"cannot write: {exc}") from exc
    finally:
        if not published:
            for folder in created:
                shutil.rmtree(folder, ignore_errors=True)
    print(f"intake {number} {binder} pages={count} ok={counts['ok']} empty={counts['empty']} "
          f"failed={counts['failed']} stamps={sum(len(r.stamps) for r in records)} "
          f"had_text={sum(r.had_text_layer for r in records)} "
          f"ocr_added={sum(r.ocr_added for r in records)}", file=out)
    for record in records:
        if record.status == "empty":
            print(f"  empty: {record.id}", file=out)
        elif record.status == "failed":
            print(f"  failed: {record.id} {record.reason}", file=out)
    return 0 if counts["ok"] == count else 1
