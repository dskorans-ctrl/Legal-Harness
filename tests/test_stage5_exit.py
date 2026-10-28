"""Stage 5 exit proof: four CLI jobs, durable coverage and reopened Word memos."""

import json
import os
import re
import shutil
import subprocess
from threading import Thread
from urllib.request import ProxyHandler, Request, build_opener

from docx import Document
import pytest

from casefile import config, extract, facts, matter, memo, playbook
from casefile.runlog import open_db
from conftest import ROOT, write_config
from fakemodel import FakeModel
from fakemodel.bench import recording_for, recordings_for
from fakemodel.server import serve


MATTER = ROOT / "tests/fixtures/matters/9001.001"
NUMBER = "9001.001"
ONE_PAGE = {"facts": [{
    "cite": "DEF0001", "quote": "The examinee reports lifting a tote of about 60 pounds.",
    "text": "The examinee reported lifting a tote of about 60 pounds.",
    "date": "06/20/2025", "category": "patient_statement", "provider": "Dr. Theodore Marchetti",
}], "flags": []}
EXPECTED = (
    "stage5 run=1 mode=replay exit=1 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 new_facts=31 new_flags=9",
    "stage5 run=2 mode=bad_schema exit=1 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 new_facts=0 new_flags=0",
    "stage5 run=3 mode=replay exit=0 chunks=1 runs=+1 read=14 open=0 facts=32 conflicts=5 gaps=4 new_facts=1 new_flags=0",
    "stage5 run=4 mode=replay exit=0 chunks=0 runs=+0 read=14 open=0 facts=32 conflicts=5 gaps=4 new_facts=0 new_flags=0",
    "stage5 memo=1 sections=15 chronology=31 dated=31 of 31 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=87 readings=31 gaps=4 runs_seen=1 open=1 open_status=uncited rule_hits=0 changed=first",
    "stage5 memo=2 sections=15 chronology=31 dated=31 of 31 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=87 readings=31 gaps=4 runs_seen=1 open=1 open_status=failed rule_hits=0 changed=0",
    "stage5 memo=3 sections=15 chronology=32 dated=32 of 32 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=89 readings=32 gaps=4 runs_seen=2 open=0 open_status=none rule_hits=0 changed=1",
    "stage5 status read=13 then 14 open=1 then 0 outputs=memo:current",
    "stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1",
)
BAD_REASON = ("gate.schema: the answer does not match the schema: facts[0].text: missing required key; "
              "the page stays open until a later run reads it")
SECTIONS = ("What changed since the last memo", "Outputs out of date", "Open items",
    "Treatment chronology", "Providers", "Diagnoses", "Restrictions and work status", "Medical history",
    "Our doctors' opinions", "Defense doctors' opinions", "Opinions in other records", "Gaps and missing records",
    "Conflicts", "Facts without a date, by page", "Facts on pages not in this matter")


def _section(document, title):
    paragraphs = document.paragraphs
    start = next(i for i, p in enumerate(paragraphs) if p.style.name == "Heading 1" and p.text == title) + 1
    end = next((i for i in range(start, len(paragraphs)) if paragraphs[i].style.name == "Heading 1"), len(paragraphs))
    return paragraphs[start:end]


def _cite(cite, page_id):
    return f"[page {page_id}]" if cite == page_id else f"[cite {cite}]"


def _read_memo(number, path, stored, pages, coverage, book, errors):
    from casefile import dates, matterinfo

    doc = Document(path)
    paragraphs = doc.paragraphs
    chronology = _section(doc, 'Treatment chronology')
    opened = _section(doc, 'Open items')
    conflicts = _section(doc, 'Conflicts')
    gaps = _section(doc, 'Gaps and missing records')
    records = stored.facts
    expected_chronology = []
    for fact in sorted(records, key=lambda f: dates.parse(f.dates[0])):
        expected_chronology.append(f'{fact.dates[0]}, {fact.providers[0] or fact.page_ids[0].rsplit('/',1)[0]}, {fact.category}: '
                                  f'"{fact.quote}" {_cite(fact.cites[0], fact.page_ids[0])}')
    actual_chronology = [p.text for p in chronology if any(run.text.startswith('"') for run in p.runs)]
    if actual_chronology != expected_chronology:
        errors.append(f'memo={number}: chronology differs')
    dated = sum(bool(f.dates[0]) for f in records)
    labels = {p.page_id: p.stamps[0] if p.stamps else p.page_id for p in pages}
    roles = {'medical':'ours', 'employer':'ours', 'defense-report':'defense'}
    flags = [f for f in stored.flags if f.kind == 'conflict']
    flags.sort(key=lambda f: 0 if {'defense','ours'} <= {roles[p.rsplit('/',1)[0]] for p in f.page_ids} else 1)
    expected_conflicts = []
    for flag in flags:
        expected_conflicts.append('Conflict between ' + ' and '.join(_cite(c,p) for c,p in zip(flag.cites,flag.page_ids)) + '.')
        expected_conflicts.extend("Model's reading: " + about for about in flag.abouts)
        for cite, page_id in zip(flag.cites, flag.page_ids):
            expected_conflicts.append('From ' + _cite(cite,page_id) + ':')
            expected_conflicts.extend(f'"{fact.quote}"' for fact in records if page_id in fact.page_ids)
    conflict_quotes_ok = int([p.text for p in conflicts[1:]] == expected_conflicts)
    if not conflict_quotes_ok:
        errors.append(f'memo={number}: scoped conflict quotes or ordering differ')
    defense_first = int([p.text for p in conflicts if p.text.startswith('Conflict between ')] ==
                        [p for p in expected_conflicts if p.startswith('Conflict between ')])
    expected_gaps = []
    for flag in stored.flags:
        if flag.kind == 'gap':
            expected_gaps.append('Gap at ' + ' and '.join(_cite(c,p) for c,p in zip(flag.cites,flag.page_ids)) + '.')
            expected_gaps.extend("Model's reading: " + about for about in flag.abouts)
    if [p.text for p in gaps] != expected_gaps:
        errors.append(f'memo={number}: gaps differ')
    if [p.text for p in paragraphs if p.style.name == 'Heading 1'] != list(SECTIONS):
        errors.append(f'memo={number}: section order differs')
    providers = _section(doc, 'Providers')
    associations = {}
    for fact in records:
        for provider, day, cite, page_id in zip(fact.providers,fact.dates,fact.cites,fact.page_ids):
            if provider:
                associations.setdefault(provider, []).append((day,cite,page_id))
    expected_providers = []
    for provider, entries in associations.items():
        days = sorted([d for d,_,_ in entries if dates.parse(d)], key=dates.parse)
        citations = list(dict.fromkeys((c,p) for _,c,p in entries))
        expected_providers.append(f'{provider}: first {days[0]}, last {days[-1]}, pages ' +
                                  ' and '.join(_cite(c,p) for c,p in citations))
    if [p.text for p in providers] != expected_providers:
        errors.append(f'memo={number}: provider dates or cites differ')
    expected_open = []
    for page in pages:
        state, reason, _ = coverage[(page.page_id, extract.card().name)]
        if state != 'read':
            expected_open.append(f'{labels[page.page_id]} ({page.page_id}): {state}: {reason}')
    if [p.text for p in opened] != (expected_open or ['none']):
        errors.append(f'memo={number}: open items differ')
    built = memo.build(stored, pages, [], matter=NUMBER,
        playbook_version=book.version, model='qwen3.8:27b', info=matterinfo.load(path.parent.parent))
    rule_hits = sum(hit.severity == 'error' for hit in memo.check(built, book.rules))
    header_ok = int([p.text for p in paragraphs[:9]] == [f'Medical memo: matter {NUMBER}',
        'Attorney Work Product | Privileged & Confidential', 'Matter type: workers-comp',
        'Client: Morgan Ashby-Vale', 'Date of accident: 03/11/2025',
        'Treating physician: Dr. Priya Okonkwo-Lind', 'IAB hearing number: 1234567',
        'Hearing date: 01/15/2026 9:00 AM', f'Matter {NUMBER}'] and
        re.fullmatch(r'Built \d{4}-\d{2}-\d{2} from case file entry ' + str(stored.outputs[-1]['built_from_seq']) +
                     re.escape(f'; playbook {book.version}; model qwen3.8:27b'), paragraphs[9].text) is not None)
    sentence = re.fullmatch(r'Pages read in (\d+) runs?; conflicts and gaps are checked only between '
        r'pages sent to the model together\. A cloud task run reads the whole matter \(stage 7b\)\.', conflicts[0].text)
    runs_seen = int(sentence[1]) if sentence else -1
    read_runs = {row[2] for row in coverage.values() if row[0] == 'read'}
    if runs_seen != len(read_runs):
        errors.append(f'memo={number}: read-run count differs')
    changed_text = [p.text for p in _section(doc, SECTIONS[0])]
    expected_change = ('First memo for this matter' if number == 1 else
        '1 fact added, 0 cites added, 1 reading added, 0 flags added' if number == 3 else
        '0 facts added, 0 cites added, 0 readings added, 0 flags added')
    if changed_text != [expected_change]:
        errors.append(f'memo={number}: changes differ')
    if [p.text for p in _section(doc, SECTIONS[1])] != ['none']:
        errors.append(f'memo={number}: outputs out of date differ')
    changed = 'first' if number == 1 else changed_text[0].split(' ',1)[0]
    entries = [] if not expected_open else opened
    open_status = entries[0].text.split(': ')[1] if entries else 'none'
    readings = sum(p.text.startswith("Model's reading") for p in chronology)
    cites = sum(p.text.count('[cite ') for p in paragraphs)
    if not header_ok or rule_hits:
        errors.append(f'memo={number}: header or firm rules differ')
    return (f'stage5 memo={number} sections=15 chronology={len(actual_chronology)} dated={dated} of {len(records)} '
        f'providers={len(providers)} conflicts={len(flags)} conflict_quotes_ok={conflict_quotes_ok} '
        f'defense_first={defense_first} header_ok={header_ok} cites={cites} readings={readings} '
        f'gaps={len(expected_gaps)//2} runs_seen={runs_seen} open={len(entries)} open_status={open_status} '
        f'rule_hits={rule_hits} changed={changed}')


@pytest.mark.socket
def test_stage5_exit(tmp_path, capsys):
    loaded = matter.load(MATTER)
    page = next(page for page in loaded.pages if page.stamps == ("DEF0001",))
    assert ONE_PAGE["facts"][0]["quote"] in page.text
    fake = FakeModel(recordings=[*recordings_for(MATTER), recording_for(extract.card(), (page,), NUMBER, ONE_PAGE)])
    server = serve(port=0, model=fake)
    thread = Thread(target=server.serve_forever)
    thread.start()
    run_lines, memo_lines, statuses, errors = [], [], [], []
    try:
        path = write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}", playbook=ROOT / "playbook")
        settings = config.load(path)
        folder = settings.paths.matters / NUMBER
        shutil.copytree(MATTER, folder)
        env = dict(os.environ, CASEFILE_CONFIG=str(path))
        opener = build_opener(ProxyHandler({}))
        book = playbook.load(settings.paths.playbook)
        previous_seq = previous_runs = previous_answers = 0
        with open_db(settings.paths.state / "runlog.sqlite") as log:
            for number, mode in enumerate(("replay", "bad_schema", "replay", "replay"), 1):
                request = Request(settings.model.host + "/_fake/mode", method="POST",
                                  data=json.dumps({"mode": mode}).encode("utf-8"),
                                  headers={"Content-Type": "application/json"})
                with opener.open(request, timeout=5) as response:
                    assert response.status == 200 and json.load(response) == {"mode": mode}
                requests0 = len(fake.requests)
                result = subprocess.run(["scripts/run.sh", "casefile", "memo", "--matter", NUMBER],
                                        cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
                stored = facts.load(folder / "casefile.jsonl")
                coverage = log.coverage(NUMBER, job="memo")
                runs = log.connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
                answers = log.connection.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
                counts = {state: sum(row[0] == state for row in coverage.values())
                          for state in ("read", "uncited", "failed")}
                opened = counts["uncited"] + counts["failed"]
                changes = stored.changed_since(previous_seq)
                chats = [r for r in fake.requests[requests0:] if r["path"] == "/api/chat"]
                line = (f"stage5 run={number} mode={mode} exit={result.returncode} chunks={runs - previous_runs} "
                        f"runs={runs - previous_runs:+d} read={counts['read']} open={opened} "
                        f"facts={len(stored.facts)} conflicts={sum(f.kind == 'conflict' for f in stored.flags)} "
                        f"gaps={sum(f.kind == 'gap' for f in stored.flags)} new_facts={changes['fact']} "
                        f"new_flags={changes['flag']}")
                run_lines.append(line)
                # CLI counts must agree with the independently read case file and coverage.
                expected_stdout = (f"memo {NUMBER} chunks=" + line.split(" chunks=", 1)[1] +
                                   f" memo={folder / 'outputs/memo.docx'}")
                expected_open = ([] if not opened else [
                    "  open: DEF0001 (defense-report/001): " +
                    ("uncited: no fact or flag cites defense-report/001" if number == 1 else "failed: " + BAD_REASON)])
                if result.stdout.splitlines() != [expected_stdout, *expected_open] or result.stderr:
                    errors.append(f"run={number}: CLI differs: {result.stdout!r} {result.stderr!r}")
                expected_chats = (1, 2, 1, 0)[number - 1]
                if len(chats) != expected_chats or answers - previous_answers != expected_chats:
                    errors.append(f"run={number}: chats={len(chats)} answers={answers - previous_answers}")
                expected_pages = [p.page_id for p in loaded.pages] if number == 1 else [page.page_id]
                for chat in chats:
                    body = json.loads(chat["body"])
                    sent = re.findall(r"^=== PAGE (\S+) BATES ", body["messages"][1]["content"], re.MULTILINE)
                    if sent != expected_pages:
                        errors.append(f"run={number}: sent pages differ: {sent}")
                expected_line_count = (42, 44, 47, 48)[number - 1]
                if len(stored.events) != expected_line_count:
                    errors.append(f"run={number}: casefile_lines={len(stored.events)} expected={expected_line_count}")
                memo_line = _read_memo(number, folder / "outputs/memo.docx", stored,
                                       loaded.pages, coverage, book, errors)
                if number <= 3:
                    memo_lines.append(memo_line)
                status = subprocess.run(["scripts/run.sh", "casefile", "status", "--matter", NUMBER],
                                        cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
                fields = dict(re.findall(r"(\w+)=([^ ]+)", status.stdout.splitlines()[0]))
                statuses.append(fields)
                expected_status = (f"status {NUMBER} pages=14 read={counts['read']} failed={counts['failed']} "
                                   f"uncited={counts['uncited']} empty=0 open={opened} facts={len(stored.facts)} "
                                   "conflicts=5 gaps=4 outputs=memo:current")
                if status.returncode != 0 or status.stderr or status.stdout.splitlines() != [expected_status, *expected_open]:
                    errors.append(f"run={number}: status differs: {status.stdout!r} {status.stderr!r}")
                previous_seq, previous_runs, previous_answers = stored.last_seq, runs, answers
    finally:
        server.shutdown()
        thread.join(timeout=5)
        stopped = not thread.is_alive()
        server.server_close()
    status_line = (f"stage5 status read={statuses[0]['read']} then {statuses[2]['read']} "
                   f"open={statuses[0]['open']} then {statuses[2]['open']} outputs={statuses[2]['outputs']}")
    chain_ok = int(facts.load(folder / "casefile.jsonl").torn == 0)
    complete_lines = len((folder / "casefile.jsonl").read_bytes().splitlines())
    lines = [*run_lines, *memo_lines, status_line]
    good_runs = sum(actual == expected for actual, expected in zip(run_lines, EXPECTED[:4]))
    good_memos = sum(actual == expected for actual, expected in zip(memo_lines, EXPECTED[4:7]))
    failed = bool(errors or lines != list(EXPECTED[:8]) or answers != 4 or complete_lines != 48
                  or not chain_ok or not stopped)
    lines.append(f"stage5 exit={int(failed)} runs={good_runs} of 4 memos={good_memos} of 3 answers={answers:+d} "
                 f"casefile_lines={complete_lines} chain_ok={chain_ok} server_stopped={int(stopped)}")
    with capsys.disabled():
        print("\n".join(lines), flush=True)
    mismatches = [f"expected: {expected}\nactual:   {actual}"
                  for actual, expected in zip(lines, EXPECTED) if actual != expected]
    assert lines == list(EXPECTED) and not errors, "stage5 exit check failed:\n" + "\n".join(errors + mismatches)
