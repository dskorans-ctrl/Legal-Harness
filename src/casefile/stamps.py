"""Find Bates-style page stamps in text (stage 3): one shared pattern convention, first raw kept."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Stamp:
    raw: str
    stamp: str


def normalize(raw: str) -> str:
    return re.sub(r"[ -]", "", raw).upper()


def find(text: str, pattern: str) -> list[Stamp]:
    # The lookbehind refuses a match that starts inside a longer letter or digit run; the lookahead
    # refuses one that stops inside it (any case), so a truncated token is never recorded (CX-7).
    found: dict[str, Stamp] = {}
    for m in re.finditer(r"(?<![A-Z0-9])(?:" + pattern + ")(?![A-Za-z0-9])", text):
        stamp = normalize(m.group(0))
        if stamp not in found:
            found[stamp] = Stamp(m.group(0), stamp)
    return list(found.values())
