"""Read memo coverage and case file counts for a matter."""

import sqlite3

from casefile import extract, facts, memo, pages
from casefile.runlog import open_db


def torn_message(casefile):
    return (f"casefile: torn last line ({casefile.torn} bytes) discarded; "
            "the event was never completed")


def committed_coverage(casefile, coverage):
    """A read is durable only after its memo run also reached the case file."""
    committed = {run["run_id"] for run in casefile.runs if run["job"] == "memo"}
    return {key: (("unread", "the reading was not saved in the case file; run casefile memo again", row[2])
                  if row[0] == "read" and row[2] not in committed else row)
            for key, row in coverage.items()}


def snapshot(loaded, casefile, coverage):
    """Keep page IDs as keys and every stamp in the attorney's label."""
    coverage = committed_coverage(casefile, coverage)
    dispositions = {}
    card_name = extract.card().name
    binders = list(dict.fromkeys(page.binder for page in loaded.pages))
    for page in loaded.pages:
        state, reason, *_ = coverage.get((page.page_id, card_name),
                                         ("unread", "no run has read this page"))
        dispositions[page.page_id] = memo.OpenItem(page.page_id, memo.label(page), state, reason)
    for page_id, stamps, state, reason in loaded.open_pages:
        binder = page_id.split("/")[0]
        if binder not in binders:
            binders.append(binder)
        label = f'{" ".join(stamps)} ({page_id})' if stamps else page_id
        dispositions[page_id] = memo.OpenItem(page_id, label, state, reason)
    if loaded.open_pages:
        binders.sort()
    ordered = sorted(dispositions.values(),
                     key=lambda item: (binders.index(item.page_id.split("/")[0]), item.page_id))
    counts = {state: sum(item.status == state for item in ordered)
              for state in ("read", "failed", "uncited", "empty")}
    opened = [item for item in ordered if item.status != "read"]
    stale = casefile.stale_outputs()
    outputs = ",".join(f'{name}:{"stale" if name in stale else "current"}'
                       for name in dict.fromkeys(row["name"] for row in casefile.outputs)) or "none"
    return dict(pages=len(ordered), **counts, open=len(opened), facts=len(casefile.facts),
                conflicts=sum(flag.kind == "conflict" for flag in casefile.flags),
                gaps=sum(flag.kind == "gap" for flag in casefile.flags), outputs=outputs,
                open_items=opened)


def matter_status(config, number) -> dict:
    loaded = pages.load(config.paths.matters, number, config.ocr.stamp_pattern)
    casefile = facts.load(config.paths.matters / number / "casefile.jsonl")
    database = config.paths.state / "runlog.sqlite"
    coverage = {}
    if database.exists():
        with open_db(database) as log:
            coverage = log.coverage(number, job="memo")
    return snapshot(loaded, casefile, coverage)


def print_open(items, out):
    for item in items:
        print(f"  open: {item.label}: {item.status}: {item.reason}", file=out)


def run(config, number, *, out, err) -> int:
    try:
        result = matter_status(config, number)
        casefile = facts.load(config.paths.matters / number / "casefile.jsonl")
        if casefile.torn:
            print(torn_message(casefile), file=err)
        fields = " ".join(f"{key}={result[key]}" for key in
                          ("pages", "read", "failed", "uncited", "empty", "open", "facts",
                           "conflicts", "gaps", "outputs"))
        print(f"status {number} {fields}", file=out)
        print_open(result["open_items"], out)
        return 0
    except (pages.PagesError, facts.CaseFileError, OSError, sqlite3.Error) as exc:
        print(f"status: cannot run: {exc}", file=err)
        return 2
