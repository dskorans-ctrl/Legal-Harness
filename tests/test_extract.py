"""Pin the production card and the invented recording helper's nonce round trip."""

import json

import docx

from casefile import config, extract, gates, matter, model
from conftest import ROOT, write_config
from fakemodel.bench import extraction_card, recording_for
from fakemodel.core import FakeModel, FakeTransport


MATTER = ROOT / "tests/fixtures/matters/9001.001"


def test_extract_card():
    card = extract.card()
    print(f"card_version={card.version} card_name={card.name} docx_import={int(docx.__name__ == 'docx')}")
    assert card.version == "4ab2bdb30535", f"card_version={card.version}"
    assert card.name == extract.CARD_NAME == "bench_extract"
    assert card.text is extract.TEXT
    assert extraction_card().text is extract.TEXT, "extraction_card().text is not extract.TEXT"
    assert extract.TEXT == extract.CARD_TEXT + extract.ID_SENTENCE
    assert len(extract.TEXT.encode("utf-8")) == 920
    assert docx.__name__ == "docx"


def test_recording_for(tmp_path):
    loaded = matter.load(MATTER)
    ideal = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))
    card = extract.card()
    row = recording_for(card, loaded.pages, loaded.number, ideal)
    fake = FakeModel(recordings=[row])
    transport = FakeTransport(fake)
    client = model.ModelClient(config.load(write_config(tmp_path)).model, transport)
    nonce = "a123456789abcdef"
    messages = gates.messages(card, loaded.pages, nonce, matter=loaded.number)
    reply = client.chat(messages, truncate=False)
    actual = json.loads(reply.content)
    expected = {"prompt_id": nonce, **ideal, "end_id": nonce}
    ok = int(actual == expected and "__PROMPT_ID__" not in reply.content)
    print(f"recording_ok={ok}")
    assert ok == 1, "recording_ok=0"
    assert len(fake.requests) == len(transport.requests) == 1
    assert json.loads(transport.requests[0][0].data)["messages"] == messages
    assert row["messages"] == gates.messages(
        card, loaded.pages, "__PROMPT_ID__", matter=loaded.number)
    assert json.loads(row["answer"]) == {
        "prompt_id": "__PROMPT_ID__", **ideal, "end_id": "__PROMPT_ID__"}
