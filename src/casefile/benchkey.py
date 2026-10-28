"""Load a benchmark answer key and check it against the matter's pages (D25)."""

from dataclasses import dataclass
from pathlib import Path

from casefile import dates, jsonrepair
from casefile.matter import Matter
from casefile.quotes import found_in, fold
from casefile.stamps import normalize as normalize_stamp

FLAG_KINDS = ("conflict", "gap")


class BenchKeyError(ValueError):
    """The answer key is malformed or disagrees with the pages."""


@dataclass(frozen=True)
class Fact:
    id: str
    cite: str
    quote: str
    text: str
    date: str = ""


@dataclass(frozen=True)
class Flag:
    id: str
    kind: str
    cites: tuple[str, ...]
    about: str


@dataclass(frozen=True)
class Key:
    facts: tuple[Fact, ...]
    flags: tuple[Flag, ...]


def load(path, matter: Matter) -> Key:
    """
    Loads a benchmark answer key from path and validates it against matter.
    """
    try:
        data = jsonrepair.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, jsonrepair.RepairError) as exc:
        raise BenchKeyError(f"{path}: {exc}") from (exc.__cause__ or exc)

    if not isinstance(data, dict) or set(data) != {"facts", "flags"}:
        raise BenchKeyError(f"{path}: expected object with keys facts and flags")

    facts_data = data.get("facts")
    if not isinstance(facts_data, list) or not facts_data:
        raise BenchKeyError(f"{path}: facts must be a nonempty list")

    flags_data = data.get("flags")
    if not isinstance(flags_data, list):
        raise BenchKeyError(f"{path}: flags must be a list")

    facts = []
    fact_ids_seen = set()
    fact_pairs_seen = {}
    for n, item in enumerate(facts_data, start=1):
        required_keys = {"id", "cite", "quote", "text", "date"}
        if not isinstance(item, dict) or set(item.keys()) != required_keys:
            raise BenchKeyError(f"{path}: fact {n}: expected keys id, cite, quote, text (nonempty strings)")

        fid = item["id"]
        if not isinstance(fid, str) or not fid:
            raise BenchKeyError(f"{path}: fact {n}: expected keys id, cite, quote, text (nonempty strings)")

        if fid in fact_ids_seen:
            raise BenchKeyError(f"{path}: fact {fid}: duplicate id")
        fact_ids_seen.add(fid)

        if not all(isinstance(item[k], str) and (k == "date" or item[k].strip()) for k in required_keys):
            raise BenchKeyError(f"{path}: fact {n}: expected keys id, cite, quote, text (nonempty strings)")

        cite = normalize_stamp(item["cite"])
        page = matter.page(cite)
        if page is None:
            raise BenchKeyError(f"{path}: fact {fid}: cite {cite} is not a page of matter {matter.number}")

        if not found_in(item["quote"], page.text):
            raise BenchKeyError(f"{path}: fact {fid}: quote not found on page {cite}")

        if item["date"] and (dates.parse(item["date"]) is None or not found_in(item["date"], page.text)):
            raise BenchKeyError(f"{path}: fact {fid}: date not written on page {cite} or not recognised")
        pair = (cite, fold(item["quote"]))
        if pair in fact_pairs_seen:
            raise BenchKeyError(f"{path}: fact {fid}: same cite and quote as fact {fact_pairs_seen[pair]}")
        fact_pairs_seen[pair] = fid

        facts.append(Fact(fid, cite, item["quote"], item["text"], item["date"]))

    flags = []
    flag_ids_seen = set()
    flag_pairs_seen = {}
    for n, item in enumerate(flags_data, start=1):
        required_keys = {"id", "kind", "cites", "about"}
        if not isinstance(item, dict) or set(item.keys()) != required_keys:
            raise BenchKeyError(f"{path}: flag {n}: expected keys id, kind, cites, about")

        gid = item["id"]
        if not isinstance(gid, str) or not gid:
            raise BenchKeyError(f"{path}: flag {n}: expected keys id, kind, cites, about")

        if gid in flag_ids_seen:
            raise BenchKeyError(f"{path}: flag {gid}: duplicate id")
        flag_ids_seen.add(gid)

        kind = item["kind"]
        if kind not in FLAG_KINDS:
            raise BenchKeyError(f"{path}: flag {gid}: kind must be conflict or gap")

        cites = item["cites"]
        if not isinstance(cites, list) or not cites:
            raise BenchKeyError(f"{path}: flag {gid}: cites must be a nonempty list of Bates stamps")

        if not all(isinstance(c, str) and c for c in cites):
            raise BenchKeyError(f"{path}: flag {gid}: cites must be a nonempty list of Bates stamps")

        cites = [normalize_stamp(c) for c in cites]
        for cite in cites:
            page = matter.page(cite)
            if page is None:
                raise BenchKeyError(f"{path}: flag {gid}: cite {cite} is not a page of matter {matter.number}")

        about = item["about"]
        if not isinstance(about, str) or not about.strip():
            raise BenchKeyError(f"{path}: flag {gid}: about must be a nonempty string")

        pair = (kind, frozenset(cites))
        if pair in flag_pairs_seen:
            raise BenchKeyError(f"{path}: flag {gid}: same kind and cites as flag {flag_pairs_seen[pair]}")
        flag_pairs_seen[pair] = gid

        flags.append(Flag(gid, kind, tuple(cites), about))

    return Key(tuple(facts), tuple(flags))
