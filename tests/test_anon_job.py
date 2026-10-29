"""Both local passes use only invented pages and an injected in-process stand-in."""

from dataclasses import replace
from io import StringIO
import json
import shutil

import pytest

from casefile import anon, anon_job, cards, config, matter, matterinfo, model, pipeline, rules
from casefile.packet import Packet
from casefile.runlog import open_db
from conftest import ROOT, write_config
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for

FIXTURE=ROOT/'tests/fixtures/matters/9001.001'
ANSWERS=ROOT/'tests/fixtures/anonymizer/9001.001'


class TTY(StringIO):
    def isatty(self):
        return True


def answer(name='entities'):
    return json.loads((ANSWERS/(name+'.json')).read_text(encoding='utf-8'))


def load(tmp_path):
    folder=tmp_path/'matters/9001.001'
    shutil.copytree(FIXTURE,folder)
    settings=config.load(write_config(tmp_path)).model
    loaded=matter.load(folder)
    info=matterinfo.load(folder)
    return folder,settings,loaded,info


def transport(pages, obj=None, *, mode='replay'):
    recordings=[] if obj is None else [recording_for(cards.card('07-ANON'),pages,'9001.001',obj)]
    return FakeTransport(FakeModel(recordings=recordings,mode=mode))


def pass_args(log,settings,opener):
    return dict(client=model.ModelClient(settings,opener),rules=rules.load(ROOT/'playbook/rules.toml'),
                log=log,matter='9001.001',playbook_version='test',job='brief')


def packet(pages):
    return Packet('9001.001','brief',{'issue':'Morgan Ashby-Vale at Quarry Ridge Logistics LLC on 03/11/2025'},'test',(),tuple(pages))


def filter_answer(obj,pages):
    refs={p.page_id for p in pages}|{s for p in pages for s in p.stamps}
    return {'pages_seen':[p.page_id for p in pages], **{k:[r for r in obj[k] if r['cite'] in refs]
            for k in ('people','organizations','places','anchor_dates')}}


def test_entity_four(tmp_path):
    folder,settings,loaded,info=load(tmp_path)
    good=answer()
    results=[]
    with open_db(tmp_path/'log.sqlite') as log:
        opener=transport(loaded.pages,good)
        hits=anon_job.entity_pass(loaded.pages,**pass_args(log,settings,opener))
        # The expected order is written from the fixture's binder/page order.
        expected=['Fennimore County Hospital','Morgan Ashby-Vale','Halvard Quist-Benning','Quarry Ridge Logistics LLC',
                  'Brightwater Family Medicine','Ines Castellanos-Reyes','Ridgeline Physical Therapy','Odalys Ferro-Lindqvist',
                  'Lakeshore Imaging','Ansgar Velloso-Krantz','Lakeshore Orthopedic Associates','Priya Okonkwo-Lind',
                  'Rosalind Mbeki-Farrow','Tobiah Varga-Ellison','Silas Vane-Harrow','Northgate Medical Evaluations','Theodore Marchetti']
        results.append([h.name for h in hits]==expected and len(hits.anchors)==3)
        bad=answer()
        # A true quote accompanies an absent name so gate 4 alone cannot catch this defect.
        bad['people'].append(dict(name='Invented Absent Person',kind='person',quote='Date of service: 03/11/2025',cite='MED0001'))
        offpage=anon_job.entity_pass(loaded.pages,**pass_args(log,settings,transport(loaded.pages,bad)))
        dropped=log.connection.execute("SELECT message FROM failures WHERE gate='gate.identifier'").fetchall()
        results.append(len(offpage)==17 and [r[0] for r in dropped]==['hit dropped: name not on medical/001'])
        size=next(n for n in range(18000,50000,500) if len(pipeline.chunk(cards.card('07-ANON'),loaded.pages,n,loaded.number)[0])==3
                  and not pipeline.chunk(cards.card('07-ANON'),loaded.pages,n,loaded.number)[1])
        chunk_settings=replace(settings,num_ctx=size)
        chunks,_=pipeline.chunk(cards.card('07-ANON'),loaded.pages,size,loaded.number)
        opener=FakeTransport(FakeModel(recordings=[recording_for(cards.card('07-ANON'),part,loaded.number,filter_answer(good,part)) for part in chunks]))
        chunked=anon_job.entity_pass(loaded.pages,**pass_args(log,chunk_settings,opener))
        requests=[json.loads(request.data) for request,_ in opener.requests]
        seen=[[p.page_id for p in part] for part in chunks]
        results.append(len(chunked)==17 and len(requests)==3 and all(
            all(pid in request['messages'][1]['content'] for pid in ids) for ids,request in zip(seen,requests)))
        with pytest.raises(anon_job.EntityError,match='kind=model'):
            anon_job.entity_pass(loaded.pages,**pass_args(log,settings,transport(loaded.pages,good,mode='bad_schema')))
        results.append(not (folder/'anon').exists() and not (folder/'outbox').exists())
    print(f'entity_pass={sum(results)} of 4')
    assert all(results),f'entity_pass={sum(results)} of 4'


def test_halt_four(tmp_path,monkeypatch):
    folder,settings,loaded,info=load(tmp_path)
    listed=anon.names(info)
    known=[anon.Hit(n,k,n,'MED0001') for n,k in listed.people.items()]
    before=(folder/'matter.toml').read_bytes()
    stdout=StringIO()
    calls=[]
    original=matterinfo.write
    def write(*args):
        calls.append(args)
        original(*args)
    monkeypatch.setattr(matterinfo,'write',write)
    same=anon_job.halt(listed,known,TTY(),stdout)
    results=[same==listed and not calls and not stdout.getvalue() and (folder/'matter.toml').read_bytes()==before]
    new=anon.Hit('Althea Quill','person','Althea Quill','MED0001')
    changed=anon_job.halt(listed,[new,new],TTY('\n'),stdout)
    reloaded=matterinfo.load(folder)
    results.append(changed.people['Althea Quill']=='person' and reloaded.anon_people['Althea Quill']=='person' and len(calls)==1 and '[person]' in stdout.getvalue())
    kept=anon_job.halt(anon.names(reloaded),[anon.Hit('Beatrice Finch','person','Beatrice Finch','MED0001')],TTY('keep\n'),StringIO())
    results.append('Beatrice Finch' in kept.keep and matterinfo.load(folder).anon_keep==('Beatrice Finch',) and len(calls)==2)
    before=(folder/'matter.toml').read_bytes()
    out=StringIO()
    with pytest.raises(anon_job.NameListNeeded) as caught:
        anon_job.halt(listed,[new],StringIO(),out)
    results.append(caught.value.code==2 and 'NAME LIST NEEDED' in out.getvalue() and len(calls)==2 and
                   (folder/'matter.toml').read_bytes()==before and not (folder/'anon').exists() and not (folder/'outbox').exists())
    print(f'halt={sum(results)} of 4')
    assert all(results),f'halt={sum(results)} of 4'


def test_anchor_three(tmp_path,capsys):
    folder,settings,loaded,info=load(tmp_path)
    hits=anon_job.Hits()
    hits.anchors=[anon.Hit('03/14/2025','anchor','03/14/2025','MED0003')]
    anonymous,key=anon_job.anonymize(packet(loaded.pages),folder=folder,info=info,hits=hits)
    results=[key.anchor=='2025-03-11' and '[DATE D+0]' in anonymous.pages[0].text]
    other=tmp_path/'other';other.mkdir()
    _,key=anon_job.anonymize(packet(loaded.pages),folder=other,info=replace(info,date_of_accident=''),hits=hits)
    results.append(key.anchor=='2025-03-14')
    missing=tmp_path/'missing';missing.mkdir()
    with pytest.raises(anon.AnonError,match='ANCHOR NEEDED'):
        anon_job.anonymize(packet(loaded.pages),folder=missing,info=replace(info,date_of_accident=''),hits=[])
    results.append(not (missing/'anon').exists())
    capture=capsys.readouterr()
    assert '03/11/2025' not in capture.err
    print(f'anchor={sum(results)} of 3')
    assert all(results),f'anchor={sum(results)} of 3'


def anonymized_fixture(folder,info,loaded,*,missed=False):
    if missed:
        people=dict(info.anon_people)
        people.pop('Rosalind Mbeki-Farrow')
        info=replace(info,anon_people=people)
    anonymous,key=anon_job.anonymize(packet(loaded.pages),folder=folder,info=info,hits=[])
    return info,anonymous,key


def check_args(log,settings,opener,stdout):
    return {**pass_args(log,settings,opener),'stdout':stdout}


def test_second_three_and_order(tmp_path):
    folder,settings,loaded,info=load(tmp_path)
    results=[]
    out=StringIO()
    with open_db(tmp_path/'log.sqlite') as log:
        info,anonymous,key=anonymized_fixture(folder,info,loaded)
        data=anonymous.to_json().encode()
        listed=anon.names(info)
        opener=transport(anonymous.pages,answer('entities-empty'))
        verdict=anon_job.check(data,key,listed,anonymous.pages,**check_args(log,settings,opener,out))
        results.append(verdict==anon.Verdict(True) and len(opener.requests)==1)
        missed=tmp_path/'missed';missed.mkdir()
        missing_info,partial,missing_key=anonymized_fixture(missed,info,loaded,missed=True)
        opener=transport(partial.pages,answer('entities-second-hit'))
        blocked=anon_job.check(partial.to_json().encode(),missing_key,anon.names(missing_info),partial.pages,
                               **check_args(log,settings,opener,out))
        expected=partial.to_json().encode().find(b'Rosalind Mbeki-Farrow')
        results.append(blocked==anon.Verdict(False,((4,'person',expected),)) and expected>0)
        failed=anon_job.check(data,key,listed,anonymous.pages,**check_args(log,settings,transport(anonymous.pages),out))
        results.append(failed==anon.Verdict(False,((4,'model',0),)))
        opener=transport(anonymous.pages,answer('entities-empty'))
        early=anon_job.check(data+b'\n03/12/2025',key,listed,anonymous.pages,**check_args(log,settings,opener,out))
        assert not early.ok and not opener.requests,'check_code must run before second pass'
        receipts=[r[0] for r in log.connection.execute("SELECT message FROM failures WHERE gate='gate.identifier'")]
        assert any('step=2 kind=date' in receipt for receipt in receipts),'code block has no identifier receipt'
        messages='\n'.join(r[0] for table in ('failures','gates') for r in log.connection.execute(f'SELECT message FROM {table}'))
        assert 'Rosalind Mbeki-Farrow' not in messages+out.getvalue(),'key_leak=1'
        assert not (folder/'outbox').exists() and not (missed/'outbox').exists()
    print(f'second_pass={sum(results)} of 3')
    assert all(results),f'second_pass={sum(results)} of 3'


def test_key_leak(tmp_path,capsys):
    folder,settings,loaded,info=load(tmp_path)
    out=StringIO()
    with open_db(tmp_path/'log.sqlite') as log:
        hits=anon_job.entity_pass(loaded.pages,**pass_args(log,settings,transport(loaded.pages,answer())))
        listed=anon_job.halt(anon.names(info),hits,StringIO(),out)
        anonymous,key=anon_job.anonymize(packet(loaded.pages),folder=folder,info=info,hits=hits)
        verdict=anon_job.check(anonymous.to_json().encode(),key,listed,anonymous.pages,
            run_id=hits.run_ids[0],**check_args(log,settings,transport(anonymous.pages,answer('entities-empty')),out))
        assert verdict.ok
        # Exercise rejected model strings without allowing their diagnostic text to escape.
        rejected=answer('entities-empty')
        rejected['people']=[dict(name='Morgan Ashby-Vale',kind='person',quote='Morgan Ashby-Vale',cite='MED0001')]
        verdict=anon_job.check(anonymous.to_json().encode(),key,listed,anonymous.pages,
            run_id=hits.run_ids[0],**check_args(log,settings,transport(anonymous.pages,rejected),out))
        assert not verdict.ok
        capture=capsys.readouterr()
        exported=out.getvalue()+capture.out+capture.err
        exported+='\n'.join(r[0] for table in ('failures','gates') for r in log.connection.execute(f'SELECT message FROM {table}'))
        for path in (folder/'outbox').rglob('*'):
            if path.is_file():
                exported+=path.read_text(encoding='utf-8')
        # Independently enumerate the private values rather than reusing check_code.
        values=[n.split()[-1] for n in info.anon_people]+[info.anon_employer,*info.anon_ids,info.anon_dob,
            info.client_name,info.date_of_accident,anon.strip_title(info.treating_physician),info.iab_hearing_number,info.hearing_date]
        leak=sum(v in exported for v in values)
        print(f'key_leak={leak}')
        assert leak==0,'key_leak=1'
        assert (folder/'anon/key.json').stat().st_mode&0o777==0o600
        raw='\n'.join(r[0] for r in log.connection.execute('SELECT raw_answer FROM answers'))
        assert 'Morgan Ashby-Vale' in raw
        assert not (folder/'outbox').exists()


def test_ambiguous_surname_and_anchor_tie(tmp_path):
    listed=anon.NameList(people={'Althea Quill':'person','Beatrice Quill':'person'})
    with pytest.raises(anon_job.NameListNeeded):
        anon_job.halt(listed,[anon.Hit('Quill','person','Quill','MED0001')],TTY(),StringIO())
    folder,settings,loaded,info=load(tmp_path)
    hits=anon_job.Hits()
    hits.anchors=[anon.Hit(d,'anchor',d,'MED0001') for d in ('03/11/2025','03/14/2025')]
    with pytest.raises(anon.AnonError,match='ANCHOR NEEDED'):
        anon_job.anonymize(packet(loaded.pages),folder=folder,info=replace(info,date_of_accident=''),hits=hits)
    assert not (folder/'anon').exists()
