"""Score a bench candidate against a matter's answer key: counts, not a percentage (D25)."""

from dataclasses import dataclass

from casefile.benchcandidate import Candidate
from casefile.benchkey import Key
from casefile.matter import Matter
from casefile.quotes import found_in, normalize


@dataclass(frozen=True)
class Score:
    key_total: int
    found: int
    invented: int
    extra: int
    flags_total: int
    flags_found: int
    flags_extra: int
    rules: int
    pages_in: int
    pages_failed: int
    missed_ids: tuple[str, ...]
    invented_quotes: tuple[str, ...]
    flags_missed_ids: tuple[str, ...]

    @property
    def missed(self) -> int:
        return self.key_total - self.found

    @property
    def flags_missed(self) -> int:
        return self.flags_total - self.flags_found

    @property
    def perfect(self) -> bool:
        return (self.missed == 0 and self.invented == 0 and self.flags_missed == 0
                and self.flags_extra == 0 and self.rules == 0 and self.pages_failed == 0)

    def line(self, matter_number: str) -> str:
        return (f"bench {matter_number} found={self.found} of {self.key_total} missed={self.missed} "
                f"invented={self.invented} extra={self.extra} flags={self.flags_found} of "
                f"{self.flags_total} flags_missed={self.flags_missed} flags_extra={self.flags_extra} "
                f"rules={self.rules} pages_failed={self.pages_failed} of {self.pages_in}")


def score(key: Key, candidate: Candidate, matter: Matter, rules, pages_failed: int) -> Score:
    matched = set()
    invented = []
    extra = 0

    for fact in candidate.facts:
        page = matter.page(fact.cite)
        if page is None or not found_in(fact.quote, page.text):
            invented.append(fact.quote[:60])
            continue

        hit = None
        for k in key.facts:
            if k.cite == fact.cite and normalize(k.quote) == normalize(fact.quote):
                hit = k
                break

        if hit is None:
            extra += 1
        else:
            matched.add(hit.id)

    key_sets = {(f.kind, frozenset(f.cites)): f.id for f in key.flags}
    cand_sets = {(f.kind, frozenset(f.cites)) for f in candidate.flags}

    flags_found = len(set(key_sets) & cand_sets)
    flags_extra = len(cand_sets - set(key_sets))

    texts_to_check = [f.text for f in candidate.facts] + [f.about for f in candidate.flags]
    rules_count = sum(len(rules.check(t, unit="text", stamped=True)) for t in texts_to_check)

    missed_ids = tuple(k.id for k in key.facts if k.id not in matched)

    flags_missed_ids = tuple(
        fid for key_tuple, fid in key_sets.items() if key_tuple not in cand_sets
    )

    return Score(
        key_total=len(key.facts),
        found=len(matched),
        invented=len(invented),
        extra=extra,
        flags_total=len(key.flags),
        flags_found=flags_found,
        flags_extra=flags_extra,
        rules=rules_count,
        pages_in=len(matter.pages),
        pages_failed=pages_failed,
        missed_ids=missed_ids,
        invented_quotes=tuple(invented),
        flags_missed_ids=flags_missed_ids
    )
