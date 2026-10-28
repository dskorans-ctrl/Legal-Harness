"""Repair only the four punctuation faults allowed by gate 2."""

from dataclasses import dataclass
import json
import re


class RepairError(ValueError):
    """The answer needs more than punctuation repair."""


@dataclass(frozen=True)
class Repaired:
    text: str
    repairs: tuple[str, ...]


def unfence(text: str) -> str:
    """Remove a complete outer Markdown fence without changing its contents."""
    found = re.fullmatch(r"\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n```\s*", text, re.DOTALL)
    return found[1] if found else text


def _constant(value):
    raise RepairError(f"not JSON: {value}")


def repair(text: str, *, nonce: str) -> Repaired:
    """Check strings and nesting, repair punctuation, then require strict JSON."""
    inner = unfence(text)
    kinds = {"fence"} if inner != text else set()
    source = inner.strip()
    output, stack, strings = [], [], []
    in_string = escaped = False
    start = 0
    for index, char in enumerate(source):
        if in_string:
            output.append(" " if ord(char) < 32 else char)
            if ord(char) < 32:
                kinds.add("control")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
                strings.append((start, len(output)))
        elif char == '"':
            start = len(output)
            output.append(char)
            in_string = True
        elif char in "[{":
            stack.append("]" if char == "[" else "}")
            output.append(char)
        elif char in "]}":
            if not stack or stack.pop() != char:
                raise RepairError("mismatched closer")
            output.append(char)
        elif char == "," and source[index + 1:].lstrip().startswith(("]", "}")):
            kinds.add("trailing-comma")
        else:
            output.append(char)
    if in_string:
        raise RepairError("unterminated string")
    repaired = "".join(output)
    if stack:
        # Start at a real string token, so a quoted imitation cannot authorize repair.
        tail = repaired[strings[-2][0]:] if len(strings) >= 2 else ""
        end_at_tail = re.fullmatch(r'"end_id"\s*:\s*' + re.escape(json.dumps(nonce))
                                  + r"[\s\]}]*", tail)
        if not end_at_tail:
            raise RepairError("closers missing and end_id not last")
        repaired += "".join(reversed(stack))
        kinds.add("closers")
    try:
        json.loads(repaired, parse_constant=_constant)
    except json.JSONDecodeError as exc:
        raise RepairError(f"not JSON: {exc.msg}") from exc
    return Repaired(repaired, tuple(kind for kind in
                    ("fence", "control", "trailing-comma", "closers") if kind in kinds))
