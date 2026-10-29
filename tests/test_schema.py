"""The fourteen subset cases and the twenty shipped card schemas."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from casefile.schema import SchemaError, check_schema, load, validate

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "schemas" / "medical_memo.schema.json"
ANSWER = {"facts": [{"cite": "MED0001", "quote": "Pain 7/10.", "text": "Pain was 7/10.", "date": "", "category": "other", "provider": ""}],
          "flags": [{"kind": "gap", "cites": ["MED0001"], "about": "An invented record is missing."}]}


def object_schema(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required),
            "additionalProperties": False}


def case_type():
    for kind, good, bad in [("object", {}, []), ("array", [], {}), ("string", "Pain", 1),
                            ("integer", 7, True), ("number", 7.5, False),
                            ("boolean", True, 1), ("null", None, "null")]:
        node = object_schema({}) if kind == "object" else {"type": kind}
        if kind == "array":
            node["items"] = {"type": "string"}
        check_schema(node)
        assert validate(good, node) == []
        assert validate(bad, node) == [f"$: expected {kind}"]
    assert validate({"facts": [], "flags": []}, load(EXTRACT)) == []
    assert validate(1.0, {"type": "integer"}) == []
    for value in (float("inf"), float("nan")):
        assert validate(value, {"type": "number"}) == ["$: expected number"]


def case_properties():
    node = load(EXTRACT)
    assert node["title"] == "medical_memo"
    assert validate(ANSWER, node) == []
    bad = deepcopy(ANSWER)
    bad["facts"][0]["text"] = 7
    assert validate(bad, node) == ["facts[0].text: expected string"]


def case_required():
    node = load(EXTRACT)
    assert validate(ANSWER, node) == []
    bad = deepcopy(ANSWER)
    del bad["facts"][0]["text"]
    assert validate(bad, node) == ["facts[0].text: missing required key"]


def case_additional():
    node = load(EXTRACT)
    assert validate(ANSWER, node) == []
    bad = deepcopy(ANSWER)
    bad["facts"][0]["page"] = 1
    assert validate(bad, node) == ["facts[0]: unknown key page"]
    for key in (None, 1):
        malformed = object_schema({})
        malformed["properties"] = {key: {"type": "string"}}
        with pytest.raises(SchemaError, match="properties"):
            check_schema(malformed)
    with pytest.raises(SchemaError, match="additionalProperties"):
        check_schema({"type": "object", "properties": {}})


def case_items():
    node = load(EXTRACT)
    assert validate(ANSWER, node) == []
    bad = deepcopy(ANSWER)
    bad["flags"][0]["cites"][0] = 1
    assert validate(bad, node) == ["flags[0].cites[0]: expected string"]


def case_enum():
    node = load(EXTRACT)
    assert validate(ANSWER, node) == []
    bad = deepcopy(ANSWER)
    bad["flags"].append({"kind": "note", "cites": [], "about": "An invented note."})
    assert validate(bad, node) == ["flags[1].kind: not one of conflict, gap"]
    assert validate(True, {"type": "boolean", "enum": [1]}) == ["$: not one of 1"]


def case_cite():
    node = object_schema({"quote": {"type": "string"}, "cite": {"type": "string"}})
    assert validate({"quote": "Pain", "cite": "MED0001"}, node) == []
    assert validate({"quote": "Pain"}, node) == ["$: quote requires a cite string"]
    assert validate({"quote": "Pain", "cite": 1}, node) == [
        "cite: expected string", "$: quote requires a cite string"]


def case_keyword_name():
    node = object_schema({"type": {"type": "string"}, "items": {"type": "integer"}}, ["type"])
    check_schema(node)
    assert validate({"type": "Pain", "items": 7}, node) == []
    assert validate({"type": 1}, node) == ["type: expected string"]


REFUSALS = [
    ("$ref", {"type": "string", "$ref": "#/invented"}, "unknown keyword "),
    ("oneOf", {"type": "string", "oneOf": [{"type": "string"}]}, "unknown keyword "),
    ("pattern", {"type": "string", "pattern": "invented"}, "unknown keyword "),
    ("open object", {"type": "object", "additionalProperties": True}, "additionalProperties"),
    ("union type", {"type": ["string", "null"]}, "unsupported type"),
    ("unknown required", object_schema({}, ["invented"]), "required"),
]


def test_schema_table(tmp_path, capsys):
    cases = [(name, action) for name, action in [
        ("type", case_type), ("properties", case_properties), ("required", case_required),
        ("additionalProperties", case_additional), ("items", case_items), ("enum", case_enum),
        ("cite", case_cite), ("keyword property name", case_keyword_name)]]
    for name, node, message in REFUSALS:
        def refusal(node=node, message=message):
            path = tmp_path / "schema.json"
            path.write_text(json.dumps(node), encoding="utf-8")
            with pytest.raises(SchemaError, match=message):
                load(path)
        cases.append((name, refusal))
    failures = []
    for name, action in cases:
        try:
            action()
        except (AssertionError, SchemaError, pytest.fail.Exception) as exc:
            failures.append((name, str(exc)))
    passed = len(cases) - len(failures)
    with capsys.disabled():
        print(f"schema_ok={passed} of 14")
    assert len(cases) == 14
    assert not failures, "\n".join(f"{name}: {message}" for name, message in failures)


def test_all_schemas_load(capsys):
    paths = sorted((ROOT / "schemas").glob("*.schema.json"))
    failures = []
    for path in paths:
        try:
            load(path)
        except SchemaError as exc:
            failures.append((path.name, str(exc)))
    with capsys.disabled():
        print(f"schemas_loaded={len(paths) - len(failures)} of 11")
    assert len(paths) == 11
    assert not failures, failures


def test_errors_are_collected():
    bad = deepcopy(ANSWER)
    del bad["facts"][0]["text"]
    bad["facts"][0]["page"] = 1
    bad["flags"][0]["kind"] = "note"
    assert validate(bad, load(EXTRACT)) == ["facts[0].text: missing required key",
        "facts[0]: unknown key page", "flags[0].kind: not one of conflict, gap"]


@pytest.mark.parametrize("node", [True, {"type": "invented"}, {"type": "array", "items": []},
    {"type": "object", "additionalProperties": {}}, {"type": "string", "enum": []},
    {"type": "string", "title": 1}, {"type": "string", "$schema": 1},
    {"type": "array"}, object_schema({}, ["x", "x"])])
def test_bad_schema_values(node):
    with pytest.raises(SchemaError):
        check_schema(node)


@pytest.mark.parametrize("contents", [b"\xff", b"{", b"[]"])
def test_load_errors_are_schema_errors(tmp_path, contents):
    path = tmp_path / "bad.json"
    path.write_bytes(contents)
    with pytest.raises(SchemaError):
        load(path)


@pytest.mark.parametrize('value,enum,node', [
    ([1], [True], {'type': 'array', 'items': {'type': 'integer'}}),
    ([True], [1], {'type': 'array', 'items': {'type': 'boolean'}}),
    ({'n': [1]}, {'n': [True]}, object_schema({'n': {'type': 'array', 'items': {'type': 'integer'}}})),
    ({'n': [False]}, {'n': [0]}, object_schema({'n': {'type': 'array', 'items': {'type': 'boolean'}}})),
])
def test_fix9_enum_json_types(value, enum, node):
    assert validate(value, dict(node, enum=[enum])), 'R9: enum conflates nested boolean and number'
    assert validate(value, dict(node, enum=[value])) == []
    assert validate([1], {'type': 'array', 'items': {'type': 'integer'}, 'enum': [[1.0]]}) == []


def test_schema_evidence():
    manifest = json.loads((ROOT / 'cards/manifest.json').read_text(encoding='utf-8'))
    paths = {row['schema'] for row in manifest['cards'] if row['stage'] in (6, 7)}
    assert {Path(path).name for path in paths} == {name + '.schema.json' for name in
        ('anonymize', 'concessions', 'elements', 'factsheet', 'medical_memo', 'questions')}
    objects = []
    def visit(node, location):
        if not isinstance(node, dict):
            return
        properties = node.get('properties', {})
        if 'quote' in properties:
            objects.append((location, node))
        for key, child in properties.items():
            visit(child, location + '.' + key)
        if 'items' in node:
            visit(node['items'], location + '[]')
    for path in sorted(paths):
        visit(load(ROOT / path), path)
    failures = [location for location, node in objects
                if not {'quote', 'cite'} <= set(node.get('required', ()))
                or node['properties'].get('cite') != {'type': 'string'}]
    count = len(objects) - len(failures)
    print(f'schema_evidence={count} of 13')
    assert len(objects) == 13 and not failures, f'schema_evidence={count} of 13; {failures}'
