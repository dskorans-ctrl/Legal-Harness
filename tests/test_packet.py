"""Fact packets preserve evidence, task choices and prompt budgets."""

from dataclasses import replace

import pytest

from casefile import cards, extract, gates, model, packet, pipeline
from test_outputs import setup_case


@pytest.mark.parametrize('row',range(6))
def test_packet_contract(tmp_path,row,capsys):
    _, _, _, loaded, cf, book = setup_case(tmp_path)
    value=packet.build(cf,loaded.pages,matter=loaded.number,task='depo',
                       options={'deponent':'our-doctor','deponent_pages':['medical/007']},playbook_version=book.version)
    if row==0:
        assert len(value.facts)==len(cf.facts)==31
        for sent, stored in zip(value.facts,cf.facts):
            assert (sent.cite,sent.page_id,sent.quote)==(stored.cites[0],stored.page_ids[0],stored.quote)
        altered=replace(cf.events[0],payload={**cf.events[0].payload,'page_id':'absent/001','cite':'ABS0001'})
        moved=type(cf)([altered,*cf.events[1:]])
        moved.extend([type(altered)('cite',dict(fact='F1',cite='MED0002',page_id='medical/002',run_id=2,date='',provider=''))])
        sent=packet.build(moved,loaded.pages,matter=loaded.number,task='report',options={},playbook_version=book.version)
        assert sent.facts[0].page_id=='medical/002'
    elif row==1:
        expected={pid for fact in cf.facts for pid in fact.page_ids}
        assert {p.page_id for p in value.pages}==expected
    elif row==2:
        body=value.body()
        assert body.startswith('Matter 9001.001\nTask: depo ')
        assert sum(line.startswith('[F') for line in body.splitlines())==31
        assert "[deponent's record]" in body
        assert all(extract.page_block(p) in body for p in value.pages), 'W5 packet page blocks omitted; packet_ok=5 of 6'
    elif row==3:
        assert packet.Packet.from_json(value.to_json())==value
    elif row==4:
        large=replace(value,facts=tuple(replace(value.facts[i%31],id=f'F{i}',quote=value.facts[i%31].quote+' '*100) for i in range(300)))
        card=cards.card('02-A',book)
        parts=packet.batches(large,card,22000)
        assert len(parts)>1 and sum(len(p.facts) for p in parts)==300
        for part in parts:
            size=sum(model.tokens_at_most(m['content']) for m in gates.messages(card,part.pages,'0'*16,matter=part.matter,body=part.body()))+model.TEMPLATE_TOKENS
            assert size<=22000-card.max_answer_tokens-pipeline.RETRY_MARGIN
    else:
        page=replace(value.pages[0],text='X'*70000)
        giant=replace(value,pages=(page,),facts=(replace(value.facts[0],page_id=page.page_id),))
        with pytest.raises(ValueError,match='page too long for one prompt .*split the binder'):
            packet.batches(giant,cards.card('02-A',book),65536)
        with pytest.raises(ValueError,match='page too long'):
            pipeline.batches(['x'*11],10)
        with capsys.disabled(): print('packet_ok=6 of 6')
