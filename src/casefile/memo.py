"""Build the interim medical memo from case file evidence (D41)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from docx import Document

from casefile.rules import Finding, Rules


class MemoError(ValueError):
    """The memo cannot be checked or written."""


@dataclass(frozen=True)
class OpenItem:
    page_id: str
    label: str
    status: str
    reason: str


@dataclass(frozen=True)
class Run:
    text: str
    exempt: str = ""


@dataclass
class Paragraph:
    runs: list[Run]
    level: int | None = None
    warning_pages: tuple[str, ...] = ()


@dataclass
class Section:
    title: str
    paragraphs: list[Paragraph] = field(default_factory=list)


@dataclass
class Memo:
    title: str
    built: str
    sections: list[Section]
    pages: tuple


def label(page):
    return f'{" ".join(page.stamps)} ({page.page_id})' if page.stamps else page.page_id


def _cite(cite, page_id, prefix=""):
    text = f'[page {page_id}]' if cite == page_id else f'[cite {cite}]'
    return Run(prefix + text, exempt="cite")


def _paragraph(text):
    return Paragraph([Run(text)])


def _added(count, noun):
    return f'{count} {noun}{"" if count == 1 else "s"} added'


def _citations(cites, page_ids, *, prefix="", suffix=""):
    runs = [Run(prefix)] if prefix else []
    for index, (cite, page_id) in enumerate(zip(cites, page_ids)):
        if index:
            runs.append(Run(" and "))
        runs.append(_cite(cite, page_id))
    if suffix:
        runs.append(Run(suffix))
    return Paragraph(runs)


def _fact_paragraphs(fact, primary, heading_page, *, detail=False, binder=""):
    runs = []
    if detail:
        runs.append(Run(f'{fact.dates[primary]}, '))
        runs.append(Run(fact.providers[primary]) if fact.providers[primary]
                    else Run(binder, exempt="binder"))
        runs.append(Run(f', {fact.category}: '))
    runs.extend([Run(f'"{fact.quote}"', exempt="quote"),
                 _cite(fact.cites[primary], fact.page_ids[primary], " ")])
    paragraphs = [Paragraph(runs)]
    others = [(cite, page_id) for index, (cite, page_id) in
              enumerate(zip(fact.cites, fact.page_ids)) if index != primary]
    if others:
        paragraphs.append(_citations([c for c, _ in others], [p for _, p in others], prefix="Also cited: "))
    for reading, page_id in zip(fact.readings, fact.reading_pages):
        runs = [Run("Model's reading")]
        if page_id != heading_page:
            cite = fact.cites[fact.page_ids.index(page_id)]
            runs.extend([Run(" of "), _cite(cite, page_id)])
        runs.append(Run(f": {reading}"))
        paragraphs.append(Paragraph(runs))
    return paragraphs


def build(casefile, pages, open_items, *, matter, playbook_version, model, info=None) -> Memo:
    from casefile import dates, matterinfo, roles

    info = info if info is not None else matterinfo.MatterInfo()
    pages = tuple(pages)
    open_items = tuple(open_items)
    previous = next((event for event in reversed(casefile.events)
                     if event.kind == "output" and event.payload["name"] == "memo"), None)
    if previous is None:
        changed = "First memo for this matter"
    else:
        counts = casefile.changed_since(previous.seq)
        changed = ", ".join(_added(count, noun) for count, noun in (
            (counts["fact"], "fact"), (counts["cite"], "cite"),
            (counts["fact"] + counts["reading"], "reading"), (counts["flag"], "flag")))
        if counts["about"]:
            changed += ", " + _added(counts["about"], "flag reading")
    changes = Section("What changed since the last memo", [_paragraph(changed)])
    stale = Section("Outputs out of date", [_paragraph(
        ", ".join(name for name in casefile.stale_outputs() if name != "memo") or "none")])
    opened = Section("Open items", [Paragraph([
        Run(item.label, exempt="cite"), Run(f': {item.status}: '), Run(item.reason, exempt="reason")])
        for item in open_items] or [_paragraph("none")])
    records = casefile.facts
    present = {page.page_id: page for page in pages}
    placement = {fact.id: next((index for index, page_id in enumerate(fact.page_ids)
                               if page_id in present), None) for fact in records}
    chronology = Section("Treatment chronology")
    dated = [(fact, placement[fact.id]) for fact in records
             if placement[fact.id] is not None and fact.dates[placement[fact.id]]]
    for fact, primary in sorted(dated, key=lambda pair: dates.parse(pair[0].dates[pair[1]])):
        page = present[fact.page_ids[primary]]
        chronology.paragraphs.extend(_fact_paragraphs(fact, primary, page.page_id,
                                                     detail=True, binder=page.binder))
    providers = Section("Providers")
    associations = {}
    for fact in records:
        for index, provider in enumerate(fact.providers):
            if provider:
                associations.setdefault(provider, []).append((fact.dates[index], fact.cites[index], fact.page_ids[index]))
    for provider, entries in associations.items():
        ordered = sorted((d for d, _, _ in entries if dates.parse(d)), key=dates.parse)
        pairs = list(dict.fromkeys((c, p) for _, c, p in entries))
        providers.paragraphs.append(_citations([c for c, _ in pairs], [p for _, p in pairs],
            prefix=f'{provider}: first {ordered[0] if ordered else "NEEDED"}, '
                   f'last {ordered[-1] if ordered else "NEEDED"}, pages '))
    diagnoses = Section("Diagnoses")
    restrictions = Section("Restrictions and work status")
    history = Section("Medical history")
    opinions = {role: Section(title) for role, title in (
        ("ours", "Our doctors' opinions"), ("defense", "Defense doctors' opinions"),
        ("other", "Opinions in other records"))}
    binder_roles = {page.binder: roles.role(page.binder, info) for page in pages}
    for role, section in opinions.items():
        if role not in binder_roles.values():
            section.paragraphs.append(_paragraph(f'ROLE NEEDED: no binder is marked {role} in matter.toml'))
        missing_roles = [binder for binder, value in binder_roles.items() if value == "ROLE NEEDED"]
        if missing_roles:
            section.paragraphs.append(Paragraph([Run('ROLE NEEDED: edit [roles] in matter.toml for '),
                Run(', '.join(missing_roles), exempt="binder"), Run('.')]))
    for fact in records:
        primary = placement[fact.id]
        if primary is None:
            continue
        page = present[fact.page_ids[primary]]
        targets = []
        if fact.category in {"diagnosis", "imaging_result"}:
            targets.append(diagnoses)
        if fact.category == "work_status":
            targets.append(restrictions)
        if fact.category in {"prior_history", "family_history", "comorbidity_social"}:
            history.paragraphs.append(_paragraph(fact.category + ":"))
            targets.append(history)
        if fact.category in {"causation_statement", "mmi_statement", "impairment_rating",
                             "future_treatment", "work_status", "diagnosis"}:
            role = binder_roles[page.binder]
            if role in opinions:
                targets.append(opinions[role])
        for target in targets:
            target.paragraphs.extend(_fact_paragraphs(fact, primary, page.page_id))
    runs = {run["run_id"] for run in casefile.runs if run["job"] == "memo" and run["read"]}
    conflicts = Section("Conflicts", [_paragraph(
        f'Pages read in {len(runs)} {"run" if len(runs) == 1 else "runs"}; '
        'conflicts and gaps are checked only between pages sent to the model together. '
        'A cloud task run reads the whole matter (stage 7b).')])
    has_pair = {"defense", "ours"} <= set(binder_roles.values())
    if not has_pair or "ROLE NEEDED" in binder_roles.values():
        conflicts.paragraphs.append(_paragraph('ROLE NEEDED: no binder pair is marked defense and ours in matter.toml; '
            'conflicts are in the order found.'))

    def priority(flag):
        values = {binder_roles.get(page_id.rsplit("/", 1)[0]) for page_id in flag.page_ids}
        return 0 if {"defense", "ours"} <= values else 1

    flags = [flag for flag in casefile.flags if flag.kind == "conflict"]
    if has_pair and "ROLE NEEDED" not in binder_roles.values():
        flags.sort(key=priority)
    gaps = Section("Gaps and missing records")
    for flag in [*flags, *(flag for flag in casefile.flags if flag.kind != "conflict")]:
        section = conflicts if flag.kind == "conflict" else gaps
        prefix = "Conflict between " if flag.kind == "conflict" else "Gap at "
        section.paragraphs.append(_citations(flag.cites, flag.page_ids, prefix=prefix, suffix="."))
        for about in flag.abouts:
            section.paragraphs.append(_paragraph(f"Model's reading: {about}"))
        if flag.kind == "conflict":
            for cite, page_id in zip(flag.cites, flag.page_ids):
                section.paragraphs.append(_citations([cite], [page_id], prefix="From ", suffix=":"))
                for fact in records:
                    if page_id in fact.page_ids:
                        section.paragraphs.append(Paragraph([Run(f'"{fact.quote}"', exempt="quote")]))
    if not flags:
        conflicts.paragraphs.append(_paragraph("none"))
    undated = Section("Facts without a date, by page")
    unstamped = tuple(page.page_id for page in pages if not page.stamps and page.text.strip())
    if unstamped:
        undated.paragraphs.append(Paragraph([], warning_pages=unstamped))
    open_status = {item.page_id: item.status for item in open_items}
    for page in pages:
        undated.paragraphs.append(Paragraph([Run('Page '), Run(label(page), exempt="cite"),
            Run(', binder '), Run(page.binder, exempt="binder")], level=2))
        quoted = False
        for fact in records:
            primary = placement[fact.id]
            if primary is None or fact.page_ids[primary] != page.page_id or fact.dates[primary]:
                continue
            undated.paragraphs.extend(_fact_paragraphs(fact, primary, page.page_id))
            quoted = True
        if not quoted and not any(fact.page_ids[placement[fact.id]] == page.page_id
                                  for fact, _ in dated):
            state = open_status.get(page.page_id)
            undated.paragraphs.append(_paragraph(
                f'Open item: {state} (see Open items).' if state is not None
                else 'No fact was quoted from this page.'))
    missing = Section("Facts on pages not in this matter")
    for fact in records:
        if placement[fact.id] is None:
            missing.paragraphs.extend(_fact_paragraphs(fact, 0, None))
    sections = [changes, stale, opened, chronology, providers, diagnoses, restrictions, history,
                *opinions.values(), gaps, conflicts, undated, missing]
    for section in sections:
        if not section.paragraphs:
            section.paragraphs.append(_paragraph("none"))
    built = (f'Built {datetime.now(timezone.utc).date().isoformat()} from case file entry '
             f'{casefile.last_seq}; playbook {playbook_version}; model {model}')
    return Memo(f'Medical memo: matter {matter}', built, sections, pages)


def _runs(paragraph, rules):
    if paragraph.warning_pages:
        return [Run('These pages carry no Bates stamp and are cited by page id: '),
                Run(', '.join(paragraph.warning_pages), exempt='cite'), Run('.')]
    return paragraph.runs



def check(memo, rules: Rules) -> list[Finding]:
    findings = []
    texts = [(memo.title, "title"), (memo.built, "build line")]
    for section in memo.sections:
        texts.append((section.title, section.title))
        for paragraph in section.paragraphs:
            texts.append(("".join(run.text if not run.exempt else "\n"
                                  for run in _runs(paragraph, rules)), section.title))
    for text, section in texts:
        for finding in rules.check(text, unit="text", stamped=all(page.stamps for page in memo.pages)):
            excerpt = " ".join(finding.excerpt.split())
            location = " ".join(section.split())
            findings.append(Finding(finding.rule_id, finding.severity, finding.start,
                                    finding.end, f'{excerpt} (in {location})'))
    return findings


def render(memo, path, *, rules: Rules):
    findings = check(memo, rules)
    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        raise MemoError("\n".join(f'{finding.rule_id}: {finding.excerpt}' for finding in errors))
    path = Path(path)
    # Only the output directory may be created; an absent matter is a refusal.
    if not path.parent.is_dir() and (path.parent.name != "outputs" or not path.parent.parent.is_dir()):
        raise MemoError(f'cannot write memo {path}: matter folder must already exist')
    document = Document()
    document.add_heading(memo.title, level=0)
    document.add_paragraph(memo.built)
    for section in memo.sections:
        document.add_heading(section.title, level=1)
        for paragraph in section.paragraphs:
            target = document.add_heading(level=paragraph.level) if paragraph.level is not None else document.add_paragraph()
            for run in _runs(paragraph, rules):
                target.add_run(run.text)
    try:
        path.parent.mkdir(exist_ok=True)
        document.save(path)
    except OSError as exc:
        raise MemoError(f'cannot write memo {path}: {exc}') from exc
