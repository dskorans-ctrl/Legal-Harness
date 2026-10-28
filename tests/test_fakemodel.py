"""All prompts and responses here are invented and contain no matter facts."""

import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

import pytest

from fakemodel import FakeModel, FakeTransport
from fakemodel.__main__ import main
from fakemodel.server import serve
from fakemodel.core import MODES
from fakemodel.bench import recordings_for
from conftest import ROOT


MESSAGES = [
    {"role": "system", "content": "Reply with the single word READY."},
    {"role": "user", "content": "casefile doctor warmup"},
]


def chat(fake, **overrides):
    request = {"model": "qwen3.8:27b", "messages": MESSAGES, "stream": False,
               "options": {"num_ctx": 65536, "temperature": 0.1}}
    request.update(overrides)
    return fake.handle("POST", "/api/chat", json.dumps(request).encode())


def test_modes(capsys):
    checks = []
    for mode in ("replay", "truncated", "malformed", "forbidden", "short_context", "empty"):
        model = FakeModel(mode=mode)
        assert model.handle("GET", "/api/ps")[1] == {"models": []}
        status, answer = chat(model)
        assert status == 200
        content = answer["message"]["content"]
        if mode == "replay":
            ok = (content == "READY" and answer["done_reason"] == "stop"
                  and answer["prompt_eval_count"] == sum(len(m["content"]) for m in MESSAGES) // 4 + 8)
        elif mode == "truncated":
            ok = answer["done_reason"] == "length" and len(content) == len("READY") // 2
        elif mode == "malformed":
            try:
                json.loads(content)
            except json.JSONDecodeError:
                ok = True
            else:
                ok = False
        elif mode == "forbidden":
            ok = "IME" in content
        elif mode == "short_context":
            ok = model.handle("GET", "/api/ps")[1]["models"][0]["context_length"] == 8192
        else:
            ok = content == "" and answer["done_reason"] == "stop"
        checks.append(ok)
        assert set(answer) == {"model", "created_at", "message", "done", "done_reason",
                               "total_duration", "load_duration", "prompt_eval_count",
                               "prompt_eval_duration", "eval_count", "eval_duration"}
        assert answer["eval_count"] == len(content) // 4 + 1
    refusals = [chat(FakeModel(), messages=[{"role": "user", "content": "unknown invented prompt"}])[0] == 404,
                chat(FakeModel(), stream=True)[0] == 400]
    with capsys.disabled():
        print(f"modes_ok={sum(checks)} of 6 refusals={sum(refusals)} of 2", flush=True)
    assert all(checks), checks
    assert all(refusals), refusals


def test_fail_closed_requests_and_modes():
    model = FakeModel()
    assert chat(model, typo="refuse")[0] == 400
    assert chat(model, stream=0)[0] == 400
    assert model.handle("POST", "/api/chat", b'{}') == (
        400, {"error": "fakemodel: stream must be false"})
    assert chat(model, model="invented-unknown-model")[0] == 404
    request = {"model": "qwen3.8:27b", "messages": MESSAGES}
    assert model.handle("POST", "/api/chat", json.dumps(request).encode()) == (
        400, {"error": "fakemodel: stream must be false"})
    for body in (b"broken", b"[]", b'"text"', b"null"):
        assert model.handle("POST", "/api/chat", body)[0] == 400
    assert model.handle("GET", "/unknown")[0] == 404
    status, payload = model.handle("POST", "/_fake/mode", b'{"mode":"unknown"}')
    assert status == 400
    assert "replay, truncated, malformed, forbidden, short_context, empty" in payload["error"]
    assert model.mode == "replay"
    assert model.handle("POST", "/_fake/mode", b'{"mode":"empty"}') == (200, {"mode": "empty"})
    assert model.handle("GET", "/_fake/mode") == (200, {"mode": "empty"})
    assert chat(model)[1]["message"]["content"] == ""
    with pytest.raises(ValueError, match="unknown mode"):
        FakeModel(mode="unknown")
    with pytest.raises(SystemExit) as exc:
        main(["--mode", "unknown"])
    assert exc.value.code == 2


def test_native_metadata_and_transport():
    model = FakeModel()
    assert model.handle("GET", "/api/version") == (200, {"version": "0.0.0-fake"})
    assert model.handle("GET", "/api/tags")[1]["models"][0]["name"] == "qwen3.8:27b"
    status, show = model.handle("POST", "/api/show", b'{"model":"qwen3.8:27b"}')
    assert status == 200 and show["parameters"] == "num_ctx 65536"
    assert show["modelfile"] == "FROM qwen\nPARAMETER num_ctx 65536"
    transport = FakeTransport(model)
    # Reversing object-key order keeps the exact same recorded messages.
    messages = [{"content": m["content"], "role": m["role"]} for m in MESSAGES]
    request = Request("http://127.0.0.1:18434/api/chat", data=json.dumps(
        {"model": "qwen3.8:27b", "messages": messages, "stream": False}).encode())
    with transport.open(request, timeout=3) as response:
        assert response.status == response.getcode() == 200
        assert json.load(response)["message"]["content"] == "READY"
    assert transport.requests == [(request, 3)]
    assert model.handle("GET", "/api/ps")[1]["models"][0]["context_length"] == 65536
    with pytest.raises(HTTPError) as exc:
        transport.open(Request("http://127.0.0.1:18434/missing"))
    assert exc.value.code == 404


def test_short_context_caps_large_recorded_prompt():
    messages = [{"role": "user", "content": "invented " * 5000}]
    model = FakeModel(mode="short_context", recordings=[
        {"name": "invented-long-prompt", "messages": messages, "answer": "READY"}])
    assert chat(model, messages=messages)[1]["prompt_eval_count"] == 8192


def test_truncate_key(capsys):
    replies = [chat(FakeModel(), truncate=value) for value in (False, True)]
    ok = all(status == 200 and answer.get("message", {}).get("content") == "READY"
             for status, answer in replies)
    with capsys.disabled():
        print(f"fake_truncate_key={int(ok)}", flush=True)
    assert ok, f"fake_truncate_key={int(ok)}"


def test_prompt_too_long(capsys):
    expected = {"error": "the prompt is longer than the context length currently available "
                "to the model; shorten the prompt, adjust the context length in settings, "
                "or use a model with a longer context length"}
    replies = [chat(FakeModel(mode="prompt_too_long"), **options)
               for options in ({}, {"truncate": False}, {"truncate": True})]
    with capsys.disabled():
        print(f"prompt_too_long_status={replies[0][0]}", flush=True)
    for status, answer in replies:
        assert status == 400 and answer == expected


def test_pipeline_canonical_lookup_and_retry():
    expected = ('replay', 'truncated', 'malformed', 'forbidden', 'short_context', 'empty', 'incomplete',
                'prompt_too_long', 'cut_prompt', 'cut_answer', 'repairable', 'unrepairable',
                'bad_schema', 'bad_quote', 'forbidden_json', 'empty_answer', 'retry_ok')
    assert MODES == expected and len(MODES) == 17
    recordings = recordings_for(ROOT / 'tests/fixtures/matters/9001.001')
    assert [r['name'] for r in recordings] == ['gates-9001.001']
    row = recordings[0]
    first, last = list(json.loads(row['answer']))[::len(json.loads(row['answer'])) - 1]
    assert (first, last) == ('prompt_id', 'end_id')
    fake = FakeModel(mode='retry_ok', recordings=recordings)
    for retry, nonce in ((False, '0123456789abcdef'), (True, 'fedcba9876543210')):
        messages = [{**m, 'content': m['content'].replace('__PROMPT_ID__', nonce)} for m in row['messages']]
        if retry:
            header, body = messages[1]['content'].split('\n', 1)
            messages[1]['content'] = header + '\nRetry: invented repair failure\n' + body
        status, reply = chat(fake, messages=messages, truncate=False)
        assert status == 200
        content = reply['message']['content']
        assert '__PROMPT_ID__' not in content
        if retry:
            obj = json.loads(content)
            assert obj['prompt_id'] == obj['end_id'] == nonce
            assert obj['facts'] == json.loads(row['answer'])['facts']
        else:
            assert content.startswith('{"prompt_id": "' + nonce + '"')
            assert content.endswith('"end_id": "' + nonce + '"}')
            with pytest.raises(json.JSONDecodeError):
                json.loads(content)
    # Only the first line is a nonce line, and only the user second line is a retry line.
    preserved = [{'role': 'system', 'content': 'prompt_id: __PROMPT_ID__\n'
                  'prompt_id: aaaaaaaaaaaaaaaa'},
                 {'role': 'user', 'content': 'Matter 9003.001\nbody\nRetry: record text'}]
    fake = FakeModel(recordings=[{'messages': preserved, 'answer': 'READY'}])
    live = [{**m, 'content': m['content']} for m in preserved]
    live[0]['content'] = live[0]['content'].replace('__PROMPT_ID__', 'bbbbbbbbbbbbbbbb')
    assert chat(fake, messages=live)[1]['message']['content'] == 'READY'


@pytest.mark.socket
def test_http_roundtrip(capsys):
    try:
        server = serve("127.0.0.1", 0, FakeModel())
    except PermissionError as exc:
        pytest.fail(f"fake HTTP bind failed: {exc}")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = Request(f"http://127.0.0.1:{server.server_port}/api/chat", data=json.dumps(
            {"model": "qwen3.8:27b", "messages": MESSAGES, "stream": False}).encode())
        with build_opener(ProxyHandler({})).open(request, timeout=5) as response:
            answer = json.load(response)
        assert answer["message"]["content"] == "READY"
        assert answer["done_reason"] == "stop"
        assert answer["prompt_eval_count"] == sum(len(m["content"]) for m in MESSAGES) // 4 + 8
        with capsys.disabled():
            print("http_ok=1", flush=True)
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_body_recording_and_output_faults(tmp_path):
    from casefile import cards, config, gates, matter, model
    from conftest import write_config
    from fakemodel.bench import recording_for

    card=cards.card('02-C-DEFDOC')
    pages=(matter.Page('probe',1,'Pain 7/10.',('MED0001',)),)
    answer=dict(section='primary',questions=[dict(text='Pain was recorded, correct?',quote='Pain 7/10.',cite='MED0001',note='')],points_for_our_expert=[])
    body='Matter 9001.001\nFacts:\n[F1] MED0001: Pain 7/10.\n'
    row=recording_for(card,pages,'9001.001',answer,body=body)
    fake=FakeModel(recordings=[]);fake.record(row)
    client=model.ModelClient(config.load(write_config(tmp_path)).model,FakeTransport(fake))
    msgs=gates.messages(card,pages,'0123456789abcdef',matter='9001.001',body=body)
    try:
        reply=json.loads(client.chat(msgs,truncate=False).content)
    except model.ModelError:
        reply=None
    ok=int(reply == dict(prompt_id='0123456789abcdef',**answer,end_id='0123456789abcdef'))
    print(f'recording_body_ok={ok}')
    assert ok == 1, 'recording_body_ok=0'
    passed=[]
    for mode in ('bad_schema','forbidden_json','empty_answer'):
        fake.mode=mode
        obj=json.loads(client.chat(msgs,truncate=False).content)
        if mode == 'bad_schema':
            assert 'text' not in obj['questions'][0]
        elif mode == 'forbidden_json':
            assert obj['questions'][0]['text'] == 'The IME found no injury.'
        else:
            assert obj['questions'] == obj['points_for_our_expert'] == []
        passed.append(mode)
    print(f'fault_branches={len(passed)} of 3')
