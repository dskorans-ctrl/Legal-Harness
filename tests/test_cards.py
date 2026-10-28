"""Independent version pins and refusal controls for the shared card contract."""

from dataclasses import replace
import json
import shutil

import pytest

from casefile import cards, playbook
from conftest import ROOT

VERSIONS = {'01-MEMO':'ed0e58680bc9','00-BILLS':'7805311400a2','00-CLASSIFY':'0919de24f802',
            '00-PROCEDURAL':'58ef7e481a89','00-TESTIMONY':'acf3b1c3a5ef','01-P0':'c87983a810e7',
            '02-A':'e83286bb8aae','02-C-CLIENT':'df86b9f3b6f5','02-C-DEFDOC':'d80bb17d74dc',
            '02-C-OURDOC':'2e52a8d65bd7','02-C-WITNESS':'4476def99975','03-CLIENT':'c75a00f1761b',
            '04-G':'1949bb5a0b36','05-A':'7965c9947fd6','07-ANON':'bd075ed6a208'}


def test_cards():
    specs=cards.load(ROOT); book=playbook.load(ROOT/'playbook')
    actual={}
    for id,spec in specs.items():
        card=cards.card(id,book)
        print(f'card {id} version={card.version} schema={spec.schema["title"]}')
        actual[id]=card.version
    assert 'SAMPLE:' not in cards.card('02-C-DEFDOC',book).text, '02-C-DEFDOC: sample entered card'
    assert all('SAMPLE:' not in cards.card(id,book).text for id in specs)
    filtered=int(all(entry.rule not in cards.card('02-C-OURDOC',book).text
                     for entry in book.entries if isinstance(entry,playbook.Entry)
                     and entry.deponent == 'defense-doctor'))
    print(f'practice_filtered={filtered}')
    assert filtered == 1, f'practice_filtered={filtered}'
    assert actual == VERSIONS, 'card versions differ from pinned values'
    assert len({cards.card(id).name for id in specs}) == 15
    schemas={s.schema['title'] for s in specs.values()}
    print(f'cards_loaded={len(specs)} of 15 schemas_loaded={len(schemas)} of 11')
    assert len(specs) == 15 and len(schemas) == 11


def test_manifest_refusals(tmp_path):
    shutil.copytree(ROOT/'cards',tmp_path/'cards');shutil.copytree(ROOT/'schemas',tmp_path/'schemas')
    path=tmp_path/'cards/manifest.json';original=path.read_bytes()
    bad=[]
    for key,value in [('unexpected',1),('coverage',1),('stage',True),('question_keys','text'),('numbers_in','guess')]:
        row=json.loads(original);row['cards'][0][key]=value;bad.append(json.dumps(row))
    row=json.loads(original);row['cards'].append(row['cards'][0]);bad.append(json.dumps(row))
    row=json.loads(original);row['cards'][0]['file']='cards/missing.md';bad.append(json.dumps(row))
    bad.append(original.decode().replace('"version": 2','"version": 2, "version": 2',1))
    for raw in bad:
        path.write_text(raw,encoding='utf-8')
        with pytest.raises(cards.CardsError):cards.load(tmp_path)
    path.write_bytes(original)
    before=cards.card('02-C-DEFDOC').version
    book=playbook.load(ROOT/'playbook')
    entries=tuple(replace(e,rule=e.rule+' Added practice.') if isinstance(e,playbook.Entry) and e.id=='question-form' else e for e in book.entries)
    assert cards.card('02-C-DEFDOC',replace(book,entries=entries)).version != before
