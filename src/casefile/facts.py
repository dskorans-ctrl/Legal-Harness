"""Append-only case file events and exact-identity views (D40)."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from casefile import dates, jsonrepair, quotes, stamps
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
    reading_pages: list[str]
    dates: list[str] = field(default_factory=list)
    category: str = "other"
    providers: list[str] = field(default_factory=list)


@dataclass
class Flag:
    id: str
    kind: str
    cites: list[str]
    page_ids: list[str]
    abouts: list[str]


CHANGE_KINDS = ("fact", "cite", "reading", "flag", "about", "split")
FIELDS_V1 = {
    "fact": {"id", "cite", "page_id", "quote", "text", "run_id"},
    "cite": {"fact", "cite", "page_id", "run_id"},
    "reading": {"fact", "text", "page_id", "run_id"},
    "flag": {"id", "kind", "cites", "page_ids", "about", "run_id"},
    "about": {"flag", "about", "run_id"},
    "run": {"run_id", "job", "card", "card_version", "pages", "ok", "read", "uncited", "failed"},
    "output": {"name", "path", "built_from_seq", "facts", "conflicts", "gaps", "open"},
}

FIELDS = {**FIELDS_V1, "fact": FIELDS_V1["fact"] | {"date", "category", "provider"},
          "cite": FIELDS_V1["cite"] | {"date", "provider"},
          "split": {"fact", "page_id", "to", "cite", "date", "provider", "text"}}


def identity(quote, date, provider):
    return quotes.fold(quote), dates.iso(date) or date, quotes.fold(provider)


def _bytes(event):
    return json.dumps({"seq": event.seq, "at": event.at, "prev": event.prev,
                       "kind": event.kind, "payload": event.payload},
                      ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


@dataclass
class CaseFile:
    """Events in sequence order; views preserve the order of the first occurrence."""

    events: list[Event] = field(default_factory=list)
    torn: int = 0
    upgraded: int = 0

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
                                         [data["page_id"]], [data["text"]], [data["page_id"]],
                                         [data.get("date", "")], data.get("category", "other"),
                                         [data.get("provider", "")])
            elif event.kind == "cite":
                fact = found[data["fact"]]
                fact.cites.append(data["cite"])
                fact.page_ids.append(data["page_id"])
                fact.dates.append(data.get("date", ""))
                fact.providers.append(data.get("provider", ""))
            elif event.kind == "reading":
                found[data["fact"]].readings.append(data["text"])
                found[data["fact"]].reading_pages.append(data["page_id"])
            elif event.kind == "split":
                fact = found[data["fact"]]
                moves = [data, *data.get("moves", [])]
                pages = [move["page_id"] for move in moves]
                moved = [(text, page_id) for text, page_id in zip(fact.readings, fact.reading_pages)
                         if page_id in pages]
                for move in moves:
                    if not any(page_id == move["page_id"] for _, page_id in moved):
                        moved.append((move["text"], move["page_id"]))
                kept = [(text, page_id) for text, page_id in zip(fact.readings, fact.reading_pages)
                        if page_id not in pages]
                fact.readings = [text for text, _ in kept]
                fact.reading_pages = [page_id for _, page_id in kept]
                indices = [i for i, page_id in enumerate(fact.page_ids) if page_id in pages]
                for values in (fact.cites, fact.page_ids, fact.dates, fact.providers):
                    for index in reversed(indices):
                        values.pop(index)
                found[data["to"]] = Fact(data["to"], fact.quote, [move["cite"] for move in moves],
                    pages, [text for text, _ in moved], [page_id for _, page_id in moved],
                    [move["date"] for move in moves], fact.category, [move["provider"] for move in moves])
        return list(found.values())

    @property
    def split_needed(self):
        return sum(len({identity(fact.quote, date, provider)
                        for date, provider in zip(fact.dates, fact.providers)}) > 1
                   for fact in self.facts)

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
    ids = {"fact": set(), "flag": set()}
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
                    or (set(obj["payload"]) != FIELDS[obj["kind"]]
                        and not (obj["kind"] == "split" and set(obj["payload"]) == FIELDS["split"] | {"moves"})
                        and not (obj["kind"] in ("fact", "cite")
                                 and set(obj["payload"]) == FIELDS_V1[obj["kind"]]))):
                raise _broken(index)
            if obj["kind"] in ("fact", "cite") and set(obj["payload"]) == FIELDS_V1[obj["kind"]]:
                casefile.upgraded += 1
            if obj["kind"] in ids:
                ident = obj["payload"]["id"]
                if not isinstance(ident, str) or ident in ids[obj["kind"]]:
                    raise _broken(index)
                ids[obj["kind"]].add(ident)
            if obj["kind"] == "split":
                data = obj["payload"]
                if (not all(isinstance(data[key], str) for key in FIELDS["split"])
                        or data["fact"] not in ids["fact"] or data["to"] in ids["fact"]):
                    raise _broken(index)
                source = next(fact for fact in casefile.facts if fact.id == data["fact"])
                extra = data.get("moves", [])
                if (not isinstance(extra, list) or any(not isinstance(move, dict)
                        or set(move) != {"page_id", "cite", "date", "provider", "text"}
                        or not all(isinstance(value, str) for value in move.values()) for move in extra)):
                    raise _broken(index)
                moves = [data, *extra]
                moved_pages = [move["page_id"] for move in moves]
                wanted = identity(source.quote, data["date"], data["provider"])
                if (len(set(moved_pages)) != len(moved_pages) or len(moved_pages) >= len(source.page_ids)
                        or any(page_id not in source.page_ids for page_id in moved_pages)
                        or any(identity(source.quote, move["date"], move["provider"]) != wanted for move in moves)):
                    raise _broken(index)
                for move in moves:
                    i = source.page_ids.index(move["page_id"])
                    if (move["cite"] != source.cites[i]
                            or move["date"] != source.dates[i] or move["provider"] != source.providers[i]):
                        raise _broken(index)
                ids["fact"].add(data["to"])
            casefile.events.append(Event(obj["kind"], obj["payload"], obj["seq"], obj["at"], obj["prev"]))
        except (jsonrepair.RepairError, UnicodeDecodeError) as exc:
            raise _broken(index) from exc
        previous = hashlib.sha256(line).hexdigest()
    return casefile


def load(path) -> CaseFile:
    return _decode(_read(Path(path)))


def append(path, events) -> CaseFile:
    """Validate the existing chain, recover an incomplete tail, and fsync appended events.

    The caller must serialize writers to this matter; memo_job holds the matter lock.
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


def upgrade_events(casefile) -> list[Event]:
    """Split later identities without changing any stored event or reading provenance."""
    events = []
    for fact in casefile.facts:
        first = identity(fact.quote, fact.dates[0], fact.providers[0])
        groups = {}
        for cite, page_id, date, provider in zip(fact.cites, fact.page_ids, fact.dates, fact.providers):
            ident = identity(fact.quote, date, provider)
            if ident == first:
                continue
            text = next((text for text, source in zip(fact.readings, fact.reading_pages)
                         if source == page_id), "")
            groups.setdefault(ident, []).append(dict(page_id=page_id, cite=cite, date=date, provider=provider, text=text))
        for moves in groups.values():
            payload = dict(fact=fact.id, to=f"F{casefile.last_seq + len(events) + 1}", **moves[0])
            if len(moves) > 1:
                payload["moves"] = moves[1:]
            events.append(Event("split", payload))
    return events


def merge(casefile: CaseFile, answer: dict, pages: Sequence[Page], run_id) -> list[Event]:
    """Merge a passing answer only; do not mutate the supplied case file."""
    facts = {identity(fact.quote, fact.dates[0], fact.providers[0]): fact for fact in casefile.facts}
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
        cite = (stamps.normalize(item["cite"]) if stamps.normalize(item["cite"]) in page.stamps
                else page.stamps[0] if page.stamps else page.page_id)
        key = identity(item["quote"], item.get("date", ""), item.get("provider", ""))
        fact = facts.get(key)
        if fact is None:
            ident = emit("fact", cite=cite, page_id=page.page_id, quote=item["quote"],
                         text=item["text"], run_id=run_id, date=item.get("date", ""),
                         category=item.get("category", "other"), provider=item.get("provider", ""))
            facts[key] = Fact(ident, item["quote"], [cite], [page.page_id], [item["text"]], [page.page_id],
                                   [item.get("date", "")], item.get("category", "other"),
                                   [item.get("provider", "")])
            continue
        if page.page_id not in fact.page_ids:
            emit("cite", fact=fact.id, cite=cite, page_id=page.page_id, run_id=run_id,
                 date=item.get("date", ""), provider=item.get("provider", ""))
            fact.cites.append(cite)
            fact.page_ids.append(page.page_id)
            fact.dates.append(item.get("date", ""))
            fact.providers.append(item.get("provider", ""))
        if (item["text"], page.page_id) not in zip(fact.readings, fact.reading_pages):
            emit("reading", fact=fact.id, text=item["text"], page_id=page.page_id, run_id=run_id)
            fact.readings.append(item["text"])
            fact.reading_pages.append(page.page_id)
    for item in answer["flags"]:
        cited_pages = list({page.page_id: page for page in
                            (_page(cite, pages) for cite in item["cites"])}.values())
        page_ids = [page.page_id for page in cited_pages]
        key = (item["kind"], tuple(sorted(set(page_ids))))
        flag = flags.get(key)
        if flag is None:
            cites = [page.stamps[0] if page.stamps else page.page_id for page in cited_pages]
            ident = emit("flag", **{"kind": item["kind"], "cites": cites, "page_ids": page_ids,
                                    "about": item["about"], "run_id": run_id})
            flags[key] = Flag(ident, item["kind"], cites, page_ids, [item["about"]])
        elif item["about"] not in flag.abouts:
            emit("about", flag=flag.id, about=item["about"], run_id=run_id)
            flag.abouts.append(item["about"])
    return events
