"""Read matter entries and ask the attorney once on an interactive terminal."""

from dataclasses import dataclass, field, replace
import json
import os
from pathlib import Path
import tomllib

WORKERS_COMP_ISSUES = ('permanency', 'termination', 'DCD', 'DACD', 'other')
OTHER_ISSUES = ('liability', 'treatment', 'other')
MATTER_TYPES = ('workers-comp', 'mva', 'slip-and-fall')
HEADER = ('matter_type', 'client_name', 'date_of_accident', 'treating_physician',
          'iab_hearing_number', 'hearing_date', 'plaintiffs')


class MatterInfoError(ValueError):
    """An attorney entry must be corrected before the task runs."""


@dataclass(frozen=True)
class MatterInfo:
    matter_type: str = ''
    client_name: str = ''
    date_of_accident: str = ''
    treating_physician: str = ''
    iab_hearing_number: str = ''
    hearing_date: str = ''
    plaintiffs: int = 1
    issues: tuple[str, ...] = ()
    standard: str = ''
    relief: str = ''
    roles: dict[str, str] = field(default_factory=dict)
    anon_employer: str = ''
    anon_dob: str = ''
    anon_ids: tuple[str, ...] = ()
    anon_places: tuple[str, ...] = ()
    anon_keep: tuple[str, ...] = ()
    anon_people: dict[str, str] = field(default_factory=dict)
    anon_organizations: dict[str, str] = field(default_factory=dict)
    folder: Path | None = field(default=None, compare=False)
    has_header: bool = field(default=False, compare=False)


def document(folder):
    path = Path(folder) / 'matter.toml'
    try:
        return tomllib.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise MatterInfoError(f'{path}: {exc}') from exc


def load(folder) -> MatterInfo:
    folder = Path(folder)
    data = document(folder)

    def refuse(key):
        raise MatterInfoError(f'{folder / "matter.toml"}: {key}: invalid or unknown value')

    unknown = data.keys() - {'number', 'binders', 'header', 'hearing', 'roles', 'anon'}
    if unknown:
        refuse(sorted(unknown)[0])
    for table, keys in (('header', set(HEADER)), ('hearing', {'issues','standard','relief'})):
        values = data.get(table, {})
        if not isinstance(values, dict):
            refuse(table)
        if values.keys() - keys:
            refuse(f'{table}.{sorted(values.keys() - keys)[0]}')
    header, hearing, roles = (data.get(key, {}) for key in ('header','hearing','roles'))
    for key, value in header.items():
        if key == 'plaintiffs':
            if type(value) is not int or value < 1:
                refuse('header.plaintiffs')
        elif not isinstance(value, str):
            refuse('header.' + key)
    kind = header.get('matter_type', '')
    if kind and kind not in MATTER_TYPES:
        refuse('header.matter_type')
    for key in ('standard','relief'):
        if key in hearing and not isinstance(hearing[key], str):
            refuse('hearing.' + key)
    issues = hearing.get('issues', [])
    allowed = WORKERS_COMP_ISSUES if kind == 'workers-comp' else OTHER_ISSUES if kind else ()
    if not isinstance(issues, list) or any(not isinstance(v, str) or v not in allowed for v in issues):
        refuse('hearing.issues')
    if not isinstance(roles, dict):
        refuse('roles')
    binders = data.get('binders', [])
    if not isinstance(binders, list) or any(not isinstance(b, str) for b in binders):
        refuse('binders')
    if (folder / 'pages').is_dir():
        binders = [p.name for p in (folder / 'pages').iterdir() if p.is_dir() and not p.name.startswith('.')]
    for binder, role in roles.items():
        if role not in ('defense','ours','other') or binder not in binders:
            refuse('roles.' + binder)
    anon = data.get('anon', {})
    anon_keys = {'employer', 'dob', 'ids', 'places', 'keep', 'people', 'organizations'}
    if not isinstance(anon, dict):
        refuse('anon')
    if anon.keys() - anon_keys:
        refuse('anon.' + sorted(anon.keys() - anon_keys)[0])
    for key in ('employer', 'dob'):
        if key in anon and not isinstance(anon[key], str):
            refuse('anon.' + key)
    for key in ('ids', 'places', 'keep'):
        if key in anon and (not isinstance(anon[key], list)
                            or any(not isinstance(v, str) for v in anon[key])):
            refuse('anon.' + key)
    for key, kinds in (('people', ('claimant', 'doctor', 'attorney', 'adjuster', 'person')),
                       ('organizations', ('employer', 'insurer', 'provider', 'other'))):
        values = anon.get(key, {})
        if not isinstance(values, dict):
            refuse('anon.' + key)
        for name, value in values.items():
            if not name.strip() or not isinstance(value, str) or value not in kinds:
                refuse(f'anon.{key}.{name}')
    anon_values = {'anon_' + key: tuple(value) if key in ('ids', 'places', 'keep') else value
                   for key, value in anon.items()}
    return MatterInfo(**header, issues=tuple(issues), standard=hearing.get('standard',''),
                      relief=hearing.get('relief',''), roles=roles, folder=folder,
                      has_header='header' in data, **anon_values)


def write(folder, info):
    """Replace only the attorney tables, preserving the layout and existing roles."""
    folder = Path(folder)
    data = document(folder)
    data.setdefault('number', folder.name)
    data['header'] = {key: getattr(info,key) for key in HEADER}
    hearing = data.setdefault('hearing', {})
    hearing.update(issues=list(info.issues), standard=info.standard, relief=info.relief)
    if info.roles:
        data['roles'] = info.roles
    data['anon'] = {key: getattr(info, 'anon_' + key) for key in
                    ('employer', 'dob', 'ids', 'places', 'keep', 'people', 'organizations')}
    lines = []
    for key,value in data.items():
        if not isinstance(value, dict):
            lines.append(f'{json.dumps(key)} = {json.dumps(value, ensure_ascii=False)}')
    for key,value in data.items():
        if isinstance(value, dict):
            lines.append(f'\n[{json.dumps(key)}]')
            lines.extend(f'{json.dumps(k)} = {json.dumps(v, ensure_ascii=False)}'
                         for k,v in value.items() if not isinstance(v, dict))
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict):
                    lines.append(f'\n[{json.dumps(key)}.{json.dumps(subkey)}]')
                    lines.extend(f'{json.dumps(k)} = {json.dumps(v, ensure_ascii=False)}'
                                 for k,v in subvalue.items())
    path = folder / 'matter.toml'
    temporary = folder / 'matter.toml.tmp'
    try:
        with temporary.open('x', encoding='utf-8') as stream:
            stream.write('\n'.join(lines) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise MatterInfoError(f'{temporary}: cannot write matter entries: {exc}') from exc
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def ask(info, stdin, stdout) -> MatterInfo:
    if info.has_header:
        return info
    if not stdin.isatty():
        for key in (*HEADER[:-1], 'issues'):
            print(f'{key}: NEEDED', file=stdout)
        return info

    def answer(label):
        print(label + ': ', end='', file=stdout, flush=True)
        value = stdin.readline().strip()
        if not value:
            print('NEEDED', file=stdout)
        return value

    kind = answer('Matter type (workers-comp, mva, slip-and-fall)')
    if kind and kind not in MATTER_TYPES:
        raise MatterInfoError('header.matter_type: invalid value')
    values = {key: answer(key.replace('_',' ').capitalize()) for key in HEADER[1:-1]}
    raw_plaintiffs = answer('Number of plaintiffs (blank means 1)')
    try:
        plaintiffs = int(raw_plaintiffs) if raw_plaintiffs else 1
        if plaintiffs < 1:
            raise ValueError
    except ValueError as exc:
        raise MatterInfoError('header.plaintiffs: expected a positive integer') from exc
    choices = WORKERS_COMP_ISSUES if kind == 'workers-comp' else OTHER_ISSUES
    raw = answer('Issues (' + ', '.join(f'{n}: {v}' for n,v in enumerate(choices,1)) + ')')
    try:
        indices = [int(v.strip()) for v in raw.split(',')] if raw else []
        if any(n < 1 or n > len(choices) for n in indices) or (indices and not kind):
            raise ValueError
        issues = tuple(dict.fromkeys(choices[n-1] for n in indices))
    except ValueError as exc:
        raise MatterInfoError('hearing.issues: expected comma-separated choice numbers') from exc
    result = replace(info, matter_type=kind, **values, plaintiffs=plaintiffs, issues=issues, has_header=True)
    if info.folder is not None:
        write(info.folder, result)
    return result


def ask_roles(info, binders, stdin, stdout) -> MatterInfo:
    """Persist unresolved binder roles once, only on an interactive terminal."""
    from casefile import roles

    if not stdin.isatty():
        return info
    selected = dict(info.roles)
    for binder in dict.fromkeys(binders):
        if roles.role(binder, info) != 'ROLE NEEDED':
            continue
        print(f'Binder {binder}: defense, ours or other: ', end='', file=stdout, flush=True)
        value = stdin.readline().strip()
        if value not in ('defense', 'ours', 'other'):
            raise MatterInfoError(f'roles.{binder}: expected defense, ours or other')
        selected[binder] = value
    if selected == info.roles:
        return info
    result = replace(info, roles=selected)
    if info.folder is not None:
        write(info.folder, result)
    return result
