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


def _cite(cite, page_id):
    return f'[page {page_id}]' if cite == page_id else f'[cite {cite}]'


def _paragraph(text):
    return Paragraph([Run(text)])


def build(casefile, pages, open_items, *, matter, playbook_version, model) -> Memo:
    pages = tuple(pages)
    previous = next((event for event in reversed(casefile.events)
                     if event.kind == "output" and event.payload["name"] == "memo"), None)
    if previous is None:
        changed = "First memo for this matter"
    else:
        counts = casefile.changed_since(previous.seq)
        changed = (f'{counts["fact"]} fact added, {counts["cite"]} cites added, '
                   f'{counts["reading"]} readings added, {counts["flag"]} flags added')
        if counts["about"]:
            changed += f', {counts["about"]} flag readings added'
    changes = Section("What changed since the last memo", [_paragraph(changed)])
    stale = Section("Outputs out of date", [_paragraph(
        ", ".join(casefile.stale_outputs()) or "none")])
    opened = Section("Open items", [Paragraph([
        Run(f'{item.label}: {item.status}: '), Run(item.reason, exempt="reason")])
        for item in open_items])
    runs = {run["run_id"] for run in casefile.runs if run["job"] == "memo" and run["read"]}
    conflicts = Section("Conflicts", [_paragraph(
        f'Pages read in {len(runs)} {"run" if len(runs) == 1 else "runs"}; '
        'conflicts between runs are checked only for pages sent together.')])
    gaps = Section("Gaps and missing records")
    for flag in casefile.flags:
        citations = [_cite(cite, page_id) for cite, page_id in zip(flag.cites, flag.page_ids)]
        section = conflicts if flag.kind == "conflict" else gaps
        prefix = "Conflict between " if flag.kind == "conflict" else "Gap at "
        section.paragraphs.append(_paragraph(prefix + " and ".join(citations) + "."))
        for about in flag.abouts:
            section.paragraphs.append(_paragraph(f"Model's reading: {about}"))
    verified = Section("Verified facts by record")
    unstamped = tuple(page.page_id for page in pages if not page.stamps)
    if unstamped:
        verified.paragraphs.append(Paragraph([], warning_pages=unstamped))
    records = casefile.facts
    for page in pages:
        verified.paragraphs.append(Paragraph([Run(f'{page.binder} page {label(page)}')], level=2))
        for fact in records:
            if fact.page_ids[0] != page.page_id:
                continue
            verified.paragraphs.append(Paragraph([
                Run(f'"{fact.quote}"', exempt="quote"),
                Run(" " + _cite(fact.cites[0], fact.page_ids[0]))]))
            if len(fact.cites) > 1:
                verified.paragraphs.append(_paragraph("Also cited: " + " and ".join(
                    _cite(cite, page_id) for cite, page_id in zip(fact.cites[1:], fact.page_ids[1:]))))
            for reading in fact.readings:
                verified.paragraphs.append(_paragraph(f"Model's reading: {reading}"))
    built = (f'built {datetime.now(timezone.utc).date().isoformat()} from case file entry '
             f'{casefile.last_seq}; playbook {playbook_version}; model {model}')
    return Memo(f'Medical memo: matter {matter}', built,
                [changes, stale, opened, conflicts, gaps, verified], pages)


def _runs(paragraph, rules):
    if paragraph.warning_pages:
        rule = next(rule for rule in rules.rules if rule.id == "bates-cites")
        return [Run(f'{rule.rule} Unstamped pages: {", ".join(paragraph.warning_pages)}.')]
    return paragraph.runs


def check_binders(pages, rules):
    """Called by the memo job before opening the run log or calling the model."""
    for binder in dict.fromkeys(page.binder for page in pages):
        for finding in rules.check(binder, unit="text", stamped=all(page.stamps for page in pages)):
            if finding.severity == "error":
                raise MemoError(f'binder {binder} fails the firm rule {finding.rule_id} '
                                f'({finding.excerpt}); remove the binder by hand and intake it '
                                'under another name (question 34)')


def check(memo, rules: Rules) -> list[Finding]:
    findings = []
    texts = [memo.title, memo.built]
    for section in memo.sections:
        texts.append(section.title)
        for paragraph in section.paragraphs:
            texts.append("".join(run.text if not run.exempt else "\n"
                                 for run in _runs(paragraph, rules)))
    for text in texts:
        for finding in rules.check(text, unit="text", stamped=all(page.stamps for page in memo.pages)):
            findings.append(Finding(finding.rule_id, finding.severity, finding.start,
                                    finding.end, f'{text}: {finding.excerpt}'))
    return findings


def render(memo, path, *, rules: Rules):
    check_binders(memo.pages, rules)
    findings = check(memo, rules)
    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        raise MemoError("; ".join(f'{finding.rule_id}: {finding.excerpt}' for finding in errors))
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
