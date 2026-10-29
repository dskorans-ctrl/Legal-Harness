"""Gated entity discovery and fail-closed identifier checks for a local matter."""

from collections import Counter
from dataclasses import replace
import sys

from casefile import anon, cards, dates, gates, matterinfo, model, pipeline, quotes, stamps

Hit = anon.Hit


class EntityError(anon.AnonError):
    """The local entity pass could not be verified; no package may be published."""


class NameListNeeded(anon.AnonError):
    """The attorney must resolve an unlisted name before replacement."""

    code = 2


class Hits(list):
    """Name hits plus independently verified anchor votes and their audit runs."""

    def __init__(self):
        super().__init__()
        self.anchors = []
        self.run_ids = []
        self.log = None


class _PrivateLog:
    """Keep raw answers private while removing values from exported diagnostics."""

    def __init__(self, log, step):
        self.log, self.step = log, step

    def __getattr__(self, key):
        return getattr(self.log, key)

    def record_failure(self, run_id, gate, message):
        self.log.record_failure(run_id, gate, f'step={self.step} kind={gate.split(".")[-1]} offset=0')

    def record_gate(self, run_id, *, attempt, gate, verdict, message):
        safe = f'step={self.step} kind={gate.split(".")[-1]} offset=0' if message else ''
        self.log.record_gate(run_id, attempt=attempt, gate=gate, verdict=verdict, message=safe)


def entity_pass(pages, *, client, rules, log, matter, playbook_version, job, step=1) -> list[Hit]:
    """Return only page-verified names and anchor votes, preserving page order."""
    pages = tuple(pages)
    card = cards.card('07-ANON')
    chunks, refused = pipeline.chunk(card, pages, client.config.num_ctx, matter)
    private = _PrivateLog(log,step)
    if refused or not chunks:
        for page, reason in refused:
            pipeline.refuse(page, reason, card=card, client=client, log=private, matter=matter,
                            playbook_version=playbook_version, job=job)
        raise EntityError(f'step={step} kind=model offset=0')
    result = Hits()
    result.log = log
    order = {p.page_id:i for i,p in enumerate(pages)}
    for part in chunks:
        try:
            outcome = gates.ask(card,part,client=client,rules=rules,log=private,matter=matter,
                playbook_version=playbook_version,job=job,echo=('pages_seen',[p.page_id for p in part]))
        except model.ModelError as exc:
            raise EntityError(f'step={step} kind=model offset=0') from exc
        result.run_ids.append(outcome.run_id)
        if not outcome.ok:
            raise EntityError(f'step={step} kind=model offset=0')
        def lookup(cite):
            return next(p for p in part if cite==p.page_id or stamps.normalize(cite) in p.stamps)
        for group in ('people','organizations','places'):
            for row in outcome.answer[group]:
                page = lookup(row['cite'])
                if not quotes.found_in(row['name'],page.text):
                    log.record_failure(outcome.run_id,'gate.identifier',
                                       f'hit dropped: name not on {page.page_id}')
                    continue
                hit = Hit(row['name'],row.get('kind','place'),row['quote'],row['cite'],page.page_id)
                if not any(quotes.same(hit.name,old.name) and hit.kind==old.kind for old in result):
                    result.append(hit)
        for row in outcome.answer['anchor_dates']:
            parsed = dates.parse(row['date'])
            written = [anon._parsed(m[0]) for m in anon.FULL_DATE.finditer(row['quote'])]
            if parsed is not None and parsed in written:
                result.anchors.append(Hit(row['date'],'anchor',row['quote'],row['cite'],lookup(row['cite']).page_id))
    def position(hit):
        page = next(p for p in pages if p.page_id==hit.page_id)
        return order[hit.page_id], quotes.normalize(page.text).find(quotes.normalize(hit.name))
    result.sort(key=position)
    return result


def _members(namelist, hit):
    return anon.members(namelist, hit.name)


def halt(namelist, hits, stdin, stdout):
    """Ask once per unlisted name on a tty, or stop without a write."""
    unknown = []
    for hit in hits:
        if hit.kind=='anchor' or anon.is_kept(namelist, hit.name):
            continue
        members = _members(namelist,hit)
        if len(members)==1:
            continue
        if len(members)>1:
            print('NAME LIST NEEDED: ambiguous name; add an alias to matter.toml [anon.aliases] with its listed full name',file=stdout)
            raise NameListNeeded('NAME LIST NEEDED')
        if not any(quotes.same(hit.name,h.name) for h in unknown):
            unknown.append(hit)
    if not unknown:
        return namelist
    if not stdin.isatty():
        detail = '; '.join(f'{h.kind} ({h.cite})' for h in unknown)
        print(f'NAME LIST NEEDED: {len(unknown)} names found on the pages are not in matter.toml [anon]: {detail}; '
              'add a listed name or an alias in [anon.aliases] with its listed full name',file=stdout)
        raise NameListNeeded('NAME LIST NEEDED')
    people, organizations = dict(namelist.people),dict(namelist.organizations)
    aliases = dict(namelist.aliases)
    places, kept = list(namelist.places),list(namelist.keep)
    for hit in unknown:
        choices = ('claimant','doctor','attorney','adjuster','person') if hit.kind in (
            'claimant','doctor','attorney','adjuster','person') else ('employer','insurer','provider','other') if hit.kind!='place' else ('place',)
        unnumbered = hit.kind in ('claimant', 'employer') and any(k == hit.kind for k in
            (*people.values(), *organizations.values()))
        default = 'alias' if unnumbered else hit.kind
        print(f'Name {hit.name} ({hit.cite}): {", ".join((*choices,"alias","keep"))} [{default}]: ',
              end='',file=stdout,flush=True)
        selected = stdin.readline().strip() or default
        if selected not in (*choices,'alias','keep'):
            raise NameListNeeded('NAME LIST NEEDED: choose a listed kind or keep')
        name = anon.strip_title(hit.name)
        if selected == 'alias' or (unnumbered and selected == hit.kind):
            print('Listed full name for this alias: ', end='', file=stdout, flush=True)
            target = stdin.readline().strip()
            records = {**people, **organizations, **{p: 'place' for p in places}}
            if target not in records:
                raise NameListNeeded('NAME LIST NEEDED: use a listed full name in matter.toml [anon.aliases]')
            aliases[hit.name] = target
        elif selected=='keep':
            kept.append(hit.name)
        elif selected=='place':
            places.append(hit.name)
        elif selected in ('claimant','doctor','attorney','adjuster','person'):
            people[name]=selected
        else:
            organizations[name]=selected
    result = replace(namelist,people=people,organizations=organizations,places=tuple(places),keep=tuple(kept),aliases=aliases)
    if namelist.info is not None and namelist.folder is not None:
        info = replace(namelist.info,anon_people=people,anon_organizations=organizations,
                       anon_places=tuple(places),anon_keep=tuple(kept),anon_aliases=aliases)
        matterinfo.write(namelist.folder,info)
        result = replace(result,info=info)
    return result


def anonymize(packet, *, folder, info, hits):
    """Choose the verified anchor, then persist stable numbering inside the matter."""
    listed = anon.names(info)
    votes = Counter(dates.iso(h.name) for h in getattr(hits,'anchors',()) if dates.parse(h.name))
    winner = votes.most_common(1)[0][0] if votes else ''
    # A tie is not a majority, so it cannot supply a missing attorney anchor.
    if votes and votes[winner] * 2 <= sum(votes.values()):
        winner = ''
    anchor = dates.iso(info.date_of_accident) if info.date_of_accident else winner
    if not anchor:
        raise anon.AnonError('ANCHOR NEEDED: add date_of_accident to matter.toml [header]')
    if winner and info.date_of_accident and anchor != winner:
        if sys.stderr.isatty():
            print(f'anchor: the pages say {winner}; matter.toml says {info.date_of_accident}',file=sys.stderr)
        else:
            print('anchor: verified pages disagree with matter.toml; using typed date',file=sys.stderr)
    log = getattr(hits,'log',None)
    if log is not None and votes and hits.run_ids:
        log.record_gate(hits.run_ids[0],attempt=1,gate='gate.identifier',verdict='pass',
                        message=f'anchor: verified votes={sum(votes.values())}')
    key = anon.load_key(folder)
    if key.anchor and key.anchor!=anchor:
        raise anon.AnonError('anon/key.json cannot change anchor')
    key.anchor = anchor
    anon.mapping(listed,hits,packet.pages,key)
    anonymous = anon.packet(packet,key)
    anon.save_key(folder,key)
    return anonymous,key


def _record(verdict, log, run_id, stdout):
    for step,kind,offset in verdict.hits:
        message = f'step={step} kind={kind} offset={offset}'
        if log is not None and run_id is not None:
            log.record_failure(run_id,'gate.identifier',message)
        if stdout is not None:
            print(message,file=stdout)
    return verdict


def check(data, key, namelist, pages, *, client, rules, log, matter, playbook_version,
          job='brief',run_id=None,stdout=None,cite_pages=None) -> anon.Verdict:
    """Block before any model request when code finds an identifier in output bytes."""
    if run_id is None and log is not None:
        row = log.connection.execute(
            "SELECT id FROM runs WHERE matter=? AND job=? AND card='07-ANON' ORDER BY id DESC LIMIT 1",
            (matter,job)).fetchone()
        run_id = row[0] if row is not None else None
    verdict = anon.check_code(data,key,namelist,pages,cite_pages=cite_pages)
    if not verdict.ok:
        return _record(verdict,log,run_id,stdout)
    try:
        hits = entity_pass(pages,client=client,rules=rules,log=log,matter=matter,
                           playbook_version=playbook_version,job=job,step=4)
    except (EntityError,model.ModelError):
        verdict = anon.Verdict(False,((4,'model',0),))
        return _record(verdict,log,run_id,stdout)
    blocked=[]
    value=data.decode('utf-8')
    for hit in hits:
        if anon.GRAMMAR.fullmatch(hit.name) or anon.is_kept(namelist, hit.name):
            continue
        # Only the attorney's kept entries authorize cleartext, regardless of the model's kind.
        offset=value.find(hit.name)
        blocked.append((4,'person' if hit.kind in ('claimant','doctor','attorney','adjuster','person') else
                        'place' if hit.kind=='place' else 'organization',len(value[:offset].encode('utf-8')) if offset>=0 else 0))
    verdict=anon.Verdict(not blocked,tuple(blocked))
    return _record(verdict,log,run_id if run_id is not None else hits.run_ids[0],stdout)
