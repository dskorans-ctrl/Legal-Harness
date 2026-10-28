"""Chunk and runner checks replay invented answers without a network connection."""

from dataclasses import replace
import json

import pytest

from casefile import config, extract, gates, matter, model, pipeline, rules
from casefile.runlog import open_db
from conftest import ROOT, write_config
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for, recordings_for


FIXTURE = ROOT / "tests/fixtures/matters/9001.001"
SPLIT_IDS = (
    tuple(f"medical/{i:03d}" for i in range(1, 6)),
    ("medical/006", "medical/007", "medical/008", "employer/001", "employer/002"),
    ("employer/003", "defense-report/001", "defense-report/002", "defense-report/003"),
)


@pytest.fixture(scope="module")
def totals():
    passed = {"chunks": [], "pipeline": []}
    yield passed
    print(f'chunks_ok={len(passed["chunks"])} of 8 pipeline_ok={len(passed["pipeline"])} of 5', flush=True)


def split_card():
    return replace(extract.card(), max_answer_tokens=65536 - 16384)


def ids(chunks):
    return tuple(tuple(page.page_id for page in part) for part in chunks)


def long_page():
    return matter.Page("probe", 1, "x" * 9000, ())


def client_for(tmp_path, card, *, mode="replay", chunks=None):
    loaded = matter.load(FIXTURE)
    recordings = recordings_for(FIXTURE)
    if chunks is not None:
        ideal = json.loads((FIXTURE / "ideal.json").read_text(encoding="utf-8"))
        recordings = []
        for part in chunks:
            stamps = {stamp for page in part for stamp in page.stamps}
            answer = {"facts": [f for f in ideal["facts"] if f["cite"] in stamps],
                      "flags": [f for f in ideal["flags"] if set(f["cites"]) <= stamps]}
            recordings.append(recording_for(card, part, loaded.number, answer))
    fake = FakeModel(recordings=recordings, mode=mode)
    transport = FakeTransport(fake)
    settings = config.load(write_config(tmp_path)).model
    return model.ModelClient(settings, opener=transport), transport, fake


def seed_read(log, pages, job):
    run_id = log.start_run(job=job, matter="9001.001", card="bench_extract", card_version="invented",
                           playbook_version="invented", model="invented", pages_in=len(pages),
                           prompt_sha256="a" * 64)
    for page in pages:
        if page.page_id != "defense-report/001":
            log.record_coverage(run_id, matter="9001.001", page_id=page.page_id, card="bench_extract",
                                status="read", reason="")


def invoke(log, pages, card, client, *, only_unread=False):
    return pipeline.run(pages, card=card, client=client, rules=rules.load(ROOT / "playbook/rules.toml"),
                        log=log, matter="9001.001", playbook_version="invented", job="memo",
                        only_unread=only_unread)


@pytest.mark.parametrize("case", ("default", "split", "long", "none", "retry_fit",
                                 "unread_memo", "unread_bench", "boundary"))
def test_chunks(case, tmp_path, totals):
    pages = matter.load(FIXTURE).pages
    card = extract.card() if case == "default" else split_card()
    if case in {"unread_memo", "unread_bench"}:
        card = extract.card()
        client, transport, _ = client_for(tmp_path, card)
        if case == "unread_memo":
            one = (pages[11],)
            answer = {"facts": [{"cite": "DEF0001", "quote": "The examinee reports lifting a tote of about 60 pounds.",
                                 "text": "The examinee reports lifting a tote of about 60 pounds."}], "flags": []}
            transport.model = FakeModel(recordings=[recording_for(card, one, "9001.001", answer)])
        with open_db(tmp_path / "unread.sqlite") as log:
            seed_read(log, pages, "memo" if case == "unread_memo" else "bench")
            result = invoke(log, pages, card, client, only_unread=True)
        expected = (("defense-report/001",),) if case == "unread_memo" else (tuple(p.page_id for p in pages),)
        assert ids(result.chunks) == expected, "only_unread mixed coverage jobs"
    elif case == "boundary":
        def page_with_block(size):
            page = matter.Page("probe", 1, "", ())
            return replace(page, text="x" * (size - len(extract.page_block(page).encode())))

        fit, overflow = page_with_block(7164), page_with_block(7165)
        assert len(extract.page_block(fit).encode()) == 7164
        assert pipeline.chunk(card, (fit,), 65536, "9001.001") == (((fit,),), ())
        chunks, refused = pipeline.chunk(card, (overflow,), 65536, "9001.001")
        assert chunks == () and refused[0][0] == overflow
    else:
        selected = (long_page(),) if case == "long" else () if case == "none" else pages
        chunks, refused = pipeline.chunk(card, selected, 65536, "9001.001")
        if case == "default":
            assert ids(chunks) == (tuple(p.page_id for p in pages),) and refused == ()
        elif case == "split":
            assert ids(chunks) == SPLIT_IDS and refused == (), "chunk split differs from [5, 5, 4]"
        elif case == "long":
            assert chunks == () and len(refused) == 1
            assert refused[0][1] == "page too long for one prompt (9000 bytes, budget 7164 bytes); split the binder"
        elif case == "none":
            assert chunks == refused == ()
        elif case == "retry_fit":
            for part in chunks:
                msgs = gates.messages(card, part, "0" * 16, matter="9001.001")
                header, body = msgs[1]["content"].split("\n", 1)
                msgs[1]["content"] = header + "\nRetry: the previous answer failed the " + "x" * 2000 + (
                    ". Answer again with one JSON object and nothing else.\n") + body
                size = sum(model.tokens_at_most(m["content"]) for m in msgs) + model.TEMPLATE_TOKENS
                assert size <= 65536 - card.max_answer_tokens, "retry prompt exceeds budget"
            assert ids(chunks) == SPLIT_IDS
    totals["chunks"].append(case)


@pytest.mark.parametrize("case", ("replay", "refused", "three", "no_reply", "empty"))
def test_pipeline(case, tmp_path, totals):
    pages = matter.load(FIXTURE).pages
    card = split_card() if case != "replay" else extract.card()
    chunks, _ = pipeline.chunk(card, pages, 65536, "9001.001")
    client, transport, fake = client_for(tmp_path, card, chunks=chunks)
    if case == "refused":
        pages = (long_page(),)
    if case in {"no_reply", "empty"}:
        original = transport.open
        calls = 0

        def open_request(request, timeout=None):
            nonlocal calls
            calls += 1
            if case == "no_reply" and calls == 2:
                raise model.ModelError("invented no reply", received=False)
            fake.mode = "empty_answer" if case == "empty" and calls in (2, 3) else "replay"
            return original(request, timeout=timeout)

        transport.open = open_request
    with open_db(tmp_path / "pipeline.sqlite") as log:
        if case == "no_reply":
            with pytest.raises(model.ModelError, match="invented no reply"):
                invoke(log, pages, card, client)
            assert log.connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 2
            assert log.connection.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 1
            assert {v[2] for v in log.coverage("9001.001", job="memo").values()} == {1}
        else:
            result = invoke(log, pages, card, client)
            coverage = log.coverage("9001.001", job="memo")
            count = lambda table: log.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if case == "replay":
                assert len(result.outcomes) == 1 and result.outcomes[0].ok and count("runs") == 1
                assert sum(v[0] == "read" for v in coverage.values()) == 13
            elif case == "refused":
                assert not transport.requests, "refused page reached the stand-in"
                assert count("runs") == count("failures") == count("coverage") == 1
                assert count("answers") == 0 and result.outcomes == ()
                run = dict(log.connection.execute("SELECT * FROM runs").fetchone())
                assert run["pages_in"] == 1 and run["job"] == "memo"
                assert run["prompt_sha256"] == extract.prompt_sha256(
                    gates.messages(card, pages, "0" * 16, matter="9001.001"))
                failure = dict(log.connection.execute("SELECT * FROM failures").fetchone())
                assert failure["gate"] == "gate.truncation"
                assert failure["message"] == ("gate.truncation: page too long for one prompt "
                    "(9000 bytes, budget 7164 bytes); split the binder; not retried: the page must be split")
                assert coverage[("probe/001", card.name)][0] == "failed", "refused page is not failed"
            elif case == "three":
                assert ids(result.chunks) == SPLIT_IDS and count("runs") == 3
                assert all(o.ok for o in result.outcomes)
                assert sum(v[0] == "read" for v in coverage.values()) == 12
                assert {key[0] for key, value in coverage.items() if value[0] == "uncited"} == {
                    "defense-report/002", "defense-report/001"}
            elif case == "empty":
                assert [o.ok for o in result.outcomes] == [True, False, True]
                assert count("runs") == 3 and count("answers") == 4
                for page in chunks[1]:
                    assert coverage[(page.page_id, card.name)][0] == "failed"
                assert all(coverage[(page.page_id, card.name)][0] in {"read", "uncited"}
                           for part in (chunks[0], chunks[2]) for page in part)
    totals["pipeline"].append(case)
