"""Read a matter's benchmark or intake pages without following matter aliases."""

from dataclasses import dataclass
from pathlib import Path
import re

from casefile import jsonrepair, matter, stamps
from casefile.intake import BINDER_PATTERN
from casefile.pathguard import classify


class PagesError(ValueError):
    """The matter's pages cannot be read safely or completely."""


@dataclass(frozen=True)
class PageSet:
    number: str
    pages: tuple[matter.Page, ...]
    open_pages: tuple[tuple[str, tuple[str, ...], str, str], ...]


def _plain(path, *, folder):
    if path.is_symlink() or (path.exists() and
                            (not path.is_dir() if folder else not path.is_file())):
        raise PagesError(f"{path}: must be a plain {'folder' if folder else 'file'}, not a link")


def _json(path):
    _plain(path, folder=False)
    try:
        data = jsonrepair.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data
    except (OSError, ValueError) as exc:
        raise PagesError(f"{path}: {exc}") from exc


def _record(path, number, binder, stamp_pattern):
    data = _json(path)
    try:
        page = data["page"]
        if type(page) is not int or page < 1 or path.name != f"{page:03d}.json":
            raise ValueError("page must match its numbered file")
        if data["matter"] != number or data["binder"] != binder or data["id"] != f"{binder}/{page:03d}":
            raise ValueError("matter, binder and id must match the matter folder and page")
        if data["status"] not in ("ok", "empty", "failed"):
            raise ValueError("status must be ok, empty or failed")
        if not isinstance(data["text"], str) or not isinstance(data["reason"], str):
            raise ValueError("text and reason must be strings")
        if data["status"] == "ok" and not data["text"].strip():
            raise ValueError("an ok page must contain text")
        if data["status"] != "ok" and not data["reason"].strip():
            raise ValueError("an open page must have a reason")
        if not isinstance(data["stamps"], list):
            raise ValueError("stamps must be a list")
        found = []
        for entry in data["stamps"]:
            if (not isinstance(entry, dict) or set(entry) != {"raw", "stamp"}
                    or not isinstance(entry["raw"], str) or not isinstance(entry["stamp"], str)
                    or not re.fullmatch(stamp_pattern, entry["raw"])
                    or stamps.normalize(entry["raw"]) != entry["stamp"]):
                raise ValueError("stamps must hold matching raw and normalised stamps")
            found.append(entry["stamp"])
        result = matter.Page(binder, page, data["text"], tuple(found))
        return result, data["status"], data["reason"]
    except (KeyError, TypeError, ValueError) as exc:
        raise PagesError(f"{path}: {exc}") from exc


def load(matters_root, number, stamp_pattern) -> PageSet:
    if not isinstance(number, str) or not re.fullmatch(matter.NUMBER_PATTERN, number):
        raise PagesError(f"{Path(matters_root) / str(number)}: not a matter number (expected 9001.001)")
    root = Path(matters_root).resolve()
    folder = root / number
    checkout = Path(__file__).resolve().parents[2]
    verdict, _ = classify(str(folder), str(checkout))
    if verdict != "outside" or folder.resolve() != folder:
        raise PagesError(f"{folder}: matter folder resolves outside its own location under the matters root")
    if not folder.is_dir():
        raise PagesError(f"matter folder not found: {folder}")
    for name in ("records", "pages", "outputs"):
        _plain(folder / name, folder=True)
    for name in ("casefile.jsonl", "matter.toml"):
        _plain(folder / name, folder=False)
    metadata, intake = folder / "matter.toml", folder / "pages"
    if metadata.exists() and intake.exists():
        raise PagesError(f"{folder}: ambiguous layout: both matter.toml and pages exist")
    if metadata.exists():
        try:
            for binder in (folder / "records").iterdir():
                if binder.name.startswith("."):
                    continue
                _plain(binder, folder=True)
                for path in binder.iterdir():
                    if path.name.startswith("."):
                        continue
                    _plain(path, folder=False)
            loaded = matter.load(folder)
            if loaded.number != number:
                raise PagesError(f"{metadata}: number differs from matter folder {number}")
            return PageSet(number, loaded.pages, ())
        except (OSError, matter.MatterError) as exc:
            raise PagesError(f"{folder}: {exc}") from exc
    if not intake.exists():
        raise PagesError(f"no pages for matter {number} under {root}: run casefile intake first")
    pages, opened = [], []
    try:
        for binder in sorted(intake.iterdir()):
            if binder.name.startswith("."):
                continue
            _plain(binder, folder=True)
            if not re.fullmatch(BINDER_PATTERN, binder.name):
                raise PagesError(f"{binder}: invalid binder folder name")
            meta = _json(binder / "binder.json")
            records = sorted(path for path in binder.iterdir()
                             if path.name != "binder.json" and not path.name.startswith("."))
            if type(meta.get("pages")) is not int or meta["pages"] != len(records):
                raise PagesError(f"{binder / 'binder.json'}: pages count differs from {len(records)} records")
            for path in records:
                if not re.fullmatch(r"\d{3}\.json", path.name):
                    raise PagesError(f"{path}: expected a numbered page JSON file")
                page, status, reason = _record(path, number, binder.name, stamp_pattern)
                if status == "ok":
                    pages.append(page)
                else:
                    opened.append((page.page_id, page.stamps, status, reason))
    except OSError as exc:
        raise PagesError(f"{intake}: {exc}") from exc
    return PageSet(number, tuple(pages), tuple(opened))
