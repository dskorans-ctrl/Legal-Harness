"""Load the firm's four rules and check output text only, never source records."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import tomllib


RULE_IDS = frozenset({"no-dme-ime", "no-hired-paid-retained", "treatment-and-bills-apart", "bates-cites"})
ENTRY_FIELDS = ("rule", "why", "good", "bad", "added", "learned")
COMMON_FIELDS = frozenset((*ENTRY_FIELDS, "id", "kind", "severity", "unit"))
KIND_FIELDS = {"forbid": {"patterns"}, "conjunction": {"all_of"},
               "cite": {"cite_pattern", "bates_pattern"}}


class RulesError(ValueError):
    """Rules are incomplete or cannot be checked reliably."""


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    start: int
    end: int
    excerpt: str


@dataclass(frozen=True)
class Rule:
    id: str
    kind: str
    severity: str
    unit: str
    rule: str
    why: str
    good: str
    bad: str
    added: date
    learned: str
    patterns: tuple[str, ...] = ()
    all_of: tuple[tuple[str, ...], ...] = ()
    cite_pattern: str | None = None
    bates_pattern: str | None = None


@dataclass(frozen=True)
class Rules:
    version: int
    rules: tuple[Rule, ...]

    def check(self, text, *, unit="text", stamped=True):
        if not isinstance(text, str):
            raise TypeError("output text must be str")
        if unit not in {"text", "question"}:
            raise ValueError("unit must be text or question")
        findings = []
        flags = re.IGNORECASE
        for rule in self.rules:
            if rule.unit == "question" and unit != "question":
                continue
            spans = set()
            severity = rule.severity
            if rule.kind == "forbid":
                for pattern in rule.patterns:
                    spans.update(m.span() for m in re.finditer(pattern, text, flags))
            elif rule.kind == "conjunction":
                groups = [[m for pattern in group for m in re.finditer(pattern, text, flags)]
                          for group in rule.all_of]
                if all(groups):
                    matches = [min(group, key=lambda m: m.start()) for group in groups]
                    spans.add((min(m.start() for m in matches), max(m.end() for m in matches)))
            else:
                for match in re.finditer(rule.cite_pattern, text, flags):
                    if re.fullmatch(rule.bates_pattern, match.group(1).strip()) is None:
                        spans.add(match.span())
                severity = "error" if stamped else "warning"
            findings.extend(Finding(rule.id, severity, start, end, text[start:end])
                            for start, end in sorted(spans))
        return findings


def _from_document(document, source):
    def error(rule_id, field, message):
        raise RulesError(f"{source}: rule {rule_id} {field}: {message}")

    if not isinstance(document, dict) or set(document) != {"version", "rule"}:
        error("<document>", "fields", "expected only version and rule")
    if type(document["version"]) is not int or document["version"] != 1:
        error("<document>", "version", "expected integer 1")
    if not isinstance(document["rule"], list):
        error("<document>", "rule", "expected array of tables")
    result = []
    seen = set()
    for entry in document["rule"]:
        if not isinstance(entry, dict):
            error("<unknown>", "rule", "expected table")
        rule_id = entry.get("id", "<unknown>")
        for field in (*ENTRY_FIELDS, "id", "kind", "severity", "unit"):
            if field not in entry:
                error(rule_id, field, "missing field")
            expected = date if field == "added" else str
            if type(entry[field]) is not expected:
                error(rule_id, field, f"expected {expected.__name__}")
            if expected is str and not entry[field].strip():
                error(rule_id, field, "must not be empty")
        if rule_id not in RULE_IDS or rule_id in seen:
            error(rule_id, "id", "unknown or duplicate id")
        seen.add(rule_id)
        kind = entry["kind"]
        if kind not in KIND_FIELDS:
            error(rule_id, "kind", "expected forbid, conjunction or cite")
        if entry["severity"] not in {"error", "warning"}:
            error(rule_id, "severity", "expected error or warning")
        if entry["unit"] not in {"text", "question"}:
            error(rule_id, "unit", "expected text or question")
        unknown = entry.keys() - COMMON_FIELDS - KIND_FIELDS[kind]
        if unknown:
            error(rule_id, sorted(unknown)[0], "unknown field")
        for field in KIND_FIELDS[kind]:
            if field not in entry:
                error(rule_id, field, "missing field")

        def pattern(value, field, bounded):
            if not isinstance(value, str) or not value:
                error(rule_id, field, "expected nonempty pattern string")
            if bounded and not ("\\b" in value or value.startswith("^") or value.endswith("$")):
                error(rule_id, field, "has no word boundary")
            try:
                return re.compile(value)
            except re.error as exc:
                error(rule_id, field, f"invalid pattern: {exc}")

        fields = {key: entry[key] for key in COMMON_FIELDS}
        if kind == "forbid":
            values = entry["patterns"]
            if not isinstance(values, list) or not values:
                error(rule_id, "patterns", "expected nonempty array")
            for index, value in enumerate(values, 1):
                pattern(value, f"pattern {index}", True)
            fields["patterns"] = tuple(values)
        elif kind == "conjunction":
            groups = entry["all_of"]
            if not isinstance(groups, list) or not groups:
                error(rule_id, "all_of", "expected nonempty array of pattern arrays")
            for index, group in enumerate(groups, 1):
                if not isinstance(group, list) or not group:
                    error(rule_id, f"all_of {index}", "expected nonempty pattern array")
                for number, value in enumerate(group, 1):
                    pattern(value, f"all_of {index} pattern {number}", True)
            fields["all_of"] = tuple(tuple(group) for group in groups)
        else:
            cite = pattern(entry["cite_pattern"], "cite_pattern", False)
            if cite.groups < 1:
                error(rule_id, "cite_pattern", "requires capture group 1")
            pattern(entry["bates_pattern"], "bates_pattern", False)
            fields.update(cite_pattern=entry["cite_pattern"], bates_pattern=entry["bates_pattern"])
        result.append(Rule(**fields))
    if seen != RULE_IDS:
        error("<document>", "id", f"missing rule ids: {', '.join(sorted(RULE_IDS - seen))}")
    return Rules(1, tuple(result))


def load(path):
    path = Path(path)
    try:
        return _from_document(tomllib.loads(path.read_text(encoding="utf-8")), path)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise RulesError(f"{path}: {exc}") from exc
