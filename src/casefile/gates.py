"""Run the fixed six gates, retry once, and publish only final page dispositions."""

from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
import json
import re
import secrets

from casefile import extract, jsonrepair, model, quotes, schema, stamps
from casefile.matter import Page
from casefile.rules import cite_body


GATES = ("truncation", "repair", "schema", "quotes", "rules", "coverage")
GATE_NAMES = {gate: f"gate.{gate}" for gate in GATES}
_SKIP_RULES = {"quote", "cite", "cites", "prompt_id", "end_id"}


@dataclass(frozen=True)
class Card:
    """Stage 4 and 5 cards use text; stage 6 question cards must set unit explicitly."""

    name: str
    text: str
    schema: dict
    coverage: bool = True
    required_any: tuple[str, ...] = ("facts", "flags")
    optional_blank: tuple[str, ...] = ()
    echo: str | None = None
    question_keys: tuple[str, ...] = ()
    numbers_in: str = "quote"
    think: bool = False
    max_answer_tokens: int = 8192

    @property
    def version(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True)
class Verdict:
    attempt: int
    gate: str
    verdict: str
    message: str


@dataclass(frozen=True)
class Outcome:
    ok: bool
    answer: dict | None
    attempts: int
    verdicts: tuple[Verdict, ...]
    read: tuple[str, ...]
    uncited: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]
    run_id: int


def messages(card, pages: Sequence[Page], nonce, *, matter, body=None):
    """The matter number is explicit because a Page carries no matter number."""
    return [{"role": "system", "content": f"prompt_id: {nonce}\n{card.text}"},
            {"role": "user", "content": body if body is not None else f"Matter {matter}\n"
             + "".join(extract.page_block(page) for page in pages)}]


def _rules_strings(obj, path=""):
    if isinstance(obj, str):
        yield path or "answer", obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key not in _SKIP_RULES:
                yield from _rules_strings(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _rules_strings(value, f"{path}[{index}]")


def _page_id(page):
    return page.page_id


def _objects(obj, path=""):
    if isinstance(obj, dict):
        yield path or "answer", obj
        for key, value in obj.items():
            yield from _objects(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _objects(value, f"{path}[{index}]")


def _page_label(page):
    return page.stamps[0] if page.stamps else page.page_id


def _references(obj, pages, rules, *, numbers_in="quote"):
    faults, rungs, cited = [], [], set()
    cite_fault = False
    cite_rule = next(rule for rule in rules.rules if rule.id == "bates-cites")
    prose = {}

    def lookup(cite, path):
        nonlocal cite_fault
        matches = [page for page in pages
                   if stamps.normalize(cite) in page.stamps or cite == page.page_id]
        if len(matches) > 1:
            cite_fault = True
            faults.append(f"{path}: cite {cite} matches more than one page (ambiguous cite)")
            return None
        if not matches:
            cite_fault = True
            faults.append(f"{path}: cite {cite} is not a page of this chunk")
            return None
        cited.add(matches[0].page_id)
        return matches[0]

    for path, item in _objects(obj):
        if "cite" in item:
            page = lookup(item["cite"], f"{path}.cite")
            if page is not None and item.get("quote", "").strip():
                hit = quotes.match(item["quote"], page.text)
                if hit is None:
                    label = (stamps.normalize(item["cite"]) if stamps.normalize(item["cite"]) in page.stamps
                             else _page_label(page))
                    faults.append(f'{path}: quote not found on {label}, the page it cites '
                                  f'(quote: "{item["quote"][:60]}")')
                else:
                    rungs.append(hit.rung)
        if "cite" in item and page is not None:
            from casefile.dates import parse as parse_date

            if item.get("date"):
                value = item["date"]
                if quotes.match(value, page.text) is None:
                    faults.append(f"{path}.date: {value} is not a date written on {_page_label(page)}")
                elif parse_date(value) is None:
                    faults.append(f"{path}.date: {value} is not a recognised date form")
            if item.get("provider") and quotes.match(item["provider"], page.text) is None:
                faults.append(f"{path}.provider: not on {_page_label(page)}")
        flag_pages = set()
        for index, cite in enumerate(item.get("cites", [])):
            page = lookup(cite, f"{path}.cites[{index}]")
            if page is not None:
                flag_pages.add(page.page_id)
        if item.get("kind") == "conflict" and len(flag_pages) < 2:
            faults.append(f"{path}: a conflict must cite two different pages")
        for key in ("text", "about", "note", "why", "absent_note"):
            if isinstance(item.get(key), str):
                location = f"{path}.{key}"

                def remove_cite(match):
                    lookup(cite_body(match), location)
                    return ""

                prose[location] = re.sub(cite_rule.cite_pattern, remove_cite, item[key],
                                         flags=re.IGNORECASE)
    for path, item in _objects(obj):
        if not isinstance(item.get("quote"), str) or not item["quote"].strip():
            continue
        source = item["quote"]
        if numbers_in == "page":
            matches = [p for p in pages if item.get("cite") == p.page_id
                       or stamps.normalize(item.get("cite", "")) in p.stamps]
            if len(matches) != 1:
                continue
            source = matches[0].text
        numbers = set(re.findall(r"\d+", source))
        keys = ("text",) if numbers_in == "quote" else ("text", "note", "why", "absent_note")
        for key in keys:
            for number in dict.fromkeys(re.findall(r"\d+", prose.get(f"{path}.{key}", ""))):
                if number not in numbers:
                    faults.append(f"{path}.{key}: number {number} is not in its {numbers_in}")
    if faults:
        noun = "fault" if len(faults) == 1 else "faults"
        detail = f"{len(faults)} {noun} (faults={len(faults)}): " + "; ".join(faults)
        if cite_fault:
            detail += "; chunk pages: " + ", ".join(_page_label(page) for page in pages)
        return detail, cited
    return " ".join(f"{rung}={rungs.count(rung)}" for rung in
                    ("exact", "whitespace", "curly", "ocr")), cited


def _end_id(text, nonce):
    # Start on a real string token so a string containing a key imitation cannot pass.
    tokens = list(re.finditer(r'"(?:[^"\\]|\\.)*"', text, re.DOTALL))
    tail = text[tokens[-2].start():] if len(tokens) >= 2 else ""
    return re.fullmatch(r'"end_id"\s*:\s*' + re.escape(json.dumps(nonce)) + r"\s*,?[\s\]}]*", tail)


def open_items(log, matter, *, job):
    return log.open_items(matter, job=job)


def ask(card, pages: Sequence[Page], *, client, rules, log, matter, nonce=None,
        job="gates", playbook_version="", body=None, echo=None, providers=()) -> Outcome:
    """Check every received reply; a failed transport without a reply remains the caller's error."""
    pages = tuple(pages)
    nonce = secrets.token_hex(8) if nonce is None else nonce
    initial = messages(card, pages, nonce, matter=matter, body=body)
    run_id = log.start_run(job=job, matter=matter, card=card.name, card_version=card.version,
                           playbook_version=playbook_version, model=client.config.name,
                           pages_in=len(pages), prompt_sha256=extract.prompt_sha256(initial))
    verdicts = []
    reason = ""
    obj = None
    cited = set()
    ok = False
    for attempt in (1, 2):
        if attempt == 2:
            nonce = secrets.token_hex(8)
        msgs = initial if attempt == 1 else messages(card, pages, nonce, matter=matter, body=body)
        if attempt == 2:
            header, tail = (msgs[1]["content"].split("\n", 1) + [""])[:2]
            msgs[1]["content"] = header + "\nRetry: the previous answer failed the " + reason + (
                ". Answer again with one JSON object and nothing else.\n") + tail
        gate, message, retryable = "truncation", "", True
        raw = None
        fields = {}
        answer = None
        budget = sum(model.tokens_at_most(m["content"]) for m in msgs) + model.TEMPLATE_TOKENS
        if budget > client.config.num_ctx - card.max_answer_tokens:
            message, retryable = "the prompt is too long (over budget)", False
        else:
            try:
                answer = client.chat(msgs, options={"num_predict": card.max_answer_tokens},
                                     think=card.think, truncate=False)
            except model.ModelError as exc:
                if not exc.received:
                    raise
                raw = "" if exc.raw is None else exc.raw
                gate = "truncation" if model.context_length_error(str(exc) + str(raw)) else "model"
                message, retryable = " ".join(str(exc).split()), gate != "truncation"
            else:
                raw = answer.raw
                fields = {key: getattr(answer, key) for key in
                          ("done_reason", "prompt_eval_count", "eval_count", "prompt_eval_cached_count")}
        if answer is not None:
            for gate in GATES:
                message = ""
                if gate == "truncation":
                    text = jsonrepair.unfence(answer.content).strip()
                    p, e = answer.prompt_eval_count, answer.eval_count
                    if answer.done_reason != "stop":
                        message = f"the answer stopped before it finished (done_reason={answer.done_reason})"
                    elif not all(type(c) is int and c > 0 for c in (p, e)):
                        message = "the reply must report positive token counts (prompt_eval_count, eval_count)"
                    elif p > client.config.num_ctx or p + e > client.config.num_ctx:
                        message = "the token counts exceed the context size (prompt_eval_count + eval_count > num_ctx)"
                    elif e >= card.max_answer_tokens:
                        message = "the answer reached its token limit (eval_count >= max_answer_tokens)"
                    elif not re.match(r'\{\s*"prompt_id"\s*:\s*' + re.escape(json.dumps(nonce)), text):
                        message, retryable = "the prompt was cut (prompt_id missing)", False
                    elif not _end_id(text, nonce):
                        message = "the answer was cut off (end_id missing)"
                elif gate == "repair":
                    try:
                        repaired = jsonrepair.repair(answer.content, nonce=nonce)
                        obj = jsonrepair.loads(repaired.text)
                        obj.pop("prompt_id", None)
                        obj.pop("end_id", None)
                    except jsonrepair.RepairError as exc:
                        message = "the answer is not valid JSON: " + str(exc).removeprefix("not JSON: ")
                    else:
                        for kind in repaired.repairs:
                            verdict = Verdict(attempt, GATE_NAMES[gate], "repaired", kind)
                            verdicts.append(verdict)
                            log.record_gate(run_id, attempt=attempt, gate=verdict.gate,
                                            verdict=verdict.verdict, message=verdict.message)
                        if repaired.repairs:
                            continue
                elif gate == "schema":
                    faults = schema.validate(obj, card.schema)
                    if faults:
                        message = "the answer does not match the schema: " + "; ".join(faults)
                elif gate == "quotes":
                    detail, cited = _references(obj, pages, rules, numbers_in=card.numbers_in)
                    if re.match(r"\d+ faults? \(faults=", detail):
                        message = detail
                elif gate == "rules":
                    findings = [(path, finding) for path, value in _rules_strings(obj)
                                for finding in rules.check(value, unit="question" if path.rsplit(".", 1)[-1] in card.question_keys else "text",
                                                           stamped=all(p.stamps for p in pages), providers=providers)]
                    instructions = {rule.id: rule.rule for rule in rules.rules}
                    message = "; ".join(f"{path}: {instructions[f.rule_id]} ({f.rule_id}: {f.excerpt})"
                                        for path, f in findings if f.severity == "error")
                elif gate == "coverage":
                    if card.echo:
                        expected = echo[1] if echo is not None and echo[0] == card.echo else [p.page_id for p in pages]
                        values = obj.get(card.echo)
                        if not isinstance(values, list) or set(values) != set(expected):
                            message = f"the answer does not echo every id at {card.echo}"
                    elif not any(isinstance(obj.get(key), list) and obj[key] for key in card.required_any):
                        message = ("the answer has no facts and no flags" if card.required_any == ("facts", "flags")
                                   else "the answer has no items in " + ", ".join(card.required_any))
                    if not message:
                        blanks = []
                        for path, item in _objects(obj):
                            if path == "answer":
                                continue
                            for key, value in item.items():
                                # Missing date and provider are explicitly allowed by the memo contract.
                                absent_metadata = card.name == "medical_memo" and key in ("date", "provider")
                                if (isinstance(value, str) and not value.strip()
                                        and key not in card.optional_blank and not absent_metadata
                                        or key == "cites" and not value):
                                    blanks.append(f"{path}.{key}")
                        if blanks:
                            message = "; ".join(f"the answer has a blank value at {path}" for path in blanks)
                if message:
                    break
                detail = ""
                if gate == "quotes":
                    detail, _ = _references(obj, pages, rules, numbers_in=card.numbers_in)
                elif gate == "rules":
                    unstamped = [p.page_id for p in pages if not p.stamps]
                    warnings = [f"{path}: {f.rule_id}: {f.excerpt}" for path, f in findings
                                if f.severity == "warning"]
                    if unstamped:
                        warnings.insert(0, "warning: no Bates stamp on " + ", ".join(unstamped)
                                        + "; cites are page ids")
                    detail = "; ".join(warnings)
                verdict = Verdict(attempt, GATE_NAMES[gate], "pass", detail)
                verdicts.append(verdict)
                log.record_gate(run_id, attempt=attempt, gate=verdict.gate,
                                verdict=verdict.verdict, message=verdict.message)
            else:
                ok = True
        if raw is not None:
            log.record_answer(run_id, raw_answer=raw if isinstance(raw, str) else json.dumps(raw),
                              status="ok" if ok else "failed", **fields)
        if ok:
            break
        message = " ".join(message.split())
        name = GATE_NAMES.get(gate, f"gate.{gate}")
        if not retryable:
            why = "the prompt was cut" if "prompt_id missing" in message else "the prompt was too long"
            next_step = f"not retried: {why}; the chunk must be made smaller"
        else:
            next_step = "retried once" if attempt == 1 else "not retried: the one retry was used"
        failure = f"{name}: {message}; {next_step}"
        verdict = Verdict(attempt, name, "fail", failure)
        verdicts.append(verdict)
        log.record_gate(run_id, attempt=attempt, gate=name, verdict="fail", message=failure)
        log.record_failure(run_id, name, failure)
        reason = f"{gate} check: {message}"
        if not retryable:
            break
    read = tuple(_page_id(page) for page in pages if _page_id(page) in cited) if ok and card.coverage else ()
    uncited = tuple(_page_id(page) for page in pages if _page_id(page) not in cited) if ok and card.coverage else ()
    final_reason = "" if ok else f"{name}: {message}; the page stays open until a later run reads it"
    failed = () if ok or not card.coverage else tuple((_page_id(page), final_reason) for page in pages)
    for page in pages if card.coverage else ():
        page_id = _page_id(page)
        status = ("read" if page_id in read else "uncited") if ok else "failed"
        why = ("" if status == "read" else f"no fact or flag cites {page_id}") if ok else final_reason
        log.record_coverage(run_id, matter=matter, page_id=page_id, card=card.name,
                            status=status, reason=why)
    return Outcome(ok, obj if ok else None, attempt, tuple(verdicts), read, uncited, failed, run_id)
