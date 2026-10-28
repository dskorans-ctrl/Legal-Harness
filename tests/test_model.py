"""Invented recorded answers exercise the native client without network access."""

from http.client import BadStatusLine, IncompleteRead, RemoteDisconnected
from io import BytesIO
import json
import socket
import time
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler

import pytest

from casefile.config import load
from casefile.doctor import MESSAGES
from casefile.model import (TEMPLATE_TOKENS, ModelClient, ModelError, build_opener,
                            context_length_error, tokens_at_most)
from conftest import write_config
from fakemodel.core import FakeModel, FakeResponse, FakeTransport
from fakemodel.server import serve


class Transport:
    def __init__(self, response):
        self.response = response

    def open(self, request, timeout):
        return self.response


def test_fields(tmp_path):
    config = load(write_config(tmp_path)).model
    transport = FakeTransport(FakeModel())
    answer = ModelClient(config, transport).chat(MESSAGES, options={"num_ctx": 1})
    body = json.loads(transport.requests[0][0].data)
    assert body["stream"] is False
    assert body["options"] == {"num_ctx": 65536, "temperature": 0.1}
    assert transport.requests[0][1] == 600
    assert (answer.content, answer.done_reason) == ("READY", "stop")
    assert answer.prompt_eval_count == answer.raw["prompt_eval_count"]
    assert answer.eval_count == answer.raw["eval_count"]


def test_chat_body_keys(tmp_path, capsys):
    config = load(write_config(tmp_path)).model
    transport = FakeTransport(FakeModel())
    client = ModelClient(config, transport)
    base = {"model": config.name, "messages": MESSAGES, "stream": False,
            "options": {"num_ctx": 65536, "temperature": 0.1}}
    cases = [({}, base), ({"think": None, "truncate": None}, base),
             ({"think": False, "truncate": False}, dict(base, think=False, truncate=False)),
             ({"think": True, "truncate": True}, dict(base, think=True, truncate=True)),
             ({"think": False}, dict(base, think=False)),
             ({"truncate": False}, dict(base, truncate=False))]
    bodies = []
    for kwargs, expected in cases:
        client.chat(MESSAGES, **kwargs)
        bodies.append(json.loads(transport.requests[-1][0].data) == expected)
    ok = int(all(bodies))
    with capsys.disabled():
        print(f"chat_body_keys={ok}")
    assert ok == 1, bodies


def test_cached_count_read(tmp_path, capsys):
    config = load(write_config(tmp_path)).model
    payload = {"message": {"content": "READY"}, "done_reason": "stop", "done": True,
               "prompt_eval_count": 20, "eval_count": 2}
    for count in (7, 0, None):
        raw = dict(payload, prompt_eval_cached_count=count)
        answer = ModelClient(config, Transport(FakeResponse(200, raw))).chat(MESSAGES)
        assert answer.prompt_eval_cached_count == count
        assert answer.raw == raw
    answer = ModelClient(config, Transport(FakeResponse(200, payload))).chat(MESSAGES)
    assert answer.prompt_eval_cached_count is None
    for count in ("x", True, 1.5, [], {}):
        raw = dict(payload, prompt_eval_cached_count=count)
        with pytest.raises(ModelError, match=r"^the reply has an invalid token count \(prompt_eval_cached_count must be an integer\)$") as info:
            ModelClient(config, Transport(FakeResponse(200, raw))).chat(MESSAGES)
        assert info.value.received is True and info.value.raw == raw
    with capsys.disabled():
        print("cached_count_read=1")


@pytest.mark.parametrize("text,want", [("", 0), ("abc", 3), ("ﬁ", 3), ("’", 3)])
def test_tokens_at_most(text, want, capsys):
    actual = tokens_at_most(text)
    with capsys.disabled():
        print(f"tokens_at_most({json.dumps(text, ensure_ascii=False)})={actual}")
    assert actual == want
    assert TEMPLATE_TOKENS == 64


@pytest.mark.parametrize("message,want", [
    ("the prompt is longer than the context length currently available to the model", True),
    ("CONTEXT LENGTH exceeded", True), ("Exceeds The Available Context", True),
    ("invented server busy", False), ("", False),
])
def test_context_length_error(message, want):
    assert context_length_error(message) is want


def test_404(tmp_path):
    client = ModelClient(load(write_config(tmp_path)).model, FakeTransport(FakeModel()))
    with pytest.raises(ModelError, match="status=404"):
        client.chat([{"role": "user", "content": "invented unmatched request"}])


def test_non_json(tmp_path):
    response = BytesIO(b"invented non-JSON")
    response.getcode = lambda: 200
    with pytest.raises(ModelError, match="^status=200: invented non-JSON$"):
        ModelClient(load(write_config(tmp_path)).model, Transport(response)).chat(MESSAGES)


@pytest.mark.parametrize("payload", [{}, {"message": {}}, {"message": {"content": "  "}},
                                     {"message": {"content": 3}}])
def test_missing_or_blank(tmp_path, payload):
    with pytest.raises(ModelError, match="^the model sent no answer text$") as caught:
        ModelClient(load(write_config(tmp_path)).model, Transport(FakeResponse(200, payload))).chat(MESSAGES)
    assert caught.value.raw == payload


def test_empty(tmp_path):
    with pytest.raises(ModelError, match="^the model sent no answer text$"):
        ModelClient(load(write_config(tmp_path)).model,
                    FakeTransport(FakeModel(mode="empty"))).chat(MESSAGES)


def test_no_proxy():
    assert not any(isinstance(h, ProxyHandler) and h.proxies for h in build_opener().handlers)


def test_redirect_refused(tmp_path):
    response = FakeResponse(302, {})
    response.headers["Location"] = "http://127.0.0.1:1/"
    with pytest.raises(ModelError, match=r"^status=302: \{\}$"):
        ModelClient(load(write_config(tmp_path)).model, Transport(response)).chat(MESSAGES)
    handler = next(h for h in build_opener().handlers if hasattr(h, "redirect_request"))
    with pytest.raises(ModelError, match="^status=302: $"):
        handler.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1:1/")


@pytest.mark.socket
@pytest.mark.parametrize("proxy", [False, True], ids=["plain", "proxy_environment"])
def test_http(tmp_path, monkeypatch, proxy):
    if proxy:
        for key in ("NO_PROXY", "no_proxy"):
            monkeypatch.delenv(key, raising=False)
        for key in ("HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
            monkeypatch.setenv(key, "http://127.0.0.1:1")
    server = serve(port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = load(write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}"))
        assert ModelClient(config.model).chat(MESSAGES).content == "READY"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("done", [False, None, 0, 1, "true"])
def test_requires_completed_answer(tmp_path, done):
    payload = {"message": {"content": "READY"}, "done_reason": "stop", "done": done,
               "prompt_eval_count": 20, "eval_count": 2}
    with pytest.raises(ModelError, match=r"^the model did not finish its reply \(done must be true\)$"):
        ModelClient(load(write_config(tmp_path)).model,
                    Transport(FakeResponse(200, payload))).chat(MESSAGES)


def test_fake_incomplete_answer(tmp_path):
    with pytest.raises(ModelError, match=r"^the model did not finish its reply \(done must be true\)$"):
        ModelClient(load(write_config(tmp_path)).model,
                    FakeTransport(FakeModel(mode="incomplete"))).chat(MESSAGES)


@pytest.mark.parametrize('field,detail', [
    ('prompt_eval_count', 'the reply has an invalid token count (prompt_eval_count must be an integer)'),
    ('eval_count', 'the reply has an invalid token count (eval_count must be an integer)'),
    ('done_reason', 'the reply has no valid stop reason (done_reason must be a string)'),
])
def test_fix2_invalid_reply_fields(tmp_path, field, detail):
    raw = {'message': {'content': 'READY'}, 'done': True, field: []}
    err = caught(tmp_path, Transport(FakeResponse(200, raw)))
    assert str(err) == detail
    assert err.raw == raw


class Refusing:
    """An opener whose open() itself fails: no status line ever arrives."""

    def __init__(self, exc):
        self.exc = exc

    def open(self, request, timeout=None):
        raise self.exc


class BrokenBody(BytesIO):
    """A reply whose status line arrived but whose body read fails."""

    def __init__(self, status, exc):
        super().__init__(b"")
        self.status = status
        self.exc = exc

    def getcode(self):
        return self.status

    def read(self, *args):
        raise self.exc


def caught(tmp_path, opener, messages=MESSAGES):
    client = ModelClient(load(write_config(tmp_path)).model, opener)
    with pytest.raises(ModelError) as info:
        client.chat(messages)
    return info.value


@pytest.mark.parametrize("exc", [ConnectionRefusedError("refused"), URLError("no route"),
                                 RemoteDisconnected("closed without a reply"), BadStatusLine("garbage"),
                                 socket.timeout("timed out")],
                         ids=["refused", "urlerror", "closed", "bad_status_line", "connect_timeout"])
def test_no_status_line_is_not_received(tmp_path, exc):
    err = caught(tmp_path, Refusing(exc))
    assert (err.received, err.raw) == (False, None)


def test_status_line_then_read_timeout_is_received(tmp_path, capsys):
    err = caught(tmp_path, Transport(BrokenBody(200, socket.timeout("timed out"))))
    with capsys.disabled():
        print(f"read_timeout received={err.received}")
    assert (err.received, err.raw) == (True, None)


def test_incomplete_read_keeps_the_partial_body(tmp_path, capsys):
    err = caught(tmp_path, Transport(BrokenBody(200, IncompleteRead(b"par", 10))))
    with capsys.disabled():
        print(f"incomplete_read_row={int(err.raw == 'par' and err.received)}")
    assert (err.raw, err.received) == ("par", True)
    assert str(err) == 'status=200: par'


def test_http_error_without_a_body_stream_has_an_empty_body(tmp_path, capsys):
    err = caught(tmp_path, Refusing(HTTPError("http://x", 503, "x", {}, None)))
    with capsys.disabled():
        print(f"no_stream_error raw={err.raw!r} received={err.received}")
    assert (err.raw, err.received) == ("", True)


def test_error_after_a_received_reply_says_received(tmp_path):
    for mode in ("empty", "incomplete"):
        err = caught(tmp_path, FakeTransport(FakeModel(mode=mode)))
        assert err.received is True, mode
    err = caught(tmp_path, FakeTransport(FakeModel()), [{"role": "user", "content": "invented unmatched request"}])
    assert (err.received, "status=404" in str(err)) == (True, True)


def test_redirect_with_an_empty_body_is_received_and_stored(tmp_path):
    response = FakeResponse(302, {})
    response.headers["Location"] = "http://127.0.0.1:1/"
    response.read = lambda *a: b""
    err = caught(tmp_path, Transport(response))
    assert (err.raw, err.received) == ("", True)


def redirect_server(mode):
    """A loopback server that sends 302 headers, then a short body (truncated) or nothing (stall)."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    release = []

    def serve_one():
        conn, _ = listener.accept()
        seen = b""
        while b"\r\n\r\n" not in seen:
            seen += conn.recv(65536)
        length = int(seen.lower().split(b"content-length:")[1].split(b"\r\n")[0])
        while len(seen.split(b"\r\n\r\n", 1)[1]) < length:    # unread request bytes would reset the socket
            seen += conn.recv(65536)
        head = b"HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1:1/\r\nContent-Length: 50\r\n\r\n"
        conn.sendall(head + (b"partial" if mode == "truncated" else b""))
        if mode == "truncated":
            conn.close()
        else:
            deadline = 5
            while deadline and not release:
                deadline -= 0.1
                time.sleep(0.1)
            conn.close()

    thread = Thread(target=serve_one, daemon=True)
    thread.start()
    return listener, thread, release


@pytest.mark.socket
@pytest.mark.parametrize("mode,raw", [("truncated", "partial"), ("stall", "")])
def test_redirect_body_failure_is_received(tmp_path, capsys, mode, raw):
    listener, thread, release = redirect_server(mode)
    try:
        config = load(write_config(tmp_path, host=f"http://127.0.0.1:{listener.getsockname()[1]}",
                                   timeout_s=1)).model
        with pytest.raises(ModelError) as info:
            ModelClient(config).chat(MESSAGES)
    finally:
        release.append(1)
        thread.join(timeout=10)
        listener.close()
    err = info.value
    with capsys.disabled():
        print(f"redirect_{mode} received={err.received} raw={err.raw!r}")
    assert str(err) == f"status=302: {raw}"
    assert (err.received, err.raw) == (True, raw)


@pytest.mark.parametrize('route', ['status', 'http_error', 'redirect_handler'])
@pytest.mark.parametrize('status,body,expected', [
    (404, b'{"error":"model not found","detail":"private debug"}', 'model not found'),
    (503, b'  invented\n  server\tbusy  ', 'invented server busy'),
    (503, json.dumps({'error': 'invented ' * 25}).encode(), 'invented ' * 16 + 'invented ...'),
    (503, b'bad \xff reply', 'bad \ufffd reply'),
    (503, b'', ''),
    (200, b'invented invalid JSON', 'invented invalid JSON'),
    (200, b'[1, 2]', '[1, 2]'),
])
def test_fix2_error_text_and_raw(tmp_path, route, status, body, expected):
    if route == 'status':
        response = BytesIO(body)
        response.getcode = lambda: status
        opener = Transport(response)
    elif route == 'http_error':
        opener = Refusing(HTTPError('http://invented', status, 'error', {}, BytesIO(body)))
    else:
        handler = next(h for h in build_opener().handlers if hasattr(h, 'redirect_request'))
        class Redirect:
            def open(self, request, timeout):
                handler.redirect_request(request, BytesIO(body), status, 'error', {}, 'http://invented')
        opener = Redirect()
    err = caught(tmp_path, opener)
    assert str(err) == f'status={status}: {expected}', 'H1: received error text differs'
    assert err.received is True
    assert err.raw == body.decode('utf-8', errors='replace')
