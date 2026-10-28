"""Binder-name defaults with explicit roles required for multiple plaintiffs."""

import re


def role(binder, info) -> str:
    if binder in info.roles:
        return info.roles[binder]
    if info.plaintiffs > 1:
        return 'ROLE NEEDED'
    name = re.sub(r'[-_\s]+', ' ', binder.casefold())
    return 'defense' if re.search(r'\bdme\b|\bdefense medical\b', name) else 'ours'
