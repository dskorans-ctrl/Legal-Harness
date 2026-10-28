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


def test_matterinfo(tmp_path):
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
        info = matterinfo.ask(matterinfo.load(folder),Terminal('workers-comp\nInvented Client\n03/11/2025\nInvented Doctor\n7654321\n01/15/2026\n1,2\n'),StringIO())
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
    print(f'matterinfo_ok={len(passed)} of 12')
    assert len(passed) == 12, f"matterinfo_ok={len(passed)} of 12; {failures}"


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
