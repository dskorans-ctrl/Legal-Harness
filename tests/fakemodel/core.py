"""Pure, recorded Ollama responses. All content is invented test data."""

from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit


MODES = ("replay", "truncated", "malformed", "forbidden", "short_context", "empty", "incomplete",
         "prompt_too_long")
DEFAULT_MODEL = "qwen3.8:27b"


def _canonical(messages):
    return json.dumps(messages, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class FakeModel:
    def __init__(self, *, mode="replay", model=DEFAULT_MODEL, context_length=65536,
                 recordings=None):
        self.mode = mode
        self.model = model
        self.context_length = context_length
        self.loaded = False
        self.requests = []
        if recordings is None:
            recordings = Path(__file__).with_name("recordings.json")
        if isinstance(recordings, (str, Path)):
            recordings = json.loads(Path(recordings).read_text(encoding="utf-8"))
        self.recordings = deepcopy(recordings)
        self._answers = {_canonical(row["messages"]): row["answer"] for row in self.recordings}

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in MODES:
            raise ValueError(f"fakemodel: unknown mode {value!r}; expected: {', '.join(MODES)}")
        self._mode = value

    @property
    def ctx(self):
        return 8192 if self.mode == "short_context" else self.context_length

    def handle(self, method, path, body=b""):
        """Return HTTP status and JSON object, without opening a socket."""
        self.requests.append({"method": method, "path": path, "body": body})
        if method == "GET":
            if path == "/api/version":
                return 200, {"version": "0.0.0-fake"}
            if path == "/_fake/mode":
                return 200, {"mode": self.mode}
            if path == "/api/ps":
                models = []
                if self.loaded:
                    models.append({"name": self.model, "model": self.model, "size": 0,
                                   "digest": "fake", "details": {},
                                   "expires_at": "2099-01-01T00:00:00Z", "size_vram": 0,
                                   "context_length": self.ctx})
                return 200, {"models": models}
            if path == "/api/tags":
                return 200, {"models": [{"name": self.model, "model": self.model,
                                         "size": 0, "digest": "fake", "details": {},
                                         "modified_at": "2026-10-25T00:00:00Z"}]}
        if method != "POST" or path not in {"/_fake/mode", "/api/chat", "/api/show"}:
            return 404, {"error": "fakemodel: unknown path"}
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return 400, {"error": "fakemodel: expected JSON object"}
        if not isinstance(data, dict):
            return 400, {"error": "fakemodel: expected JSON object"}
        allowed = {"/_fake/mode": {"mode"}, "/api/show": {"model", "verbose"},
                   "/api/chat": {"model", "messages", "stream", "options", "format",
                                 "keep_alive", "tools", "think", "truncate"}}[path]
        unknown = data.keys() - allowed
        if unknown:
            return 400, {"error": f"fakemodel: unknown keys: {', '.join(sorted(unknown))}"}
        if path == "/_fake/mode":
            try:
                self.mode = data.get("mode")
            except ValueError as exc:
                return 400, {"error": str(exc)}
            return 200, {"mode": self.mode}
        if path == "/api/chat" and data.get("stream") is not False:
            return 400, {"error": "fakemodel: stream must be false"}
        if data.get("model") != self.model:
            return 404, {"error": "fakemodel: unknown model"}
        if path == "/api/show":
            return 200, {"modelfile": f"FROM qwen\nPARAMETER num_ctx {self.ctx}",
                         "parameters": f"num_ctx {self.ctx}", "details": {}}
        messages = data.get("messages")
        if not isinstance(messages, list) or not all(
            isinstance(m, dict) and set(m) == {"role", "content"}
            and isinstance(m["role"], str) and isinstance(m["content"], str)
            for m in messages
        ):
            return 400, {"error": "fakemodel: messages require role and content strings"}
        key = _canonical(messages)
        if key not in self._answers:
            return 404, {"error": "fakemodel: no recording for these messages"}
        content = self._answers[key]
        if self.mode == "prompt_too_long":
            return 400, {"error": "the prompt is longer than the context length currently available "
                        "to the model; shorten the prompt, adjust the context length in settings, "
                        "or use a model with a longer context length"}
        done_reason = "stop"
        if self.mode == "truncated":
            content = content[:len(content) // 2]
            done_reason = "length"
        elif self.mode == "malformed":
            content = '{"facts": [{"page": 1,'
        elif self.mode == "forbidden":
            content = "The IME found no injury; the doctor was retained by the employer."
        elif self.mode == "empty":
            content = ""
        prompt_count = sum(len(m["content"]) for m in messages) // 4 + 8
        if self.mode == "short_context":
            prompt_count = min(prompt_count, 8192)
        self.loaded = True
        return 200, {"model": self.model, "created_at": "2026-10-25T00:00:00Z",
                     "message": {"role": "assistant", "content": content}, "done": self.mode != "incomplete",
                     "done_reason": done_reason, "total_duration": 1000, "load_duration": 100,
                     "prompt_eval_count": prompt_count, "prompt_eval_duration": 200,
                     "eval_count": len(content) // 4 + 1, "eval_duration": 300}


class FakeResponse(BytesIO):
    def __init__(self, status, payload):
        super().__init__(json.dumps(payload).encode("utf-8"))
        self.status = status
        self.code = status
        self.headers = {"Content-Type": "application/json"}

    def getcode(self):
        return self.status


class FakeTransport:
    """urllib-compatible opener which never uses a network transport."""

    def __init__(self, model):
        self.model = model
        self.requests = []

    def open(self, request, timeout=None):
        self.requests.append((request, timeout))
        status, payload = self.model.handle(request.get_method(),
                                            urlsplit(request.full_url).path,
                                            request.data or b"")
        response = FakeResponse(status, payload)
        if status >= 400:
            raise HTTPError(request.full_url, status, payload.get("error", "error"),
                            response.headers, response)
        return response
