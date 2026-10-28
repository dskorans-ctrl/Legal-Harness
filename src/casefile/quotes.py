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
    return _bounded(quote, normalize(page_text))


def _bounded(quote: str, page: str) -> bool:
    """Require both edges of a hit to be outside letters and digits."""
    start = 0
    while quote and (index := page.find(quote, start)) >= 0:
        end = index + len(quote)
        if (index == 0 or not page[index - 1].isalnum()) and (end == len(page) or not page[end].isalnum()):
            return True
        start = index + 1
    return False


@dataclass(frozen=True)
class Match:
    rung: str
    text: str


def fold(text: str) -> str:
    """Fold a quote without dropping lines; no page context is available here."""
    def join_word(hit):
        before = text[hit.start() - 1:hit.start()]
        after = text[hit.end():hit.end() + 1]
        return "" if before.isalpha() and after.isalpha() else hit[0]

    return normalize(re.sub(r"-[^\S\r\n]*(?:\r\n?|\n)[^\S\r\n]*", join_word, text))


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
        if _bounded(quoted, page):
            return Match(rung, quoted)
    page = "\n".join(line for line in page_text.splitlines() if not _drop_line(line))
    quoted = fold(quote)
    if _bounded(quoted, fold(page)):
        return Match("ocr", quoted)
    return None
