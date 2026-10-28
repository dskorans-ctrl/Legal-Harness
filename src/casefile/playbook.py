"""Fail-closed loading of firm rules and invented SAMPLE practice entries."""

from dataclasses import dataclass
from datetime import date
import hashlib
from pathlib import Path
import tomllib

from . import rules


KINDS = frozenset({"depo-goal", "topic-order", "question", "hearing", "checklist", "rule"})
REQUIRED = (*rules.ENTRY_FIELDS, "id", "kind", "sample")


class PlaybookError(ValueError):
    """A playbook must be corrected before it can be used."""


@dataclass(frozen=True)
class Entry:
    id: str
    kind: str
    rule: str
    why: str
    good: str
    bad: str
    added: date
    learned: str
    sample: bool
    source: Path
    deponent: str | None = None


@dataclass(frozen=True)
class Playbook:
    """Entries include the four Rule objects, which have no sample attribute."""

    version: str
    entries: tuple[rules.Rule | Entry, ...]
    rules: rules.Rules


def _entries(document, source):
    if set(document) != {"entry"} or not isinstance(document["entry"], list) or not document["entry"]:
        raise PlaybookError(f"{source}: entry: expected nonempty [[entry]] tables only")
    result = []
    for number, entry in enumerate(document["entry"], 1):
        rule_id = entry.get("id", "<unknown>") if isinstance(entry, dict) else "<unknown>"

        def error(message):
            raise PlaybookError(f"{source}: entry {number} ({rule_id}): {message}")

        if not isinstance(entry, dict):
            error("expected table")
        unknown = entry.keys() - set(REQUIRED) - {"deponent"}
        if unknown:
            error(f"unknown field {sorted(unknown)[0]}")
        for field in REQUIRED:
            if field not in entry:
                error(f"missing field {field}")
            elif field in entry:
                expected = date if field == "added" else bool if field == "sample" else str
                if type(entry[field]) is not expected:
                    error(f"field {field}: expected {expected.__name__}")
                if expected is str and not entry[field].strip():
                    error(f"field {field}: must not be empty")
        if "deponent" in entry and (not isinstance(entry["deponent"], str) or not entry["deponent"].strip()):
            error("field deponent: expected nonempty str")
        if entry["kind"] not in KINDS:
            error(f"field kind: expected one of {', '.join(sorted(KINDS))}")
        if entry["sample"]:
            if not entry["rule"].startswith("SAMPLE:"):
                error("field sample: sample = true requires rule starting SAMPLE:")
        elif entry["rule"].startswith("SAMPLE:") or not entry["learned"].startswith("firm skill "):
            error("field sample: practice requires an unmarked rule and learned starting firm skill ")
        # The missing-field guard above is the refusal boundary for all six fields.
        values = {field: entry.get(field) for field in REQUIRED}
        result.append(Entry(**values, deponent=entry.get("deponent"), source=source))
    return result


def load(dir):
    root = Path(dir)
    if not root.is_dir():
        raise PlaybookError(f"{root}: playbook directory not found")
    try:
        files = sorted(root.rglob("*.toml"), key=lambda p: p.relative_to(root).as_posix())
        if root / "rules.toml" not in files:
            raise PlaybookError(f"{root / 'rules.toml'}: missing rules.toml")
        snapshots = [(p.relative_to(root), p.read_bytes()) for p in files]
        digest = hashlib.sha256()
        entries = []
        loaded_rules = None
        for relative, data in snapshots:
            source = root / relative
            digest.update(relative.as_posix().encode("utf-8") + b"\0" + data + b"\0")
            try:
                document = tomllib.loads(data.decode("utf-8"))
            except (UnicodeError, tomllib.TOMLDecodeError) as exc:
                raise PlaybookError(f"{source}: {exc}") from exc
            if relative == Path("rules.toml"):
                try:
                    loaded_rules = rules._from_document(document, source)
                except rules.RulesError as exc:
                    raise PlaybookError(str(exc)) from exc
                entries.extend(loaded_rules.rules)
            else:
                entries.extend(_entries(document, source))
        seen = set()
        for number, entry in enumerate(entries, 1):
            if entry.id in seen:
                source = getattr(entry, "source", root / "rules.toml")
                raise PlaybookError(f"{source}: entry {number} ({entry.id}): duplicate id")
            seen.add(entry.id)
        return Playbook("pb-" + digest.hexdigest()[:12], tuple(entries), loaded_rules)
    except OSError as exc:
        raise PlaybookError(f"{root}: {exc}") from exc
