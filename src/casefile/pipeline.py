"""Chunk pages within the byte budget and run the fixed gate pipeline."""

from dataclasses import dataclass

from casefile import extract, gates, model
from casefile.benchcandidate import EMPTY, Candidate, CandidateFact, CandidateFlag
from casefile.model import ModelClient, ModelError
from casefile import playbook


RETRY_MARGIN = 8192


@dataclass(frozen=True)
class PipelineResult:
    outcomes: tuple[gates.Outcome, ...]
    refused: tuple[tuple[object, str], ...]
    chunks: tuple[tuple, ...]


@dataclass(frozen=True)
class RunResult:
    candidate: Candidate
    pages_failed: int
    failure: str | None
    reply_received: bool
    uncited: tuple[str, ...] = ()


def _size(card, pages, matter):
    return sum(model.tokens_at_most(msg["content"]) for msg in
               gates.messages(card, pages, "0" * 16, matter=matter)) + model.TEMPLATE_TOKENS


def chunk(card, pages, num_ctx, matter):
    """Keep input page order and reserve room for a fresh retry's error line."""
    budget = num_ctx - card.max_answer_tokens - RETRY_MARGIN
    chunks, refused, current = [], [], []
    for page in pages:
        if _size(card, (page,), matter) > budget:
            if current:
                chunks.append(tuple(current))
                current = []
            overhead = _size(card, (), matter)
            reason = (f"page too long for one prompt ({model.tokens_at_most(page.text)} bytes, "
                      f"budget {budget - overhead} bytes); split the binder")
            refused.append((page, reason))
        else:
            if current and _size(card, (*current, page), matter) > budget:
                chunks.append(tuple(current))
                current = []
            current.append(page)
    if current:
        chunks.append(tuple(current))
    return tuple(chunks), tuple(refused)


def refuse(page, reason, *, card, client, log, matter, playbook_version, job):
    """Record a prompt refusal without calling the model or storing an answer."""
    msgs = gates.messages(card, (page,), "0" * 16, matter=matter)
    run_id = log.start_run(job=job, matter=matter, card=card.name, card_version=card.version,
                           playbook_version=playbook_version, model=client.config.name,
                           pages_in=1, prompt_sha256=extract.prompt_sha256(msgs))
    failure = f"gate.truncation: {reason}; not retried: the page must be split"
    log.record_failure(run_id, "gate.truncation", failure)
    log.record_coverage(run_id, matter=matter, page_id=page.page_id, card=card.name,
                        status="failed", reason=failure)


def run(pages, *, card, client, rules, log, matter, playbook_version, job,
        only_unread) -> PipelineResult:
    pages = tuple(pages)
    if only_unread:
        coverage = log.coverage(matter, job=job)
        pages = tuple(page for page in pages
                      if coverage.get((page.page_id, card.name), (None,))[0] != "read")
    chunks, refused = chunk(card, pages, client.config.num_ctx, matter)
    for page, reason in refused:
        refuse(page, reason, card=card, client=client, log=log, matter=matter,
               playbook_version=playbook_version, job=job)
    outcomes = []
    for part in chunks:
        outcomes.append(gates.ask(card, part, client=client, rules=rules, log=log,
                                  matter=matter, playbook_version=playbook_version, job=job))
    return PipelineResult(tuple(outcomes), refused, chunks)


def bench_run(matter, config, log, playbook_version, opener=None) -> RunResult:
    """Score every page through the gates and merge passing chunks without writing the matter."""
    from casefile import facts

    card = extract.card()
    client = ModelClient(config.model, opener)
    rules = playbook.load(config.paths.playbook).rules
    try:
        result = run(matter.pages, card=card, client=client, rules=rules, log=log,
                     matter=matter.number, playbook_version=playbook_version, job="bench",
                     only_unread=False)
    except ModelError as exc:
        return RunResult(EMPTY, len(matter.pages), f"gate.model: {exc}", exc.received)

    casefile = facts.CaseFile()
    for part, outcome in zip(result.chunks, result.outcomes):
        if outcome.ok:
            casefile.extend(facts.merge(casefile, outcome.answer, part, outcome.run_id))
    candidate = Candidate(
        tuple(CandidateFact(cite, fact.quote, fact.readings[0])
              for fact in casefile.facts for cite in fact.cites),
        tuple(CandidateFlag(flag.kind, tuple(flag.cites), flag.abouts[0])
              for flag in casefile.flags))
    coverage = log.coverage(matter.number, job="bench")
    pages_failed = sum(coverage.get((page.page_id, card.name), (None,))[0] == "failed"
                       for page in matter.pages)
    uncited = tuple(gates._page_label(page) for page in matter.pages
                    if coverage.get((page.page_id, card.name), (None,))[0] == "uncited")
    failure = next((verdict.message for outcome in result.outcomes if not outcome.ok
                    for verdict in reversed(outcome.verdicts) if verdict.verdict == "fail"), None)
    if failure is None and result.refused:
        failure = (f"gate.truncation: {result.refused[0][1]}; "
                   "not retried: the page must be split")
    return RunResult(candidate, pages_failed, failure, True, uncited)
