"""Append-only case file events and exact-identity views (D40)."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from casefile import jsonrepair, quotes, stamps
from casefile.matter import Page


class CaseFileError(ValueError):
    """The case file cannot be read or safely appended."""


def _now():
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Event:
    """A pending event has seq=0; payload keeps a flag's kind separate from the event kind."""

    kind: str
    payload: dict
    seq: int = 0
    at: str = field(default_factory=_now)
    prev: str = ""


@dataclass
class Fact:
    id: str
    quote: str
    cites: list[str]
    page_ids: list[str]
    readings: list[str]


@dataclass
class Flag:
    id: str
    kind: str
    cites: list[str]
    page_ids: list[str]
    abouts: list[str]


CHANGE_KINDS = ("fact", "cite", "reading", "flag", "about")
FIELDS = {
    "fact": {"id", "cite", "page_id", "quote", "text", "run_id"},
    "cite": {"fact", "cite", "page_id", "run_id"},
    "reading": {"fact", "text", "run_id"},
    "flag": {"id", "kind", "cites", "page_ids", "about", "run_id"},
    "about": {"flag", "about", "run_id"},
    "run": {"run_id", "job", "card", "card_version", "pages", "ok", "read", "uncited", "failed"},
    "output": {"name", "path", "built_from_seq", "facts", "conflicts", "gaps", "open"},
}


def _bytes(event):
    return json.dumps({"seq": event.seq, "at": event.at, "prev": event.prev,
                       "kind": event.kind, "payload": event.payload},
                      ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


@dataclass
class CaseFile:
    """Events in sequence order; views preserve the order of the first occurrence."""

    events: list[Event] = field(default_factory=list)
    torn: int = 0

    @property
    def last_seq(self):
        return self.events[-1].seq if self.events else 0

    def extend(self, events):
        """Apply pending events in memory, as used by a benchmark with no matter writes."""
        previous = hashlib.sha256(_bytes(self.events[-1])).hexdigest() if self.events else ""
        for event in events:
            event = replace(event, seq=self.last_seq + 1, prev=previous)
            self.events.append(event)
            previous = hashlib.sha256(_bytes(event)).hexdigest()

    @property
    def facts(self):
        found = {}
        for event in self.events:
            data = event.payload
            if event.kind == "fact":
                found[data["id"]] = Fact(data["id"], data["quote"], [data["cite"]],
                                         [data["page_id"]], [data["text"]])
            elif event.kind == "cite":
                fact = found[data["fact"]]
                fact.cites.append(data["cite"])
                fact.page_ids.append(data["page_id"])
            elif event.kind == "reading":
                found[data["fact"]].readings.append(data["text"])
        return list(found.values())

    @property
    def flags(self):
        found = {}
        for event in self.events:
            data = event.payload
            if event.kind == "flag":
                found[data["id"]] = Flag(data["id"], data["kind"], list(data["cites"]),
                                         list(data["page_ids"]), [data["about"]])
            elif event.kind == "about":
                found[data["flag"]].abouts.append(data["about"])
        return list(found.values())

    @property
    def runs(self):
        return [event.payload for event in self.events if event.kind == "run"]

    @property
    def outputs(self):
        return [event.payload for event in self.events if event.kind == "output"]

    def changed_since(self, seq):
        return {kind: sum(event.kind == kind and event.seq > seq for event in self.events)
                for kind in CHANGE_KINDS}

    def stale_outputs(self):
        latest = {output["name"]: output for output in self.outputs}
        return [name for name, output in latest.items()
                if any(event.kind in CHANGE_KINDS and event.seq > output["built_from_seq"]
                       for event in self.events)]


def _broken(line):
    return CaseFileError(f"case file chain broken at line {line}; the file was edited or truncated")


def _read(path):
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return b""
    except OSError as exc:
        raise CaseFileError(f"cannot read case file {path}: {exc}") from exc


def _decode(raw):
    casefile = CaseFile()
    previous = ""
    lines = raw.split(b"\n")
    for index, line in enumerate(lines, start=1):
        if index == len(lines) and not line:
            break
        try:
            # A complete object without its newline is still an event. Strict decoding below
            # refuses duplicate keys even when the ordinary decoder can parse that object.
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError("not an object")
        except (ValueError, UnicodeDecodeError, RecursionError) as exc:
            if index == len(lines):
                casefile.torn = len(line)
                break
            raise _broken(index) from exc
        try:
            obj = jsonrepair.loads(line.decode("utf-8"))
            if (set(obj) != {"seq", "at", "prev", "kind", "payload"}
                    or type(obj["seq"]) is not int or obj["seq"] != index
                    or obj["prev"] != previous or not isinstance(obj["at"], str)
                    or not isinstance(obj["kind"], str) or obj["kind"] not in FIELDS
                    or not isinstance(obj["payload"], dict)
                    or set(obj["payload"]) != FIELDS[obj["kind"]]):
                raise _broken(index)
            casefile.events.append(Event(obj["kind"], obj["payload"], obj["seq"], obj["at"], obj["prev"]))
        except (jsonrepair.RepairError, UnicodeDecodeError) as exc:
            raise _broken(index) from exc
        previous = hashlib.sha256(line).hexdigest()
    return casefile


def load(path) -> CaseFile:
    return _decode(_read(Path(path)))


def append(path, events) -> CaseFile:
    """Validate the existing chain, recover an incomplete tail, and fsync appended events.

    The caller must serialize writers to this matter; the CLI lock belongs to stage 8.
    """
    path = Path(path)
    raw = _read(path)
    casefile = _decode(raw)
    pending = list(events)
    if not pending:
        return casefile
    complete = raw[:-casefile.torn] if casefile.torn else raw
    previous = hashlib.sha256(complete.rstrip(b"\n").rsplit(b"\n", 1)[-1]).hexdigest() if complete else ""
    additions = []
    for event in pending:
        event = replace(event, seq=casefile.last_seq + len(additions) + 1, prev=previous)
        encoded = _bytes(event)
        additions.append(encoded + b"\n")
        previous = hashlib.sha256(encoded).hexdigest()
    suffix = (b"\n" if complete and not complete.endswith(b"\n") else b"") + b"".join(additions)
    # Refuse malformed pending events before opening the file for mutation.
    result = _decode(complete + suffix)
    try:
        with path.open("ab") as stream:
            if casefile.torn:
                os.ftruncate(stream.fileno(), len(complete))
            stream.write(suffix)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise CaseFileError(f"cannot append case file {path}: {exc}") from exc
    return result


def _page(cite, pages):
    matches = [page for page in pages
               if stamps.normalize(cite) in page.stamps or cite == page.page_id]
    if len(matches) != 1:
        reason = "matches more than one page (ambiguous cite)" if matches else "is not a page of this chunk"
        raise CaseFileError(f"cite {cite} {reason}")
    return matches[0]


def merge(casefile: CaseFile, answer: dict, pages: Sequence[Page], run_id) -> list[Event]:
    """Merge a passing answer only; do not mutate the supplied case file."""
    facts = {quotes.fold(fact.quote): fact for fact in casefile.facts}
    flags = {(flag.kind, tuple(sorted(set(flag.page_ids)))): flag for flag in casefile.flags}
    events = []

    def emit(event_kind, **payload):
        seq = casefile.last_seq + len(events) + 1
        if event_kind in ("fact", "flag"):
            payload = {"id": f'{"F" if event_kind == "fact" else "G"}{seq}', **payload}
        event = Event(event_kind, payload, seq=seq)
        events.append(event)
        return payload.get("id")

    for item in answer["facts"]:
        page = _page(item["cite"], pages)
        cite = stamps.normalize(item["cite"]) if stamps.normalize(item["cite"]) in page.stamps else page.page_id
        identity = quotes.fold(item["quote"])
        fact = facts.get(identity)
        if fact is None:
            ident = emit("fact", cite=cite, page_id=page.page_id, quote=item["quote"],
                         text=item["text"], run_id=run_id)
            facts[identity] = Fact(ident, item["quote"], [cite], [page.page_id], [item["text"]])
            continue
        if page.page_id not in fact.page_ids:
            emit("cite", fact=fact.id, cite=cite, page_id=page.page_id, run_id=run_id)
            fact.cites.append(cite)
            fact.page_ids.append(page.page_id)
        if item["text"] not in fact.readings:
            emit("reading", fact=fact.id, text=item["text"], run_id=run_id)
            fact.readings.append(item["text"])
    for item in answer["flags"]:
        cited_pages = [_page(cite, pages) for cite in item["cites"]]
        page_ids = list(dict.fromkeys(page.page_id for page in cited_pages))
        identity = (item["kind"], tuple(sorted(set(page_ids))))
        flag = flags.get(identity)
        if flag is None:
            cites = [page.stamps[0] if page.stamps else page.page_id for page in cited_pages]
            ident = emit("flag", **{"kind": item["kind"], "cites": cites, "page_ids": page_ids,
                                    "about": item["about"], "run_id": run_id})
            flags[identity] = Flag(ident, item["kind"], cites, page_ids, [item["about"]])
        elif item["about"] not in flag.abouts:
            emit("about", flag=flag.id, about=item["about"], run_id=run_id)
            flag.abouts.append(item["about"])
    return events
