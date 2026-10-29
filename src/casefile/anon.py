"""Exact, reversible casefile-anon/1 transformations without a model call."""

from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta
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
GRAMMAR = re.compile(r'\[(?:CLAIMANT|EMPLOYER|DOB|(?:DR|ATTY|PERSON|ORG|PLACE|EMAIL|SSN|PHONE|STREET|ZIP|ID|DATE-REF|SRC)-(?:\d+|n)|DATE D[+-](?:\d+|n)|MONTH M[+-](?:\d+|n)|YEAR Y[+-](?:\d+|n))\]')
MONTH = '(?:' + '|'.join(m.capitalize() for m in dates.MONTHS) + ')'
SPACE = r'[ \t]*(?:\r?\n[ \t]*)?'
FULL_DATE = re.compile(r'(?<!\w)(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|'
                       + MONTH + r'[ \t]+\d{1,2},?' + SPACE + r'\d{4})(?!\w)', re.I)
MONTH_DATE = re.compile(r'(?<!\w)' + MONTH + r'[ \t]+(?:\r?\n[ \t]*)?\d{4}(?!\w)', re.I)
YEAR = re.compile(r'(?<![\w./-])(?:19[3-9]\d|20[0-4]\d)(?![\w./-])')
DATE_REF = re.compile(r'(?<!\w)' + MONTH + r'\s+\d{1,2}(?![\w\d])')
PATTERNS = (
    ('email', re.compile(r'(?<![\w.])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?!\w)')),
    ('ssn', re.compile(r'(?<!\w)\d{3}-\d{2}-\d{4}(?!\w)')),
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
                    info.date_of_accident, info.folder, info)


def variants(name, kind):
    name = strip_title(name) if kind in ('claimant','doctor','attorney','adjuster','person') else name
    values = [name]
    if kind in ('claimant','doctor','attorney','adjuster','person'):
        values.append(name.split()[-1])
    return list(dict.fromkeys(v for value in values for v in (value, value.upper()) if v))


def boundary(value):
    return re.compile(r'(?<![\w\[])' + re.escape(value) + r'(?![\w\]])')


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
    records = [(n,k) for n,k in namelist.people.items()] + [(n,k) for n,k in namelist.organizations.items()]
    records += [(n,'place') for n in namelist.places]
    def position(row):
        forms = variants(*row)
        return next(((i, min(m.start() for v in forms for m in boundary(v).finditer(p.text)))
                     for i,p in enumerate(pages) if any(boundary(v).search(p.text) for v in forms)), (len(pages), 0))
    for name, kind in sorted(records, key=position):
        if kind in ('adjuster','provider','insurer') or name in namelist.keep:
            continue
        forms = variants(name, kind)
        for hit in hits:
            if hit.kind != 'anchor' and any(quotes.same(strip_title(hit.name), v) for v in forms):
                forms.extend(v for v in variants(hit.name, kind) if v not in forms)
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
        if re.fullmatch(r'\d{1,2}-\d{1,2}-\d{4}', compact):
            m,d,y = map(int, compact.split('-'))
            return date(y,m,d)
        return dates.parse(re.sub(r'([A-Za-z]+ \d{1,2}) (\d{4})', r'\1, \2', compact))
    except ValueError:
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
    return tag + ('\r\n' if '\r\n' in value else '\n' if '\n' in value else '')


def text(value, key, *, protected, namelist=None) -> str:
    """Transform each line, preserving protected syntax and newline counts."""
    if not value:
        return value
    keep = namelist.kept if namelist else getattr(key, "_keep", ())
    tokens = (*protected, *keep)
    value = _sub(GRAMMAR, lambda m: _allocate(key.srcs, 'SRC', m[0]), value, tokens, tags=False)
    for kind, pattern in PATTERNS:
        value = _sub(pattern, lambda m, k=kind: _allocate(key.refs, k.upper(), m[0]), value, tokens)
    # List ids must precede the date and bare-year readers.
    for identifier in sorted(namelist.ids if namelist else getattr(key, '_ids', ()), key=len, reverse=True):
        value = _sub(boundary(identifier), lambda m: _allocate(key.refs, 'ID', m[0]), value, tokens)
    dob = namelist.dob if namelist else key.refs.get('[DOB]', '')
    def full(m):
        label = value[value.rfind('\n', 0, m.start()) + 1:m.start()]
        labelled = re.search(r'\b(?:DOB|Date of Birth)\s*[:=]?\s*$', label, re.I)
        return _date_tag(m[0], key, m[0] if labelled else dob)
    value = _sub(FULL_DATE, full, value, tokens)
    def month(m):
        words = m[0].split()
        anchor = date.fromisoformat(key.anchor)
        offset = (int(words[-1]) - anchor.year)*12 + dates.MONTHS.index(words[0].casefold()) + 1 - anchor.month
        tag = f'[MONTH M{offset:+d}]'
        key.dates.setdefault(f'M{offset:+d}', [])
        if m[0] not in key.dates[f'M{offset:+d}']:
            key.dates[f'M{offset:+d}'].append(m[0])
        return tag + ('\n' if '\n' in m[0] else '')
    value = _sub(MONTH_DATE, month, value, tokens)
    def year(m):
        label = f'Y{int(m[0])-date.fromisoformat(key.anchor).year:+d}'
        seen = key.dates.setdefault(label, [])
        if m[0] not in seen:
            seen.append(m[0])
        return f'[YEAR {label}]'
    value = _sub(YEAR, year, value, tokens)
    value = _sub(DATE_REF, lambda m: _allocate(key.refs, 'DATE-REF', m[0]), value, tokens)
    forms = sorted(((v,tag) for tag,row in key.entities.items() for v in row['variants']), key=lambda p:len(p[0]), reverse=True)
    if forms:
        lookup = dict(forms)
        pattern = re.compile(r'(?<![\w\[])(?:' + '|'.join(re.escape(v) for v in dict(forms)) + r')(?![\w\]])')
        value = _sub(pattern, lambda m: lookup[m[0]], value, tokens)
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
    return replace(packet, options=convert(packet.options),
        facts=tuple(replace(f, **{k:convert(getattr(f,k)) for k in ('quote','text','provider','date')}) for f in packet.facts),
        pages=tuple(replace(p, text=convert(p.text)) for p in packet.pages),
        flags=tuple({k:convert(v) if k in ('about','abouts') else v for k,v in f.items()} for f in packet.flags))


def _canonical(tag, key):
    if tag in key.entities:
        return key.entities[tag]['name']
    if tag in key.refs:
        return key.refs[tag]
    if m := re.fullmatch(r'\[DATE D([+-]\d+)\]', tag):
        d = date.fromisoformat(key.anchor) + timedelta(days=int(m[1]))
        return f'{d.month}/{d.day}/{d.year}'
    if m := re.fullmatch(r'\[MONTH M([+-]\d+)\]', tag):
        anchor = date.fromisoformat(key.anchor)
        y,mo = divmod(anchor.year*12 + anchor.month-1 + int(m[1]),12)
        return f'{dates.MONTHS[mo].capitalize()} {y}'
    if m := re.fullmatch(r'\[YEAR Y([+-]\d+)\]', tag):
        return str(date.fromisoformat(key.anchor).year+int(m[1]))
    return tag


def restore(value, key) -> str:
    value = re.sub(r'(?<![\w\[])(DR-\d+)(?![\w\]])', r'[\1]', value)
    value = re.sub(r'(?<![\w\[])(D[+-]\d+)(?![\w\]])', r'[DATE \1]', value)
    value = TAG.sub(lambda m: _canonical(m[0],key), value)
    return TAG.sub(lambda m: key.srcs.get(m[0],m[0]),value)


def _known(tag, key):
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
        values = values or key.dates.get(label) or [_canonical(tag,key)]
        for value in values:
            next_end = m.end()
            if '\n' in value and quote[next_end:next_end+1] == '\n':
                next_end += 1
            candidate = prefix + quote[end:m.start()] + value
            if quotes.found_in(candidate, page.text) or quotes.match(candidate,page.text):
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


def check_code(data, key, namelist, pages) -> Verdict:
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
    for row in key.entities.values():
        for variant in row['variants']:
            wanted = quotes.fold(variant)
            for m in re.finditer(r'(?<!\w)' + re.escape(wanted) + r'(?!\w)', folded):
                start, end = source[m.start()], source[m.end()-1]+1
                if not any(start < b and end > a for a,b in hidden):
                    add(1,row['kind'],start)
    for identifier in (*namelist.ids, *([namelist.dob] if namelist.dob else []), *key.dates.get('DOB', [])):
        for m in boundary(identifier).finditer(value):
            if not inside(m):
                add(1,'dob' if _parsed(identifier) == _parsed(namelist.dob) and _parsed(identifier) is not None else 'id',m.start())
    exemptions = _spans(value, (*protected(pages), *namelist.kept))
    def exempt(m):
        return any(m.start()<b and m.end()>a for a,b in exemptions)
    for pattern in (FULL_DATE, MONTH_DATE, YEAR, DATE_REF):
        for m in pattern.finditer(value):
            if not exempt(m):
                add(2,'date',m.start())
    for kind,pattern in PATTERNS:
        for m in pattern.finditer(value):
            if not exempt(m):
                add(3,kind,m.start())
    for m in re.finditer(r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?)\s+[A-Z][\w-]*',value):
        if not exempt(m):
            add(3,'titled_name',m.start())
    cites = {p.page_id for p in pages} | {s for p in pages for s in p.stamps}
    for m in TAG.finditer(value):
        tag = m[0]
        generic = bool(GRAMMAR.fullmatch(tag) and ('n' in tag or tag in ('[CLAIMANT]','[EMPLOYER]','[DOB]')))
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


def drafter_rules():
    return ('Drafter rules (casefile-anon/1):\n'
        '1. Preserve every placeholder exactly, including brackets and signs.\n'
        '2. Use [CLAIMANT], [EMPLOYER] and [DOB] without numbers.\n'
        '3. Keep titles outside [DR-n], [ATTY-n] and [PERSON-n].\n'
        '4. Keep date offsets such as [DATE D+n], [MONTH M+n] and [YEAR Y+n].\n'
        '5. Preserve [ID-n], [DATE-REF-n] and all contact placeholders.\n'
        '6. Quote only supplied text and retain its supplied citation.\n'
        '7. Do not guess identities, dates or missing facts.\n')


def load_key(folder) -> Key:
    directory = Path(folder)/'anon'
    path = directory/'key.json'
    if not directory.exists():
        return Key()
    try:
        if directory.is_symlink() or path.is_symlink() or path.stat().st_mode & 0o077:
            raise AnonError('anon/key.json must be mode 600')
        data = jsonrepair.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data,dict) or set(data)!=set(Key.__dataclass_fields__) or data['convention']!='casefile-anon/1':
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
    for table in ('entities','refs','dates','srcs'):
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
