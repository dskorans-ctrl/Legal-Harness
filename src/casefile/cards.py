"""Load the engine-neutral card contract and build text from the playbook."""

from dataclasses import dataclass
from pathlib import Path

from casefile import jsonrepair, playbook, rules, schema

ROOT = Path(__file__).resolve().parents[2]


class CardsError(ValueError):
    """A manifest or card must be corrected before running."""


@dataclass(frozen=True)
class Spec:
    id: str
    title: str
    file: Path
    schema: dict
    job: str | None
    stage: int
    kinds: tuple[str, ...]
    deponent: str | None
    question_keys: tuple[str, ...]
    numbers_in: str
    required_any: tuple[str, ...]
    optional_blank: tuple[str, ...]
    echo: str | None
    coverage: bool


def load(root=ROOT) -> dict[str, Spec]:
    root = Path(root)
    path = root / 'cards/manifest.json'
    try:
        data = jsonrepair.loads(path.read_text(encoding='utf-8'))
        if (not isinstance(data, dict) or set(data) != {'version', 'cards'}
                or type(data['version']) is not int or data['version'] != 2
                or not isinstance(data['cards'], list) or not data['cards']):
            raise CardsError(f'{path}: expected version 2 and a nonempty cards array')
        result, names = {}, set()
        fields = set(Spec.__dataclass_fields__)
        for row in data['cards']:
            if not isinstance(row, dict) or set(row) != fields:
                raise CardsError(f'{path}: unknown or missing card keys')
            for key in ('id', 'title', 'file', 'schema'):
                if not isinstance(row[key], str) or not row[key].strip():
                    raise CardsError(f'{path}: {key}: expected nonempty string')
            for key in ('kinds', 'question_keys', 'required_any', 'optional_blank'):
                if (not isinstance(row[key], list) or any(not isinstance(v, str) or not v
                                                         for v in row[key])
                        or len(set(row[key])) != len(row[key])):
                    raise CardsError(f'{path}: {key}: expected distinct strings')
            if (row['job'] not in (None, 'memo', 'depo', 'hearing', 'report')
                    or type(row['stage']) is not int or row['stage'] not in (6, 7, 8)
                    or row['deponent'] not in (None, 'our-doctor', 'defense-doctor', 'client', 'witness')
                    or row['numbers_in'] not in ('quote', 'page')
                    or row['echo'] not in (None, 'compared', 'pages_seen')
                    or type(row['coverage']) is not bool
                    or not set(row['kinds']) <= playbook.KINDS):
                raise CardsError(f'{path}: invalid card options for {row["id"]}')
            file, schema_path = root / row['file'], root / row['schema']
            for target in (file, schema_path):
                if not target.resolve().is_relative_to(root.resolve()) or not target.is_file():
                    raise CardsError(f'{path}: missing or outside file {target}')
            loaded = schema.load(schema_path)
            name = loaded.get('title')
            if row['id'] in result:
                raise CardsError(f'{path}: duplicate card id {row["id"]}')
            if not isinstance(name, str) or not name:
                raise CardsError(f'{schema_path}: title: expected card name')
            card_name = 'medical_memo' if row['id'] == '01-MEMO' else row['id']
            if card_name in names:
                raise CardsError(f'{path}: duplicate card name {card_name}')
            names.add(card_name)
            result[row['id']] = Spec(**{**row, 'file': file, 'schema': loaded,
                **{k: tuple(row[k]) for k in ('kinds','question_keys','required_any','optional_blank')}})
        return result
    except (OSError, UnicodeError, jsonrepair.RepairError, schema.SchemaError) as exc:
        raise CardsError(f'{path}: {exc}') from exc


def text(spec, book) -> str:
    from casefile.extract import ID_SENTENCE

    by_id = {rule.id: rule for rule in book.rules.rules}
    core = 'Firm rules:\n' + ''.join(f'{n}. {by_id[id].rule}\n'
                                         for n, id in enumerate(rules.RULE_IDS, 1))
    core += ('Use only the text in this request.\n'
             'Never guess, infer or fill in; leave out what is not on the page.\n'
             'Copy qualifiers, sides, dates, numbers and checkbox marks exactly as written.\n'
             'Say who said it.\nDo only the job on this card.\n')
    entries = [entry for entry in book.entries if isinstance(entry, playbook.Entry)
               and not entry.sample and entry.kind in spec.kinds
               and (entry.deponent is None or entry.deponent == spec.deponent)]
    practice = 'Practice:\n' + ''.join(f'- {e.rule} Good: {e.good} Bad: {e.bad}\n' for e in entries)
    return core + spec.file.read_text(encoding='utf-8').rstrip() + '\n' + practice + ID_SENTENCE


def card(id, book=None):
    from casefile.gates import Card

    book = playbook.load(ROOT / 'playbook') if book is None else book
    try:
        spec = load()[id]
    except KeyError as exc:
        raise CardsError(f'unknown card id {id}') from exc
    return Card('medical_memo' if id == '01-MEMO' else id, text(spec, book), spec.schema, coverage=spec.coverage,
                required_any=spec.required_any, optional_blank=spec.optional_blank,
                echo=spec.echo, question_keys=spec.question_keys, numbers_in=spec.numbers_in)
