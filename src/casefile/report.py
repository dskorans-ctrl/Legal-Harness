"""Report analysis from gated answers and durable case-file evidence."""

from casefile import cards, outputs, packet


def prepare(casefile, pages, book, *, number, provider='', binder=(), selected=None, defense=False, info=None):
    report_pages = outputs.select_pages(casefile, pages, provider=provider, binder=binder, selected=selected, info=info)
    ids = [page.page_id for page in report_pages]
    categories = set().union(*(outputs.GROUPS[key] for key in
                     ('History', 'Examination findings', 'Imaging', 'Diagnoses', 'Opinions')))
    records = [fact for fact in casefile.facts if set(fact.page_ids) & set(ids)
               or defense and fact.category in categories]
    result = packet.build(casefile, pages, matter=number, task='report',
                          options={'side': 'defense' if defense else 'ours', 'report_pages': ids},
                          playbook_version=book.version, facts=records)
    if not defense:
        result = packet.build(casefile, report_pages, matter=number, task='report',
                              options={'side': 'ours', 'report_pages': ids},
                              playbook_version=book.version,
                              facts=[f for f in casefile.facts if set(f.page_ids) & set(ids)])
    return result


def render(answers, packet, casefile, pages, info, *, open_items, playbook_version, model):
    options = packet.options
    ids = set(options['report_pages'])
    own_pages = tuple(page for page in pages if page.page_id in ids)
    records = [fact for fact in casefile.facts if set(fact.page_ids) & ids]
    header = outputs.header(info, packet.matter, 'report')
    header.extend(outputs.page_warning(pages))
    header.append(outputs.build_line(casefile, playbook_version, model))
    coverage = outputs.Section('Coverage', [outputs.Paragraph([
        outputs.Run('Report page: '), outputs.cite(page.stamps[0] if page.stamps else page.page_id),
        outputs.Run(': ' + ('open' if any(item.page_id == page.page_id for item in open_items) else 'read'))])
        for page in own_pages])
    sections = [coverage, outputs.Section('What the report states', outputs.grouped(records, own_pages)),
                outputs.Section('Conflicts with other records', outputs.conflicts(
                    casefile, pages, info, predicate=lambda flag: bool(set(flag.page_ids) & ids)))]
    failed, extra = [], outputs.needed(info, pages)
    step = 'concessions' if options['side'] == 'defense' else 'elements'
    answer = answers.get(step)
    reason = options.get('failures', {}).get(step)
    if answer is None:
        failed.append(step)
        extra.append(step + ': failed section')
    if options['side'] == 'defense':
        concessions = outputs.Section("Concessions (the report's own words)")
        labels = outputs.Section('Undefined labels')
        danger = outputs.Section('Danger zone')
        topics = outputs.Section('Candidate cross topics (document-based)')
        if answer is None:
            concessions.paragraphs.append(outputs.failure(concessions.title, reason))
        else:
            for item in answer['concessions']:
                concessions.paragraphs.append(outputs.evidence(item, item['type'] + ': '))
                topics.paragraphs.append(outputs.evidence(item, item['type'] + ': '))
            for item in answer['undefined_labels']:
                labels.paragraphs += [outputs.p("Model's note: " + item['label']), outputs.evidence(item)]
                labels.paragraphs.append(outputs.p('Findings the report gives:'))
                labels.paragraphs.extend(outputs.evidence(finding) for finding in item['supporting_findings'])
                if not item['supporting_findings']:
                    labels.paragraphs.append(outputs.p('none stated on the pages sent: ' + ', '.join(
                        page.stamps[0] if page.stamps else page.page_id for page in own_pages)))
                topics.paragraphs.append(outputs.evidence(item, "Model's note: " + item['label'] + ': '))
            for item in answer['danger_zone']:
                danger.paragraphs += [outputs.evidence(item), outputs.note(item['why'])]
        topics.paragraphs.extend(outputs.conflicts(casefile, pages, info,
                                predicate=lambda flag: bool(set(flag.page_ids) & ids)))
        topics.paragraphs.append(outputs.p("Records review audit: not built this round; the report's "
            'records-referenced statements are listed under What the report states for your own comparison.'))
        sections += [concessions, labels, danger, topics]
    else:
        elements, gaps, subjects = outputs.elements(answer, own_pages, reason=reason)
        from casefile.roles import role
        defense_ids = {page.page_id for page in pages if role(page.binder, info) == 'defense'}
        comparison = outputs.Section('Defense comparison', outputs.conflicts(casefile, pages, info,
            predicate=lambda flag: bool(set(flag.page_ids) & ids and set(flag.page_ids) & defense_ids)))
        sections += [elements, gaps, comparison, subjects]
    sections.append(outputs.open_items_section(open_items, extra))
    return outputs.Doc('Report analysis', header, sections)


def run(config, number, *, out, err, opener=None, provider='', binder=(), selected=None,
        pages=None, defense=False, ours=False):
    try:
        if defense == ours:
            raise outputs.OutputError('choose exactly one of --defense or --ours')
        with outputs.start(config, number, 'report', opener=opener, out=out) as started:
            value = prepare(started.casefile, started.loaded.pages, started.book, number=number,
                            provider=provider, binder=binder, selected=selected or pages, defense=defense, info=started.info)
            own_pages = [p for p in value.pages if p.page_id in value.options['report_pages']]
            if not own_pages:
                raise outputs.OutputError('no report pages selected')
            slug = binder[0] if len(binder) == 1 else (provider.lower().replace(' ', '-') if provider else
                    '-'.join(p.stamps[0] if p.stamps else p.page_id.replace('/', '-') for p in (own_pages[0], own_pages[-1])))
            if not slug or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in slug.lower()):
                slug = own_pages[0].binder
            step, card_id = ('concessions', '04-G') if defense else ('elements', '05-A')
            card = cards.card(card_id, started.book)
            answers, failures = {}, {}
            merged = {'searched_pages': []}
            for part in packet.batches(value, card, config.model.num_ctx):
                outcome = outputs.ask(part, card, client=started.client, rules=started.book.rules,
                    log=started.log, job='report', playbook_version=started.book.version)
                if not outcome.ok:
                    failures[step] = outputs.failure_reason(outcome)
                    break
                merged['searched_pages'].extend(p.page_id for p in part.pages)
                for key, items in outcome.answer.items():
                    merged.setdefault(key, []).extend(items)
            answers[step] = None if failures else merged
            value.options['failures'] = failures
            document = render(answers, value, started.casefile, started.loaded.pages, started.info,
                open_items=started.counts['open_items'], playbook_version=started.book.version, model=config.model.name)
            return outputs.finish(started, 'report-' + slug, document, failed_steps=failures, out=out)
    except outputs.ERRORS as exc:
        print(f'report: cannot run: {exc}', file=err)
        return 2
