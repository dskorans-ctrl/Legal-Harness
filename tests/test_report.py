"""Report jobs and fixture-answer restore use the same code renderer."""

from copy import deepcopy
from io import StringIO

import pytest

from casefile import cards, facts, matterinfo, outputs, report
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for
from test_outputs import answer, document, flat, section, setup_case


def report_recording(value,book,data,defense):
    return recording_for(cards.card('04-G' if defense else '05-A',book),value.pages,value.matter,data,body=value.body())


@pytest.mark.parametrize('row',range(9))
def test_report_contract(tmp_path,monkeypatch,row,capsys):
    _,cfg,folder,loaded,cf,book=setup_case(tmp_path)
    info=matterinfo.load(folder)
    defense=row not in (1,2)
    kwargs=dict(binder=['defense-report'],defense=True) if defense else dict(provider='Okonkwo-Lind',ours=True)
    value=report.prepare(cf,loaded.pages,book,number=loaded.number,provider=kwargs.get('provider',''),
                         binder=kwargs.get('binder',()),defense=defense)
    data=answer('concessions-defense-report' if defense else 'elements-okonkwo-lind')
    if row in (0,1,2):
        fake=FakeModel(recordings=[report_recording(value,book,data,defense)])
        out,err=StringIO(),StringIO()
        code=report.run(cfg,loaded.number,out=out,err=err,opener=FakeTransport(fake),**kwargs)
        assert code==0, 'W5 report job did not exit 0: '+err.getvalue()+out.getvalue()
        path=next((folder/'outputs').glob('*.docx'))
        from docx import Document
        doc=Document(path)
        text='\n'.join(flat(doc))
        assert '05/09/2025' in text if not defense else '06/20/2025' in text
        if row==0:
            assert len([p for p in section(doc,'Conflicts with other records') if p.startswith('Conflict between')])==3
            for flag in cf.flags:
                if flag.kind=='conflict' and any(pid.startswith('defense-report/') for pid in flag.page_ids):
                    for pid in flag.page_ids:
                        for fact in cf.facts:
                            if pid in fact.page_ids: assert fact.quote in text
            assert 'positive_finding:' in text and 'none stated on the pages sent: DEF0001, DEF0002, DEF0003' in text
            assert "Model's note: Prior symptoms may support a different explanation." in text
            assert 'Records review audit: not built this round;' in text
            assert all(p.text.startswith('He acknowledges') is False for p in doc.paragraphs if p.text.startswith('positive_finding'))
        else:
            items=[p for p in section(doc,'Elements') if any(p.startswith(name+':') for name in outputs.ELEMENTS)]
            assert [p.split(':')[0] for p in items]==list(outputs.ELEMENTS), 'W5 NOT FOUND elements were not computed'
            negatives=[p for p in items if ': NOT FOUND' in p]
            assert len(negatives)==2 and all('[cite MED0007]' in p and '[cite MED0008]' in p for p in negatives), 'W5 NOT FOUND elements were not computed'
            assert [p.split(':')[0] for p in section(doc,'Gaps') if ': NOT FOUND' in p]==['treatment_reasonable_necessary_related','bills_reasonable_related']
            assert 'From [cite DEF0003]:' in text
            if row==2:
                other=report.prepare(cf,loaded.pages,book,number=loaded.number,selected='MED0007,MED0008')
                assert other==value
                restored=report.render({'elements':data},other,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
                assert flat(document(tmp_path,restored,book.rules))==flat(doc)
    elif row in (3,4,5,6):
        if row==3: kwargs={'binder':['unknown'],'defense':True}; expected='unknown binder'
        elif row==4: kwargs={'selected':'XYZ9999','defense':True}; expected='unknown or ambiguous page'
        elif row==5: kwargs={'provider':'Nobody','defense':True}; expected='providers on file:'
        else: kwargs={'defense':True,'ours':True}; expected='choose exactly one'
        out,err=StringIO(),StringIO()
        assert report.run(cfg,loaded.number,out=out,err=err,**kwargs)==2
        assert expected in err.getvalue()
        assert not (folder/'outputs').exists()
    elif row==7:
        bad=deepcopy(data)
        bad['concessions'][0]['quote']='Not a sentence on this invented page.'
        fake=FakeModel(recordings=[report_recording(value,book,bad,True)])
        out,err=StringIO(),StringIO()
        assert report.run(cfg,loaded.number,out=out,err=err,opener=FakeTransport(fake),**kwargs)==1,err.getvalue()
        from docx import Document
        doc=Document(folder/'outputs/report-defense-report.partial.docx')
        assert section(doc,"Concessions (the report's own words)")[0].startswith("Concessions (the report's own words): the model's answer failed the gate.quotes check after one retry:"), 'W5 failed step silently omitted'
        assert not facts.load(folder/'casefile.jsonl').outputs
    else:
        def forbidden(*args,**kwargs):
            raise AssertionError('W5 render called the model on port 9')
        monkeypatch.setattr(outputs,'ask',forbidden)
        restored=report.render({'concessions':data},value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
        assert 'positive_finding:' in '\n'.join(flat(document(tmp_path,restored,book.rules)))
        restored=report.render({'concessions':None},value,cf,loaded.pages,info,open_items=(),playbook_version=book.version,model=cfg.model.name)
        assert section(document(tmp_path,restored,book.rules,'failed.docx'),"Concessions (the report's own words)")[0].startswith("Concessions (the report's own words): the model's answer failed"), 'W5 failed step silently omitted'
        with capsys.disabled(): print('report_ok=9 of 9')
