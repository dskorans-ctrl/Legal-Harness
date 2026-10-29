"""Exact, reversible casefile-anon/1 transformations without a model call."""

from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta
from functools import lru_cache
import json
import os
from pathlib import Path
import re

from casefile import dates, jsonrepair, quotes, stamps


class AnonError(ValueError):
    """An anonymization prerequisite or private key is invalid."""


@dataclass
class Key:
    convention: str = 'casefile-anon/1'
    anchor: str = ''
    entities: dict = field(default_factory=dict)
    refs: dict = field(default_factory=dict)
    dates: dict = field(default_factory=dict)
    srcs: dict = field(default_factory=dict)
    aliases: dict = field(default_factory=dict)
    ages: list = field(default_factory=list)

    def to_json(self):
        return json.dumps(asdict(self), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True)
class NameList:
    people: dict = field(default_factory=dict)
    organizations: dict = field(default_factory=dict)
    employer: str = ''
    ids: tuple = ()
    places: tuple = ()
    keep: tuple = ()
    dob: str = ''
    anchor: str = ''
    folder: Path | None = None
    info: object = field(default=None, compare=False, repr=False)
    aliases: dict = field(default_factory=dict)

    @property
    def kept(self):
        return tuple(dict.fromkeys((*self.keep,
            *(n for n, k in self.people.items() if k == 'adjuster'),
            *(n for n, k in self.organizations.items() if k in ('provider', 'insurer')))))


@dataclass(frozen=True)
class Hit:
    name: str
    kind: str
    quote: str
    cite: str
    page_id: str = ''


@dataclass(frozen=True)
class Verdict:
    ok: bool
    hits: tuple = ()


TITLE = re.compile(r'^(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?)\s+')
TAG = re.compile(r'\[[^\]\n]*\]')
GRAMMAR = re.compile(r'\[(?:CLAIMANT|EMPLOYER|DOB|AGE|(?:AGE|DR|ATTY|PERSON|ORG|PLACE|EMAIL|SSN|PHONE|STREET|ZIP|ID|DATE-REF|SRC)-(?:\d+|n)|DATE D[+-](?:\d+|n)|MONTH M[+-](?:\d+|n)|YEAR Y[+-](?:\d+|n))\]')
AGE_WORD = r'(?:age[ds]?|(?:years?|yrs?)[ \t-]+old|yo|y[ \t]*/[ \t]*o|y\.[ \t]*o\.?)'
AGE = re.compile(r'(?<!\w)(?:' + AGE_WORD + r'[ \t:=-]+\d{1,3}|\d{1,3}[ \t-]+' + AGE_WORD
                 + r'|\d{1,3}(?:yo|y/o|y\.o\.))(?!\w)', re.I)
# Independent exit detector, deliberately not assembled from AGE or AGE_WORD.
CHECK_AGE = re.compile(
    r'\b(?:aged?|ages|years?[\s-]+old|yrs?[\s-]+old|y\s*/\s*o|y\.\s*o\.?|yo)[\s:=-]+[0-9]{1,3}\b|'
    r'\b[0-9]{1,3}[\s-]+(?:aged?|ages|years?[\s-]+old|yrs?[\s-]+old|y\s*/\s*o|y\.\s*o\.?|yo)(?!\w)|'
    r'\b[0-9]{1,3}(?:y/?o|y\.o\.)(?!\w)', re.I)
MONTH_FORMS = {form: i + 1 for i, month in enumerate(dates.MONTHS)
               for form in (month, month[:3], *(['sept'] if month == 'september' else []))}
MONTH = '(?:' + '|'.join(sorted(MONTH_FORMS, key=len, reverse=True)) + r')\.?'
SPACE = r'[ \t]*(?:\r?\n[ \t]*)?'
FULL_DATE = re.compile(r'(?<!\w)(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-](?:\d{4}|\d{2})|'
                       + MONTH + r'[ \t]+(?:the[ \t]+)?\d{1,2}(?:st|nd|rd|th)?,?' + SPACE + r'\d{4}|'
                       + r'(?:the[ \t]+)?\d{1,2}(?:st|nd|rd|th)?[ \t]+(?:of[ \t]+)?' + MONTH + r',?' + SPACE + r'\d{4})(?!\w)', re.I)
MONTH_DATE = re.compile(r'(?<!\w)' + MONTH + r'(?:[ \t]+|[ \t]*\r?\n[ \t]*)\d{4}(?!\w)', re.I)
YEAR = re.compile(r'(?<![\w./-])(?:19[3-9]\d|20[0-4]\d)(?![\w./-])')
DATE_REF = re.compile(r'(?<!\w)(?=(?-i:[A-Z]))' + MONTH + r'[ \t]+\d{1,2}(?:st|nd|rd|th)?(?![\w\d])', re.I)
# The exit guard deliberately admits more forms than the replacement parser.
CHECK_DATE = re.compile(
    r'(?<!\w)(?:\d{1,4}[/-]\d{1,2}[/-]\d{1,4}|'
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|'
    r'Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?'
    r'[ \t\r\n]+(?:\d{1,2}(?:st|nd|rd|th)?(?:,?[ \t\r\n]+\d{2,4})?|\d{4})|'
    r'\d{1,2}(?:st|nd|rd|th)?[ \t]+[A-Za-z]{3,9}\.?[, \t\r\n]+\d{2,4}|'
    r'(?:19[3-9]\d|20[0-4]\d))(?!\w)', re.I)
CHECK_DAY = re.compile(
    r'(?<!\w)(?:(?:the\s+)?(?P<before>\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?'
    r'(?:\[MONTH M[+-]\d+\]|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?(?!\w))|'
    r'(?:\[MONTH M[+-]\d+\]|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?)'
    r'\s+(?:the\s+)?(?P<after>\d{1,2})(?:st|nd|rd|th)?(?!\w))', re.I)
PATTERNS = (
    ('email', re.compile(r'(?<![\w.])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?!\w)')),
    ('ssn', re.compile(r'(?<!\w)\d{3}[ .-]\d{2}[ .-]\d{4}(?!\w)')),
    ('phone', re.compile(r'(?<!\w)(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]\d{4}(?!\w)')),
    ('street', re.compile(r'(?<!\w)\d+[ \t]+(?:[A-Z][\w.-]*[ \t]+){1,5}(?:Street|St\.?|Road|Rd\.?|Avenue|Ave\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?)(?!\w)')),
    ('zip', re.compile(r'(?<=\b[A-Z]{2} )\d{5}(?:-\d{4})?\b')),
    ('id', re.compile(r'(?<![\w./-])(?:[A-Z]+(?:-[A-Z0-9]+)*[- ]?\d{5,}(?:-[A-Z0-9]+)*|\d{6,})(?![\w./-])')),
)


def strip_title(value):
    return TITLE.sub('', value).split(',')[0].strip()


def names(info) -> NameList:
    people = {strip_title(n): k for n, k in info.anon_people.items()}
    if info.client_name:
        people[strip_title(info.client_name)] = 'claimant'
    if info.treating_physician:
        people.setdefault(strip_title(info.treating_physician), 'doctor')
    orgs = dict(info.anon_organizations)
    if info.anon_employer:
        orgs[info.anon_employer] = 'employer'
    return NameList(people, orgs, info.anon_employer,
                    tuple(dict.fromkeys((*info.anon_ids, *([info.iab_hearing_number] if info.iab_hearing_number else [])))),
                    info.anon_places, info.anon_keep, info.anon_dob,
                    info.date_of_accident, info.folder, info,
                    {alias: strip_title(target) if target in info.anon_people or target in
                     (info.client_name, info.treating_physician) else target for alias, target in info.anon_aliases.items()})


def variants(name, kind):
    name = strip_title(name) if kind in ('claimant','doctor','attorney','adjuster','person') else name
    values = [name]
    if kind in ('claimant','doctor','attorney','adjuster','person'):
        words = name.split()
        values.extend((words[-1], words[0]))
        if len(words) > 1:
            values.append(f'{words[-1]}, {words[0]}')
    return list(dict.fromkeys(v for value in values for v in (value, value.upper()) if v))


@lru_cache(maxsize=4096)
def boundary(value):
    return re.compile(r'(?<![\w\[])' + re.escape(value) + r'(?![\w\]])')


PERSON_KINDS = ('claimant', 'doctor', 'attorney', 'adjuster', 'person')
ORG_KINDS = ('employer', 'other', 'provider', 'insurer')


@lru_cache(maxsize=4096)
def entity_pattern(name, kind, forms):
    """Match list variants, keeping person case rules and organization punctuation rules."""
    parts = [re.escape(form) for form in forms if '\n' not in form and '\r' not in form]
    if kind in PERSON_KINDS and len(name.split()) > 1:
        given, surname = name.split()[0], name.split()[-1]
        parts.extend(re.escape(g[0]) + r'\.?[ \t]+' + re.escape(s)
                     for g, s in ((given, surname), (given.upper(), surname.upper())))
        parts.extend(re.escape(g) + r'[ \t]+[A-Z]\.?' + r'(?:[ \t]+' + re.escape(s) + r')?'
                     for g, s in ((given, surname), (given.upper(), surname.upper())))
    if kind in ORG_KINDS:
        words = re.sub(r'[.,]', '', name).split()
        suffix = words.pop() if words and words[-1].casefold() in ('llc', 'inc', 'co', 'corp') else ''
        base = r'[ \t]*[.,]?[ \t]+'.join(re.escape(word) for word in words)
        if suffix:
            legal = r'\.?'.join(re.escape(char) for char in suffix)
            base += r'(?:[ \t.,]+' + legal + r')?'
        parts.insert(0, '(?i:' + base + ')')
    return re.compile(r'(?<![\w\[])(?:' + '|'.join(sorted(set(parts), key=len, reverse=True)) + r')(?![\w\]])')


def members(namelist, value):
    """Resolve explicit aliases first, then all list variants without choosing an ambiguity."""
    records = [*namelist.people.items(), *namelist.organizations.items(), *((n, 'place') for n in namelist.places)]
    target = next((target for alias, target in namelist.aliases.items() if quotes.same(alias, value)), None)
    if target is not None:
        return [(n, k) for n, k in records if n == target]
    wanted = TITLE.sub('', value).strip()
    return [(n, k) for n, k in records if entity_pattern(n, k, tuple(variants(n, k))).fullmatch(wanted)]


def is_kept(namelist, value):
    if any(quotes.same(value, alias) and target in namelist.kept for alias, target in namelist.aliases.items()):
        return True
    resolved = members(namelist, value)
    if resolved and all(k in ('adjuster', 'provider', 'insurer') or n in namelist.keep for n, k in resolved):
        return True
    wanted = TITLE.sub('', value).strip()
    return any(entity_pattern(strip_title(n), 'person', tuple(variants(n, 'person'))).fullmatch(wanted)
               for n in namelist.keep)


def protected(pages):
    return tuple(dict.fromkeys(v for p in pages for v in
                              (p.page_id, *p.stamps, *(stamps.normalize(s) for s in p.stamps))))


def _spans(value, tokens, *, tags=True):
    result = [(m.start(), m.end()) for token in tokens if token for m in boundary(token).finditer(value)]
    result += [(m.start(), m.end()) for m in re.finditer(r'(?m)^=== PAGE .*?===[^\n]*|\[(?:cite|page) [^\]\n]+\]', value)]
    if tags:
        result += [(m.start(), m.end()) for m in TAG.finditer(value)]
    return result


def _sub(pattern, callback, value, tokens=(), *, tags=True):
    spans = _spans(value, tokens, tags=tags)
    return pattern.sub(lambda m: m[0] if any(m.start() < b and m.end() > a for a,b in spans)
                       else callback(m), value)


def _allocate(table, prefix, value):
    for tag, stored in table.items():
        if stored == value:
            return tag
    used = [int(m[1]) for tag in table if (m := re.fullmatch(r'\[' + prefix + r'-(\d+)\]', tag))]
    tag = f'[{prefix}-{max(used, default=0) + 1}]'
    table[tag] = value
    return tag


def mapping(namelist, hits, pages, key) -> Key:
    pages = tuple(pages)
    key._ids = namelist.ids
    key._keep = namelist.kept
    key._kept_people = {f'kept:{i}': {'name': n, 'kind': k, 'variants': variants(n, k)}
                        for i, (n, k) in enumerate(namelist.people.items())
                        if k == 'adjuster' or n in namelist.keep}
    records = [(n,k) for n,k in namelist.people.items()] + [(n,k) for n,k in namelist.organizations.items()]
    records += [(n,'place') for n in namelist.places]
    def position(row):
        patterns = [entity_pattern(*row, tuple(variants(*row))),
                    *(re.compile(boundary(alias).pattern, re.I) for alias, target in namelist.aliases.items() if target == row[0])]
        return next(((i, min(m.start() for m in matches)) for i, p in enumerate(pages)
                     if (matches := [m for pattern in patterns if (m := pattern.search(p.text))])), (len(pages), 0))
    for name, kind in sorted(records, key=position):
        if kind in ('adjuster','provider','insurer') or name in namelist.keep:
            continue
        forms = variants(name, kind)
        for hit in hits:
            if hit.kind != 'anchor' and members(namelist, hit.name) == [(name, kind)]:
                form = TITLE.sub('', hit.name).strip()
                if form not in forms:
                    forms.append(form)
        existing = next((tag for tag, row in key.entities.items() if row['name'] == name and row['kind'] == kind), None)
        if existing:
            key.entities[existing]['variants'] = list(dict.fromkeys((*key.entities[existing]['variants'], *forms)))
            continue
        prefix = {'claimant':'CLAIMANT', 'employer':'EMPLOYER', 'doctor':'DR', 'attorney':'ATTY',
                  'person':'PERSON','other':'ORG','place':'PLACE'}[kind]
        if prefix in ('CLAIMANT', 'EMPLOYER'):
            tag = f'[{prefix}]'
            if tag in key.entities:
                raise AnonError('conflicting unnumbered entity')
        else:
            numbers = [int(m[1]) for tag in key.entities if (m := re.fullmatch(r'\['+prefix+r'-(\d+)\]',tag))]
            tag = f'[{prefix}-{max(numbers, default=0)+1}]'
        key.entities[tag] = {'name': name, 'kind': kind, 'variants': forms}
    for alias, target in namelist.aliases.items():
        tag = next((tag for tag, row in key.entities.items() if row['name'] == target), None)
        if tag:
            if alias in key.aliases and key.aliases[alias] != tag:
                raise AnonError('anon.aliases: cannot change an existing alias; correct matter.toml')
            key.aliases[alias] = tag
            forms = key.entities[tag]['variants']
            if alias not in forms:
                forms.append(alias)
    # Preallocate all non-entity references in page order, before packet metadata.
    for page in pages:
        text(page.text, key, protected=(*protected(pages), *namelist.kept), namelist=namelist)
    return key


def _parsed(value):
    compact = ' '.join(value.split())
    parsed = dates.parse(compact)
    if parsed:
        return parsed
    try:
        if m := re.fullmatch(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2}|\d{4})', compact):
            mo, d, y = map(int, m.groups())
            if len(m[3]) == 2:
                y += 1900 if y >= 69 else 2000
            return date(y, mo, d)
        compact = re.sub(r'(?<=\d)(?:st|nd|rd|th)\b', '', compact, flags=re.I)
        compact = re.sub(r'\b(?:the|of)\s+', '', compact, flags=re.I)
        compact = compact.replace(',', '').replace('.', '')
        if m := re.fullmatch(r'([A-Za-z]+) (\d{1,2}) (\d{4})', compact):
            return date(int(m[3]), MONTH_FORMS[m[1].casefold()], int(m[2]))
        if m := re.fullmatch(r'(\d{1,2}) ([A-Za-z]+) (\d{4})', compact):
            return date(int(m[3]), MONTH_FORMS[m[2].casefold()], int(m[1]))
        return None
    except (ValueError, KeyError):
        return None


def _date_tag(value, key, dob=''):
    parsed = _parsed(value)
    if not parsed:
        return value
    if dob and parsed == _parsed(dob):
        key.refs.setdefault('[DOB]', dob)
        key.dates.setdefault('DOB', [])
        spellings = key.dates['DOB']
        tag = '[DOB]'
    else:
        if not key.anchor:
            raise AnonError('ANCHOR NEEDED: add date_of_accident to matter.toml [header]')
        offset = (parsed - date.fromisoformat(key.anchor)).days
        label = f'D{offset:+d}'
        spellings = key.dates.setdefault(label, [])
        tag = f'[DATE {label}]'
    if value not in spellings:
        spellings.append(value)
    return tag + ''.join(re.findall(r'[\r\n]', value))


def _age_groups(key):
    groups = {}
    for spelling in key.ages:
        number = int(re.search(r'\d+', spelling)[0])
        groups.setdefault(number, []).append(spelling)
    return list(groups.values())


def _remember_ages(value, key, tokens):
    def remember(m):
        if m[0] not in key.ages:
            key.ages.append(m[0])
        return m[0]
    _sub(AGE, remember, value, tokens)


def _age_spellings(tag, key):
    groups = _age_groups(key)
    if tag == '[AGE]':
        return groups[0] if len(groups) == 1 else []
    if m := re.fullmatch(r'\[AGE-(\d+)\]', tag):
        return groups[int(m[1]) - 1] if 0 < int(m[1]) <= len(groups) else []
    return []


def text(value, key, *, protected, namelist=None) -> str:
    """Transform each line, preserving protected syntax and newline counts."""
    if not value:
        return value
    keep = namelist.kept if namelist else getattr(key, "_keep", ())
    tokens = (*protected, *keep)
    value = _sub(GRAMMAR, lambda m: _allocate(key.srcs, 'SRC', m[0]), value, tokens, tags=False)
    _remember_ages(value, key, tokens)
    def age(m):
        groups = _age_groups(key)
        index = next(i for i, spellings in enumerate(groups, 1) if m[0] in spellings)
        return '[AGE]' if len(groups) == 1 else f'[AGE-{index}]'
    value = _sub(AGE, age, value, tokens)
    for kind, pattern in PATTERNS:
        value = _sub(pattern, lambda m, k=kind: _allocate(key.refs, k.upper(), m[0]), value, tokens)
    # List ids must precede the date and bare-year readers.
    for identifier in sorted(namelist.ids if namelist else getattr(key, '_ids', ()), key=len, reverse=True):
        value = _sub(boundary(identifier), lambda m: _allocate(key.refs, 'ID', m[0]), value, tokens)
    dob = namelist.dob if namelist else key.refs.get('[DOB]', '')
    def full(m):
        label = value[value.rfind('\n', 0, m.start()) + 1:m.start()]
        labelled = re.search(r'\b(?:D\.?O\.?B\.?|Date[ \t]+of[ \t]+Birth|Birth[ \t]+date)[ \t]*[:=]?[ \t]*$', label, re.I)
        return _date_tag(m[0], key, m[0] if labelled else dob)
    value = _sub(FULL_DATE, full, value, tokens)
    def month(m):
        words = m[0].split()
        anchor = date.fromisoformat(key.anchor)
        offset = (int(words[-1]) - anchor.year)*12 + MONTH_FORMS[words[0].casefold().rstrip('.')] - anchor.month
        tag = f'[MONTH M{offset:+d}]'
        key.dates.setdefault(f'M{offset:+d}', [])
        if m[0] not in key.dates[f'M{offset:+d}']:
            key.dates[f'M{offset:+d}'].append(m[0])
        return tag + ''.join(re.findall(r'[\r\n]', m[0]))
    value = _sub(MONTH_DATE, month, value, tokens)
    def year(m):
        label = f'Y{int(m[0])-date.fromisoformat(key.anchor).year:+d}'
        seen = key.dates.setdefault(label, [])
        if m[0] not in seen:
            seen.append(m[0])
        return f'[YEAR {label}]'
    value = _sub(YEAR, year, value, tokens)
    value = _sub(DATE_REF, lambda m: _allocate(key.refs, 'DATE-REF', m[0]), value, tokens)
    candidates = []
    for tag, row in {**key.entities, **getattr(key, '_kept_people', {})}.items():
        pattern = entity_pattern(row['name'], row['kind'], tuple(row['variants']))
        candidates.extend((m.start(), m.end(), tag) for m in pattern.finditer(value))
    for alias, tag in key.aliases.items():
        candidates.extend((m.start(), m.end(), tag) for m in re.finditer(boundary(alias).pattern, value, re.I))
    spans = _spans(value, tokens)
    cursor, parts = 0, []
    for start, end, _ in sorted(set(candidates), key=lambda item: (item[0], -item[1])):
        if start < cursor or any(start < b and end > a for a, b in spans):
            continue
        raw = value[start:end]
        tags = {tag for a, b, tag in candidates if a == start and b == end}
        alias_tag = next((tag for alias, tag in key.aliases.items() if quotes.same(alias, raw)), None)
        if alias_tag:
            tags = {alias_tag}
        if len(tags) != 1:
            continue
        tag = next(iter(tags))
        if tag not in key.entities:
            continue
        row = key.entities[tag]
        if raw not in row['variants']:
            row['variants'].append(raw)
        parts.extend((value[cursor:start], tag + ''.join(re.findall(r'[\r\n]', raw))))
        cursor = end
    value = ''.join((*parts, value[cursor:]))
    return value


def packet(packet, key):
    """Transform all payload strings while retaining evidence identities."""
    tokens = protected(packet.pages)
    def convert(value):
        if isinstance(value, str):
            return text(value, key, protected=tokens)
        if isinstance(value, dict):
            return {k:convert(v) for k,v in value.items()}
        if isinstance(value, (list,tuple)):
            return [convert(v) for v in value]
        return value
    def remember(value):
        if isinstance(value, str):
            _remember_ages(value, key, (*tokens, *getattr(key, '_keep', ())))
        elif isinstance(value, dict):
            for part in value.values():
                remember(part)
        elif isinstance(value, (list, tuple)):
            for part in value:
                remember(part)
    # Discover ages on every surface before rendering any surface with its final tags.
    remember([packet.options, *([getattr(f, k) for k in ('quote', 'text', 'provider', 'date')]
              for f in packet.facts), *(p.text for p in packet.pages),
              *({k: v for k, v in flag.items() if k in ('about', 'abouts')} for flag in packet.flags)])
    return replace(packet, options=convert(packet.options),
        facts=tuple(replace(f, **{k:convert(getattr(f,k)) for k in ('quote','text','provider','date')}) for f in packet.facts),
        pages=tuple(replace(p, text=convert(p.text)) for p in packet.pages),
        flags=tuple({k:convert(v) if k in ('about','abouts') else v for k,v in f.items()} for f in packet.flags))


def _canonical(tag, key):
    if tag == '[AGE]' or re.fullmatch(r'\[AGE-\d+\]', tag):
        if spellings := _age_spellings(tag, key):
            return spellings[0]
        if tag == '[AGE]' and key.ages:
            raise AnonError('ambiguous age: use a numbered age placeholder')
    if tag in key.entities:
        return key.entities[tag]['name']
    if tag in key.refs:
        return key.refs[tag]
    if m := re.fullmatch(r'\[DATE D([+-]\d+)\]', tag):
        d = date.fromisoformat(key.anchor) + timedelta(days=int(m[1]))
        spellings = key.dates.get(f'D{int(m[1]):+d}', [])
        return spellings[0] if len(spellings) == 1 else d.strftime('%m/%d/%Y')
    if m := re.fullmatch(r'\[MONTH M([+-]\d+)\]', tag):
        anchor = date.fromisoformat(key.anchor)
        y,mo = divmod(anchor.year*12 + anchor.month-1 + int(m[1]),12)
        return f'{dates.MONTHS[mo].capitalize()} {y}'
    if m := re.fullmatch(r'\[YEAR Y([+-]\d+)\]', tag):
        return str(date.fromisoformat(key.anchor).year+int(m[1]))
    return tag


def restore(value, key) -> str:
    value = TAG.sub(lambda m: _canonical(m[0],key), value)
    return TAG.sub(lambda m: key.srcs.get(m[0],m[0]),value)


def _known(tag, key):
    if tag == '[AGE]' or re.fullmatch(r'\[AGE-\d+\]', tag):
        return bool(_age_spellings(tag, key))
    if tag in key.entities or tag in key.refs or tag in key.srcs:
        return True
    if m := re.fullmatch(r'\[(DATE D|MONTH M)([+-]\d+)\]', tag):
        return m[1][-1]+m[2] in key.dates
    if m := re.fullmatch(r'\[YEAR (Y[+-]\d+)\]', tag):
        return m[1] in key.dates
    return False


def restore_quote(quote, key, page) -> str | None:
    """Search variants with page-prefix pruning rather than canonicalizing evidence."""
    matches = list(TAG.finditer(quote))
    def walk(index, end, prefix):
        if index == len(matches):
            result = prefix + quote[end:]
            return result if quotes.match(result,page.text) else None
        m = matches[index]
        tag = m[0]
        if not _known(tag,key):
            return None
        values = key.entities[tag]['variants'] if tag in key.entities else [key.srcs[tag]] if tag in key.srcs else None
        label = tag[6:-1] if tag.startswith('[DATE ') else tag[7:-1] if tag.startswith('[MONTH ') else 'DOB' if tag=='[DOB]' else ''
        values = values or _age_spellings(tag, key) or key.dates.get(label) or [_canonical(tag,key)]
        values = sorted(values, key=len, reverse=True)
        candidates = []
        for value in values:
            next_end = m.end()
            if '\n' in value and quote[next_end:next_end+1] == '\n':
                next_end += 1
            candidate = prefix + quote[end:m.start()] + value
            if quotes.found_in(candidate, page.text) or quotes.match(candidate,page.text):
                candidates.append((candidate, next_end))
        for candidate, next_end in sorted(candidates, key=lambda item: item[0] not in page.text):
            if (result := walk(index+1,next_end,candidate)) is not None:
                return result
        return None
    return walk(0,0,'')


def _fold_positions(value):
    """Retain source offsets while applying the quote ladder's folding."""
    removed = set()
    for m in re.finditer(r'(?<=[^\W\d_])-[^\S\r\n]*(?:\r\n?|\n)[^\S\r\n]*(?=[^\W\d_])', value):
        removed.update(range(m.start(),m.end()))
    result, positions = [], []
    pending = None
    for i,char in enumerate(value):
        if i in removed:
            continue
        for folded in quotes.CURLY.get(char,char).casefold():
            if folded.isspace():
                if result and pending is None:
                    pending = i
                continue
            if pending is not None:
                result.append(' ')
                positions.append(pending)
                pending = None
            result.append(folded)
            positions.append(i)
    return ''.join(result),positions


def check_code(data, key, namelist, pages, *, cite_pages=None) -> Verdict:
    """Inspect exact UTF-8 bytes and report offsets without disclosing values."""
    try:
        value = data.decode('utf-8')
    except UnicodeError:
        return Verdict(False, ((1,'encoding',0),))
    original = value
    positions = list(range(len(value)))
    try:
        decoded = jsonrepair.loads(value)
    except ValueError:
        decoded = None
    if isinstance(decoded, (dict,list)):
        surface = [' '] * len(value)
        for token in re.finditer(r'"(?:[^"\\]|\\.)*"', value):
            part = json.loads(token[0])
            raw_index = token.start() + 1
            dest = token.start() + 1
            for char in part:
                surface[dest] = char
                positions[dest] = raw_index
                if value[raw_index:raw_index+1] == '\\':
                    raw_index += 6 if value[raw_index+1:raw_index+2] == 'u' else 2
                else:
                    raw_index += 1
                dest += 1
        value = ''.join(surface)
    hits = []
    def add(step,kind,index):
        hit = (step,kind,len(original[:positions[index]].encode('utf-8')))
        if hit not in hits:
            hits.append(hit)
    hidden = _spans(value, (), tags=True)
    def inside(m):
        return any(m.start()<b and m.end()>a for a,b in hidden)
    folded, source = _fold_positions(value)
    found = {}
    rows = {**key.entities, **{f'kept:{i}': {'name': n, 'kind': k, 'variants': variants(n, k)}
            for i, (n, k) in enumerate(namelist.people.items()) if k == 'adjuster' or n in namelist.keep}}
    for tag, row in rows.items():
        forms = tuple(quotes.fold(v) for v in row['variants'])
        pattern = entity_pattern(quotes.fold(row['name']), row['kind'], forms)
        for m in re.finditer(pattern.pattern, folded, re.I):
            found.setdefault((m.start(), m.end()), set()).add(tag)
    for (left, right), tags in found.items():
        start, end = source[left], source[right - 1] + 1
        if any(start < b and end > a for a, b in hidden):
            continue
        current_alias = next((alias for alias in namelist.aliases if quotes.same(alias, folded[left:right])), None)
        if current_alias is not None:
            if not is_kept(namelist, current_alias):
                resolved = members(namelist, current_alias)
                add(1, resolved[0][1] if len(resolved) == 1 else 'ambiguous', start)
            continue
        explicit = next((tag for alias, tag in key.aliases.items() if quotes.same(alias, folded[left:right])), None)
        if explicit:
            tags = {explicit}
        if len(tags) == 1 and next(iter(tags)) not in key.entities:
            continue
        add(1, 'ambiguous' if len(tags) > 1 else rows[next(iter(tags))]['kind'], start)
    for alias in namelist.aliases:
        if is_kept(namelist, alias):
            continue
        resolved = members(namelist, alias)
        for m in re.finditer(boundary(quotes.fold(alias)).pattern, folded, re.I):
            start, end = source[m.start()], source[m.end() - 1] + 1
            if not any(start < b and end > a for a, b in hidden):
                add(1, resolved[0][1] if len(resolved) == 1 else 'ambiguous', start)
    for identifier in (*namelist.ids, *([namelist.dob] if namelist.dob else []), *key.dates.get('DOB', [])):
        for m in boundary(identifier).finditer(value):
            if not inside(m):
                add(1,'dob' if _parsed(identifier) == _parsed(namelist.dob) and _parsed(identifier) is not None else 'id',m.start())
    exemptions = _spans(value, (*protected(pages), *namelist.kept))
    def exempt(m):
        return any(m.start()<b and m.end()>a for a,b in exemptions)
    for pattern in (CHECK_DATE,):
        for m in pattern.finditer(value):
            if not exempt(m):
                add(2,'date',m.start())
    for m in CHECK_DAY.finditer(value):
        index = m.start('before') if m['before'] is not None else m.start('after')
        if not any(a <= index < b for a, b in exemptions):
            add(2, 'date', index)
    for m in CHECK_AGE.finditer(value):
        if not exempt(m):
            add(3, 'age', m.start())
    for m in re.finditer(r'(?<!\w)[A-Z]\.?[ \t]+\[(?:CLAIMANT|(?:DR|ATTY|PERSON)-(?:\d+|n))\]', value):
        if not any(a <= m.start() < b for a, b in exemptions):
            add(3, 'initial', m.start())
    for kind,pattern in PATTERNS:
        for m in pattern.finditer(value):
            if not exempt(m):
                add(3,kind,m.start())
    for m in re.finditer(r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?)\s+[A-Z][\w-]*',value):
        if not exempt(m):
            add(3,'titled_name',m.start())
    sources = pages if cite_pages is None else cite_pages
    cites = {p.page_id for p in sources} | {s for p in sources for s in p.stamps}
    for m in TAG.finditer(value):
        tag = m[0]
        generic = bool(GRAMMAR.fullmatch(tag) and ('n' in tag or tag in ('[CLAIMANT]','[EMPLOYER]','[DOB]', '[AGE]')))
        citation = re.fullmatch(r'\[(?:cite|page) (.+)\]',tag)
        if not (_known(tag,key) or generic or (citation and citation[1] in cites)):
            add(5,'placeholder',m.start())
    return Verdict(not hits,tuple(hits))


def review(value, key, namelist, pages):
    path = Path('/usr/share/dict/words')
    if not path.is_file():
        return 'unavailable'
    dictionary = set(path.read_text(encoding='utf-8').casefold().split())
    value = TAG.sub('',value)
    for token in (*protected(pages), *namelist.kept):
        value = value.replace(token,'')
    return len({v for v in re.findall(r'\b[A-Z][a-z]+\b',value) if v.casefold() not in dictionary and v.casefold() not in dates.MONTHS})


def drafter_rules(book=None):
    convention = ('Drafter rules (casefile-anon/1):\n'
        '1. Preserve every placeholder exactly, including brackets and signs.\n'
        '2. Use [CLAIMANT], [EMPLOYER] and [DOB] without numbers; preserve [AGE] for one distinct age or [AGE-n] for multiple ages.\n'
        '3. Keep titles outside [DR-n], [ATTY-n] and [PERSON-n].\n'
        '4. Keep date offsets such as [DATE D+n], [MONTH M+n] and [YEAR Y+n].\n'
        '5. Preserve [ID-n], [DATE-REF-n] and all contact placeholders.\n'
        '6. Quote only supplied text and retain its supplied citation.\n'
        '7. Do not guess identities, dates or missing facts. D+0 is the date of accident.\n'
        '8. Cite every factual sentence with its supplied Bates stamp, written like [cite MED0001], in the paragraph or in a Word footnote; use straight double quotes.\n')
    if book is not None:
        entries = [*book.rules.rules, *(entry for entry in book.entries if entry.id == 'header-block')]
        convention += '\nFirm drafting rules:\n' + '\n'.join(f'{entry.id}: {entry.rule}' for entry in entries) + '\n'
    return convention


def load_key(folder) -> Key:
    directory = Path(folder)/'anon'
    path = directory/'key.json'
    if not directory.exists():
        return Key()
    try:
        if directory.is_symlink() or path.is_symlink() or path.stat().st_mode & 0o077:
            raise AnonError('anon/key.json must be mode 600')
        data = jsonrepair.loads(path.read_text(encoding='utf-8'))
        if (not isinstance(data,dict) or not set(Key.__dataclass_fields__) - {'aliases', 'ages'} <= data.keys()
                or data.keys() - set(Key.__dataclass_fields__)
                or data['convention']!='casefile-anon/1'):
            raise ValueError
        if not isinstance(data['anchor'],str) or (data['anchor'] and not dates.parse(data['anchor'])):
            raise ValueError
        for table in ('entities','refs','dates','srcs'):
            if not isinstance(data[table],dict):
                raise ValueError
        for tag,row in data['entities'].items():
            if not GRAMMAR.fullmatch(tag) or not isinstance(row,dict) or set(row)!={'name','kind','variants'}:
                raise ValueError
            if any(not isinstance(row[k],str) for k in ('name','kind')) or not isinstance(row['variants'],list) or any(not isinstance(v,str) for v in row['variants']):
                raise ValueError
        for table in ('refs','srcs'):
            if any(not isinstance(v,str) for v in data[table].values()):
                raise ValueError
        if any(not isinstance(v,list) or any(not isinstance(s,str) for s in v) for v in data['dates'].values()):
            raise ValueError
        if not isinstance(data.get('ages', []), list) or any(not isinstance(v, str) or not AGE.fullmatch(v) for v in data.get('ages', [])):
            raise ValueError
        if (not isinstance(data.get('aliases', {}), dict) or any(not isinstance(alias, str)
                or tag not in data['entities'] for alias, tag in data.get('aliases', {}).items())):
            raise ValueError
        key = Key(**data)
        key._ids = tuple(v for k,v in key.refs.items() if k.startswith('[ID-'))
        return key
    except (OSError,UnicodeError,ValueError,TypeError) as exc:
        if isinstance(exc,AnonError):
            raise
        raise AnonError('cannot read anon/key.json') from exc


def save_key(folder, key):
    folder = Path(folder)
    old = load_key(folder)
    if old.anchor and old.anchor != key.anchor:
        raise AnonError('anon/key.json cannot change anchor')
    if key.ages[:len(old.ages)] != old.ages:
        raise AnonError('anon/key.json cannot drop or change an entry')
    for table in ('entities','refs','dates','srcs','aliases'):
        for tag,value in getattr(old,table).items():
            new = getattr(key,table).get(tag)
            retained = (isinstance(new,list) and new[:len(value)]==value) if table=='dates' else (
                isinstance(new,dict) and new.get('name')==value['name'] and new.get('kind')==value['kind']
                and new.get('variants',[])[:len(value['variants'])]==value['variants']) if table=='entities' else new==value
            if not retained:
                raise AnonError('anon/key.json cannot drop or change an entry')
    directory = folder/'anon'
    created = False
    temporary = directory/'key.json.tmp'
    owned = False
    try:
        if not directory.exists():
            directory.mkdir(mode=0o700)
            created = True
        fd = os.open(temporary, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
        owned = True
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            stream.write(key.to_json()+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary,directory/'key.json')
    except BaseException:
        if owned:
            temporary.unlink(missing_ok=True)
        if created:
            directory.rmdir()
        raise
