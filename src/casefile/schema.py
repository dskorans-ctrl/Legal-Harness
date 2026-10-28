"""Load and enforce the card schemas' explicitly supported JSON Schema subset."""

import math
from pathlib import Path

from casefile import jsonrepair

KEYWORDS = {"type", "properties", "required", "additionalProperties", "items", "enum", "title", "$schema"}
TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


class SchemaError(ValueError):
    """A schema uses a shape or constraint the validator cannot enforce."""


def check_schema(schema):
    """Fail closed on unsupported keywords, values and implicit open objects."""
    if not isinstance(schema, dict):
        raise SchemaError("schema must be an object")
    unknown = schema.keys() - KEYWORDS
    if unknown:
        raise SchemaError(f"unknown keyword {sorted(unknown)[0]}")
    kind = schema.get("type")
    if not isinstance(kind, str) or kind not in TYPES:
        raise SchemaError("unsupported type")
    for key in ("title", "$schema"):
        if key in schema and not isinstance(schema[key], str):
            raise SchemaError(f"{key} must be a string")
    if "additionalProperties" in schema and schema["additionalProperties"] is not False:
        raise SchemaError("additionalProperties must be false")
    if kind == "object" and schema.get("additionalProperties") is not False:
        raise SchemaError("object requires additionalProperties: false")
    properties = schema.get("properties", {})
    if not isinstance(properties, dict) or any(not isinstance(key, str) for key in properties):
        raise SchemaError("properties must map names to schemas")
    for child in properties.values():
        check_schema(child)
    required = schema.get("required", [])
    if (not isinstance(required, list) or any(not isinstance(key, str) for key in required)
            or len(set(required)) != len(required) or any(key not in properties for key in required)):
        raise SchemaError("required must name distinct properties")
    if "items" in schema:
        check_schema(schema["items"])
    elif kind == "array":
        raise SchemaError("array requires items")
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]):
        raise SchemaError("enum must be a nonempty array")


def load(path) -> dict:
    """Read UTF-8 JSON and refuse schemas outside the supported subset."""
    try:
        schema = jsonrepair.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise SchemaError(f"cannot load schema {path}: {exc}") from exc
    check_schema(schema)
    return schema


def _has_type(value, kind):
    numeric = type(value) in (int, float)
    finite = numeric and (type(value) is int or math.isfinite(value))
    return {"object": isinstance(value, dict), "array": isinstance(value, list),
            "string": isinstance(value, str), "integer": finite and value == int(value),
            "number": finite, "boolean": type(value) is bool, "null": value is None}[kind]


def _json_equal(left, right):
    """Compare composite JSON values without Python's bool and number coercion."""
    if type(left) in (int, float) and type(right) in (int, float):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(_json_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_json_equal(left[key], right[key]) for key in left)
    return left == right


def validate(instance, schema) -> list[str]:
    """Collect every type, shape and cite-pair error with its instance path."""
    check_schema(schema)
    errors = []

    def visit(value, node, path):
        def error(message, where=path):
            errors.append(f"{where or '$'}: {message}")

        kind = node["type"]
        if not _has_type(value, kind):
            error(f"expected {kind}")
            return
        if "enum" in node and not any(_json_equal(value, item) for item in node["enum"]):
            error("not one of " + ", ".join(str(item) for item in node["enum"]))
        if isinstance(value, dict):
            properties = node.get("properties", {})
            for key in node.get("required", []):
                if key not in value:
                    error("missing required key", f"{path}.{key}".lstrip("."))
            for key, child in value.items():
                if key not in properties:
                    error(f"unknown key {key}")
                else:
                    visit(child, properties[key], f"{path}.{key}".lstrip("."))
            if "quote" in value and not isinstance(value.get("cite"), str):
                error("quote requires a cite string")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, node["items"], f"{path}[{index}]")

    visit(instance, schema, "")
    return errors
