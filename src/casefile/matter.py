"""Load an invented benchmark matter: one text file per page, the Bates stamp alone on the last
line (D25)."""

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

from casefile.stamps import normalize

STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"
NUMBER_PATTERN = r"\d{4}\.\d{3}"
PAGE_NAME = re.compile(r"(\d{3})\.txt\Z")


class MatterError(ValueError):
    """A matter folder is incomplete or malformed; nothing is loaded."""


@dataclass(frozen=True)
class Page:
    binder: str
    number: int
    text: str
    stamps: tuple[str, ...]

    @property
    def page_id(self) -> str:
        return f"{self.binder}/{self.number:03d}"


@dataclass(frozen=True)
class Matter:
    number: str
    root: Path
    pages: tuple[Page, ...]

    def page(self, cite: str) -> Page | None:
        """The first page that carries the cite as one of its stamps, compared by normalised form
        (MED0001, MED 0001 and MED-0001 are one stamp, owner Q40), else None."""
        wanted = normalize(cite)
        for page in self.pages:
            if wanted in page.stamps:
                return page
        return None


def load(root) -> Matter:
    root = Path(root)
    meta = root / "matter.toml"
    if not meta.is_file():
        raise MatterError(f"{meta}: matter.toml not found")

    try:
        with meta.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise MatterError(f"{meta}: {exc}") from exc

    if set(data) != {"number", "binders"}:
        raise MatterError(f"{meta}: expected keys number and binders")

    number = data["number"]
    if not isinstance(number, str) or not re.fullmatch(NUMBER_PATTERN, number):
        raise MatterError(f"{meta}: number must look like 9001.001")

    binders = data["binders"]
    if not isinstance(binders, list) or not binders or any(not isinstance(b, str) or not b for b in binders):
        raise MatterError(f"{meta}: binders must be a nonempty list of names")
    if len(set(binders)) != len(binders):
        raise MatterError(f"{meta}: binders must be distinct")

    # A name that starts with a dot (a Finder .DS_Store) is not a record; it is the only ignore rule.
    records = root / "records"
    try:
        names = sorted(p.name for p in records.iterdir() if not p.name.startswith("."))
    except OSError as exc:
        raise MatterError(f"{records}: {exc}") from exc

    for name in names:
        if name not in binders:
            raise MatterError(f"{records}: unlisted binder folder {name}")

    # Every listing is checked before any page is read, so a stray file is named first.
    listings = {}
    for binder in binders:
        folder = records / binder
        if not folder.is_dir():
            raise MatterError(f"{folder}: binder folder not found")
        try:
            entries = sorted(p.name for p in folder.iterdir() if not p.name.startswith("."))
        except OSError as exc:
            raise MatterError(f"{folder}: {exc}") from exc
        for index, name in enumerate(entries, start=1):
            if name != f"{index:03d}.txt":
                raise MatterError(f"{folder}: expected page files 001.txt, 002.txt, ...; found {name}")
        listings[binder] = entries

    pages = []
    seen = set()
    for binder, entries in listings.items():
        folder = records / binder
        for index, name in enumerate(entries, start=1):
            path = folder / name
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise MatterError(f"{path}: {exc}") from exc

            lines = text.rstrip().splitlines()
            stamp = lines[-1].strip() if lines else ""
            if not re.fullmatch(STAMP_PATTERN, stamp):
                raise MatterError(f"{path}: last line is not a Bates stamp")

            body = "\n".join(lines[:-1]).strip()
            if not body:
                raise MatterError(f"{path}: no page text above the stamp")

            if normalize(stamp) in seen:
                raise MatterError(f"{path}: duplicate Bates stamp {stamp}")
            seen.add(normalize(stamp))

            pages.append(Page(binder, index, body, (normalize(stamp),)))

    return Matter(number, root, tuple(pages))
