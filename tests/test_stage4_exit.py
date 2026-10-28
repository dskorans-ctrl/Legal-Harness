"""Stage 4 exit proof over a loopback stand-in and a temporary durable run log."""

from dataclasses import replace
import json
import re
from threading import Thread
from urllib.request import ProxyHandler, Request, build_opener

import pytest

from casefile import config, gates, matter, model, rules
from casefile.runlog import open_db
from conftest import ROOT, write_config
from fakemodel import FakeModel
from fakemodel.bench import extraction_card, recordings_for
from fakemodel.server import serve


MATTER = ROOT / "tests/fixtures/matters/9001.001"
PROBE_NUMBER = "9003.001"
# Mode, attempts, first failing gate (None means all gates pass).
CASES = (
    ("budget", 1, "truncation"),
    ("cut_prompt", 1, "truncation"),
    ("prompt_too_long", 1, "truncation"),
    ("truncated", 2, "truncation"),
    ("cut_answer", 2, "truncation"),
    ("repairable", 1, None),
    ("unrepairable", 2, "repair"),
    ("bad_schema", 2, "schema"),
    ("bad_quote", 2, "quotes"),
    ("forbidden_json", 2, "rules"),
    ("retry_ok", 2, "repair"),
    ("empty_answer", 2, "coverage"),
    ("replay", 1, None),
    ("probe", 1, None),
)
TRUNCATED = ("truncated", "cut_answer", "cut_prompt", "prompt_too_long")
SEARCHED = ('MED0001, MED0002, MED0003, MED0004, MED0005, MED0006, MED0007, MED0008, '
            'EMP0001, EMP0002, EMP0003, DEF0001, DEF0002, DEF0003')
BAD_QUOTE_FAULTS = (
    'facts[0]: quote not found on MED0001, the page it cites (quote: "Date of service: 13/11/2025")',
    'facts[1].cite: cite MED0099 is not a page of this chunk',
    'flags[0].cites[2]: cite MED0098 is not a page of this chunk',
    'facts[0].text: number 03 is not in its quote',
    'facts[2].text: number 99999 is not in its quote',
)
EXPECTED = (
    "stage4 gate=truncation good=pass bad=2 of 2 truncated=4 of 4 retry=1",
    "stage4 gate=repair good=pass bad=1 of 1 truncated=0 of 4 reached repaired=4",
    "stage4 gate=schema good=pass bad=1 of 1 truncated=0 of 4 reached",
    "stage4 gate=quotes good=pass bad=1 of 1 faults=5 truncated=0 of 4 reached",
    "stage4 gate=rules good=2 of 2 bad=1 of 1 truncated=0 of 4 reached warning=1",
    "stage4 gate=coverage good=13 read 1 uncited bad=14 failed empty=14 failed "
    "truncated=0 of 4 reached open_items=14 then 1",
    "stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1",
)


def _probe(card):
    pages = (
        matter.Page("probe", 1, "Harrowgate Occupational Clinic notes pain of 7/10.", ()),
        matter.Page("probe", 2, "The IME report of 03/02/2026 notes a normal gait.", ()),
        matter.Page("probe", 3, "Harrowgate Occupational Clinic recommends follow-up.", ()),
    )
    answer = {"facts": [
        {"cite": page.page_id, "quote": page.text,
         "text": "The report notes a normal gait." if page.number == 2 else page.text}
        for page in pages], "flags": []}
    row = {
        "name": "stage4-invented-unstamped-probe",
        "messages": gates.messages(card, pages, "__PROMPT_ID__", matter=PROBE_NUMBER),
        "answer": json.dumps({"prompt_id": "__PROMPT_ID__", **answer, "end_id": "__PROMPT_ID__"}),
    }
    return pages, answer, row


def _rows(log, table, run_id):
    return [dict(row) for row in log.connection.execute(
        f"SELECT * FROM {table} WHERE run_id=? ORDER BY id", (run_id,))]


def _counts(log):
    return tuple(log.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                 for table in ("runs", "answers"))


def _check_case(name, attempts, failing, result, ideal, probe_answer):
    outcome = result["outcome"]
    checked, answers, coverage = (result[key] for key in ("gates", "answers", "coverage"))
    successful = name in {"replay", "repairable", "retry_ok", "probe"}
    assert outcome.ok is successful, f"{name}: ok={outcome.ok}"
    assert outcome.attempts == attempts, f"{name}: attempts={outcome.attempts}"
    assert len(answers) == (0 if name == "budget" else attempts), f"{name}: answer count"
    assert [row["status"] for row in answers] == (
        ["failed", "ok"] if name == "retry_ok" else
        ["ok" if successful else "failed"] * len(answers)), f"{name}: answer statuses"
    assert [(v.attempt, v.gate, v.verdict, v.message) for v in outcome.verdicts] == [
        (row["attempt"], row["gate"], row["verdict"], row["message"]) for row in checked
    ], f"{name}: persisted verdicts differ"
    for attempt in range(1, attempts + 1):
        failed_gate = None if name == "retry_ok" and attempt == 2 else failing
        sequence = [(f"gate.{gate}", "pass") for gate in (
            "truncation", "repair", "schema", "quotes", "rules", "coverage")]
        if failed_gate:
            index = next(i for i, (gate, _) in enumerate(sequence) if gate == f"gate.{failed_gate}")
            sequence = sequence[:index] + [(f"gate.{failed_gate}", "fail")]
        if name == "repairable":
            sequence[1:2] = [("gate.repair", "repaired")] * 4
        assert [(row["gate"], row["verdict"]) for row in checked if row["attempt"] == attempt] == sequence, (
            f"{name}: attempt {attempt} gate order")
    assert len(coverage) == (3 if name == "probe" else 14), f"{name}: coverage count"
    expected_ids = {f"probe/{i:03d}" for i in (1, 2, 3)} if name == "probe" else result["page_ids"]
    assert {row["page_id"] for row in coverage} == expected_ids, f"{name}: coverage page ids"
    if successful:
        assert outcome.answer == (probe_answer if name == "probe" else ideal), f"{name}: answer differs"
        assert not outcome.failed, f"{name}: successful pages failed"
        expected_uncited = () if name == "probe" else ("defense-report/001",)
        assert outcome.uncited == expected_uncited, f"{name}: uncited={outcome.uncited}"
        assert set(outcome.read) == expected_ids - set(expected_uncited), f"{name}: read ids"
        assert {row["page_id"] for row in coverage if row["status"] == "read"} == set(outcome.read)
        assert {row["page_id"] for row in coverage if row["status"] == "uncited"} == set(expected_uncited)
        assert all(row["reason"] == ("no fact or flag cites defense-report/001" if row["status"] == "uncited" else "")
                   for row in coverage), f"{name}: coverage reasons"
        assert result["open"] == ({("defense-report/001", "bench_extract")} if name != "probe" else set()), (
            f"{name}: open_items={len(result['open'])} expected={0 if name == 'probe' else 1}")
    else:
        assert outcome.answer is None, f"{name}: failed answer saved"
        assert outcome.read == () and outcome.uncited == (), f"{name}: failed pages marked read"
        last = result["failures"][-1]
        detail = last['message'].removeprefix(last['gate'] + ': ').rsplit('; ', 1)[0]
        if name in {'budget', 'cut_prompt', 'prompt_too_long'}:
            detail = detail.rsplit('; not retried: ', 1)[0]
        reason = f"{last['gate']}: {detail}; the page stays open until a later run reads it"
        assert dict(outcome.failed) == dict.fromkeys(expected_ids, reason), f"{name}: failed page reasons"
        assert all(row["status"] == "failed" and row["reason"] == reason for row in coverage)
        assert result["open"] == {(page_id, "bench_extract") for page_id in expected_ids}
    failed_rows = [row for row in checked if row["verdict"] == "fail"]
    assert [(row["gate"], row["message"]) for row in result["failures"]] == [
        (row["gate"], row["message"]) for row in failed_rows], f"{name}: failure log differs"
    expected_reason = {
        'budget': 'the prompt is too long (over budget)',
        'cut_prompt': 'the prompt was cut (prompt_id missing)',
        'truncated': 'the answer stopped before it finished (done_reason=length)',
        'cut_answer': 'the answer was cut off (end_id missing)',
        'empty_answer': 'the answer has no facts and no flags',
        'prompt_too_long': ('status=400: the prompt is longer than the context length currently available '
                            'to the model; shorten the prompt, adjust the context length in settings, or use a model ...'),
        'forbidden_json': ('facts[0].text: Never name the exam as a DME or IME in any form; write "the report". '
                           '(no-dme-ime: IME)'),
        'bad_schema': 'the answer does not match the schema: facts[0].text: missing required key',
        'unrepairable': "the answer is not valid JSON: Expecting ',' delimiter",
        'retry_ok': "the answer is not valid JSON: Expecting ',' delimiter",
        'bad_quote': '5 faults (faults=5): ' + '; '.join(BAD_QUOTE_FAULTS) + '; chunk pages: ' + SEARCHED,
    }.get(name)
    if expected_reason:
        steps = ['retried once', 'not retried: the one retry was used'][:len(failed_rows)]
        if name in {'budget', 'cut_prompt', 'prompt_too_long'}:
            why = 'the prompt was cut' if name == 'cut_prompt' else 'the prompt was too long'
            steps = [f'not retried: {why}; the chunk must be made smaller']
        assert [row['message'] for row in failed_rows] == [
            f'gate.{failing}: {expected_reason}; {step}' for step in steps], f'{name}: failure reason'


@pytest.mark.socket
def test_stage4_exit(tmp_path, capsys):
    loaded = matter.load(MATTER)
    ideal = json.loads((MATTER / "ideal.json").read_text(encoding="utf-8"))
    card = extraction_card()
    probe_pages, probe_answer, probe_row = _probe(card)
    fake = FakeModel(recordings=[*recordings_for(MATTER), probe_row])
    server = serve(port=0, model=fake)
    thread = Thread(target=server.serve_forever)
    thread.start()
    results = {}
    errors = []
    try:
        settings = config.load(write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}"))
        client = model.ModelClient(settings.model)
        firm = rules.load(ROOT / "playbook/rules.toml")
        opener = build_opener(ProxyHandler({}))
        with open_db(settings.paths.state / "stage4.sqlite") as log:
            runs0, answers0 = _counts(log)
            for name, attempts, failing in CASES:
                mode = "replay" if name in {"budget", "probe"} else name
                request = Request(settings.model.host + "/_fake/mode", method="POST",
                                  data=json.dumps({"mode": mode}).encode("utf-8"),
                                  headers={"Content-Type": "application/json"})
                with opener.open(request, timeout=5) as response:
                    assert response.status == 200
                    assert json.load(response) == {"mode": mode}
                pages = probe_pages if name == "probe" else loaded.pages
                number = PROBE_NUMBER if name == "probe" else loaded.number
                active_card = replace(card, max_answer_tokens=65536 - 10) if name == "budget" else card
                requests0 = len(fake.requests)
                outcome = gates.ask(active_card, pages, client=client, rules=firm, log=log, matter=number)
                result = {table: _rows(log, table, outcome.run_id)
                          for table in ("answers", "gates", "failures", "coverage")}
                result.update(outcome=outcome, open=set(gates.open_items(log, number)),
                              page_ids={p.page_id for p in loaded.pages})
                results[name] = result
                try:
                    _check_case(name, attempts, failing, result, ideal, probe_answer)
                    chats = [r for r in fake.requests[requests0:] if r["path"] == "/api/chat"]
                    assert len(chats) == (0 if name == "budget" else attempts), f"{name}: requests"
                    for chat in chats:
                        body = json.loads(chat["body"])
                        assert body["truncate"] is False and body["think"] is False
                        assert body["options"]["num_predict"] == active_card.max_answer_tokens
                    if name == "retry_ok":
                        first, second = [json.loads(chat["body"])["messages"] for chat in chats]
                        assert len(first) == len(second) == 2
                        assert first[0]["content"].splitlines()[0] != second[0]["content"].splitlines()[0]
                        assert second[1]["content"].splitlines()[1].startswith(
                            "Retry: the previous answer failed the repair check:")
                except AssertionError as exc:
                    errors.append(f"{name}: {exc}")
            runs1, answers1 = _counts(log)
    finally:
        server.shutdown()
        thread.join(timeout=5)
        stopped = not thread.is_alive()
        server.server_close()

    def passed(name, gate):
        return any(row["gate"] == f"gate.{gate}" and row["verdict"] == "pass"
                   for row in results[name]["gates"])

    def failed(name, gate):
        rows = results[name]["failures"]
        return bool(rows) and all(row["gate"] == f"gate.{gate}" for row in rows)

    def reached(gate):
        return sum(any(row["gate"] == f"gate.{gate}" for row in results[name]["gates"])
                   for name in TRUNCATED)

    def covered(name, status):
        return sum(row["status"] == status for row in results[name]["coverage"])

    def good(gate):
        return "pass" if passed("replay", gate) else "fail"

    repairs = [row["message"] for row in results["repairable"]["gates"] if row["verdict"] == "repaired"]
    repaired = sum(repairs.count(kind) == 1 for kind in ("fence", "control", "trailing-comma", "closers"))
    quote_faults = [row["message"] for row in results["bad_quote"]["failures"]]
    count = re.search(r'\(faults=(\d+)\)', quote_faults[0]) if quote_faults else None
    faults = int(count[1]) if count else 0
    warning = int(any(row["gate"] == "gate.rules" and row["verdict"] == "pass" and row["message"] ==
                      "warning: no Bates stamp on probe/001, probe/002, probe/003; cites are page ids"
                      for row in results["probe"]["gates"]))
    empty_saved = 0
    for result in results.values():
        outcome = result["outcome"]
        empty_saved += int(not outcome.ok and outcome.answer is not None)
        empty_saved += int(outcome.ok and not outcome.answer.get("facts") and not outcome.answer.get("flags"))
        bad_attempts = {row["attempt"] for row in result["gates"] if row["verdict"] == "fail"}
        empty_saved += sum(row["status"] == "ok" and attempt in bad_attempts
                           for attempt, row in enumerate(result["answers"], start=1))
    lines = [
        f"stage4 gate=truncation good={good('truncation')} bad="
        f"{sum(failed(n, 'truncation') for n in ('cut_prompt', 'prompt_too_long'))} of 2 "
        f"truncated={sum(failed(n, 'truncation') for n in TRUNCATED)} of 4 "
        f"retry={int(results['retry_ok']['outcome'].ok and results['retry_ok']['outcome'].attempts == 2)}",
        f"stage4 gate=repair good={good('repair')} bad={int(failed('unrepairable', 'repair'))} of 1 "
        f"truncated={reached('repair')} of 4 reached repaired={repaired}",
        f"stage4 gate=schema good={good('schema')} bad={int(failed('bad_schema', 'schema'))} of 1 "
        f"truncated={reached('schema')} of 4 reached",
        f"stage4 gate=quotes good={good('quotes')} bad={int(failed('bad_quote', 'quotes'))} of 1 "
        f"faults={faults} truncated={reached('quotes')} of 4 reached",
        f"stage4 gate=rules good={sum(passed(n, 'rules') for n in ('replay', 'probe'))} of 2 "
        f"bad={int(failed('forbidden_json', 'rules'))} of 1 truncated={reached('rules')} of 4 reached warning={warning}",
        f"stage4 gate=coverage good={covered('replay', 'read')} read {covered('replay', 'uncited')} uncited "
        f"bad={covered('unrepairable', 'failed')} failed empty={covered('empty_answer', 'failed')} failed "
        f"truncated={reached('coverage')} of 4 reached "
        f"open_items={len(results['empty_answer']['open'])} then {len(results['replay']['open'])}",
    ]
    gate_count = sum(actual == expected for actual, expected in zip(lines, EXPECTED))
    exit_code = int(bool(errors) or gate_count != 6 or (runs1 - runs0, answers1 - answers0) != (14, 21)
                    or empty_saved != 0 or not stopped or len(CASES) != 14)
    lines.append(f"stage4 exit={exit_code} gates={gate_count} of 6 cases={len(results) - len(errors)} of 14 "
                 f"runs={runs1 - runs0:+d} answers={answers1 - answers0:+d} "
                 f"empty_saved={empty_saved} server_stopped={int(stopped)}")
    with capsys.disabled():
        print("\n".join(lines), flush=True)
    mismatches = [f"expected: {expected}\nactual:   {actual}"
                  for actual, expected in zip(lines, EXPECTED) if actual != expected]
    assert lines == list(EXPECTED) and not errors, "stage4 exit check failed:\n" + "\n".join(errors + mismatches)
