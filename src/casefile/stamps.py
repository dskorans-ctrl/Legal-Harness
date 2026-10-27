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
    # A stamp is a whole token. It must not run on into a joined token at either end: after the match,
    # no letter or digit (any case), and no "-", "." or "/" followed by a letter or digit; before it,
    # the same two tests mirrored, so "QRL-2025-0418", "MED0001-A", "xMED0001" and "AB-MED0001" give
    # nothing while "MED0001." at the end of a sentence still matches (CX-7, H1).
    found: dict[str, Stamp] = {}
    for m in re.finditer((r"(?<![A-Za-z0-9])(?<![A-Za-z0-9][-./])(?:" + pattern + r")(?![A-Za-z0-9])(?![-./][A-Za-z0-9])"), text):
        stamp = normalize(m.group(0))
        if stamp not in found:
            found[stamp] = Stamp(m.group(0), stamp)
    return list(found.values())
