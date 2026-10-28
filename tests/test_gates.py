"""Pipeline checks use invented pages and an in-process recorded model only."""

from dataclasses import replace
import json

import pytest

from casefile import benchrun, config, gates, matter, model, rules
from casefile.runlog import open_db
from conftest import ROOT, write_config
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import extraction_card, recordings_for


FIXTURE = ROOT / 'tests/fixtures/matters/9001.001'
NONCE = '0123456789abcdef'
SEARCHED = ('MED0001, MED0002, MED0003, MED0004, MED0005, MED0006, MED0007, MED0008, '
            'EMP0001, EMP0002, EMP0003, DEF0001, DEF0002, DEF0003')
BAD_QUOTE_FAULTS = (
    f'quote on MED0001 not found (pages searched: {SEARCHED})',
    f'cite MED0099 is not a page of this chunk (pages searched: {SEARCHED})',
    f'cite MED0098 is not a page of this chunk (pages searched: {SEARCHED})',
    'text number 03 not in quote',
    'text number 99999 not in quote',
)
CASES = (
    'good', 'budget', 'prompt_too_long', 'cut_prompt', 'truncated', 'cut_answer',
    'length_only', 'missing_count', 'zero_count', 'sum_count', 'answer_limit',
    'repairable', 'unrepairable', 'bad_schema', 'bad_quote', 'fact_cite', 'text_number',
    'flag_cite', 'forbidden_json', 'quoted_ime', 'unstamped', 'empty_answer', 'retry_ok',
    'retry_budget', 'no_reply', 'open_items', 'request_body',
)


def probe():
    pages = (
        matter.Page('probe', 1, 'Harrowgate Occupational Clinic notes pain of 7/10.', ()),
        matter.Page('probe', 2, 'The IME report of 03/02/2026 notes a normal gait.', ()),
        matter.Page('probe', 3, 'Harrowgate Occupational Clinic recommends follow-up.', ()),
    )
    facts = [{'cite': p.page_id, 'quote': p.text,
              'text': 'The report notes a normal gait.' if p.number == 2 else p.text} for p in pages]
    return pages, {'facts': facts, 'flags': []}


def recording(card, pages, number, obj):
    return {'name': 'invented-probe',
            'messages': gates.messages(card, pages, '__PROMPT_ID__', matter=number),
            'answer': json.dumps({'prompt_id': '__PROMPT_ID__', **obj, 'end_id': '__PROMPT_ID__'})}


def rows(log, table, run_id):
    return [dict(row) for row in log.connection.execute(
        f'SELECT * FROM {table} WHERE run_id=? ORDER BY id', (run_id,))]


def content_edit(change):
    def edit(reply):
        obj = json.loads(reply['message']['content'])
        change(obj)
        reply['message']['content'] = json.dumps(obj)
    return edit


@pytest.fixture(scope='module')
def gate_totals():
    passed = []
    yield passed
    print(f'gate_cases={len(passed)} of 27', flush=True)


@pytest.mark.parametrize('case', CASES)
def test_gate_cases(case, tmp_path, gate_totals):
    loaded = matter.load(FIXTURE)
    ideal = json.loads((FIXTURE / 'ideal.json').read_text(encoding='utf-8'))
    card = extraction_card()
    firm = rules.load(ROOT / 'playbook/rules.toml')
    settings = config.load(write_config(tmp_path)).model
    assert len(CASES) == 27
    with open_db(tmp_path / f'{case}.sqlite') as log:
        _case(case, log, loaded, ideal, card, firm, settings)
    gate_totals.append(case)


def _case(case, log, loaded, ideal, card, firm, settings):
    pages, number = loaded.pages, loaded.number
    recordings = recordings_for(FIXTURE)
    mode = case if case in {'prompt_too_long', 'cut_prompt', 'truncated', 'cut_answer',
                           'repairable', 'unrepairable', 'bad_schema', 'bad_quote',
                           'forbidden_json', 'empty_answer', 'retry_ok'} else 'replay'
    edit = None
    if case == 'budget':
        card = replace(card, max_answer_tokens=65536 - 10)
    elif case == 'length_only':
        edit = lambda reply: reply.update(done_reason='length')
    elif case == 'missing_count':
        edit = lambda reply: reply.update(prompt_eval_count=None)
    elif case == 'zero_count':
        edit = lambda reply: reply.update(eval_count=0)
    elif case == 'sum_count':
        edit = lambda reply: reply.update(prompt_eval_count=settings.num_ctx - 5, eval_count=10)
    elif case == 'answer_limit':
        edit = lambda reply: reply.update(eval_count=card.max_answer_tokens)
    elif case == 'fact_cite':
        edit = content_edit(lambda obj: obj['facts'][0].update(cite='MED0099'))
    elif case == 'text_number':
        edit = content_edit(lambda obj: obj['facts'][0].update(text='Pain was 99999/10.'))
    elif case == 'flag_cite':
        edit = content_edit(lambda obj: obj['flags'][0]['cites'].append('MED0098'))
    elif case in {'quoted_ime', 'unstamped'}:
        pages, obj = probe()
        if case == 'quoted_ime':
            pages = tuple(replace(p, stamps=(f'MED{p.number:04d}',)) for p in pages)
        number = '9003.001'
        recordings = [recording(card, pages, number, obj)]
    elif case == 'retry_budget':
        mode = 'unrepairable'
        msgs = gates.messages(card, pages, NONCE, matter=number)
        ceiling = sum(model.tokens_at_most(m['content']) for m in msgs) + model.TEMPLATE_TOKENS
        card = replace(card, max_answer_tokens=settings.num_ctx - ceiling)
    elif case == 'open_items':
        mode = 'unrepairable'
    fake = FakeModel(mode=mode, recordings=recordings)
    transport = FakeTransport(fake, edit=edit)
    client = model.ModelClient(settings, transport)
    if case == 'no_reply':
        class NoReply:
            config = settings

            def chat(self, *args, **kwargs):
                raise model.ModelError('invented offline server', received=False)

        with pytest.raises(model.ModelError, match='invented offline server'):
            gates.ask(card, pages, client=NoReply(), rules=firm, log=log, matter=number, nonce=NONCE)
        assert log.connection.execute('SELECT COUNT(*) FROM runs').fetchone()[0] == 1
        for table in ('answers', 'failures', 'gates', 'coverage'):
            assert log.connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 0, table
        return
    outcome = gates.ask(card, pages, client=client, rules=firm, log=log, matter=number, nonce=NONCE,
                        job='invented-extraction', playbook_version='pb-invented')
    received = rows(log, 'answers', outcome.run_id)
    checked = rows(log, 'gates', outcome.run_id)
    failures = rows(log, 'failures', outcome.run_id)
    coverage = rows(log, 'coverage', outcome.run_id)
    requests = [json.loads(req.data) for req, _ in transport.requests]
    assert len(coverage) == len(pages), f'{case}: coverage rows={len(coverage)}'
    assert [(v.attempt, v.gate, v.verdict, v.message) for v in outcome.verdicts] == [
        (r['attempt'], r['gate'], r['verdict'], r['message']) for r in checked]
    assert outcome.run_id == coverage[0]['run_id']
    run = dict(log.connection.execute(
        'SELECT * FROM runs WHERE id=?', (outcome.run_id,)).fetchone())
    assert (run['card'], run['card_version'], run['matter'], run['job'], run['playbook_version'],
            run['pages_in']) == (card.name, card.version, number, 'invented-extraction', 'pb-invented', len(pages))
    assert run['prompt_sha256'] == benchrun.prompt_sha256(gates.messages(card, pages, NONCE, matter=number))
    for request in requests:
        assert request['truncate'] is False and request['think'] is False
        assert request['options'] == {'num_predict': card.max_answer_tokens, 'num_ctx': 65536, 'temperature': 0.1}
        assert len(request['messages']) == 2
        nonce = request['messages'][0]['content'].splitlines()[0].split(': ')[1]
        assert sum(m['content'].count(nonce) for m in request['messages']) == 1
    successful = {'good', 'repairable', 'quoted_ime', 'unstamped', 'retry_ok', 'request_body'}
    if case in successful:
        assert outcome.ok, f'{case}: unexpectedly failed: {outcome.failed}'
        assert outcome.failed == ()
        assert outcome.attempts == (2 if case == 'retry_ok' else 1)
        assert [r['status'] for r in received] == (['failed', 'ok'] if case == 'retry_ok' else ['ok'])
        if case in {'quoted_ime', 'unstamped'}:
            assert len(outcome.read) == 3 and outcome.uncited == ()
        else:
            assert len(outcome.read) == 13 and outcome.uncited == ('DEF0001',), (
                f'good read={len(outcome.read)} uncited={outcome.uncited}')
            assert outcome.answer == ideal
        if case == 'good':
            assert [(r['gate'], r['verdict']) for r in checked] == [
                (f'gate.{g}', 'pass') for g in gates.GATES]
            assert len(checked) == 6
            assert [r['status'] for r in coverage].count('read') == 13
            assert len(gates.open_items(log, number)) == 1
        if case == 'repairable':
            assert [r['message'] for r in checked if r['verdict'] == 'repaired'] == [
                'fence', 'control', 'trailing-comma', 'closers']
        if case == 'unstamped':
            assert next(r['message'] for r in checked if r['gate'] == 'gate.rules') == (
                'warning: no Bates stamp on probe/001, probe/002, probe/003; cites are page ids')
    else:
        expected_gate = {
            'unrepairable': 'repair', 'bad_schema': 'schema', 'bad_quote': 'quotes', 'fact_cite': 'quotes',
            'text_number': 'quotes', 'flag_cite': 'quotes', 'forbidden_json': 'rules',
            'empty_answer': 'coverage', 'open_items': 'repair',
        }.get(case, 'truncation')
        assert not outcome.ok, f'{case}: unexpectedly passed'
        assert outcome.answer is None, f'{case}: answer must be None, got {outcome.answer!r}'
        assert outcome.read == () and outcome.uncited == () and len(outcome.failed) == 14
        assert {r['status'] for r in coverage} == {'failed'}
        assert all(r['status'] == 'failed' for r in received)
        expected_failures = (['gate.repair', 'gate.truncation'] if case == 'retry_budget'
                             else [f'gate.{expected_gate}'] * len(failures))
        assert [r['gate'] for r in failures] == expected_failures, failures
        expected_requests = 0 if case == 'budget' else 1 if case in {
            'prompt_too_long', 'cut_prompt', 'retry_budget'} else 2
        assert len(requests) == expected_requests, f'{case} requests={len(requests)} expected={expected_requests}'
        assert len(received) == expected_requests
        assert outcome.attempts == (1 if case in {'budget', 'prompt_too_long', 'cut_prompt'} else 2)
        if case not in {'budget', 'prompt_too_long', 'retry_budget'}:
            expected_rows = [(f'gate.{g}', 'pass') for g in
                             ('truncation', 'repair', 'schema', 'quotes', 'rules', 'coverage')[
                                 :('truncation', 'repair', 'schema', 'quotes', 'rules', 'coverage').index(expected_gate)]]
            expected_rows.append((f'gate.{expected_gate}', 'fail'))
            assert [(r['gate'], r['verdict']) for r in checked if r['attempt'] == 1] == expected_rows, (
                f'{case} gate rows differ: {[(r["gate"], r["verdict"]) for r in checked]}')
        if case in {'budget', 'retry_budget'}:
            assert failures[-1]['message'] == 'over budget'
        elif case == 'cut_prompt':
            assert failures[0]['message'] == 'prompt cut (prompt_id missing)'
        elif case == 'cut_answer':
            assert failures[0]['message'] == 'answer cut (end_id missing)', failures
        elif case in {'truncated', 'length_only'}:
            assert all(r['message'] == 'done_reason=length' for r in failures)
        elif case in {'missing_count', 'zero_count'}:
            assert failures[0]['message'] == 'counts must be positive integers'
        elif case == 'sum_count':
            assert failures[0]['message'] == 'counts exceed context'
        elif case == 'answer_limit':
            assert failures[0]['message'] == 'counts reach max_answer_tokens'
        elif case == 'bad_quote':
            for failure in failures:
                parts = failure['message'].split('; ')
                assert parts[1:-1] == list(BAD_QUOTE_FAULTS)
                assert failure['message'] == (
                    'faults=5; ' + '; '.join(BAD_QUOTE_FAULTS) + '; check source pages and retry')
        elif case == 'text_number':
            assert 'text number 99999 not in quote' in failures[0]['message']
        elif case == 'forbidden_json':
            assert failures[0]['message'].startswith('no-dme-ime:')
        elif case == 'empty_answer':
            assert failures[0]['message'] == 'empty answer'
    if case in {'unrepairable', 'retry_ok'}:
        second = requests[1]['messages']
        assert second[0]['content'].splitlines()[0] != requests[0]['messages'][0]['content'].splitlines()[0]
        assert second[0]['content'].split('\n', 1)[1] == card.text
        assert second[1]['content'].splitlines()[1].startswith(
            'Retry: the previous answer failed the repair check:')
        assert len(second) == 2
        assert second[1]['content'].split('\n', 2)[2] == requests[0]['messages'][1]['content'].split('\n', 1)[1]
    if case == 'open_items':
        assert len(gates.open_items(log, number)) == 14
        fake.mode = 'retry_ok'
        later = gates.ask(card, pages, client=client, rules=firm, log=log, matter=number)
        assert later.ok and later.attempts == 2
        opened = gates.open_items(log, number)
        assert set(opened) == {('DEF0001', 'bench_extract')}, f'open_items={len(opened)} expected=1'
        assert opened[('DEF0001', 'bench_extract')] == (
            'uncited', 'no fact or flag cites DEF0001', later.run_id)
        assert len(rows(log, 'coverage', later.run_id)) == 14
