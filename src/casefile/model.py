"""Small Ollama native client with no proxies or redirects."""

from dataclasses import dataclass
import http.client
import json
from urllib import error, request


TEMPLATE_TOKENS = 64


def tokens_at_most(text: str) -> int:
    return len(text.encode("utf-8"))


def context_length_error(message: str) -> bool:
    folded = message.casefold()
    return "context length" in folded or "exceeds the available context" in folded


class ModelError(RuntimeError):
    """The model did not return a usable answer."""

    def __init__(self, message, raw=None, *, received=False):
        super().__init__(message)
        self.raw = raw
        # True once a status line arrived; False means the server never replied (bench exit 2, Q26).
        self.received = received


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # The status line arrived, so a body that fails to read still counts as a received reply.
        try:
            reply = b"" if fp is None else fp.read()
        except http.client.IncompleteRead as short:
            reply = short.partial
        except (OSError, http.client.HTTPException):
            reply = b""
        raise ModelError(f"redirect refused: {code} to {newurl}", reply.decode("utf-8", errors="replace"),
                         received=True)


def build_opener():
    return request.build_opener(request.ProxyHandler({}), NoRedirect())


@dataclass(frozen=True)
class Answer:
    content: str
    done_reason: str | None
    prompt_eval_count: int | None
    eval_count: int | None
    prompt_eval_cached_count: int | None
    raw: dict


class ModelClient:
    def __init__(self, config, opener=None):
        self.config = config
        self.opener = build_opener() if opener is None else opener

    def get(self, path):
        return self._request(path)

    def _request(self, path, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = request.Request(self.config.host.rstrip("/") + path, data=data,
                              headers={"Content-Type": "application/json"})
        received = False
        try:
            with self.opener.open(req, timeout=self.config.timeout_s) as response:
                received = True
                status = response.getcode()
                if 300 <= status < 400:
                    reply = response.read()
                    raise ModelError(f"redirect refused: {status} to {response.headers.get('Location', '')}",
                                     reply.decode("utf-8", errors="replace"), received=True)
                payload = response.read()
        except error.HTTPError as exc:
            try:
                reply = exc.read()
            except http.client.IncompleteRead as short:
                reply = short.partial
            except (OSError, http.client.HTTPException):
                reply = b""
            if 300 <= exc.code < 400:
                raise ModelError(f"redirect refused: {exc.code} to {exc.headers.get('Location', '')}",
                                 reply.decode("utf-8", errors="replace"), received=True) from exc
            raise ModelError(f"status={exc.code}: {reply[:200]!r}", reply.decode("utf-8", errors="replace"),
                             received=True) from exc
        except http.client.IncompleteRead as exc:
            partial = exc.partial.decode("utf-8", errors="replace")
            raise ModelError(f"incomplete read: {exc}", partial, received=received) from exc
        except (OSError, error.URLError, http.client.HTTPException) as exc:
            raise ModelError(str(exc) or type(exc).__name__, received=received) from exc
        if status != 200:
            raise ModelError(f"status={status}: {payload[:200]!r}", payload.decode("utf-8", errors="replace"),
                             received=True)
        text = payload.decode("utf-8", errors="replace")
        try:
            result = json.loads(payload)
        except (ValueError, UnicodeError) as exc:
            raise ModelError(f"status={status} non-JSON: {payload[:200]!r}", text,
                             received=True) from exc
        if not isinstance(result, dict):
            raise ModelError(f"status={status} expected JSON object: {payload[:200]!r}", text, received=True)
        return result

    def chat(self, messages, *, options=None, think=None, truncate=None):
        # Required settings cannot be removed or overridden by a caller.
        settings = dict(options or {})
        settings.update(num_ctx=self.config.num_ctx, temperature=self.config.temperature)
        body = {"model": self.config.name, "messages": messages,
                "stream": False, "options": settings}
        if think is not None:
            body["think"] = think
        if truncate is not None:
            body["truncate"] = truncate
        raw = self._request("/api/chat", body)
        message = raw.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ModelError(f"status=200 missing message.content: {str(raw)[:200]}", raw, received=True)
        if not content.strip():
            raise ModelError(f"status=200 empty message.content: {str(raw)[:200]}", raw, received=True)
        if raw.get("done") is not True:
            raise ModelError("status=200 done must be true", raw, received=True)
        for field in ("prompt_eval_count", "eval_count", "prompt_eval_cached_count"):
            if raw.get(field) is not None and type(raw[field]) is not int:
                raise ModelError(f"status=200 invalid {field}", raw, received=True)
        if raw.get("done_reason") is not None and not isinstance(raw["done_reason"], str):
            raise ModelError("status=200 invalid done_reason", raw, received=True)
        return Answer(content, raw.get("done_reason"), raw.get("prompt_eval_count"),
                      raw.get("eval_count"), raw.get("prompt_eval_cached_count"), raw)
