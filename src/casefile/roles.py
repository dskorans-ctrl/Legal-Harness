"""Binder-name defaults with explicit roles required for multiple plaintiffs."""

import re


def role(binder, info) -> str:
    if binder in info.roles:
        return info.roles[binder]
    if info.plaintiffs > 1:
        return 'ROLE NEEDED'
    name = re.sub(r'\b([di])[\W_]*m[\W_]*e', r'\1me', binder.casefold())
    name = re.sub(r'[^\w]+', ' ', name.replace('_', ' '))
    if re.search(r'\b(?:dme|ime)\d*\b|\b(?:defense|independent) medical\b', name):
        return 'defense'
    if re.search(r'\b(?:dme|ime)\w+', name):
        return 'ROLE NEEDED'
    return 'ours'
