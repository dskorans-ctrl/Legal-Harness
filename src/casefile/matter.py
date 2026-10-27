"""Load an invented benchmark matter: one text file per page, the Bates stamp alone on the last
line (D25)."""

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"
NUMBER_PATTERN = r"\d{4}\.\d{3}"
PAGE_NAME = re.compile(r"(\d{3})\.txt\Z")


class MatterError(ValueError):
    """A matter folder is incomplete or malformed; nothing is loaded."""


@dataclass(frozen=True)
class Page:
    binder: str
    number: int
    bates: str
    text: str

    @property
    def page_id(self) -> str:
        return f"{self.binder}/{self.number:03d}"


@dataclass(frozen=True)
class Matter:
    number: str
    root: Path
    pages: tuple[Page, ...]

    def page(self, bates: str) -> Page | None:
        """The first page whose stamp equals bates, else None."""
        for page in self.pages:
            if page.bates == bates:
                return page
        return None


def load(root) -> Matter:
    # 1. root = Path(root); meta = root / "matter.toml".
    root = Path(root)
    meta = root / "matter.toml"

    # 2. If not meta.is_file(): f"{meta}: matter.toml not found".
    if not meta.is_file():
        raise MatterError(f"{meta}: matter.toml not found")

    # 3. Load matter.toml.
    try:
        with meta.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise MatterError(f"{meta}: {exc}")

    # 4. Check keys.
    if set(data) != {"number", "binders"}:
        raise MatterError(f"{meta}: expected keys number and binders")

    # 5. Validate number.
    number = data["number"]
    if not isinstance(number, str) or not re.fullmatch(NUMBER_PATTERN, number):
        raise MatterError(f"{meta}: number must look like 9001.001")

    # 6. Validate binders.
    binders = data["binders"]
    if not isinstance(binders, list) or not binders or any(not isinstance(b, str) or not b for b in binders):
        raise MatterError(f"{meta}: binders must be a nonempty list of names")

    # 7. Check records directory.
    records = root / "records"
    try:
        names = sorted(p.name for p in records.iterdir())
    except OSError as exc:
        raise MatterError(f"{records}: {exc}")

    for name in names:
        if name not in binders:
            raise MatterError(f"{records}: unlisted binder folder {name}")

    # 8. Process pages.
    pages = []
    seen = set()

    for binder in binders:
        folder = records / binder

        # Check if folder exists and is a directory
        if not folder.is_dir():
            raise MatterError(f"{folder}: binder folder not found")

        try:
            entries = sorted(p.name for p in folder.iterdir())
        except OSError as exc:
            raise MatterError(f"{folder}: {exc}")

        # Check file names
        for index, name in enumerate(entries, start=1):
            expected_name = f"{index:03d}.txt"
            if name != expected_name:
                raise MatterError(f"{folder}: expected page files 001.txt, 002.txt, ...; found {name}")

            path = folder / name

            # Read text
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise MatterError(f"{path}: {exc}")

            lines = text.rstrip().splitlines()

            # Get stamp
            stamp = lines[-1].strip() if lines else ""

            # Validate stamp
            if not re.fullmatch(STAMP_PATTERN, stamp):
                raise MatterError(f"{path}: last line is not a Bates stamp")

            # Extract body
            body = "\n".join(lines[:-1]).strip()

            # Validate body
            if not body:
                raise MatterError(f"{path}: no page text above the stamp")

            # Check duplicates
            if stamp in seen:
                raise MatterError(f"{path}: duplicate Bates stamp {stamp}")
            seen.add(stamp)

            # Create Page
            pages.append(Page(binder, index, stamp, body))

    # 9. Return Matter
    return Matter(number, root, tuple(pages))
