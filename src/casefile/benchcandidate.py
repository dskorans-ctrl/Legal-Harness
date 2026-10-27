"""Parse a bench run's answer into facts and flags; shape only, nothing is scored here (D25)."""

from dataclasses import dataclass
import json

FLAG_KINDS = ("conflict", "gap")


class CandidateError(ValueError):
    """A run's answer is not in the candidate shape; nothing is scored."""


@dataclass(frozen=True)
class CandidateFact:
    cite: str
    quote: str
    text: str


@dataclass(frozen=True)
class CandidateFlag:
    kind: str
    cites: tuple[str, ...]
    about: str


@dataclass(frozen=True)
class Candidate:
    facts: tuple[CandidateFact, ...]
    flags: tuple[CandidateFlag, ...]


EMPTY = Candidate((), ())


def parse(data) -> Candidate:
    """Parse a JSON object representing a candidate into Candidate objects."""

    # Check overall structure
    if not isinstance(data, dict) or set(data) != {"facts", "flags"} or \
       not isinstance(data["facts"], list) or not isinstance(data["flags"], list):
        raise CandidateError("expected a JSON object with keys facts and flags")

    facts = []
    # Process facts
    for n, item in enumerate(data["facts"], start=1):
        if not isinstance(item, dict) or set(item) != {"cite", "quote", "text"}:
            raise CandidateError(f"fact {n}: expected keys cite, quote, text (strings)")

        if not all(isinstance(item[k], str) for k in ["cite", "quote", "text"]):
            raise CandidateError(f"fact {n}: expected keys cite, quote, text (strings)")

        facts.append(CandidateFact(item["cite"], item["quote"], item["text"]))

    flags = []
    # Process flags
    for n, item in enumerate(data["flags"], start=1):
        if not isinstance(item, dict) or set(item) != {"kind", "cites", "about"}:
            raise CandidateError(f"flag {n}: expected keys kind, cites, about")

        kind = item["kind"]
        cites = item["cites"]
        about = item["about"]

        if kind not in FLAG_KINDS:
            raise CandidateError(f"flag {n}: kind must be conflict or gap")

        if not isinstance(cites, list) or not cites or not all(isinstance(s, str) for s in cites):
            raise CandidateError(f"flag {n}: cites must be a nonempty list of strings")

        if not isinstance(about, str):
            raise CandidateError(f"flag {n}: about must be a string")

        flags.append(CandidateFlag(kind, tuple(cites), about))

    # Return result
    return Candidate(tuple(facts), tuple(flags))


def parse_text(text: str) -> Candidate:
    """Parse a JSON string into a Candidate object."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CandidateError(f"not JSON: {exc}") from exc
    return parse(data)
