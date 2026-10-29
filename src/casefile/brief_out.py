"""Build and check an anonymized brief package before publishing it."""

from dataclasses import replace
import hashlib
from pathlib import Path
import re
import shutil
import sys

from casefile import anon, anon_job, brief, dates, facts, outputs, packet


def _review_words(value, listed, pages):
    """List the surviving words for the attorney's review, never as a blocking gate."""
    dictionary = Path('/usr/share/dict/words')
    if not dictionary.is_file():
        return 'unavailable'
    known = set(dictionary.read_text(encoding='utf-8').casefold().split())
    value = anon.TAG.sub('', value)
    for token in (*anon.protected(pages), *listed.kept):
        value = value.replace(token, '')
    words = sorted({word for word in re.findall(r'\b[A-Z][a-z]+\b', value)
                    if word.casefold() not in known and word.casefold() not in dates.MONTHS})
    return ', '.join(words) or 'none'


def run(config, number, issue, *, out, err, opener=None, stdin=None, pages_all=False):
    try:
        with outputs.start(config, number, 'brief', opener=opener, stdin=stdin, out=out) as started:
            value = packet.build(started.casefile, started.loaded.pages, matter=number, task='brief',
                                 options={'issue': issue}, playbook_version=started.book.version)
            used = {p.page_id for p in value.pages}
            used.update(pid for flag in value.flags for pid in flag['page_ids'])
            # Entity discovery covers the full matter, including pages without an extracted fact.
            value = replace(value, pages=tuple(started.loaded.pages))
            common = dict(client=started.client, rules=started.book.rules, log=started.log,
                          matter=number, playbook_version=started.book.version, job='brief')
            hits = anon_job.entity_pass(value.pages, **common)
            listed = anon_job.halt(anon.names(started.info), hits,
                                   sys.stdin if stdin is None else stdin, out)
            info = listed.info or started.info
            anonymous, key = anon_job.anonymize(value, folder=started.folder, info=info, hits=hits)
            protected = anon.protected(value.pages)
            if not pages_all:
                value = replace(value, pages=tuple(p for p in value.pages if p.page_id in used))
                anonymous = replace(anonymous, pages=tuple(p for p in anonymous.pages if p.page_id in used))
            markdown = brief.package_text(value, started.casefile, value.pages, info, issue=issue,
                keep=listed.kept, rules_text=anon.drafter_rules(), pages_all=pages_all,
                transform=lambda s: anon.text(s, key, protected=protected))
            files = {'package.md': markdown.encode('utf-8'),
                     'package.json': anonymous.to_json().encode('utf-8')}
            # Inspect each serialized surface independently, then share one entity pass over its pages.
            for data in files.values():
                verdict = anon.check_code(data, key, listed, anonymous.pages)
                if not verdict.ok:
                    anon_job._record(verdict, started.log, hits.run_ids[0], None)
                    break
            else:
                verdict = anon_job.check(files['package.json'], key, listed, anonymous.pages,
                                         run_id=hits.run_ids[0], **common)
            if not verdict.ok:
                for step, kind, offset in verdict.hits:
                    remedy = ('retry the identifier pass' if kind == 'model' else
                              'correct matter.toml [anon.people], [anon.organizations] or [anon.aliases] and rerun')
                    print(f'brief-out: blocked at step {step} ({kind}, offset {offset}); {remedy}; nothing was written', file=err)
                return 1
            review = anon.review(markdown, key, listed, anonymous.pages)
            files['check.txt'] = (f'steps=1,2,3,4,5 check=pass leaks=0 entities={len(hits)} '
                                  f'pages={len(anonymous.pages)} review={review}\n'
                                  f'Review words: {_review_words(markdown, listed, anonymous.pages)}\n').encode('utf-8')
            digest = hashlib.sha256(files['package.md']).hexdigest()
            packet_id = digest[:12]
            outbox = started.folder / 'outbox'
            existed = outbox.exists()
            target = brief.publish_package(outbox, packet_id, files)
            try:
                counts = started.counts
                facts.append(started.folder / 'casefile.jsonl', [facts.Event('output', dict(
                    name='brief-out', path=str(target), built_from_seq=started.casefile.last_seq,
                    facts=counts['facts'], conflicts=counts['conflicts'], gaps=counts['gaps'], open=counts['open']))])
            except BaseException:
                shutil.rmtree(target)
                if not existed and not any(outbox.iterdir()):
                    outbox.rmdir()
                raise
            print(f'brief-out {number} packet={packet_id} sha256={digest} facts={len(value.facts)} '
                  f'pages={len(value.pages)} conflicts={started.counts["conflicts"]} '
                  f'check=pass review={review}', file=out)
            return 0
    except anon_job.NameListNeeded:
        return 2
    except anon_job.EntityError:
        print('brief-out: blocked at step 1 (model, offset 0); nothing was written', file=err)
        return 1
    except outputs.ERRORS as exc:
        print(f'brief-out: cannot run: {exc}', file=err)
        return 2
