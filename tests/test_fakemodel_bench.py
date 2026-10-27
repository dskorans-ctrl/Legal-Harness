import json

from casefile import matter as matters
from casefile.benchrun import CARD_TEXT
from conftest import ROOT
from fakemodel.bench import recordings_for
from fakemodel.core import FakeModel

MATTER = ROOT / "tests/fixtures/matters/9001.001"


def test_bench_recording(capsys):
    m = matters.load(MATTER)
    body = "Matter 9001.001\n" + "".join(f"=== PAGE {p.page_id} BATES {p.bates} ===\n{p.text}\n" for p in m.pages)
    expected = [{"role": "system", "content": CARD_TEXT}, {"role": "user", "content": body}]
    assert body.count("=== PAGE ") == 14
    assert all(p.text in body for p in m.pages)
    fake = FakeModel(recordings=recordings_for(MATTER))
    request = {"model": "qwen3.8:27b", "messages": expected, "stream": False,
               "options": {"num_ctx": 65536, "temperature": 0.1}}

    status, payload = fake.handle("POST", "/api/chat", json.dumps(request).encode())
    ideal = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))
    replay = payload["message"]["content"]
    assert status == 200
    assert json.loads(replay) == ideal

    n = 0
    modes = ("truncated", "malformed", "forbidden", "incomplete")

    def is_json(text):
        try:
            json.loads(text)
            return True
        except ValueError:
            return False

    for mode in modes:
        fake.mode = mode
        status, answer = fake.handle("POST", "/api/chat", json.dumps(request).encode())
        content = answer["message"]["content"]
        
        condition_holds = False
        if status == 200:
            if mode == "truncated":
                condition_holds = (answer["done_reason"] == "length" and len(content) == len(replay) // 2)
            elif mode == "malformed":
                condition_holds = (content != replay and not is_json(content))
            elif mode == "forbidden":
                condition_holds = ("IME" in content)
            elif mode == "incomplete":
                condition_holds = (answer["done"] is False and content == replay)
            
            if condition_holds:
                n += 1

    with capsys.disabled():
        print(f"bench_recording_ok=1 modes={n} pages_in_request={body.count('=== PAGE ')}")
    assert n == 4
