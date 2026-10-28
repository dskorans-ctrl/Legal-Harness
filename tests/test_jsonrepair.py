"""Gate 2's thirteen punctuation cases and string-boundary probes."""

import json

import pytest

from casefile.jsonrepair import RepairError, repair, unfence

NONCE = "0123456789abcdef"
GOOD = '{"prompt_id": "' + NONCE + '", "facts": [], "end_id": "' + NONCE + '"}'
TAIL = '{"facts": [{"end_id": "' + NONCE + '"}'
TAIL_CLOSED = TAIL + "]}"
CONTROL = GOOD.replace('"facts": []', '"text": "Pain\t7/10"')
TRAILING = GOOD.replace('"facts": []', '"facts": ["Pain 7/10",]')
COMBINED = "```json\n" + CONTROL.replace('"text":', '"facts": [1,], "text":')[:-1] + "\n```"

# An expected error is separate from the string case whose punctuation must stay intact.
REPAIRS = [
    ("fence", "```json\n" + GOOD + "\n```", GOOD, ("fence",)),
    ("control", CONTROL, CONTROL.replace("\t", " "), ("control",)),
    ("object comma", GOOD[:-1] + ",}", GOOD, ("trailing-comma",)),
    ("array comma", TRAILING, TRAILING.replace('",]', '"]'), ("trailing-comma",)),
    ("closers", TAIL, TAIL_CLOSED, ("closers",)),
    ("all four", COMBINED, CONTROL.replace("\t", " ").replace('"text":', '"facts": [1], "text":'),
     ("fence", "control", "trailing-comma", "closers")),
    ("missing comma", '{"facts": [{"text": "Pain"} {"text": "No weakness"}]}', None, "not JSON"),
    ("single quotes", "{'facts': []}", None, "not JSON"),
    ("unquoted key", '{facts: []}', None, "not JSON"),
    ("unterminated string", '{"facts": [{"text": "Pain', None, "unterminated string"),
    ("text after closers", GOOD + " extra", None, "not JSON"),
    ("string comma", '{"text": "Pain,] persists,}"}', '{"text": "Pain,] persists,}"}', ()),
    ("closers missing, no end_id", '{"facts": [{"text": "Pain"}', None,
     "closers missing and end_id not last"),
]


def test_repair_table(capsys):
    failures = []
    for name, source, expected, changes in REPAIRS:
        try:
            if expected is None:
                with pytest.raises(RepairError, match=changes):
                    repair(source, nonce=NONCE)
            else:
                result = repair(source, nonce=NONCE)
                assert result.text == expected, (result.text, expected)
                assert result.repairs == changes, (result.repairs, changes)
                assert json.loads(result.text) == json.loads(expected)
        except (AssertionError, RepairError, pytest.fail.Exception) as exc:
            failures.append((name, str(exc)))
    passed = len(REPAIRS) - len(failures)
    with capsys.disabled():
        print(f"repair_ok={passed} of 13")
    assert len(REPAIRS) == 13
    assert not failures, "\n".join(f"{name}: {message}" for name, message in failures)


def test_unfence_is_pure():
    inner = "  " + GOOD + "  "
    for opening in ("```json", "```"):
        assert unfence(" \n" + opening + "\n" + inner + "\n```\n ") == inner
    for source in (inner, "```json\n" + GOOD, GOOD + "\n```", "```python\n" + GOOD + "\n```"):
        assert unfence(source) == source


@pytest.mark.parametrize("text", [r'He said \"no weakness\".', r'path\\', r'escaped \\\" comma,]'])
def test_escaped_quotes_and_backslashes(text):
    source = '{"text": "' + text + '", "end_id": "' + NONCE + '"'
    result = repair(source, nonce=NONCE)
    assert result.text == source + "}"
    assert result.repairs == ("closers",)
    assert json.loads(result.text)["text"] == json.loads('"' + text + '"')


@pytest.mark.parametrize("source", [
    '{"value": NaN}', '{"value": Infinity}', '{"value": -Infinity}', '{/* comment */ "value": 1}',
    GOOD + '{}', '{"text": "bad\\q"}', '{"facts": [}',
    '{"end_id": "' + NONCE + '", "later": "Pain"',
    '{"end_id": "wrong"', '{"text": "\\\"end_id\\\": \\\"' + NONCE + '\\\""',
])
def test_non_punctuation_faults_are_refused(source):
    with pytest.raises(RepairError):
        repair(source, nonce=NONCE)


def test_every_raw_control_is_replaced_but_escaped_controls_are_kept():
    source = '{"text": "' + "".join(chr(n) for n in range(32)) + r'\n\r\t"}'
    result = repair(source, nonce=NONCE)
    assert result.text == '{"text": "' + " " * 32 + r'\n\r\t"}'
    assert result.repairs == ("control",)


@pytest.mark.parametrize('loader', ['schema', 'candidate', 'key', 'model'])
def test_fix7_adjacent_json_loaders(tmp_path, loader):
    from io import BytesIO
    from casefile import benchcandidate, benchkey, config, matter, model, schema
    from conftest import ROOT, write_config

    path = tmp_path / 'duplicate.json'
    if loader == 'schema':
        path.write_text('{"type":"integer", "type":"string"}', encoding='utf-8')
        action, error, key = lambda: schema.load(path), schema.SchemaError, 'type'
    elif loader == 'candidate':
        source = '{"facts":[], "facts":[], "flags":[]}'
        action, error, key = lambda: benchcandidate.parse_text(source), benchcandidate.CandidateError, 'facts'
    elif loader == 'key':
        root = ROOT / 'tests/fixtures/matters/9001.001'
        path.write_text('{"facts":[], ' + (root / 'key.json').read_text(encoding='utf-8')[1:],
                        encoding='utf-8')
        action, error, key = lambda: benchkey.load(path, matter.load(root)), benchkey.BenchKeyError, 'facts'
    else:
        source = ('{"message":{"content":"READY"}, "done":false, "done":true, '
                  '"done_reason":"stop", "prompt_eval_count":10, "eval_count":2}')
        class Opener:
            def open(self, request, timeout):
                response = BytesIO(source.encode('utf-8'))
                response.getcode = lambda: 200
                return response
        client = model.ModelClient(config.load(write_config(tmp_path)).model, Opener())
        action, error, key = lambda: client.chat([]), model.ModelError, 'done'
    with pytest.raises(error, match=f'duplicate key {key}') as caught:
        action()
    if loader == 'model':
        assert caught.value.received and caught.value.raw == source
