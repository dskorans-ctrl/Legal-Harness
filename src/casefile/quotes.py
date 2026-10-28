"""Compare quoted spans by the stage 4 ladder; retain stage 2 normalisation helpers."""

from dataclasses import dataclass
import re

from casefile.config import DEFAULTS
from casefile import stamps

CURLY = {"‘": "'", "’": "'", "“": '"', "”": '"'}


def normalize(text: str) -> str:
    for curly, straight in CURLY.items():
        text = text.replace(curly, straight)
    return " ".join(text.split()).casefold()


def found_in(quote: str, page_text: str) -> bool:
    quote = normalize(quote)
    return bool(quote) and quote in normalize(page_text)


@dataclass(frozen=True)
class Match:
    rung: str
    text: str


def fold(text: str) -> str:
    """Fold a quote without dropping lines; no page context is available here."""
    return normalize(re.sub(r"-[^\S\r\n]*(?:\r\n?|\n)[^\S\r\n]*", "", text))


def same(a: str, b: str) -> bool:
    return fold(a) == fold(b)


def _drop_line(line: str) -> bool:
    line = line.strip()
    if re.match(r"^page \d+ of \d+$", line, flags=re.IGNORECASE):
        return True
    found = stamps.find(line, DEFAULTS["ocr"]["stamp_pattern"])
    return len(found) == 1 and found[0].raw == line


def match(quote: str, page_text: str) -> Match | None:
    """Return the first matching rung and the quote text as compared at that rung."""
    if not quote.strip():
        return None
    for rung, quoted, page in (
        ("exact", quote, page_text),
        ("whitespace", " ".join(quote.split()), " ".join(page_text.split())),
        ("curly", normalize(quote), normalize(page_text)),
    ):
        if quoted in page:
            return Match(rung, quoted)
    page = "\n".join(line for line in page_text.splitlines() if not _drop_line(line))
    quoted = fold(quote)
    if quoted and quoted in fold(page):
        return Match("ocr", quoted)
    return None
