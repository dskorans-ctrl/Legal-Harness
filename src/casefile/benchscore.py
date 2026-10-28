"""Score a bench candidate against a matter's answer key: counts, not a percentage (D25)."""

from dataclasses import dataclass

from casefile.benchcandidate import Candidate
from casefile.benchkey import Key
from casefile.matter import Matter
from casefile import quotes
from casefile.stamps import normalize as normalize_stamp


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
    invented_facts: tuple[tuple[str, str, str], ...] = ()
    flags_extra_items: tuple[tuple[str, tuple[str, ...]], ...] = ()
    rule_hits: tuple[tuple[str, str, str], ...] = ()
    rungs: tuple[tuple[str, int], ...] = ()

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

    def line(self, matter_number: str, model: str) -> str:
        return (f"bench {matter_number} model={model} found={self.found} of {self.key_total} missed={self.missed} "
                f"invented={self.invented} extra={self.extra} flags={self.flags_found} of "
                f"{self.flags_total} flags_missed={self.flags_missed} flags_extra={self.flags_extra} "
                f"rules={self.rules} pages_failed={self.pages_failed} of {self.pages_in}")

    def details(self) -> list[str]:
        """Detail lines for a bench run, only the non-empty ones (critic M1)."""
        out = []
        if self.missed_ids:
            out.append("  missed: " + " ".join(self.missed_ids))
        for cite, quote, reason in self.invented_facts:
            out.append(f'  invented: {cite} "{quote}" ({reason})')
        if self.flags_missed_ids:
            out.append("  flags_missed: " + " ".join(self.flags_missed_ids))
        for kind, cites in self.flags_extra_items:
            out.append(f"  flags_extra: {kind} {','.join(cites)}")
        for rule_id, where, excerpt in self.rule_hits:
            out.append(f'  rules: {rule_id} {where} "{excerpt}"')
        if any(count for rung, count in self.rungs if rung != "exact"):
            out.append("  rungs: " + " ".join(f"{rung}={count}" for rung, count in self.rungs))
        return out


def score(key: Key, candidate: Candidate, matter: Matter, rules, pages_failed: int) -> Score:
    matched = set()
    invented = []
    invented_facts = []
    extra = 0
    flags_extra_items = []
    rungs = dict.fromkeys(("exact", "whitespace", "curly", "ocr"), 0)

    for fact in candidate.facts:
        cite = normalize_stamp(fact.cite)
        page = matter.page(cite)
        matched_quote = None if page is None else quotes.match(fact.quote, page.text)
        if matched_quote is None:
            reason = "no such page" if page is None else "quote not on the page"
            invented_facts.append((cite, fact.quote[:60], reason))
            invented.append(fact.quote[:60])
            continue
        rungs[matched_quote.rung] += 1

        hit = None
        for k in key.facts:
            if k.cite == cite and quotes.same(k.quote, fact.quote):
                hit = k
                break

        if hit is None:
            extra += 1
        else:
            matched.add(hit.id)

    key_sets = {(f.kind, frozenset(f.cites)): f.id for f in key.flags}
    cand_sets = {(f.kind, frozenset(normalize_stamp(c) for c in f.cites)) for f in candidate.flags}

    flags_found = len(set(key_sets) & cand_sets)

    flags_extra_items_list = []
    seen = set()
    for flag in candidate.flags:
        cites = frozenset(normalize_stamp(c) for c in flag.cites)
        flag_key = (flag.kind, cites)
        if flag_key in key_sets or flag_key in seen:
            continue
        seen.add(flag_key)
        flags_extra_items_list.append((flag.kind, tuple(sorted(cites))))
    flags_extra = len(flags_extra_items_list)

    checks = [(f.text, f.cite) for f in candidate.facts]
    checks += [(f.about, "flag " + ",".join(sorted({normalize_stamp(c) for c in f.cites}))) for f in candidate.flags]
    rule_hits = []
    for text, where in checks:
        for finding in rules.check(text, unit="text", stamped=True):
            rule_hits.append((finding.rule_id, where, finding.excerpt))
    rules_count = len(rule_hits)

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
        flags_missed_ids=flags_missed_ids,
        invented_facts=tuple(invented_facts),
        flags_extra_items=tuple(flags_extra_items_list),
        rule_hits=tuple(rule_hits),
        rungs=tuple(rungs.items())
    )
