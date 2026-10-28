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
    assert card.version == "ed0e58680bc9", f"card_version={card.version}"
    assert card.name == extract.CARD_NAME == "medical_memo"
    assert extraction_card().text == card.text
    assert card.text.endswith(extract.ID_SENTENCE)
    assert 'date of service' in card.text
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


def test_no_reply_forms(tmp_path):
    from io import StringIO
    from urllib.error import URLError
    from casefile import bench, doctor
    from test_doctor import passing_smoke
    from test_status import setup_matter, invoke

    class Offline:
        def open(self,*args,**kwargs):
            raise URLError(ConnectionRefusedError())
    path,settings,_=setup_matter(tmp_path)
    reason='no reply from the model server at http://127.0.0.1:9 (connection refused)'
    out=StringIO()
    doctor.run(settings,out=out,opener=Offline(),ocr_smoke=passing_smoke)
    checks=[f'doctor ollama_loopback FAIL {reason} | do: start the Ollama app' in out.getvalue()]
    code,_,error=invoke(settings,Offline())
    checks.append(code == 2 and error == f'memo: cannot run: {reason}; the pages of this run stay open until a later run reads them\n')
    out,err=StringIO(),StringIO()
    code=bench.main(MATTER.parent,path,out=out,err=err,opener=Offline())
    checks.append(code == 2 and err.getvalue() == f'bench: cannot run: {reason}\n')
    print(f'no_reply_forms={sum(checks)} of 3')
    assert all(checks), f'no_reply_forms={sum(checks)} of 3'
