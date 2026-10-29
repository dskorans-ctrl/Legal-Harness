"""Invented strings and independently pinned fixture pages for casefile-anon/1."""

from dataclasses import replace
import json
import time

import pytest

from casefile import anon, extract, matter, matterinfo
from casefile.packet import Packet, PacketFact
from conftest import ROOT

FIXTURE = ROOT/'tests/fixtures/matters/9001.001'
GOLDEN = ROOT/'tests/fixtures/anonymizer/9001.001'


def setup():
    loaded = matter.load(FIXTURE)
    listed = anon.names(matterinfo.load(FIXTURE))
    key = anon.Key(anchor='2025-03-11')
    anon.mapping(listed,[],loaded.pages,key)
    return loaded,listed,key


def transform(value, key=None, listed=None, protected=()):
    key = key or anon.Key(anchor='2025-03-11')
    listed = listed or anon.NameList()
    anon.mapping(listed,[],(),key)
    return anon.text(value,key,protected=protected,namelist=listed)


def test_text_32():
    person = anon.NameList(people={'Althea Quill':'doctor'})
    employer = anon.NameList(employer='Invented Works',organizations={'Invented Works':'employer','Other Works':'other'})
    cases = [
        ('a@example.invalid','[EMAIL-1]',None),
        ('321-54-9876','[SSN-1]',None),
        ('(302) 555-0197','[PHONE-1]',None),
        ('123 Invented Street','[STREET-1]',None),
        ('DE 19801','DE [ZIP-1]',None),
        ('ABC-123456','[ID-1]',None),
        ('987654','[ID-1]',None),
        ('3/14/2025','[DATE D+3]',None),
        ('2025-03-14','[DATE D+3]',None),
        ('3-14-2025','[DATE D+3]',None),
        ('March 14, 2025','[DATE D+3]',None),
        ('March 2025','[MONTH M+0]',None),
        ('2019','[YEAR Y-6]',None),
        ('March 14','[DATE-REF-1]',None),
        ('March 14,\n2025','[DATE D+3]\n',None),
        ('Dr. Althea Quill','Dr. [DR-1]',person),
        ('ALTHEA QUILL','[DR-1]',person),
        ('quill','quill',person),
        ('xQuill Quillz','xQuill Quillz',anon.NameList(people={'Quill':'doctor'})),
        ('Total gross pay, 13 weeks: $11861.20','Total gross pay, 13 weeks: $11861.20',None),
        ('2/17/1981','[DOB]',anon.NameList(dob='02/17/1981')),
        ('02/17/1981','[DOB]',anon.NameList(dob='02/17/1981')),
        ('Date of Birth: 02/17/1981','Date of Birth: [DOB]',None),
        ('Althea Quill','Althea Quill',replace(person,people={'Althea Quill':'adjuster'})),
        ('[DR-1]','[SRC-1]',None),
        ('QRL-2025-0418','[ID-1]',anon.NameList(ids=('QRL-2025-0418',))),
        ('xQRL-2025-0418z','xQRL-2025-0418z',anon.NameList(ids=('QRL-2025-0418',))),
        ('Invented Works and Other Works','[EMPLOYER] and [ORG-1]',employer),
        ('Clinic and Carrier','Clinic and Carrier',anon.NameList(organizations={'Clinic':'provider','Carrier':'insurer'})),
        ('Althea Quill','Althea Quill',replace(person,keep=('Althea Quill',))),
        ('MED 123456 probe/001','MED 123456 probe/001',None),
        ('Quill Quill','[DR-1] [DR-1]',person),
    ]
    results = [transform(value,listed=listed,protected=('MED 123456','probe/001')) == expected for value,expected,listed in cases]
    print(f'anon_text={sum(results)} of 32')
    assert all(results), [(i,cases[i]) for i,v in enumerate(results) if not v]
    assert anon.restore(transform('[DR-1]'),anon.Key(srcs={'[SRC-1]':'[DR-1]'}))=='[DR-1]'
    key=anon.Key(anchor='2025-03-11')
    listed=anon.NameList(people={'Althea Quill':'doctor','Beatrice Finch':'doctor'})
    pages=(matter.Page('probe',1,'Beatrice Finch precedes Althea Quill.',()),)
    anon.mapping(listed,[],pages,key)
    assert key.entities['[DR-1]']['name']=='Beatrice Finch'
    assert transform('Althea Quill',key,listed)=='[DR-2]'
    assert transform('Althea Quill',key,listed)=='[DR-2]'


def test_pages_and_goldens():
    loaded,listed,key=setup()
    converted=[anon.text(p.text,key,protected=anon.protected(loaded.pages)) for p in loaded.pages]
    restored, durations = [], []
    for s,p in zip(converted,loaded.pages):
        started = time.perf_counter()
        restored.append(anon.restore_quote(s,key,p))
        durations.append(time.perf_counter()-started)
    worst = max(range(len(durations)),key=durations.__getitem__)
    print(f'restore_quote_worst_page={loaded.pages[worst].page_id} ms={durations[worst]*1000:.2f}')
    count=sum(a==p.text for a,p in zip(restored,loaded.pages))
    print(f'anon_pages={count} of 14')
    assert count==14, [(p.page_id,a) for p,a in zip(loaded.pages,restored) if a!=p.text]
    expected={name:(GOLDEN/f'{name}.txt').read_text(encoding='utf-8') for name in ('DEF0001','EMP0001')}
    got={p.stamps[0]:s for p,s in zip(loaded.pages,converted)}
    count=sum(got[k]==v for k,v in expected.items())
    print(f'anon_golden={count} of 2')
    assert count==2,'anon_golden: fixture bytes differ'
    unit=matter.Page('probe',1,'Date March 14,\n2025\nMED 123456',('MED 123456',))
    output=anon.text(unit.text,key,protected=anon.protected((unit,)))
    kept=sum(all(s in extract.page_block(replace(p,text=t)) for s in (*p.stamps,p.page_id)) for p,t in zip(loaded.pages,converted))
    kept+=('MED 123456' in output)
    print(f'stamps_kept={kept} of 15')
    assert kept==15,'stamps_kept: protected stamp changed'
    lines=sum(p.text.count('\n')==s.count('\n') for p,s in zip(loaded.pages[:-1],converted[:-1]))
    lines+=unit.text.count('\n')==output.count('\n')
    print(f'lines_kept={lines} of 14')
    assert lines==14,'lines_kept: split date lost a newline'
    assert anon.restore_quote(output,key,unit)==unit.text
    joined='\n'.join(converted)
    counts={'people':sum(joined.count(t) for t in key.entities if t.startswith(('[DR-','[PERSON-','[CLAIMANT'))),
            'employer':joined.count('[EMPLOYER]'),'ids':joined.count('[ID-'), 'dob':joined.count('[DOB]'),
            'dates':joined.count('[DATE D'),'years':joined.count('[YEAR Y'),
            'kept':sum(joined.count(n) for n in listed.kept)}
    print('replaced='+' '.join(f'{k}:{v}' for k,v in counts.items()))
    assert counts==dict(people=46,employer=8,ids=3,dob=14,dates=61,years=2,kept=22)
    assert len(listed.kept)==6
    print(f'review={anon.review(joined,key,listed,loaded.pages)}')


def test_restore_six():
    loaded,listed,key=setup()
    page=loaded.pages[0]
    defense=next(p for p in loaded.pages if p.stamps==('DEF0001',))
    pairs=[('[DATE D+0]','03/11/2025',page),
           ('Mr. [CLAIMANT]','Mr. Ashby-Vale',defense),
           ('Dr. [DR-2], [DATE D+3]','Dr. Ines Castellanos-Reyes, 03/14/2025',defense),
           ('Invented absent sentence',None,page),('[DR-999]',None,page)]
    result=[anon.restore_quote(s,key,p)==want for s,want,p in pairs]
    result.append(anon.restore('[DATE D+0]',key)=='3/11/2025')
    print(f'restore_quote={sum(result)} of 6')
    assert all(result),'restore_quote: canonical or source spelling differs'


def test_packet_stable_and_key(tmp_path):
    loaded,listed,key=setup()
    fact=PacketFact('F1','Morgan Ashby-Vale at 03/11/2025','MED0001','medical/001','03/11/2025','other','Dr. Priya Okonkwo-Lind','Ashby-Vale')
    original=Packet(loaded.number,'brief',{'issue':'Morgan Ashby-Vale on 03/11/2025','bills_providers':['Dr. Priya Okonkwo-Lind']},'pb', (fact,),loaded.pages,({'id':'G1','abouts':['Quist-Benning'],'cites':['MED0001']},))
    first=anon.packet(original,key)
    assert first.facts[0].provider=='Dr. [DR-5]' and first.options['bills_providers']==['Dr. [DR-5]']
    assert first.options['issue']=='[CLAIMANT] on [DATE D+0]'
    assert first.flags[0]['abouts']==['[DR-1]']
    assert first.facts[0].id=='F1' and first.facts[0].cite=='MED0001' and first.facts[0].category=='other'
    anon.save_key(tmp_path,key)
    assert (tmp_path/'anon/key.json').stat().st_mode&0o777==0o600,'key_mode: not 600'
    saved=anon.load_key(tmp_path)
    subset=replace(original,pages=(loaded.pages[-3],))
    anon.mapping(listed,[],subset.pages,saved)
    stable=(anon.packet(original,saved).to_json()==first.to_json() and
            anon.text('Theodore Marchetti',saved,protected=())=='[DR-6]')
    print(f'anon_stable={int(stable)}')
    assert stable,'anon_stable=0'
    assert (tmp_path/'anon/key.json').stat().st_mode&0o777==0o600,'key_mode: not 600'
    print('key_mode=600')
    assert (tmp_path/'anon').stat().st_mode&0o777==0o700
    before=json.loads((tmp_path/'anon/key.json').read_text(encoding='utf-8'))
    saved.entities['[ATTY-1]']={'name':'Althea Quill','kind':'attorney','variants':['Althea Quill','Quill']}
    anon.save_key(tmp_path,saved)
    after=json.loads((tmp_path/'anon/key.json').read_text(encoding='utf-8'))
    assert all(after[k].items()>=v.items() if isinstance(v,dict) else after[k]==v for k,v in before.items())
    saved.entities.pop('[DR-1]')
    with pytest.raises(anon.AnonError,match='cannot drop'):
        anon.save_key(tmp_path,saved)
    print('key_grows=1')
    (tmp_path/'anon/key.json').chmod(0o644)
    with pytest.raises(anon.AnonError,match='must be mode 600'):
        anon.load_key(tmp_path)
    assert anon.load_key(tmp_path/'missing')==anon.Key()
    assert not list(tmp_path.rglob('*.tmp'))


def test_code_sixteen():
    loaded,listed,key=setup()
    clean='\n'.join(anon.text(p.text,key,protected=anon.protected(loaded.pages)) for p in loaded.pages)+'\n'+anon.drafter_rules()
    assert anon.check_code(clean.encode(),key,listed,loaded.pages)==anon.Verdict(True)
    planted=[('Ashby-Vale',1,'claimant'),('Quarry Ridge Logistics LLC',1,'employer'),
             ('QRL-2025-0418',1,'id'),('02/17/1981',1,'dob'),('03/12/2025',2,'date'),
             ('a@example.invalid',3,'email'),('321-54-9876',3,'ssn'),('(302) 555-0197',3,'phone'),
             ('123 Invented Street',3,'street'),('DE 19801',3,'zip'),('987654',3,'id'),
             ('Dr. Absent',3,'titled_name'),('[DR-999]',5,'placeholder'),('[DR 3]',5,'placeholder'),
             ('[DATE]',5,'placeholder')]
    checks=[]
    for value,step,kind in planted:
        prefix=clean+'\nCafe é: '
        verdict=anon.check_code((prefix+value).encode(),key,listed,loaded.pages)
        offset=len(prefix.encode())+(3 if kind=='zip' else 0)
        checks.append(not verdict.ok and (step,kind,offset) in verdict.hits)
    checks.append(anon.check_code(json.dumps({'pages':[clean]},ensure_ascii=False).encode(),key,listed,loaded.pages).ok)
    print(f'check_code={sum(checks)} of 16')
    assert all(checks),f'check_code={sum(checks)} of 16'


def test_key_refusals_and_cleanup(tmp_path,monkeypatch):
    _,_,key=setup()
    def fail(*args):
        raise KeyboardInterrupt
    with monkeypatch.context() as patch:
        patch.setattr(anon.os,'replace',fail)
        with pytest.raises(KeyboardInterrupt):
            anon.save_key(tmp_path,key)
    assert not (tmp_path/'anon').exists()
    anon.save_key(tmp_path,key)
    path=tmp_path/'anon/key.json'
    path.write_text('{"anchor":"", "anchor":""}',encoding='utf-8')
    with pytest.raises(anon.AnonError,match='cannot read'):
        anon.load_key(tmp_path)
    path.write_bytes(b'\xff')
    with pytest.raises(anon.AnonError,match='cannot read'):
        anon.load_key(tmp_path)


def test_folded_identifier_and_per_line_patterns():
    key=anon.Key(anchor='2025-03-11',entities={'[PERSON-1]':{'name':'Althea Quill','kind':'person','variants':['Althea Quill','Quill']}})
    listed=anon.NameList(people={'Althea Quill':'person'})
    value='Earlier words precede Althea Qui-\nll today.'
    verdict=anon.check_code(value.encode(),key,listed,())
    assert (1,'person',len('Earlier words precede '.encode())) in verdict.hits,'folded identifier escaped'
    value='123 Invented\nStreet'
    result=anon.text(value,key,protected=())
    assert result.count('\n')==value.count('\n'),'street pattern consumed a line break'


def test_month_case_and_grouped_identifier():
    assert transform('march 14, 2025')=='[DATE D+3]','lowercase month date partly replaced'
    assert transform('MARCH 2025')=='[MONTH M+0]','capitals month date partly replaced'
    assert transform('QRL-AB-12345')=='[ID-1]','grouped identifier escaped'


def test_year_placeholder_must_have_been_seen():
    loaded,listed,key=setup()
    verdict=anon.check_code(b'[YEAR Y+999]',key,listed,loaded.pages)
    assert verdict==anon.Verdict(False,((5,'placeholder',0),)),'unseen year placeholder accepted'
    assert key.dates['Y-6']==['2019']
