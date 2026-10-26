"""Invented recorded answers exercise the native client without network access."""

from io import BytesIO
import json
from threading import Thread
from urllib.request import ProxyHandler

import pytest

from casefile.config import load
from casefile.doctor import MESSAGES
from casefile.model import ModelClient, ModelError, build_opener
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


def test_404(tmp_path):
    client = ModelClient(load(write_config(tmp_path)).model, FakeTransport(FakeModel()))
    with pytest.raises(ModelError, match="status=404"):
        client.chat([{"role": "user", "content": "invented unmatched request"}])


def test_non_json(tmp_path):
    response = BytesIO(b"invented non-JSON")
    response.getcode = lambda: 200
    with pytest.raises(ModelError, match="non-JSON"):
        ModelClient(load(write_config(tmp_path)).model, Transport(response)).chat(MESSAGES)


@pytest.mark.parametrize("payload,match", [({}, "missing"), ({"message": {"content": "  "}}, "empty")])
def test_missing_or_blank(tmp_path, payload, match):
    with pytest.raises(ModelError, match=match):
        ModelClient(load(write_config(tmp_path)).model, Transport(FakeResponse(200, payload))).chat(MESSAGES)


def test_empty(tmp_path):
    with pytest.raises(ModelError, match="empty"):
        ModelClient(load(write_config(tmp_path)).model,
                    FakeTransport(FakeModel(mode="empty"))).chat(MESSAGES)


def test_no_proxy():
    assert not any(isinstance(h, ProxyHandler) and h.proxies for h in build_opener().handlers)


def test_redirect_refused(tmp_path):
    response = FakeResponse(302, {})
    response.headers["Location"] = "http://127.0.0.1:1/"
    with pytest.raises(ModelError, match="redirect refused"):
        ModelClient(load(write_config(tmp_path)).model, Transport(response)).chat(MESSAGES)
    handler = next(h for h in build_opener().handlers if hasattr(h, "redirect_request"))
    with pytest.raises(ModelError, match="redirect refused"):
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
