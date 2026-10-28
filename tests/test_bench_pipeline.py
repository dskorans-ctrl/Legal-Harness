"""Bench exercises the production pipeline on invented pages and received replies."""

from dataclasses import replace
from http.client import HTTPMessage
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO, StringIO
import json
import socket
from threading import Thread
from urllib.error import HTTPError

import pytest

from casefile import bench, benchkey, benchscore, config, extract, matter, pipeline, playbook, runlog
from conftest import split_card, ROOT, write_config
from fakemodel.bench import recording_for, recordings_for
from fakemodel.core import FakeModel, FakeTransport


MATTER = ROOT / "tests/fixtures/matters/9001.001"
PERFECT = ("bench 9001.001 model=qwen3.8:27b found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 "
           "flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14")
MODES = (
    ("replay", 0, None, ("ok",)),
    ("retry_ok", 0, None, ("failed", "ok")),
    ("truncated", 1, "truncation", ("failed", "failed")),
    ("cut_answer", 1, "truncation", ("failed", "failed")),
    ("unrepairable", 1, "repair", ("failed", "failed")),
    ("bad_schema", 1, "schema", ("failed", "failed")),
    ("bad_quote", 1, "quotes", ("failed", "failed")),
    ("forbidden_json", 1, "rules", ("failed", "failed")),
    ("empty_answer", 1, "coverage", ("failed", "failed")),
    ("cut_prompt", 1, "truncation", ("failed",)),
    ("prompt_too_long", 1, "truncation", ("failed",)),
    ("no_reply", 2, "model", ()),
)


@pytest.fixture(scope="module")
def totals():
    passed = {"modes": [], "replies": []}
    yield passed
    print(f'bench_modes={len(passed["modes"])} of 12', flush=True)
    print(f'reply_rows={len(passed["replies"])} of 9', flush=True)


class NeverReplies:
    def open(self, request, timeout=None):
        raise ConnectionRefusedError("invented server refused")


def settings(tmp_path, **overrides):
    return config.load(write_config(tmp_path, playbook=ROOT / "playbook", **overrides))


def rows(log, table, columns="*"):
    return [tuple(row) for row in log.connection.execute(f"SELECT {columns} FROM {table} ORDER BY id")]


@pytest.mark.parametrize("mode, exit_code, gate, statuses", MODES, ids=[m[0] for m in MODES])
def test_bench_modes(mode, exit_code, gate, statuses, tmp_path, monkeypatch, totals):
    cfg = settings(tmp_path)
    fake = FakeModel(recordings=recordings_for(MATTER), mode="replay" if mode == "no_reply" else mode)
    transport = NeverReplies() if mode == "no_reply" else FakeTransport(fake)
    native_client = pipeline.ModelClient
    monkeypatch.setattr(pipeline, "ModelClient", lambda cfg, opener=None: native_client(cfg, transport))
    # A second replay in the same log proves a benchmark never skips pages already read.
    attempts = 2 if mode == "replay" else 1
    for attempt in range(attempts):
        out, err = StringIO(), StringIO()
        code = bench.main(MATTER.parent, cfg.source, out=out, err=err)
        lines = out.getvalue().splitlines()
        assert code == exit_code, f"{mode}: exit={code}, expected={exit_code}: {err.getvalue()}"
        with runlog.open_db(cfg.paths.state / "runlog.sqlite") as log:
            assert len(rows(log, "runs")) == attempt + 1, "bench replay must add one run every time"
            actual = rows(log, "answers", "status")
            assert actual == [(status,) for status in statuses] * (attempt + 1), f"{mode}: answers={actual}"
        if code == 0:
            assert lines == [PERFECT, "  uncited: DEF0001", "bench matters=1 imperfect=0"], lines
            assert err.getvalue() == ""
        elif code == 1:
            assert lines[0].startswith(f"bench 9001.001 failure gate.{gate}: "), lines
            assert lines[1].endswith("pages_failed=14 of 14"), lines
            assert lines[-1] == "bench matters=1 imperfect=1"
            assert err.getvalue() == ""
        else:
            assert err.getvalue().startswith(
                f"bench: cannot run: no reply from the model server at {cfg.model.host} "), err.getvalue()
            assert lines == [f"bench 9001.001 failure gate.model: no reply from the model server at {cfg.model.host} "
                             "(connection refused)"]
    if mode == "replay":
        request = json.loads(fake.requests[0]["body"])
        assert request["options"] == {"num_ctx": 65536, "temperature": 0.1, "num_predict": 8192}
        assert request["truncate"] is False and request["think"] is False and request["stream"] is False
        assert request["messages"][1]["content"].count("=== PAGE ") == 14
    totals["modes"].append(mode)


class Reply:
    def __init__(self, status, body):
        self.status, self.body = status, body

    def open(self, request, timeout=None):
        response = BytesIO(self.body.encode("utf-8"))
        response.getcode = lambda: self.status
        response.headers = {"Location": "http://127.0.0.1:1/status"}
        return response


class ErrorReply:
    def __init__(self, status, body):
        self.status, self.body = status, body

    def open(self, request, timeout=None):
        headers = HTTPMessage()
        headers["Location"] = "http://127.0.0.1:1/error"
        raise HTTPError(request.full_url, self.status, "invented error", headers,
                        None if self.body is None else BytesIO(self.body.encode("utf-8")))


class ReadTimeout:
    def open(self, request, timeout=None):
        class Body(BytesIO):
            def getcode(self):
                return 200

            def read(self, *args):
                raise socket.timeout("invented read timeout")
        return Body()


REPLIES = ("non_json_200", "404", "503_status", "503_no_stream", "302_status", "307_error",
           pytest.param("302_real_opener", marks=pytest.mark.socket), "302_empty", "read_timeout")


@pytest.mark.parametrize("case", REPLIES)
def test_reply_rows(case, tmp_path, totals):
    cfg = settings(tmp_path)
    server = thread = None
    if case == "non_json_200":
        raw, opener = "invented reply that is not JSON", None
        opener = Reply(200, raw)
    elif case == "404":
        raw = '{"error": "fakemodel: unknown model"}'
        opener = FakeTransport(FakeModel(recordings=recordings_for(MATTER), model="other:model"))
    elif case == "503_status":
        raw = "invented server busy reply " * 20
        assert len(raw.encode()) > 200
        opener = Reply(503, raw)
    elif case == "503_no_stream":
        raw, opener = "", ErrorReply(503, None)
    elif case == "302_status":
        raw = "invented status redirect body"
        opener = Reply(302, raw)
    elif case == "307_error":
        raw = "invented error redirect body"
        opener = ErrorReply(307, raw)
    elif case == "302_empty":
        raw, opener = "", Reply(302, "")
    elif case == "read_timeout":
        raw, opener = "", ReadTimeout()
    else:
        raw, opener = "invented opener redirect body", None

        class Redirecting(BaseHTTPRequestHandler):
            def do_POST(self):
                body = raw.encode()
                self.send_response(302)
                self.send_header("Location", "http://127.0.0.1:1/opener")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Redirecting)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        cfg = settings(tmp_path, host=f"http://127.0.0.1:{server.server_port}")
    try:
        with runlog.open_db(tmp_path / "reply.sqlite") as log:
            result = pipeline.bench_run(matter.load(MATTER), cfg, log, "invented", opener)
            assert result.reply_received is True, f"{case}: received reply lost"
            assert result.pages_failed == 14 and result.candidate.facts == ()
            assert result.failure.startswith("gate.model:"), result.failure
            actual = rows(log, "answers", "status, raw_answer")
            assert actual == [("failed", raw)] * 2, f"{case}: answers={actual!r}; expected two received rows"
            assert rows(log, "failures", "gate") == [("gate.model",)] * 2
            assert len(rows(log, "runs")) == 1
    finally:
        if server is not None:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
            assert not thread.is_alive(), "redirect server did not stop"
    totals["replies"].append(case)


def split_setup(monkeypatch, *, repeated=False, duplicate=False):
    loaded = matter.load(MATTER)
    card = split_card(extract.card())
    monkeypatch.setattr(pipeline.extract, "card", lambda book=None: card)
    ideal = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))
    quote = ideal["facts"][1]["quote"]
    if repeated:
        pages = list(loaded.pages)
        pages[5] = replace(pages[5], text=pages[5].text + "\n" + quote)
        loaded = replace(loaded, pages=tuple(pages))
        ideal["facts"].append({"cite": "MED0006", "quote": quote,
                               "text": "The report records the service date.", "date": "", "category": "other", "provider": ""})
        if duplicate:
            ideal["facts"].append(dict(ideal["facts"][-1]))
    chunks, refused = pipeline.chunk(card, loaded.pages, 65536, loaded.number)
    assert [len(part) for part in chunks] == [5, 5, 4] and not refused
    recordings = []
    for part in chunks:
        stamps = {stamp for page in part for stamp in page.stamps}
        answer = {"facts": [fact for fact in ideal["facts"] if fact["cite"] in stamps],
                  "flags": [flag for flag in ideal["flags"] if set(flag["cites"]) <= stamps]}
        recordings.append(recording_for(card, part, loaded.number, answer))
    return loaded, FakeTransport(FakeModel(recordings=recordings)), quote


def test_bench_chunks(tmp_path, monkeypatch, capsys):
    cfg = settings(tmp_path)
    loaded, transport, _ = split_setup(monkeypatch)
    with runlog.open_db(tmp_path / "split.sqlite") as log:
        result = pipeline.bench_run(loaded, cfg, log, "invented", transport)
        count = len(rows(log, "runs"))
    key = benchkey.load(MATTER / "key.json", loaded)
    score = benchscore.score(key, result.candidate, loaded, playbook.load(cfg.paths.playbook).rules,
                             result.pages_failed)
    with capsys.disabled():
        print(f"bench_chunks=3 found={score.found} of {score.key_total} flags={score.flags_found} "
              f"of {score.flags_total} runs=+{count} uncited={len(result.uncited)}")
    assert (score.found, score.key_total, score.flags_found, score.flags_total, count) == (36, 36, 5, 9, 3)
    assert "  flags_missed: G1 G3 G6 G9" in score.details()
    assert result.pages_failed == 0 and result.failure is None
    assert result.uncited == ("DEF0001",), "split coverage must retain every uncited page"


@pytest.mark.parametrize("duplicate", (False, True), ids=("second_page", "same_page_duplicate"))
def test_merge_identity(tmp_path, monkeypatch, duplicate):
    cfg = settings(tmp_path)
    loaded, transport, quote = split_setup(monkeypatch, repeated=True, duplicate=duplicate)
    with runlog.open_db(tmp_path / "merge.sqlite") as log:
        result = pipeline.bench_run(loaded, cfg, log, "invented", transport)
    key = benchkey.load(MATTER / "key.json", loaded)
    score = benchscore.score(key, result.candidate, loaded, playbook.load(cfg.paths.playbook).rules, 0)
    assert score.extra == 3, f"merged extra={score.extra}, expected 3 for one new page cite"
    found = [fact for fact in result.candidate.facts if fact.quote == quote]
    first_reading = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))["facts"][1]["text"]
    assert [(fact.cite, fact.text) for fact in found] == [("MED0001", first_reading), ("MED0006", first_reading)], (
        "merged fact must retain two cites and use its first reading for both")


@pytest.mark.parametrize("field, value", (("eval_count", 0), ("prompt_eval_count", 0),
                                         ("eval_count", None), ("done", False)))
def test_invalid_envelope(tmp_path, field, value):
    cfg = settings(tmp_path)
    fake = FakeModel(recordings=recordings_for(MATTER))
    transport = FakeTransport(fake, edit=lambda payload: payload.update({field: value}))
    with runlog.open_db(tmp_path / "counts.sqlite") as log:
        result = pipeline.bench_run(matter.load(MATTER), cfg, log, "invented", transport)
        assert result.pages_failed == 14 and result.reply_received is True
        assert result.failure.startswith("gate.model:" if field == "done" else "gate.truncation:")
        assert rows(log, "answers", "status") == [("failed",)] * 2
