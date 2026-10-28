"""Small Ollama native client with no proxies or redirects."""

from dataclasses import dataclass
import errno
import http.client
import json
import socket
from urllib import error, request

from casefile import jsonrepair


TEMPLATE_TOKENS = 64


def tokens_at_most(text: str) -> int:
    return len(text.encode("utf-8"))


def context_length_error(message: str) -> bool:
    folded = message.casefold()
    return "context length" in folded or "exceeds the available context" in folded


def reply_error(status, payload):
    """Keep the received body intact while making a short, readable error line."""
    text = payload.decode("utf-8", errors="replace")
    try:
        body = jsonrepair.loads(text)
    except (ValueError, UnicodeError):
        body = None
    detail = body.get("error") if isinstance(body, dict) else None
    detail = " ".join((detail if isinstance(detail, str) else text).split())
    if len(detail) > 160:
        detail = detail[:157].rsplit(" ", 1)[0] if " " in detail[:157] else ""
        detail = detail.rstrip() + " ..."
    return f"status={status}: {detail}"


def no_reply_reason(exc, host):
    """Describe transport failures without exposing exception representations."""
    cause = exc.reason if isinstance(exc, error.URLError) else exc
    if isinstance(cause, ConnectionRefusedError):
        detail = "connection refused"
    elif isinstance(cause, TimeoutError):
        detail = "connection timed out"
    elif isinstance(cause, socket.gaierror):
        detail = "server address could not be found"
    elif isinstance(cause, OSError) and cause.errno in (errno.ENETUNREACH, errno.EHOSTUNREACH):
        detail = "network unreachable"
    elif isinstance(cause, (ConnectionError, http.client.RemoteDisconnected)):
        detail = "connection closed before a reply"
    elif isinstance(cause, http.client.HTTPException):
        detail = "no complete reply"
    else:
        detail = "server could not be reached"
    return f"no reply from the model server at {host} ({detail})"


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
        raise ModelError(reply_error(code, reply), reply.decode("utf-8", errors="replace"),
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
                    raise ModelError(reply_error(status, reply),
                                     reply.decode("utf-8", errors="replace"), received=True)
                payload = response.read()
        except error.HTTPError as exc:
            try:
                reply = exc.read()
            except http.client.IncompleteRead as short:
                reply = short.partial
            except (OSError, http.client.HTTPException):
                reply = b""
            raise ModelError(reply_error(exc.code, reply), reply.decode("utf-8", errors="replace"),
                             received=True) from exc
        except http.client.IncompleteRead as exc:
            partial = exc.partial.decode("utf-8", errors="replace")
            message = reply_error(status, exc.partial) if received else no_reply_reason(exc, self.config.host)
            raise ModelError(message, partial, received=received) from exc
        except (OSError, error.URLError, http.client.HTTPException) as exc:
            message = (str(exc) or type(exc).__name__) if received else no_reply_reason(exc, self.config.host)
            raise ModelError(message, received=received) from exc
        if status != 200:
            raise ModelError(reply_error(status, payload), payload.decode("utf-8", errors="replace"),
                             received=True)
        text = payload.decode("utf-8", errors="replace")
        try:
            result = jsonrepair.loads(payload)
        except (ValueError, UnicodeError) as exc:
            raise ModelError(reply_error(status, payload), text,
                             received=True) from exc
        if not isinstance(result, dict):
            raise ModelError(reply_error(status, payload), text, received=True)
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
        if not isinstance(content, str) or not content.strip():
            raise ModelError("the model sent no answer text", raw, received=True)
        if raw.get("done") is not True:
            raise ModelError("the model did not finish its reply (done must be true)", raw, received=True)
        for field in ("prompt_eval_count", "eval_count", "prompt_eval_cached_count"):
            if raw.get(field) is not None and type(raw[field]) is not int:
                raise ModelError(f"the reply has an invalid token count ({field} must be an integer)",
                                 raw, received=True)
        if raw.get("done_reason") is not None and not isinstance(raw["done_reason"], str):
            raise ModelError("the reply has no valid stop reason (done_reason must be a string)",
                             raw, received=True)
        return Answer(content, raw.get("done_reason"), raw.get("prompt_eval_count"),
                      raw.get("eval_count"), raw.get("prompt_eval_cached_count"), raw)
