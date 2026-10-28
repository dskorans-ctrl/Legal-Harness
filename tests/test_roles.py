"""Binder labels default only in a single-plaintiff matter."""

from dataclasses import replace

from casefile import matterinfo, roles


def test_roles():
    info = matterinfo.MatterInfo()
    cases = [('DME-report','defense'), ('defense_medical','defense'),
             ('Defense Medical Exam','defense'), ('medical','ours'), ('records','ours'),
             ('ime-free-notes','defense')]
    count = sum(roles.role(name,info) == expected for name,expected in cases)
    print(f'roles_by_name={count} of 6')
    assert count == 6, f'roles_by_name={count} of 6'
    assert roles.role('medical',replace(info,roles={'medical':'defense'})) == 'defense'
    assert roles.role('DME-report',replace(info,plaintiffs=2)) == 'ROLE NEEDED'
    assert roles.role('medical',replace(info,plaintiffs=2,roles={'medical':'other'})) == 'other'
