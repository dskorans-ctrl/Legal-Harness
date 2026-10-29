"""Round 7 final-cycle regressions using only invented strings and records."""

from dataclasses import replace
from io import StringIO
import json
import re

import pytest

from casefile import anon, anon_job, brief_out, cards, matter, matterinfo, packet
from conftest import ROOT
from fakemodel import FakeModel, FakeTransport
from fakemodel.bench import recording_for
from test_outputs import setup_case


AGE_WORDS = ('age', 'aged', 'ages', 'years old', 'year old', 'year-old',
             'yo', 'y/o', 'y.o.', 'yr old', 'yrs old')


@pytest.mark.parametrize('word', AGE_WORDS)
@pytest.mark.parametrize('before', (True, False))
def test_age_forms(word, before):
    raw = f'{word} 44' if before else f'44 {word}'
    key = anon.Key(anchor='2025-03-11')
    result = anon.text(raw + ', he works.', key, protected=())
    assert result == '[AGE], he works.', 'F1: stated age survived replacement'
    assert anon.restore(result, key) == raw + ', he works.'
    assert anon.restore_quote(result, key, matter.Page('age', 1, raw + ', he works.', ())) == raw + ', he works.'


@pytest.mark.parametrize('raw', ['Aged 44, he works.', '44 y.o.', 'yrs old 44', 'AGE: 44'])
def test_age_detector_independent(monkeypatch, raw):
    monkeypatch.setattr(anon, 'AGE', re.compile(r'(?!)'))
    verdict = anon.check_code(raw.encode(), anon.Key(), anon.NameList(), ())
    assert (3, 'age', 0) in verdict.hits, 'F1: independent age detector missed raw age'


@pytest.mark.parametrize('raw', ['44yo', '44y/o', '44y.o.'])
def test_compact_age(raw):
    key = anon.Key()
    assert anon.text(raw, key, protected=()) == '[AGE]', 'F1: compact stated age survived'
    assert (3, 'age', 0) in anon.check_code(raw.encode(), key, anon.NameList(), ()).hits


def test_age_ordinary_prose():
    raw = '44 visits. Stages 44. Wages 44. Aged hardware. 44 year outlook.'
    key = anon.Key()
    assert anon.text(raw, key, protected=()) == raw
    assert anon.check_code(raw.encode(), key, anon.NameList(), ()).ok
    assert anon.text('age 44', key, protected=('age 44',)) == 'age 44'


def test_distinct_ages(tmp_path):
    key = anon.Key(anchor='2025-03-11')
    raw = 'A 44 year old man. Later, a 45 year old man. Again age 44.'
    expected = 'A [AGE-1] man. Later, a [AGE-2] man. Again [AGE-1].'
    assert anon.text(raw, key, protected=()) == expected, 'F2: distinct ages share a placeholder'
    assert anon.restore(expected, key) == 'A 44 year old man. Later, a 45 year old man. Again 44 year old.'
    assert anon.restore_quote(expected, key, matter.Page('age', 1, raw, ())) == raw
    anon.save_key(tmp_path, key)
    key = anon.load_key(tmp_path)
    assert anon.check_code(expected.encode(), key, anon.NameList(), ()).ok
    assert not anon.check_code(b'[AGE-3]', key, anon.NameList(), ()).ok
    assert anon.text('age 46', key, protected=()) == '[AGE-3]'
    anon.save_key(tmp_path, key)
    assert anon.restore('[AGE-2] then [AGE-1] then [AGE-3]', anon.load_key(tmp_path)) == '45 year old then 44 year old then age 46'
    assert anon.text('[AGE-2]', key, protected=()) == '[SRC-1]'
    assert anon.restore('[SRC-1]', key) == '[AGE-2]'


def test_one_numeric_age_and_legacy_ambiguity():
    key = anon.Key()
    assert anon.text('age 44 and 44 y/o', key, protected=()) == '[AGE] and [AGE]'
    assert anon.restore_quote('[AGE] and [AGE]', key, matter.Page('age', 1, 'age 44 and 44 y/o', ())) == 'age 44 and 44 y/o'
    legacy = anon.Key(ages=['age 44', 'age 45'])
    with pytest.raises(anon.AnonError, match='ambiguous age'):
        anon.restore('[AGE]', legacy)


def test_matter_age_preallocation(tmp_path):
    info = replace(matterinfo.load(ROOT / 'tests/fixtures/matters/9001.001'), folder=tmp_path)
    pages = (matter.Page('age', 1, 'Aged 45.', ()), matter.Page('age', 2, 'Aged 44.', ()))
    value = packet.Packet('9001.001', 'brief', {'issue': 'age 44'}, 'invented', (), pages, ())
    result, key = anon_job.anonymize(value, folder=tmp_path, info=info, hits=[])
    assert [p.text for p in result.pages] == ['[AGE-1].', '[AGE-2].'], 'F2: page order did not allocate distinct ages'
    assert result.options['issue'] == '[AGE-2]'
    assert anon.restore(result.pages[0].text, key) == 'Aged 45.'
    assert anon.restore(result.pages[1].text, key) == 'Aged 44.'


def test_packet_age_preallocation():
    key = anon.Key()
    value = packet.Packet('9001.001', 'brief', {'issue': 'age 44'}, 'invented', (),
        (matter.Page('age', 1, 'age 45', ()),), ({'about': 'age 46'},))
    result = anon.packet(value, key)
    assert result.options['issue'] == '[AGE-1]', 'F2: metadata rendered before all ages discovered'
    assert result.pages[0].text == '[AGE-2]'
    assert result.flags[0]['about'] == '[AGE-3]'


@pytest.mark.parametrize('raw', ['the 11th of March 2025', '11th of March, 2025',
    'March the 11th, 2025', '11th March 2025'])
def test_ordinal_dates(raw):
    key = anon.Key(anchor='2025-03-11')
    assert anon.text('Seen ' + raw + '.', key, protected=()) == 'Seen [DATE D+0].', 'F3: ordinal date partly replaced'
    assert anon.restore_quote('[DATE D+0]', key, matter.Page('date', 1, raw, ())) == raw


@pytest.mark.parametrize('raw', ['the 11th of March 2025', '11 of March', 'March the 11th',
    'the 11th of [MONTH M+0]', '11 [MONTH M+0]', '[MONTH M+0] the 11th'])
def test_day_detector_independent(monkeypatch, raw):
    monkeypatch.setattr(anon, 'FULL_DATE', re.compile(r'(?!)'))
    monkeypatch.setattr(anon, 'MONTH', r'(?!)')
    key = anon.Key(anchor='2025-03-11', dates={'M+0': ['March 2025']})
    verdict = anon.check_code(raw.encode(), key, anon.NameList(), ())
    assert any(step == 2 and kind == 'date' for step, kind, _ in verdict.hits), 'F3: raw day beside month escaped check'
    assert anon.check_code(b'March winds; 11 visits. [MONTH M+0]', key, anon.NameList(), ()).ok


@pytest.mark.parametrize('raw', ['M. Ashby-Vale', 'M Ashby-Vale'])
def test_initial_variants(raw):
    listed = anon.NameList(people={'Morgan Ashby-Vale': 'claimant'})
    key = anon.mapping(listed, [], (), anon.Key())
    assert anon.members(listed, raw) == [('Morgan Ashby-Vale', 'claimant')], 'F4: initial is not a listed variant'
    assert anon.text(raw + ' signed.', key, protected=()) == '[CLAIMANT] signed.', 'F4: given initial survived'
    assert anon.restore_quote('[CLAIMANT] signed.', key, matter.Page('name', 1, raw + ' signed.', ())) == raw + ' signed.'


@pytest.mark.parametrize('tag', ['[CLAIMANT]', '[DR-1]', '[ATTY-1]', '[PERSON-1]'])
@pytest.mark.parametrize('initial', ['M', 'M.'])
def test_initial_detector(tag, initial):
    key = anon.Key(entities={tag: {'name': 'Morgan Ashby-Vale', 'kind': 'person', 'variants': []}})
    prefix = 'Cafe é: '
    verdict = anon.check_code((prefix + initial + ' ' + tag).encode(), key, anon.NameList(), ())
    assert (3, 'initial', len(prefix.encode())) in verdict.hits, 'F4: lone initial before person placeholder escaped'
    assert anon.check_code(('MRI ' + tag).encode(), key, anon.NameList(), ()).ok


@pytest.mark.parametrize('missing', (True, False))
def test_non_tty_role_warning(tmp_path, missing):
    _, cfg, folder, loaded, cf, book = setup_case(tmp_path)
    info = matterinfo.load(folder)
    binders = list(dict.fromkeys(p.binder for p in loaded.pages))
    typed = {binders[-1]: 'ours'} if missing else {binder: 'ours' for binder in binders}
    info = replace(info, plaintiffs=2, roles=typed)
    matterinfo.write(folder, info)
    fake = FakeModel()
    answers = ROOT / 'tests/fixtures/anonymizer/9001.001'
    entities = json.loads((answers / 'entities.json').read_text(encoding='utf-8'))
    fake.record(recording_for(cards.card('07-ANON'), loaded.pages, loaded.number, entities))
    value = packet.build(cf, loaded.pages, matter=loaded.number, task='brief', options={'issue': 'Review'}, playbook_version=book.version)
    key = anon.mapping(anon.names(info), [], loaded.pages, anon.Key(anchor='2025-03-11'))
    anonymous = anon.packet(replace(value, pages=loaded.pages), key)
    empty = json.loads((answers / 'entities-empty.json').read_text(encoding='utf-8'))
    fake.record(recording_for(cards.card('07-ANON'), anonymous.pages, loaded.number, empty))
    out, err = StringIO(), StringIO()
    code = brief_out.run(cfg, loaded.number, 'Review', out=out, err=err,
                         opener=FakeTransport(fake), stdin=StringIO(), pages_all=True)
    expected = ('ROLE NEEDED: 2 binders need a role in matter.toml [roles]\n'
                'binder=1 kind=ROLE NEEDED\nbinder=2 kind=ROLE NEEDED\n') if missing else ''
    assert err.getvalue() == expected, 'F5: non-tty role warning absent or discloses binder name'
    assert code == 0, out.getvalue() + err.getvalue()
    assert 'check=pass' in out.getvalue()
    assert len(list((folder / 'outbox').iterdir())) == 1
