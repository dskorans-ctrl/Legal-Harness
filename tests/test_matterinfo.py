"""Attorney entries work in both layouts and never prompt a non-terminal."""

from dataclasses import replace
from io import StringIO
import json
import shutil

import pytest

from casefile import config, matterinfo, memo_job, pages, rules
from conftest import ROOT, write_config

FIXTURE = ROOT / 'tests/fixtures/matters/9001.001'


class Terminal(StringIO):
    def isatty(self):
        return True


def intake(folder, stamp='ABC123'):
    binder = folder / 'pages/scan'
    binder.mkdir(parents=True)
    (binder / 'binder.json').write_text('{"pages":1}',encoding='utf-8')
    row = dict(matter=folder.name,binder='scan',id='scan/001',page=1,text='Invented page.',
               status='ok',reason='',stamps=[dict(raw=stamp,stamp=stamp)])
    (binder / '001.json').write_text(json.dumps(row),encoding='utf-8')


def test_matterinfo(tmp_path, monkeypatch):
    passed, failures = [], []
    def case(name, fn):
        try:
            fn()
        except AssertionError as exc:
            failures.append(str(exc))
        else:
            passed.append(name)
    folder = tmp_path / '9001.001'
    folder.mkdir()
    def empty():
        info = matterinfo.load(folder)
        assert info == matterinfo.MatterInfo() and not info.has_header
        assert info.plaintiffs == 1 and info.roles == {}
        assert not (folder / 'matter.toml').exists()
    case('empty', empty)
    fixture = matterinfo.load(FIXTURE)
    def filled():
        assert (fixture.matter_type,fixture.client_name,fixture.date_of_accident,
                fixture.treating_physician,fixture.iab_hearing_number,fixture.hearing_date,
                fixture.plaintiffs,fixture.issues,fixture.roles,fixture.standard,fixture.relief) == (
            'workers-comp','Morgan Ashby-Vale','03/11/2025','Dr. Priya Okonkwo-Lind','1234567',
            '01/15/2026 9:00 AM',1,('permanency','termination'),{'defense-report':'defense'},'','')
    case('fixture',filled)
    def layout():
        intake(folder,'ABC1234')
        (folder / 'matter.toml').write_text('number = "9001.001"\n[header]\nclient_name = "Invented Client"\n')
        assert matterinfo.load(folder).client_name == 'Invented Client'
        assert len(pages.load(tmp_path,'9001.001',r'[A-Z]+\d{4,}').pages) == 1
        (folder / 'matter.toml').unlink()
    case('intake',layout)
    def prompt():
        info = matterinfo.ask(matterinfo.load(folder),Terminal('workers-comp\nInvented Client\n03/11/2025\nInvented Doctor\n7654321\n01/15/2026\n1\n1,2\n'),StringIO())
        assert info.has_header and info.issues == ('permanency','termination')
        assert matterinfo.load(folder) == info
        before=(folder / 'matter.toml').read_bytes()
        assert matterinfo.ask(matterinfo.load(folder), Terminal(''), StringIO()) == info
        assert (folder / 'matter.toml').read_bytes() == before
    case('prompt',prompt)
    def blank():
        (folder / 'matter.toml').unlink()
        out=StringIO()
        info=matterinfo.ask(matterinfo.load(folder),Terminal('workers-comp\n\n\n\n\n\n\n'),out)
        assert info.client_name == '' and 'NEEDED' in out.getvalue()
        assert matterinfo.load(folder).client_name == ''
    case('blank',blank)
    def non_tty():
        (folder / 'matter.toml').unlink()
        inp=StringIO('workers-comp\nInvented Client\n03/11/2025\n\n\n\n1\n')
        out=StringIO();info=matterinfo.ask(matterinfo.load(folder),inp,out)
        assert info == matterinfo.MatterInfo() and inp.tell() == 0
        assert not (folder / 'matter.toml').exists(), 'non-tty prompt wrote matter.toml'
        assert 'NEEDED' in out.getvalue()
    case('non_tty',non_tty)
    def preserve():
        (folder / 'matter.toml').write_text('number="9001.001"\n[roles]\nscan="other"\n')
        matterinfo.write(folder,replace(matterinfo.load(folder),client_name='Invented Client'))
        assert matterinfo.load(folder).roles == {'scan':'other'}
    case('preserve_roles',preserve)
    def refuse(text,key):
        (folder / 'matter.toml').write_text('number="9001.001"\n'+text)
        try:
            matterinfo.load(folder)
        except matterinfo.MatterInfoError as exc:
            assert key in str(exc)
        else:
            raise AssertionError(f'matterinfo accepted {key}')
    case('unknown',lambda:refuse('[header]\nunknown="x"\n','header.unknown'))
    case('type',lambda:refuse('[header]\nclient_name=1\n','header.client_name'))
    case('issue',lambda:refuse('[header]\nmatter_type="mva"\n[hearing]\nissues=["permanency"]\n','hearing.issues'))
    def role_refusals():
        refuse('[roles]\nscan="unknown"\n','roles.scan')
        refuse('[roles]\nabsent="ours"\n','roles.absent')
    case('roles',role_refusals)
    def ambiguous():
        (folder / 'matter.toml').write_text('number="9001.001"\nbinders=["scan"]\n')
        with pytest.raises(pages.PagesError, match='ambiguous layout'):
            pages.load(tmp_path,'9001.001',r'[A-Z]+\d{4,}')
    case('ambiguous',ambiguous)
    def ask_roles():
        role_folder = tmp_path / 'roles'
        role_folder.mkdir()
        (role_folder / 'matter.toml').write_text(
            'number="9001.002"\nbinders=["Imelda Health", "medical", "dmexport"]\n'
            '[header]\nclient_name="Invented Client"\n[roles]\nmedical="other"\n', encoding='utf-8')
        info = matterinfo.load(role_folder)
        out = StringIO()
        writes = []
        original_write = matterinfo.write
        def counted_write(folder, value):
            writes.append(folder)
            return original_write(folder, value)
        monkeypatch.setattr(matterinfo, 'write', counted_write)
        result = matterinfo.ask_roles(info, ['Imelda Health', 'medical', 'Imelda Health', 'dmexport'],
                                      Terminal('ours\ndefense\n'), out)
        assert result.roles == {'medical': 'other', 'Imelda Health': 'ours', 'dmexport': 'defense'}
        assert matterinfo.load(role_folder) == result and writes == [role_folder]
        assert out.getvalue().count('Binder ') == 2
        before = (role_folder / 'matter.toml').read_bytes()
        untouched = Terminal('other\n')
        assert matterinfo.ask_roles(result, ['Imelda Health', 'dmexport'], untouched, StringIO()) == result
        assert untouched.tell() == 0 and (role_folder / 'matter.toml').read_bytes() == before
    case('ask_roles', ask_roles)
    def roles_non_tty():
        role_folder = tmp_path / 'roles-non-tty'
        role_folder.mkdir()
        info = replace(matterinfo.MatterInfo(), folder=role_folder)
        inp = StringIO('ours\n')
        assert matterinfo.ask_roles(info, ['Imelda Health'], inp, StringIO()) == info
        assert not (role_folder / 'matter.toml').exists(), 'non-tty role prompt wrote matter.toml'
        assert inp.tell() == 0, 'non-tty role prompt consumed input'
    case('roles_non_tty', roles_non_tty)
    def anon_fixture():
        assert fixture.anon_employer == 'Quarry Ridge Logistics LLC'
        assert fixture.anon_dob == '02/17/1981' and fixture.anon_ids == ('QRL-2025-0418',)
        assert fixture.anon_places == fixture.anon_keep == ()
        assert fixture.anon_people == {
            'Morgan Ashby-Vale': 'claimant', 'Halvard Quist-Benning': 'doctor',
            'Ines Castellanos-Reyes': 'doctor', 'Odalys Ferro-Lindqvist': 'doctor',
            'Ansgar Velloso-Krantz': 'doctor', 'Priya Okonkwo-Lind': 'doctor',
            'Theodore Marchetti': 'doctor', 'Rosalind Mbeki-Farrow': 'person',
            'Tobiah Varga-Ellison': 'person', 'Silas Vane-Harrow': 'person'}
        assert fixture.anon_organizations == {'Quarry Ridge Logistics LLC': 'employer',
            **{name: 'provider' for name in ('Fennimore County Hospital', 'Brightwater Family Medicine',
                'Ridgeline Physical Therapy', 'Lakeshore Imaging', 'Lakeshore Orthopedic Associates',
                'Northgate Medical Evaluations')}}
        # The other accepted person kinds include the automatically kept adjuster.
        (folder / 'matter.toml').write_text('[anon.people]\nInvented="adjuster"\n', encoding='utf-8')
        assert matterinfo.load(folder).anon_people == {'Invented': 'adjuster'}
    case('anon_fixture', anon_fixture)
    case('anon_kind', lambda: refuse('[anon.people]\nInvented="unknown"\n', 'anon.people entry 1'))
    def anon_roundtrip():
        target = tmp_path / 'anon-roundtrip'
        shutil.copytree(FIXTURE, target)
        info = matterinfo.load(target)
        matterinfo.write(target, info)
        try:
            restored = matterinfo.load(target)
        except matterinfo.MatterInfoError as exc:
            raise AssertionError(f'anon.people round trip refused: {exc}') from exc
        assert restored == info, 'anon.people round trip differs'
        assert '["anon"."people"]' in (target / 'matter.toml').read_text(encoding='utf-8')
    case('anon_roundtrip', anon_roundtrip)
    case('anon_type', lambda: refuse('[anon]\nemployer=1\n', 'anon.employer'))
    print(f'matterinfo_ok={len(passed)} of {len(passed) + len(failures)}')
    assert len(passed) == 18, f"matterinfo_ok={len(passed)} of 18; {failures}"


def test_stamps_compatible(tmp_path):
    firm = rules.load(ROOT / 'playbook/rules.toml')
    from casefile import matter
    rules.check_stamps(matter.load(FIXTURE).pages,firm)
    settings=config.load(write_config(tmp_path, ocr={'stamp_pattern':r'[A-Z]{1,8}\d{3,}'}))
    shutil.copytree(ROOT / 'playbook',settings.paths.playbook,dirs_exist_ok=True)
    folder=settings.paths.matters / '9002.001';intake(folder)
    out,err=StringIO(),StringIO()
    code=memo_job.run(settings,'9002.001',out=out,err=err)
    assert code == 2
    assert err.getvalue() == ("memo: cannot run: stamp ABC123 on page scan/001 does not match the playbook's "
                             "bates-cites pattern; align [ocr].stamp_pattern with rules.toml bates_pattern before running\n")
    assert not (settings.paths.state / 'runlog.sqlite').exists(), 'stamp refusal created run log'
    print('stamps_compatible=2 of 2')
