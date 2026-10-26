"""All prompts and responses here are invented and contain no matter facts."""

import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

import pytest

from fakemodel import FakeModel, FakeTransport
from fakemodel.__main__ import main
from fakemodel.server import serve


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
