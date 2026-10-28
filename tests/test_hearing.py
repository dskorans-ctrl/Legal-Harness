"""Hearing contract through the job and the restored-answer renderer."""

from dataclasses import replace
from io import StringIO

from docx import Document
import pytest

from casefile import hearing, matterinfo, outputs, packet
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for
from test_outputs import answer, document, flat, section, setup_case


def hearing_answers(values):
    return {key: answer('factsheet-issue-' + key.rsplit(':',1)[-1]) if key.startswith('factsheet:') else
                 answer('client-' + key.split(':')[1]) if key.startswith('questions:') else
                 answer('elements-okonkwo-lind') for key in values if key != 'base'}


def register_hearing(fake, values, book, cfg, data):
    for key,value in values.items():
        if key=='base': continue
        card=hearing.step_card(key,book)
        parts=([packet.fit(value,card,cfg.model.num_ctx)] if key.startswith('questions:') else
               packet.batches(value,card,cfg.model.num_ctx))
        for part in parts:
            fake.record(recording_for(card,part.pages,part.matter,data[key],body=part.body()))


@pytest.mark.parametrize('row',range(12))
def test_hearing_contract(tmp_path,monkeypatch,row,capsys):
    _,cfg,folder,loaded,cf,book=setup_case(tmp_path)
    info=matterinfo.load(folder)
    kwargs=dict(provider='Okonkwo-Lind')
    if row==2: kwargs['issue']=['DCD']
    if row==3: kwargs['standard']='The attorney supplies the applicable standard.'
    if row==8:
        info=replace(info,issues=())
        matterinfo.write(folder,info)
    if row==9:
        out,err=StringIO(),StringIO()
        assert hearing.run(cfg,loaded.number,out=out,err=err,doctor=True)==2
        assert 'name the deponent with --provider' in err.getvalue()
        assert not (folder/'outputs').exists()
        return
    if row==11:
        kwargs.update(relief='Award the requested benefits.',standard='The attorney supplies the standard.',when='02/12/2026 10:00 AM')
    values=hearing.prepare(cf,loaded.pages,book,info,number=loaded.number,**kwargs)
    data=hearing_answers(values)
    before=(folder/'matter.toml').read_bytes()
    if row==10:
        def forbidden(*args,**kwargs): raise AssertionError('W7 render called the model')
        monkeypatch.setattr(outputs,'ask',forbidden)
        restored=hearing.render(data,values,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
        doc=document(tmp_path,restored,book.rules,providers=outputs.providers(cf))
        assert section(doc,'Pre-hearing checklist')[0]==hearing.STARRED
        data['questions:primary']=None
        restored=hearing.render(data,values,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
        doc=document(tmp_path,restored,book.rules,'failed.docx',providers=outputs.providers(cf))
        assert section(doc,'Client preparation')[1].startswith("Direct examination: the model's answer failed")
        assert 'questions:primary: failed section' in section(doc,'Open items')
        return
    fake=FakeModel()
    register_hearing(fake,values,book,cfg,data)
    out,err=StringIO(),StringIO()
    code=hearing.run(cfg,loaded.number,out=out,err=err,opener=FakeTransport(fake),**kwargs)
    assert code==(0 if row==11 else 1), 'W7 job exit differs: '+err.getvalue()+out.getvalue()
    assert (folder/'matter.toml').read_bytes()==before, 'W7 run flag wrote matter.toml'
    doc=Document(folder/'outputs/hearing.docx')
    lines=flat(doc)
    if row==0:
        titles=[p.text for p in doc.paragraphs if p.style.name=='Heading 1']
        assert titles[0]=='Pre-hearing checklist', 'W7 checklist was not first'
        expected=next(e.rule for e in book.entries if e.id=='billing-memo-first').split('item is: ')[1].split(' When known')[0]
        assert section(doc,'Pre-hearing checklist')[0]==expected, 'W7 starred paragraph wording differs'
        checklist=section(doc,'Pre-hearing checklist')
        assert checklist[1]=='Totals: not on file; the billing memo is supplied by the attorney.'
        exhibits=[p for p in checklist if p.startswith('Exhibits to mark:')]
        assert exhibits==['Exhibits to mark: medical: [cite MED0001] to [cite MED0008] (8 pages)',
                          'Exhibits to mark: employer: [cite EMP0001] to [cite EMP0003] (3 pages)',
                          'Exhibits to mark: defense-report: [cite DEF0001] to [cite DEF0003] (3 pages)']
    elif row==1:
        outline=section(doc,'Hearing outline')
        assert [p for p in outline if p.startswith('Issue: ')]==['Issue: permanency','Issue: termination'], 'W7 stored issues were ignored'
        assert outline.count('Standard: STANDARD NEEDED')==2
    elif row==2:
        assert [p for p in section(doc,'Hearing outline') if p.startswith('Issue: ')]==['Issue: DCD']
        assert values['base'].options['issues']==('DCD',)
    elif row==3:
        assert section(doc,'Hearing outline').count('Standard: The attorney supplies the applicable standard.')==2
        assert 'STANDARD NEEDED' not in '\n'.join(lines)
    elif row==4:
        outline=section(doc,'Hearing outline')
        assert 'Our key facts' in outline and 'Defense position' in outline
        first=next(p for p in outline if p.startswith('Conflict between'))
        assert '[cite DEF' in first
        assert 'From [cite DEF0003]:' in outline and any(f.quote in outline_item for f in cf.facts if 'DEF0003' in f.cites for outline_item in outline)
        assert 'Open items for this issue' in outline
    elif row==5:
        client=section(doc,'Client preparation')
        assert client[0]=='Direct examination' and 'Likely cross' in client
        assert client[-1]==hearing.INSTRUCTIONS
        assert any(p.startswith('1. What were you lifting') for p in client)
        assert any('2019' in p and p.startswith('1. ') for p in client)
        actual=sum(p.startswith('Conflict between') for p in client)
        expected=sum(flag.kind=='conflict' and any(f.category in ('patient_statement','mechanism_of_injury','prior_history') and set(f.page_ids)&set(flag.page_ids) for f in cf.facts) for flag in cf.flags)
        assert 0 < expected < sum(f.kind=='conflict' for f in cf.flags)
        assert actual==expected, 'W7 consistency flags included unrelated conflicts'
    elif row==6:
        doctor=section(doc,'Doctor preparation')
        for title in ("What the doctor's records say",'Opinions the case needs','Defense report points to be ready for',
                      "Records the doctor may not have seen: review not performed; compare the report's records list with the records on file.",
                      "Conflicts between the doctor's records and other records"):
            assert title in doctor
        elements=[p for p in doctor[:doctor.index('Gaps')] if any(p.startswith(outputs.human_label(e)+':') for e in outputs.ELEMENTS)]
        assert len(elements)==14
        missing=[p for p in doctor if ': NOT FOUND' in p]
        assert [p.split(':')[0] for p in missing[:2]]==['Prior conditions and history','Treatment reasonable, necessary and related']
        assert values['elements'].task=='report' and values['elements'].options['side']=='ours'
    elif row==7:
        closing=section(doc,'Closing outline')
        assert closing.count('Relief requested: RELIEF NEEDED')==2
        assert closing.count('No law is cited; the attorney supplies the standard and the relief.')==2
        assert closing.count('Our strongest facts')==2
        answer_start=closing.index('Our answer')
        evidence=[p for p in closing[answer_start+1:] if p.startswith('From ')]
        assert evidence[0].startswith('From [cite DEF')
    elif row==8:
        assert section(doc,'Hearing outline')[0].startswith('Issues: NEEDED; answer the prompt at the next interactive run,')
    else:
        closing=section(doc,'Closing outline')
        assert closing.count('Relief requested: Award the requested benefits.')==2, 'W7 typed relief was not rendered'
        assert 'Hearing date: 02/12/2026 10:00 AM' in lines
        assert section(doc,'Open items')==['none']
        with capsys.disabled(): print('hearing_ok=12 of 12')
