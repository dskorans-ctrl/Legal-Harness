"""Restore and fact-check a Word draft against its matter's source pages."""

from pathlib import Path
import re
from zipfile import BadZipFile

from docx.opc.exceptions import PackageNotFoundError

from casefile import anon, brief, outputs


def check_draft(draft, key, namelist, pages):
    """Reject identifiers and every placeholder absent from this matter's key."""
    data = '\n'.join(draft).encode('utf-8')
    checked = anon.check_code(data, key, namelist, pages)
    text = data.decode('utf-8')
    citations = {len(text[:m.start()].encode('utf-8')) for m in
                 re.finditer(r'\[(?:cite|page) [^\[\]\n]+\]', text)}
    # Citation resolution belongs to the fact check, so an unknown cite gets a marked partial.
    hits = [hit for hit in checked.hits if not (hit[0] == 5 and hit[2] in citations)]
    for match in re.finditer(r'\[[^\]\n]*\]?|\]', text):
        token = match[0]
        if re.fullmatch(r'\[(?:cite|page) [^\[\]\n]+\]', token):
            continue
        if not anon._known(token, key):
            hit = (5, 'placeholder', len(text[:match.start()].encode('utf-8')))
            if hit not in hits:
                hits.append(hit)
    return anon.Verdict(not hits, tuple(hits))


def run(config, number, file, *, out, err):
    try:
        file = Path(file)
        if file.suffix.lower() != '.docx':
            raise outputs.OutputError('brief-in needs a Word .docx draft')
        with outputs.start(config, number, 'brief', out=out) as started:
            key = anon.load_key(started.folder)
            if not key.anchor:
                raise outputs.OutputError('run casefile brief-out first; anon/key.json is needed')
            draft = brief.read_draft(file)
            verdict = check_draft(draft, key, anon.names(started.info), started.loaded.pages)
            if not verdict.ok:
                for step, kind, offset in verdict.hits:
                    print(f'brief-in: blocked at step {step} ({kind}, offset {offset}); nothing was written', file=err)
                return 2
            report = brief.fact_check(draft, started.loaded.pages, started.book.rules,
                restore_prose=lambda s: anon.restore(s, key),
                restore_quote=lambda s, page: anon.restore_quote(s, key, page))
            document = brief.render(report, started.info, playbook_version=started.book.version,
                                    model=config.model.name)
            name = 'brief-in-' + file.stem
            outputs.publish(started.folder, name, document, started.book.rules, started.casefile,
                            started.counts, failed_steps=() if report.ok else ('restore',))
            code = 0 if report.ok else 1
            output = name + ('.docx' if report.ok else '.partial.docx')
            print(f'brief-in {number} file={file.stem} checks={report.checks} of {report.total} '
                  f'failed={report.failed} uncited={len(report.uncited)} rule_hits={report.rule_hits} '
                  f'output={output} exit={code}', file=out)
            return code
    except (*outputs.ERRORS, BadZipFile, PackageNotFoundError) as exc:
        print(f'brief-in: cannot run: {exc}', file=err)
        return 2
