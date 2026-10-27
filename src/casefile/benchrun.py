"""Stage 2 bench runner: one model call per matter with a fixed card; replaced by the pipeline at
stage 5 (D25)."""

from dataclasses import dataclass
import hashlib
import json

from casefile.benchcandidate import EMPTY, Candidate, CandidateError, parse_text
from casefile.matter import Matter, Page
from casefile.model import ModelClient, ModelError

CARD = "bench.extract"
CARD_TEXT = (
    "You are reading the pages of one workers' compensation matter. Use only the text in this request.\n"
    "Answer with one JSON object and nothing else: {\"facts\": [...], \"flags\": [...]}.\n"
    "Each fact: {\"cite\": the Bates stamp of the page, \"quote\": an exact span copied from that page, "
    "\"text\": one sentence that says no more than the quote}.\n"
    "Each flag: {\"kind\": \"conflict\" or \"gap\", \"cites\": the Bates stamps involved, \"about\": one sentence}.\n"
    "A conflict is two pages that disagree. A gap is a record a page refers to that is not among these pages.\n"
    "Never name an examination as a DME or an IME in any form; write \"the report\".\n"
    "Never write who hired, paid or retained a doctor, any fee, or how many examinations a doctor does.\n"
    "Never guess, infer or fill in. If a value is not on the page, leave it out.\n")


def card_version() -> str:
    return hashlib.sha256(CARD_TEXT.encode()).hexdigest()[:12]


def page_block(page: Page) -> str:
    return f"=== PAGE {page.page_id} BATES {" ".join(page.stamps)} ===\n{page.text}\n"


def messages(matter: Matter) -> list[dict]:
    body = f"Matter {matter.number}\n" + "".join(page_block(p) for p in matter.pages)
    return [{"role": "system", "content": CARD_TEXT}, {"role": "user", "content": body}]


def prompt_sha256(msgs) -> str:
    return hashlib.sha256(json.dumps(msgs, sort_keys=True).encode()).hexdigest()


def counts_ok(answer) -> bool:
    return all(type(c) is int and c > 0 for c in (answer.prompt_eval_count, answer.eval_count))


@dataclass(frozen=True)
class RunResult:
    candidate: Candidate
    pages_failed: int
    failure: str | None
    reply_received: bool


def _fail(log, run_id, raw_text, fields, n, gate, message) -> RunResult:
    log.record_answer(run_id, raw_answer=raw_text, status="failed", **fields)
    log.record_failure(run_id, gate, message)
    return RunResult(EMPTY, n, f"{gate}: {message}", True)


def run(matter: Matter, config, log, playbook_version: str, opener=None) -> RunResult:
    msgs = messages(matter)
    n = len(matter.pages)
    run_id = log.start_run(job="bench", matter=matter.number, card=CARD, card_version=card_version(),
                           playbook_version=playbook_version, model=config.model.name, pages_in=n,
                           prompt_sha256=prompt_sha256(msgs))
    client = ModelClient(config.model, opener)
    try:
        answer = client.chat(msgs, options={"num_ctx": config.model.num_ctx})
    except ModelError as exc:
        # Every received reply is a row (OR-8), even when its body never came; no reply stores none.
        if exc.raw is not None or exc.received:
            raw_answer = "" if exc.raw is None else exc.raw if isinstance(exc.raw, str) else json.dumps(exc.raw)
            log.record_answer(run_id, raw_answer=raw_answer, status="failed")
        log.record_failure(run_id, "bench.model", str(exc))
        return RunResult(EMPTY, n, f"bench.model: {exc}", exc.received)

    fields = dict(done_reason=answer.done_reason, prompt_eval_count=answer.prompt_eval_count,
                  eval_count=answer.eval_count)
    raw_text = json.dumps(answer.raw)

    # Guard 1: Check done_reason
    if answer.done_reason != "stop":
        return _fail(log, run_id, raw_text, fields, n, "bench.truncation", f"done_reason={answer.done_reason}")

    # Guard 2: Check counts
    if not counts_ok(answer):
        return _fail(log, run_id, raw_text, fields, n, "bench.counts", "prompt_eval_count and eval_count must be positive integers")

    # Guard 3: Check parse_text
    try:
        candidate = parse_text(answer.content)
    except CandidateError as exc:
        return _fail(log, run_id, raw_text, fields, n, "bench.answer", str(exc))

    # Success
    log.record_answer(run_id, raw_answer=raw_text, status="ok", **fields)
    return RunResult(candidate, 0, None, True)
