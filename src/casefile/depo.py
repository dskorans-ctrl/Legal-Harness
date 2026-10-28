"""Deposition packages assembled from checked evidence and gated JSON answers."""

from dataclasses import replace
import re

from casefile import cards, outputs, packet, quotes

CARD_IDS = {'our-doctor': '02-C-OURDOC', 'defense-doctor': '02-C-DEFDOC',
            'client': '02-C-CLIENT', 'witness': '02-C-WITNESS'}
SECTIONS = ('primary', 'cross', 'redirect')
TITLES = ('Questions: primary', 'Questions: anticipated cross', 'Questions: redirect')


def prepare(casefile, pages, book, info, *, number, deponent, taken_by, purpose='discovery',
            provider='', binder=(), selected=None):
    own = outputs.select_pages(casefile, pages, provider=provider, binder=binder, selected=selected,
                               doctor=deponent.endswith('doctor'), info=info)
    return packet.build(casefile, pages, matter=number, task='depo', options=dict(
        deponent=deponent, taken_by=taken_by, purpose=purpose, deponent_pages=[p.page_id for p in own]),
        playbook_version=book.version)


def question_packet(value, answer, section, card, num_ctx):
    labels = {fact.id: item['use'] for fact in value.facts for item in (answer or {}).get('facts', ())
              if quotes.same(fact.quote, item['quote']) and item['cite'] in (fact.cite, fact.page_id)}
    return packet.fit(replace(value, options={**value.options, 'labels': labels, 'section': section}), card, num_ctx)


def missing_questions(answer, options):
    if options['deponent'] != 'our-doctor' or options['taken_by'] != 'us' or answer is None:
        return []
    return [f'Missing: the {name} question (firm practice: two separate questions)' for name, pattern in
            (('treatment', r'\btreatment\b'), ('bills', r'\bbills?\b'))
            if not any(re.search(pattern, item['text'], re.I) and not (re.search(r'\btreatment\b', item['text'], re.I) and re.search(r'\bbills?\b', item['text'], re.I)) for item in answer['questions'])]


def render(answers, packet, casefile, pages, info, *, open_items, playbook_version, model):
    options = packet.options
    header = outputs.header(info, packet.matter, 'depo', when=options.get('when', ''),
                            deponent=options.get('name') or options['deponent'])
    header.extend(outputs.page_warning(pages))
    header += [outputs.p('Purpose: ' + options['purpose']), outputs.build_line(casefile, playbook_version, model)]
    labels = answers.get('factsheet')
    failures = options.get('failures', {})
    extra = outputs.needed(info, pages)
    sections = []
    for title, uses in (('Case outline: our view', ('our_case', 'both')),
                        ('Case outline: the defense view', ('defense_case', 'both'))):
        paragraphs = (outputs.grouped(outputs.labelled_facts(labels, casefile, uses), pages) if labels is not None
                      else [outputs.failure(title, failures.get('factsheet'))])
        paragraphs.append(outputs.p('', page_break=True))
        sections.append(outputs.Section(title, paragraphs))
    if labels is None:
        extra.append('factsheet: failed section')
    points = []
    for section, title in zip(SECTIONS, TITLES):
        key = 'questions:' + section
        answer = answers.get(key)
        paragraphs = outputs.question_paragraphs(answer, title, reason=failures.get(key),
                                                omitted=options.get('omitted', {}).get(section, 0),
                                                bills_question=options['deponent'] == 'our-doctor')
        if section == 'primary':
            missing = missing_questions(answer, options)
            paragraphs = [outputs.p(text) for text in missing] + paragraphs
            extra.extend(missing)
        if answer is None:
            extra.append(key + ': failed section')
        else:
            for item in answer['points_for_our_expert']:
                points += [outputs.evidence(item), outputs.note(item['text'])]
        sections.append(outputs.Section(title, paragraphs))
    danger = []
    for item in (labels or {}).get('facts', ()):
        if item['use'] == 'danger':
            danger += [outputs.evidence(item), outputs.note(item['note'] or 'none given')]
    sections += [outputs.Section('Danger zone', danger), outputs.Section('Points for our expert', points),
                 outputs.open_items_section(open_items, extra)]
    return outputs.Doc('Deposition preparation', header, sections)


def run(config, number, *, out, err, opener=None, deponent, taken_by, purpose='discovery',
        provider='', binder=(), selected=None, pages=None, name='', when=''):
    try:
        if deponent not in CARD_IDS or taken_by not in ('us', 'defense') or purpose not in ('discovery', 'trial'):
            raise outputs.OutputError('invalid deponent, taken-by or purpose')
        with outputs.start(config, number, 'depo', opener=opener, out=out) as started:
            value = prepare(started.casefile, started.loaded.pages, started.book, started.info, number=number,
                            deponent=deponent, taken_by=taken_by, purpose=purpose, provider=provider,
                            binder=binder, selected=selected or pages)
            answers, failures, omitted = {}, {}, {}
            card = cards.card('02-A', started.book)
            merged = []
            for part in packet.batches(value, card, config.model.num_ctx):
                outcome = outputs.ask(part, card, client=started.client, rules=started.book.rules,
                    log=started.log, job='depo', playbook_version=started.book.version)
                if not outcome.ok:
                    failures['factsheet'] = outputs.failure_reason(outcome)
                    break
                merged.extend(outcome.answer['facts'])
            answers['factsheet'] = None if failures else {'facts': merged}
            card = cards.card(CARD_IDS[deponent], started.book)
            for section in SECTIONS:
                part = question_packet(value, answers['factsheet'], section, card, config.model.num_ctx)
                omitted[section] = part.options['omitted']
                outcome = outputs.ask(part, card, client=started.client, rules=started.book.rules,
                    log=started.log, job='depo', playbook_version=started.book.version)
                key = 'questions:' + section
                answers[key] = outcome.answer
                if not outcome.ok:
                    failures[key] = outputs.failure_reason(outcome)
            value.options.update(failures=failures, omitted=omitted, name=name, when=when)
            doc = render(answers, value, started.casefile, started.loaded.pages, started.info,
                         open_items=started.counts['open_items'], playbook_version=started.book.version,
                         model=config.model.name)
            return outputs.finish(started, f'depo-{deponent}-{taken_by}', doc, failed_steps=failures, out=out)
    except outputs.ERRORS as exc:
        print(f'depo: cannot run: {exc}', file=err)
        return 2
