"""Pure, recorded Ollama responses. All content is invented test data."""

from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.parse import urlsplit


MODES = ("replay", "truncated", "malformed", "forbidden", "short_context", "empty", "incomplete",
         "prompt_too_long", "cut_prompt", "cut_answer", "repairable", "unrepairable",
         "bad_schema", "bad_quote", "forbidden_json", "empty_answer", "retry_ok")
DEFAULT_MODEL = "qwen3.8:27b"


def _canonical(messages):
    messages, _, _ = _prompt_parts(messages)
    return json.dumps(messages, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _prompt_parts(messages):
    canonical, nonce, retry = [], None, False
    for message in messages:
        lines = message["content"].split("\n")
        if lines and re.fullmatch(r"prompt_id: [0-9a-f]{16}", lines[0]):
            nonce = lines[0].split(": ", 1)[1]
            lines[0] = "prompt_id: __PROMPT_ID__"
        if message["role"] == "user" and len(lines) > 1 and lines[1].startswith("Retry: "):
            retry = True
            del lines[1]
        canonical.append({**message, "content": "\n".join(lines)})
    return canonical, nonce, retry


def _fault_content(content, mode):
    obj = json.loads(content)
    if "facts" not in obj and mode in {"bad_schema", "forbidden_json", "empty_answer"}:
        arrays = [v for k,v in obj.items() if isinstance(v, list)]
        if mode == "empty_answer":
            for value in arrays:
                value.clear()
        else:
            item = next(item for values in arrays for item in values if isinstance(item, dict))
            key = next(key for key,value in item.items() if isinstance(value, str))
            if mode == "bad_schema":
                del item[key]
            else:
                item[key] = "The IME found no injury."
        return json.dumps(obj, ensure_ascii=False)
    if mode == "bad_schema":
        del obj["facts"][0]["text"]
    elif mode == "bad_quote":
        obj["facts"][0]["quote"] = re.sub(
            r"\d", lambda hit: str((int(hit[0]) + 1) % 10), obj["facts"][0]["quote"], count=1)
        obj["facts"][1]["cite"] = "MED0099"
        quote_numbers = set(re.findall(r"\d+", obj["facts"][2]["quote"]))
        number = "99999"
        while number in quote_numbers:
            number += "9"
        obj["facts"][2]["text"] = re.sub(r"\d+", number, obj["facts"][2]["text"], count=1)
        obj["flags"][0]["cites"].append("MED0098")
    elif mode == "forbidden_json":
        obj["facts"][0]["text"] = "The IME found no injury."
    elif mode == "empty_answer":
        obj["facts"], obj["flags"] = [], []
    elif mode == "repairable":
        obj["facts"][0]["text"] = obj["facts"][0]["text"].replace(" ", "\t", 1)
    text = json.dumps(obj, ensure_ascii=False)
    if mode == "unrepairable":
        boundary = json.dumps(obj["facts"][0], ensure_ascii=False) + ", "
        text = text.replace(boundary, boundary[:-2] + " ", 1)
    elif mode == "repairable":
        facts = json.dumps(obj["facts"], ensure_ascii=False)
        text = text.replace(facts, facts[:-1] + ",]", 1).replace("\\t", "\t", 1)
        text = "```json\n" + text[:-1] + "\n```"
    return text


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

    def record(self, row):
        row = deepcopy(row)
        self.recordings.append(row)
        self._answers[_canonical(row["messages"])] = row["answer"]

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
        _, nonce, retry = _prompt_parts(messages)
        if nonce is not None:
            content = content.replace("__PROMPT_ID__", nonce)
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
        elif self.mode == "cut_prompt":
            content = content.replace(nonce or "__PROMPT_ID__", "unknown")
        elif self.mode == "cut_answer":
            content = content[:len(content) // 2]
        elif self.mode == "retry_ok":
            if not retry:
                content = _fault_content(content, "unrepairable")
        elif self.mode in {"repairable", "unrepairable", "bad_schema", "bad_quote",
                           "forbidden_json", "empty_answer"}:
            content = _fault_content(content, self.mode)
        prompt_count = sum(len(m["content"]) for m in messages) // 4 + 8
        if self.mode == "short_context":
            prompt_count = min(prompt_count, 8192)
        elif self.mode == "cut_prompt":
            prompt_count = self.ctx // 2 + 3
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

    def __init__(self, model, edit=None):
        self.model = model
        self.edit = edit
        self.requests = []

    def open(self, request, timeout=None):
        self.requests.append((request, timeout))
        status, payload = self.model.handle(request.get_method(),
                                            urlsplit(request.full_url).path,
                                            request.data or b"")
        if self.edit is not None:
            self.edit(payload)
        response = FakeResponse(status, payload)
        if status >= 400:
            raise HTTPError(request.full_url, status, payload.get("error", "error"),
                            response.headers, response)
        return response
