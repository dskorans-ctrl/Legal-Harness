"""Hearing preparation from stored choices, verified facts and gated step answers."""

from dataclasses import replace
from datetime import date

from casefile import cards, dates, matterinfo, outputs, packet, report, roles

STARRED = '★ GIVE THE BILLING MEMO TO THE HEARING OFFICER. Hand it up at the outset with the exhibits.'
INSTRUCTIONS = ('Listen to the whole question; pause; answer only what was asked; do not guess; '
                '"I don\'t know" or "I don\'t remember" only when true; speak to the Hearing Officer; keep answers short.')
CONSISTENCY = ('patient_statement', 'mechanism_of_injury', 'prior_history')


def prepare(casefile, pages, book, info, *, number, outline=False, client=False, doctor=False,
            closing=False, provider='', binder=(), selected=None, issue=(), standard=None,
            relief=None, when=''):
    parts = dict(outline=outline, client=client, doctor=doctor, closing=closing)
    if not any(parts.values()):
        parts = dict.fromkeys(parts, True)
    issues = tuple(issue) if issue else info.issues
    allowed = matterinfo.WORKERS_COMP_ISSUES if info.matter_type == 'workers-comp' else matterinfo.OTHER_ISSUES if info.matter_type else ()
    if any(value not in allowed for value in issues):
        raise matterinfo.MatterInfoError('hearing.issues: choose from the matter type list: ' + ', '.join(allowed))
    choices = dict(parts=parts, issues=issues, standard=info.standard if standard is None else standard,
                   relief=info.relief if relief is None else relief, when=when,
                   deponent_pages=[p.page_id for p in pages])
    base = packet.build(casefile, pages, matter=number, task='hearing', options=choices,
                        playbook_version=book.version)
    result = {'base': base}
    if parts['outline'] or parts['closing']:
        for n, text in enumerate(issues, 1):
            result[f'factsheet:issue:{n}'] = replace(base, options={'issue': text})
    if parts['client']:
        for section in ('primary', 'cross'):
            result['questions:' + section] = replace(base, options={'section': section,
                'deponent_pages': [p.page_id for p in pages]})
    if parts['doctor']:
        # The same elements step is restorable for hearing preparation and our report analysis.
        result['elements'] = report.prepare(casefile, pages, book, info=info, number=number,
                                             provider=provider, binder=binder, selected=selected)
    return result


def step_card(key, book):
    return cards.card('02-A' if key.startswith('factsheet:') else
                      '03-CLIENT' if key.startswith('questions:') else '05-A', book)


def _gaps(casefile):
    result = []
    for flag in casefile.flags:
        if flag.kind == 'gap':
            result.append(outputs.Paragraph([outputs.Run('Gap: '), *[outputs.cite(c) for c in flag.cites]]))
            result.extend(outputs.p("Model's reading: " + text) for text in flag.abouts)
    return result or [outputs.p('none')]


def _chronological(records, pages):
    present = {page.page_id for page in pages}
    def key(fact):
        i = next((i for i,pid in enumerate(fact.page_ids) if pid in present), 0)
        return dates.parse(fact.dates[i]) or date.max
    return sorted(records, key=key)


def _closing_answer(casefile, pages, info, defense_ids):
    result = []
    for flag in casefile.flags:
        if flag.kind != 'conflict' or not set(flag.page_ids) & defense_ids:
            continue
        result.extend(outputs.p("Model's reading: " + text) for text in flag.abouts)
        pairs = sorted(zip(flag.page_ids, flag.cites), key=lambda pair: pair[0] not in defense_ids)
        for pid, cite in pairs:
            result.append(outputs.Paragraph([outputs.Run('From '), outputs.cite(cite), outputs.Run(':')]))
            result.extend(outputs.evidence(dict(quote=f.quote, cite=cite)) for f in casefile.facts if pid in f.page_ids)
    return result or [outputs.p('none')]


def render(answers, packets, casefile, pages, info, *, open_items, playbook_version, model):
    base = packets['base']
    choices, parts = base.options, base.options['parts']
    header_info = replace(info, hearing_date=choices['when']) if choices.get('when') else info
    header = outputs.header(header_info, base.matter, 'hearing')
    header.extend(outputs.page_warning(pages))
    header.append(outputs.build_line(casefile, playbook_version, model))
    checklist = [outputs.p(STARRED), outputs.p('Totals: not on file; the billing memo is supplied by the attorney (question 28).')]
    for binder in dict.fromkeys(p.binder for p in pages):
        entries = [p for p in pages if p.binder == binder]
        first, last = (p.stamps[0] if p.stamps else p.page_id for p in (entries[0], entries[-1]))
        checklist.append(outputs.Paragraph([outputs.Run('Exhibits to mark: '), outputs.Run(binder, exempt='binder'),
            outputs.Run(': '), outputs.cite(first), outputs.Run(' to '), outputs.cite(last),
            outputs.Run(f' ({len(entries)} pages)')]))
    checklist.extend(outputs.p(text) for text in ('Deposition transcripts to submit: none on file (transcripts are stage 8).',
                     'Witness availability: not on file.', 'Stipulations: none on file.'))
    sections = [outputs.Section('Pre-hearing checklist', checklist)]
    extra = outputs.needed(header_info, pages)
    failures = choices.get('failures', {})
    failed = [key for key in packets if key != 'base' and answers.get(key) is None]
    extra.extend(key + ': failed section' for key in failed)
    defense_ids = {p.page_id for p in pages if roles.role(p.binder, info) == 'defense'}
    issues = choices['issues']
    if (parts['outline'] or parts['closing']) and not issues:
        missing = ('Issues: NEEDED; answer the prompt at the next interactive run, add [hearing] issues '
                   'to matter.toml, or pass --issue "..." from the type\'s list.')
        extra.append(missing)
    if issues and (parts['outline'] or parts['closing']):
        if not choices['standard']:
            extra.append('STANDARD NEEDED')
        if parts['closing'] and not choices['relief']:
            extra.append('RELIEF NEEDED')
    if parts['outline']:
        paragraphs = [] if issues else [outputs.p(missing)]
        for n, issue in enumerate(issues, 1):
            key = f'factsheet:issue:{n}'
            answer = answers.get(key)
            if answer is None:
                paragraphs.append(outputs.failure('Issue: ' + issue, failures.get(key)))
            paragraphs += [outputs.p('Issue: ' + issue, level=2), outputs.p('Standard: ' + (choices['standard'] or 'STANDARD NEEDED')),
                           outputs.p('Our key facts', level=3)]
            paragraphs.extend(outputs.grouped(outputs.labelled_facts(answer, casefile, ('our_case','both')), pages))
            paragraphs += [outputs.p('Deposition designations: none on file.'), outputs.p('Defense position', level=3)]
            paragraphs.extend(outputs.grouped(outputs.labelled_facts(answer, casefile, ('defense_case','both')), pages))
            paragraphs.append(outputs.p('Conflicts', level=3))
            paragraphs.extend(outputs.conflicts(casefile, pages, info,
                              predicate=lambda flag: bool(set(flag.page_ids) & defense_ids)))
            paragraphs.append(outputs.p('Open items for this issue', level=3))
            paragraphs.extend(_gaps(casefile))
            paragraphs.extend(outputs.open_items_section(open_items).paragraphs)
        sections.append(outputs.Section('Hearing outline', paragraphs))
    if parts['client']:
        paragraphs = []
        for section, title in (('primary','Direct examination'),('cross','Likely cross')):
            key = 'questions:' + section
            paragraphs.append(outputs.p(title, level=2))
            paragraphs.extend(outputs.question_paragraphs(answers.get(key), title, reason=failures.get(key),
                              omitted=choices.get('omitted', {}).get(key, 0)))
        paragraphs.append(outputs.p('Consistency flags', level=2))
        paragraphs.extend(outputs.conflicts(casefile, pages, info, predicate=lambda flag: any(
            f.category in CONSISTENCY and set(f.page_ids) & set(flag.page_ids) for f in casefile.facts)))
        paragraphs.append(outputs.p(INSTRUCTIONS))
        sections.append(outputs.Section('Client preparation', paragraphs))
    if parts['doctor']:
        own = packets['elements']
        ids = set(own.options['report_pages'])
        records = [f for f in casefile.facts if set(f.page_ids) & ids]
        paragraphs = [outputs.p("What the doctor's records say", level=2), *outputs.grouped(records, own.pages),
                      outputs.p('Opinions the case needs', level=2)]
        elements, gaps, _ = outputs.elements(answers.get('elements'), own.pages,
                               title='Opinions the case needs', reason=failures.get('elements'))
        paragraphs.extend(elements.paragraphs)
        paragraphs += [outputs.p('Gaps', level=3), *(gaps.paragraphs or [outputs.p('none')]),
                       outputs.p('Defense report points to be ready for', level=2)]
        defense_opinions = [f for f in casefile.facts if f.category in outputs.GROUPS['Opinions']
                           and set(f.page_ids) & defense_ids]
        for fact in defense_opinions:
            paragraphs.extend(outputs.fact_paragraphs(fact, pages))
            paragraphs.extend(outputs.conflicts(casefile, pages, info,
                              predicate=lambda flag: bool(set(flag.page_ids) & set(fact.page_ids))))
        if not defense_opinions:
            paragraphs.append(outputs.p('none'))
        paragraphs += [outputs.p('Records the doctor may not have seen: not checked this round (no records audit card runs).'),
                       outputs.p("Conflicts between the doctor's records and other records", level=2)]
        paragraphs.extend(outputs.conflicts(casefile, pages, info,
                          predicate=lambda flag: bool(set(flag.page_ids) & ids)))
        sections.append(outputs.Section('Doctor preparation', paragraphs))
    if parts['closing']:
        paragraphs = [] if issues else [outputs.p(missing)]
        for n, issue in enumerate(issues, 1):
            key = f'factsheet:issue:{n}'
            answer = answers.get(key)
            if answer is None:
                paragraphs.append(outputs.failure('Closing: ' + issue, failures.get(key)))
            paragraphs += [outputs.p('Issue: ' + issue, level=2), outputs.p('Standard: ' + (choices['standard'] or 'STANDARD NEEDED')),
                           outputs.p('Our strongest facts', level=3)]
            for fact in _chronological(outputs.labelled_facts(answer, casefile, ('our_case','both')), pages):
                paragraphs.extend(outputs.fact_paragraphs(fact, pages))
            paragraphs.append(outputs.p('Defense says', level=3))
            for fact in outputs.labelled_facts(answer, casefile, ('defense_case',)):
                paragraphs.extend(outputs.fact_paragraphs(fact, pages))
            paragraphs += [outputs.p('Our answer', level=3), *_closing_answer(casefile, pages, info, defense_ids),
                           outputs.p('Relief requested: ' + (choices['relief'] or 'RELIEF NEEDED')),
                           outputs.p('No law is cited; the attorney supplies the standard and the relief.')]
        sections.append(outputs.Section('Closing outline', paragraphs))
    sections.append(outputs.open_items_section(open_items, extra))
    return outputs.Doc('Hearing preparation', header, sections)


def run(config, number, *, out, err, opener=None, outline=False, client=False, doctor=False,
        closing=False, provider='', binder=(), selected=None, pages=None, issue=(), standard=None,
        relief=None, when=''):
    try:
        with outputs.start(config, number, 'hearing', opener=opener, out=out) as started:
            values = prepare(started.casefile, started.loaded.pages, started.book, started.info,
                number=number, outline=outline, client=client, doctor=doctor, closing=closing,
                provider=provider, binder=binder, selected=selected or pages, issue=issue,
                standard=standard, relief=relief, when=when)
            answers, failures, omitted = {}, {}, {}
            for key, value in values.items():
                if key == 'base':
                    continue
                card = step_card(key, started.book)
                if key.startswith('questions:'):
                    value = packet.fit(value, card, config.model.num_ctx)
                    omitted[key] = value.options['omitted']
                    batches = [value]
                else:
                    batches = packet.batches(value, card, config.model.num_ctx)
                merged = {'searched_pages': []}
                for part in batches:
                    outcome = outputs.ask(part, card, client=started.client, rules=started.book.rules,
                        log=started.log, job='hearing', playbook_version=started.book.version)
                    if not outcome.ok:
                        failures[key] = outputs.failure_reason(outcome)
                        break
                    merged['searched_pages'].extend(p.page_id for p in part.pages)
                    for field, items in outcome.answer.items():
                        if isinstance(items, list):
                            merged.setdefault(field, []).extend(items)
                        else:
                            merged[field] = items
                answers[key] = None if key in failures else merged
            values['base'].options.update(failures=failures, omitted=omitted)
            doc = render(answers, values, started.casefile, started.loaded.pages, started.info,
                         open_items=started.counts['open_items'], playbook_version=started.book.version,
                         model=config.model.name)
            return outputs.finish(started, 'hearing', doc, failed_steps=failures, out=out)
    except outputs.ERRORS as exc:
        print(f'hearing: cannot run: {exc}', file=err)
        return 2
