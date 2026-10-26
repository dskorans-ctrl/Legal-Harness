"""Small Ollama native client with no proxies or redirects."""

from dataclasses import dataclass
import json
from urllib import error, request


class ModelError(RuntimeError):
    """The model did not return a usable answer."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ModelError(f"redirect refused: {code} to {newurl}")


def build_opener():
    return request.build_opener(request.ProxyHandler({}), NoRedirect())


@dataclass(frozen=True)
class Answer:
    content: str
    done_reason: str | None
    prompt_eval_count: int | None
    eval_count: int | None
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
        try:
            with self.opener.open(req, timeout=self.config.timeout_s) as response:
                status = response.getcode()
                if 300 <= status < 400:
                    raise ModelError(f"redirect refused: {status} to {response.headers.get('Location', '')}")
                payload = response.read()
        except error.HTTPError as exc:
            if 300 <= exc.code < 400:
                raise ModelError(f"redirect refused: {exc.code} to {exc.headers.get('Location', '')}") from exc
            raise ModelError(f"status={exc.code}: {exc.read(200)!r}") from exc
        except (OSError, error.URLError) as exc:
            raise ModelError(str(exc)) from exc
        if status != 200:
            raise ModelError(f"status={status}: {payload[:200]!r}")
        try:
            result = json.loads(payload)
        except (ValueError, UnicodeError) as exc:
            raise ModelError(f"status={status} non-JSON: {payload[:200]!r}") from exc
        if not isinstance(result, dict):
            raise ModelError(f"status={status} expected JSON object: {payload[:200]!r}")
        return result

    def chat(self, messages, *, options=None):
        # Required settings cannot be removed or overridden by a caller.
        settings = dict(options or {})
        settings.update(num_ctx=self.config.num_ctx, temperature=self.config.temperature)
        raw = self._request("/api/chat", {"model": self.config.name, "messages": messages,
                                          "stream": False, "options": settings})
        message = raw.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ModelError(f"status=200 missing message.content: {str(raw)[:200]}")
        if not content.strip():
            raise ModelError(f"status=200 empty message.content: {str(raw)[:200]}")
        if raw.get("done") is not True:
            raise ModelError("status=200 done must be true")
        for field in ("prompt_eval_count", "eval_count"):
            if raw.get(field) is not None and type(raw[field]) is not int:
                raise ModelError(f"status=200 invalid {field}")
        if raw.get("done_reason") is not None and not isinstance(raw["done_reason"], str):
            raise ModelError("status=200 invalid done_reason")
        return Answer(content, raw.get("done_reason"), raw.get("prompt_eval_count"),
                      raw.get("eval_count"), raw)
