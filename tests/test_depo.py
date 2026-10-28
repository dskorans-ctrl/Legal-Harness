"""Deposition job checks, including restored answers without a model."""

from io import StringIO
import json

from docx import Document
import pytest

from casefile import cards, depo, facts, matterinfo, outputs, packet, status
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for
from test_outputs import answer, document, flat, section, setup_case


def answers_for(who):
    return {'factsheet': answer('factsheet-' + who), **{
        'questions:' + part: answer(f'questions-{who}-{part}') for part in depo.SECTIONS}}


def recorded_body(value):
    # Keep an independent marker expectation so recording generation cannot hide its loss.
    lines=value.body().splitlines()
    own=set(value.options.get('deponent_pages', ()))
    for fact in value.facts:
        if fact.page_id in own:
            index=next(i for i,line in enumerate(lines) if line.startswith('['+fact.id+'] '))
            if not lines[index].endswith(" [deponent's record]"):
                lines[index]+=" [deponent's record]"
    return '\n'.join(lines)+'\n'


def register(fake, value, book, data, cfg, who):
    card = cards.card('02-A', book)
    for part in packet.batches(value, card, cfg.model.num_ctx):
        fake.record(recording_for(card, part.pages, value.matter, data['factsheet'], body=recorded_body(part)))
    card = cards.card(depo.CARD_IDS[who], book)
    for part in depo.SECTIONS:
        request = depo.question_packet(value, data['factsheet'], part, card, cfg.model.num_ctx)
        fake.record(recording_for(card, request.pages, value.matter, data['questions:' + part], body=recorded_body(request)))


def run_job(cfg, loaded, fake, **kwargs):
    out, err = StringIO(), StringIO()
    code = depo.run(cfg, loaded.number, out=out, err=err, opener=FakeTransport(fake), **kwargs)
    return code, out.getvalue() + err.getvalue()


@pytest.mark.parametrize('row', range(12))
def test_depo_contract(tmp_path, monkeypatch, row, capsys):
    _, cfg, folder, loaded, cf, book = setup_case(tmp_path)
    info = matterinfo.load(folder)
    who = 'our-doctor' if row in (1,2,3,5) else 'client' if row==4 else 'defense-doctor'
    kwargs = dict(deponent=who, taken_by='defense' if row==6 else 'us')
    if who.endswith('doctor'):
        kwargs['provider'] = 'Okonkwo-Lind' if who=='our-doctor' else 'Marchetti'
    value = depo.prepare(cf, loaded.pages, book, info, number=loaded.number, **kwargs)
    data = answers_for('our-doctor' if who=='our-doctor' else 'defense-doctor')
    if who=='client':
        for part in depo.SECTIONS:
            data['questions:'+part] = dict(section=part, questions=[
                dict(text='When were you hired by Quarry Ridge Logistics LLC?',cite='EMP0001',quote='Date of hire: 08/02/2021',note=''),
                dict(text='Who hired you at the warehouse?',cite='EMP0001',quote='Date of hire: 08/02/2021',note='')],points_for_our_expert=[])
    if row==2:
        alternate=depo.prepare(cf,loaded.pages,book,info,number=loaded.number,deponent=who,taken_by='us',selected='MED0007,MED0008')
        assert alternate==value, 'W6 page override packet differs'
        kwargs.pop('provider'); kwargs['selected']='MED0007,MED0008'
    if row==3:
        data['questions:primary']['questions']=data['questions:primary']['questions'][:1]
    if row==5:
        kwargs.pop('provider')
        code, text=run_job(cfg,loaded,FakeModel(),**kwargs)
        assert code==2 and 'name the deponent with --provider' in text
        assert not (folder/'outputs').exists()
        return
    if row==7:
        class QuestionsForbidden(FakeModel):
            def handle(self, method, path, body=b''):
                if path=='/api/chat':
                    request=json.loads(body)
                    self.mode='forbidden_json' if 'Section: ' in request['messages'][-1]['content'] else 'replay'
                return super().handle(method,path,body)
        fake=QuestionsForbidden()
    else:
        fake=FakeModel()
    if row==8:
        data['questions:primary']['questions'][0].update(cite='DEF0002',quote='Ridgeline Physical Therapy notes')
    if row==9:
        data['questions:primary']['questions'][0]['text']='Your report records 99999 pounds, correct?'
    if row==11:
        def forbidden(*args,**kwargs): raise AssertionError('W6 render called model')
        monkeypatch.setattr(outputs,'ask',forbidden)
        data['questions:cross']=None
        doc=depo.render(data,value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
        restored=document(tmp_path,doc,book.rules,providers=outputs.providers(cf))
        assert section(restored,'Questions: anticipated cross')[0].startswith("Questions: anticipated cross: the model's answer failed"), 'W6 render silently ignored None answer'
        assert 'questions:cross: failed section' in section(restored,'Open items')
        with capsys.disabled(): print('depo_ok=12 of 12')
        return
    register(fake,value,book,data,cfg,who)
    code,text=run_job(cfg,loaded,fake,**kwargs)
    if row in (7,8,9):
        assert code==1, 'W6 invalid question was not disclosed: '+text
        doc=Document(folder/f'outputs/depo-{who}-{kwargs["taken_by"]}.partial.docx')
        expected='gate.rules' if row==7 else 'gate.quotes'
        assert expected in '\n'.join(section(doc,'Questions: primary'))
        assert not facts.load(folder/'casefile.jsonl').outputs
        return
    assert code==(1 if row==3 else 0), ('W6 missing bills question was not disclosed: ' if row==3 else 'W6 deponent records unmarked: ' if row==0 else 'W6 job failed: ')+text
    doc=Document(folder/f'outputs/depo-{who}-{kwargs["taken_by"]}.docx')
    if row==0:
        assert sum(len(r._r.xpath('.//w:br[@w:type="page"]')) for p in doc.paragraphs for r in p.runs)==2
        for title,uses in (('Case outline: our view',('our_case','both')),('Case outline: the defense view',('defense_case','both'))):
            expected=[f for f in cf.facts if any(i['use'] in uses and i['quote']==f.quote and i['cite'] in f.cites for i in data['factsheet']['facts'])]
            if 'defense view' in title:
                expected = [f for f in expected if any(pid.startswith('defense-report/') for pid in f.page_ids)]
            actual=[p for p in section(doc,title) if ': "' in p]
            assert len(actual)==len(expected), 'W6 outline included none or danger labels'
        for part,title in zip(depo.SECTIONS,depo.TITLES):
            lines=section(doc,title)
            assert len([p for p in lines if p.startswith('Rests on:')])==len(data['questions:'+part]['questions'])
            assert lines[0].startswith('1. ')
        assert any('lumbar strain in 2019' in p for p in section(doc,'Danger zone'))
        assert any(p.startswith("Model's note:") for p in section(doc,'Points for our expert'))
        assert "[deponent's record]" in value.body(), 'W6 deponent records unmarked'
        assert {'DEF0001','DEF0002','DEF0003'} <= {p.stamps[0] for p in value.pages}
    elif row==1:
        primary=section(doc,'Questions: primary')
        bills=next(p for p in primary if 'as to the bills themselves' in p)
        assert sum(provider in bills for provider in outputs.providers(cf))==5, 'W6 providers_named differs from 5 of 5 (defense-only providers excluded)'
        assert not any(p.startswith('Missing:') for p in primary)
        assert not [f for f in outputs.check(depo.render(data,value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name),book.rules,providers=outputs.providers(cf)) if f.severity=='error']
    elif row==3:
        assert section(doc,'Questions: primary')[0]=='Missing: the bills question (firm practice: two separate questions)', 'W6 missing bills question was not disclosed'
    elif row==4:
        assert set(value.options['deponent_pages'])=={p.page_id for p in loaded.pages}
        assert 'Who hired you at the warehouse?' in '\n'.join(flat(doc))
    elif row==6:
        assert 'taken_by="defense"' in value.body()
        assert 'primary is theirs, cross ours, redirect theirs' in cards.card('02-C-DEFDOC',book).text
    elif row==10:
        assert f'depo-{who}-us:current' in status.matter_status(cfg,loaded.number)['outputs']
        restored=depo.render(data,value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
        assert flat(document(tmp_path,restored,book.rules,providers=outputs.providers(cf)))==flat(doc)


def test_questions_numbers_use_page(tmp_path):
    _,cfg,folder,loaded,cf,book=setup_case(tmp_path)
    info=matterinfo.load(folder)
    value=depo.prepare(cf,loaded.pages,book,info,number=loaded.number,deponent='defense-doctor',taken_by='us',provider='Marchetti')
    data=answers_for('defense-doctor')
    item=data['questions:primary']['questions'][2]
    assert '06/20/2025' in item['text'] and '06/20/2025' not in item['quote']
    fake=FakeModel()
    register(fake,value,book,data,cfg,'defense-doctor')
    code,text=run_job(cfg,loaded,fake,deponent='defense-doctor',taken_by='us',provider='Marchetti')
    assert code==0, 'W6 numbers_in read quote instead of page: '+text
