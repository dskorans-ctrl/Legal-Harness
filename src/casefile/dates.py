"""Parse only the date forms the extraction contract permits."""

from datetime import date
import re

MONTHS = ('january february march april may june july august september october november december').split()


def parse(text) -> date | None:
    if not isinstance(text, str):
        return None
    try:
        if m := re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text):
            month, day, year = map(int, m.groups())
        elif m := re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text):
            year, month, day = map(int, m.groups())
        elif m := re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', text):
            month = MONTHS.index(m[1].casefold()) + 1
            day, year = int(m[2]), int(m[3])
        else:
            return None
        return date(year, month, day)
    except ValueError:
        return None


def iso(text) -> str:
    value = parse(text)
    return value.isoformat() if value else ''
