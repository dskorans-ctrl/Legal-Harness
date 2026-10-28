"""Engine-neutral facts, cited pages and task choices for a synthesis step."""

from dataclasses import asdict, dataclass, replace
import json

from casefile import extract, gates, jsonrepair, model, pipeline
from casefile.matter import Page


@dataclass(frozen=True)
class PacketFact:
    id: str
    quote: str
    cite: str
    page_id: str
    date: str
    category: str
    provider: str
    text: str


@dataclass(frozen=True)
class Packet:
    matter: str
    task: str
    options: dict
    playbook_version: str
    facts: tuple[PacketFact, ...]
    pages: tuple[Page, ...]
    flags: tuple[dict, ...] = ()

    def body(self):
        choices = ' '.join(f'{key}={json.dumps(value, ensure_ascii=False, sort_keys=True)}'
                           for key, value in self.options.items()
                           if key not in ('labels', 'section', 'issue', 'omitted'))
        lines = [f'Matter {self.matter}', f'Task: {self.task} {choices}'.rstrip(), 'Facts:']
        own = self.options.get('deponent_pages', ())
        for fact in self.facts:
            marker = " [deponent's record]" if fact.page_id in own else ''
            lines.append(f'[{fact.id}] {fact.cite} ({fact.page_id}; {fact.date}, {fact.category}): '
                         f'"{fact.quote}"{marker}')
        lines.append('Pages:')
        lines.extend(extract.page_block(page) for page in self.pages)
        if 'labels' in self.options:
            lines.append('Labels:')
            lines.extend(f'[{key}] {value}' for key, value in self.options['labels'].items())
        if 'section' in self.options:
            lines.append('Section: ' + self.options['section'])
        if 'issue' in self.options:
            lines.append('Issue: ' + self.options['issue'])
        return '\n'.join(lines) + '\n'

    def to_json(self):
        return json.dumps(asdict(self), ensure_ascii=False, allow_nan=False)

    @classmethod
    def from_json(cls, text):
        data = jsonrepair.loads(text)
        return cls(data['matter'], data['task'], data['options'], data['playbook_version'],
                   tuple(PacketFact(**f) for f in data['facts']),
                   tuple(Page(**{**p, 'stamps': tuple(p['stamps'])}) for p in data['pages']),
                   tuple(data['flags']))


def build(casefile, pages, *, matter, task, options, playbook_version, facts=None):
    pages = tuple(pages)
    present = {page.page_id for page in pages}
    selected = []
    wanted_pages = set()
    for fact in casefile.facts if facts is None else facts:
        primary = next((i for i, pid in enumerate(fact.page_ids) if pid in present), 0)
        selected.append(PacketFact(fact.id, fact.quote, fact.cites[primary], fact.page_ids[primary],
                                   fact.dates[primary], fact.category, fact.providers[primary],
                                   fact.readings[0]))
        wanted_pages.update(pid for pid in fact.page_ids if pid in present)
    # Explicit report/deponent pages include records without an extracted fact.
    wanted_pages.update(options.get('deponent_pages', ()))
    wanted_pages.update(options.get('report_pages', ()))
    return Packet(matter, task, dict(options), playbook_version, tuple(selected),
                  tuple(p for p in pages if p.page_id in wanted_pages),
                  tuple(asdict(flag) for flag in casefile.flags))


def _subset(packet, facts):
    ids = {fact.page_id for fact in facts}
    return replace(packet, facts=tuple(facts), pages=tuple(p for p in packet.pages if p.page_id in ids))


def batches(packet, card, num_ctx):
    """Split by facts with their source pages and reserve the same retry space as extraction."""
    budget = num_ctx - card.max_answer_tokens - pipeline.RETRY_MARGIN

    def size(part):
        return sum(model.tokens_at_most(m['content']) for m in gates.messages(
            card, part.pages, '0' * 16, matter=part.matter, body=part.body())) + model.TEMPLATE_TOKENS

    # Use the shared splitter for the lower bound; complete bodies also account for shared pages.
    pipeline.batches([fact.quote for fact in packet.facts], budget)
    result, current = [], []
    for fact in packet.facts:
        alone = _subset(packet, [fact])
        if size(alone) > budget:
            page = next((p for p in alone.pages if p.page_id == fact.page_id), None)
            count = model.tokens_at_most(page.text) if page else 0
            overhead = size(replace(alone, facts=(), pages=()))
            raise ValueError(f'page too long for one prompt ({count} bytes, budget '
                             f'{budget - overhead} bytes); split the binder')
        if current and size(_subset(packet, [*current, fact])) > budget:
            result.append(_subset(packet, current))
            current = []
        current.append(fact)
    if current:
        result.append(_subset(packet, current))
    if len(result) <= 1 and size(packet) <= budget:
        return [packet]
    return result


def fit(packet, card, num_ctx):
    """Prioritize the deponent's records for one question call and disclose omissions."""
    own = packet.options.get('deponent_pages', ())
    ordered = sorted(packet.facts, key=lambda fact: fact.page_id not in own)
    chosen = []

    def subset(records):
        part = _subset(packet, records)
        ids = {p.page_id for p in part.pages} | set(own)
        return replace(part, pages=tuple(p for p in packet.pages if p.page_id in ids))
    for fact in ordered:
        trial = subset([*chosen, fact])
        if sum(model.tokens_at_most(m['content']) for m in gates.messages(
                card, trial.pages, '0' * 16, matter=packet.matter, body=trial.body())) + model.TEMPLATE_TOKENS <= (
                num_ctx - card.max_answer_tokens - pipeline.RETRY_MARGIN):
            chosen.append(fact)
    part = subset(chosen)
    return replace(part, options={**part.options, 'omitted': len(packet.facts) - len(chosen)})
