# `docs/loop/agent-log.md` and the live page's data

Two views of the same facts: a tracked markdown table (the source of record, read by anyone
browsing the repo) and a live HTML page (`assets/loop-watch.html`, published as a private artifact,
read by the owner without opening the repo). Update both at every spawn and every completion —
not only at round close — because a page or table that only updates at the end shows nothing while
the round is actually running, which is when the owner is most likely to check it.

## Why log every spawn, not just every completion

A worker that dies before its first commit (an API error, a kill, a restart) still cost wall-clock
time and still needs a row — otherwise the log under-counts what a round actually took, and a
future round can't learn "this tier failed three times before a retry worked" if the three
failures were never written down.

## The markdown table format

```markdown
# Agent log — who did what, on which tier, for how long

Maintained by the chair at every spawn and completion. Tokens are the worker's own usage as
reported at completion (the chair's tokens are not included). Elapsed is wall-clock for the
worker. Tiers: sonnet (code) · opus (orchestrator, verifier, graders) · fable (brief, revision) · codex gpt-6.1-sol (plan and round review). <any standing tier restriction, e.g. "no Fable sub-agents without
owner permission">.

## Round <N> — <date> (opened ~<time>, merged to main <time> at `<sha>`)

| # | Task | Tier | Elapsed | Tokens | Outcome |
|---|---|---|---|---|---|
| 1 | <what this worker was asked to do, one line> | sonnet | 3.4 min | 120 k | done |
| 2 | <task> | opus | 8.9 min | 200 k | done; <one-clause outcome detail, e.g. "overturned 5 plan claims"> |
| 3 | Lane A lead (+2 children: <child task> sonnet 8 min 128 k · <child task> sonnet 16 min 142 k) | opus | 106 min | 489 k + 270 k children | done; <outcome> |
| 4 | <task>, attempt 1 | opus | — | — | **killed: <reason>** |
| 5 | <task>, attempt 2 (tier switched) | sonnet | 73.6 min | 493 k | done |
| | **Round <N> total** | | **~<wall> h wall-clock** | **~<M> M** | <N> workers, <N> verify cycles |

## Side tasks (not part of a round)

| # | Task | Tier | Started | Elapsed | Tokens | Outcome |
|---|---|---|---|---|---|---|
| S1 | <task> | sonnet | <date time> | running | | |
```

Columns, in order, and where each comes from:

- **#** — spawn order within the round; side tasks get an `S`-prefixed number in their own table
  so they never collide with a round's numbering.
- **Task** — one line naming what the worker was asked to do; a child's task nests inline inside
  its parent's row in parentheses (`Lane A lead (+N children: …)`) rather than getting its own
  top-level row, so the table's row count matches "how many top-level things did the chair spawn."
- **Tier** — `sonnet` / `opus` / `fable` / `codex gpt-6.1-sol` (a Codex CLI run: tokens from its
  log's usage line, or `—` if it prints none), whichever the worker actually ran as (a tier switch mid-
  attempt, e.g. after repeated API failures, is its own row, not an edit to the failed one).
- **Started** — wall-clock time the worker was spawned; omit the column entirely if every round's
  own table always starts at the round's own open time (round 1 style); add it once any round has
  workers starting at meaningfully different times (parallel lanes, an overnight run).
- **Elapsed** — the worker's own wall-clock duration, not the chair's; a killed worker before its
  first commit gets `—` here, not `0 min`, since it didn't finish measuring anything.
- **Tokens** — the worker's own usage as reported in its completion notice, never the chair's
  running total; a worker with children reports `<own> + <children total> children` so the parent
  row's number is legible on its own without summing the child rows by hand.
- **Outcome** — `done`, `done; <one-clause detail>`, `**verdict FAIL**: <what>`, `**killed: <why>**`,
  `stopped: <why>`, or `running` for a worker still in flight when the log was last updated.

A **total row** closes every round's table: worker count, wall-clock span, summed tokens
(including children), and verify-cycle count — enough that a reader never has to sum the table by
hand to answer "how much did this round cost."

## Where the numbers come from

Every number in this table comes from the worker's own completion notice — the tool result that
arrives when a spawned agent finishes — never from the chair's estimate or from re-reading the
worker's report prose. A worker's report can claim "fast" or "cheap"; only the completion notice's
own elapsed/token fields are the number that goes in the table. A lane lead's children numbers
come the same way, one level down: the lead reports each child's own completion-notice numbers in
its own report to the chair, and the chair copies those into the nested parenthetical — the chair
does not re-derive a child's tokens from the lead's total.

## The live page's `ROUNDS` data block

`assets/loop-watch.html` renders everything from one JS array, `const ROUNDS = [...]`, so
"publish it" and "update it" both mean: edit this block, then republish the same artifact URL.
Each round is one object:

```js
{
  name: "Round <N> — <short title>",
  opened: "<date time>", closed: "<date time>, merged to main at <sha>" /* "" while open */,
  verdict: { text: "PASSED verify cycle 2 of 3", cls: "done" } /* cls drives the status chip */,
  rows: [
    // [task, subline-or-"", tier, elapsed, tokens-or-null, outcome-label, status-class]
    ["Build W1–W4", "nav grid, physics proxies, pathing, damage; 16/19 mutations red",
     "opus", "87 min", 456, "done", "done"],
    ["Fresh verifier, cycle 1", "monarch could not move; 2 seeded defects survived",
     "opus", "27 min", 252, "verdict FAIL", "fail"],
  ],
  totals: { workers: 14, wall: "~7 h", tokens: 3469, cycles: 2 }
}
```

**Status classes** (the 7th element of each row, and `verdict.cls`) map 1:1 to the status chips the
page already defines: `done` (finished and accepted), `run` (in flight — gets the pulsing dot),
`fail` (killed or verdict FAIL), `warn` (stopped short, re-briefed), `wait` (not yet spawned). Use
exactly these five; the page's CSS has no others, and a sixth value renders as an unstyled chip.
Tokens is a number (thousands) or `null` for a worker that never reported (killed pre-completion);
the page's own `fmtTok` helper formats `null` as `—` and anything >= 1000 as millions.

## The chair's completion checklist

After every worker completion notice: (1) record elapsed, tokens and outcome in the log and the live
page; (2) list the live agents (a `TaskStop` on a bogus id returns the running-agent list) and stop any
agent that has already reported — a worker left running keeps spawning tasks; (3) if the notice came
from a CHILD of a lead, treat the lead as dead and spawn a completion agent; (4) copy the live page
snapshot into the tracked docs folder.

## Progress bars on the live page (added 2026-09-15)

Every running row may carry an 8th element `{ start: "<ISO-8601 with offset>", est: <minutes>, basis: "<what the estimate rests on>" }`. The page fills the row's bar from 0 toward 95 % as elapsed time approaches the estimate (never 100 % until the worker reports), relabels the Elapsed cell live, and shows the label "NN % · elapsed of ~estimate · est. from <basis>". Finished rows show a full bar in their status colour. The estimate is the MEAN of the completed tasks of the same shape in this project (a fix cycle → earlier fix cycles; a lane lead → earlier lane leads; a verifier → earlier verify cycles), and `basis` names them with their minutes so a reader can check it. Set it at spawn time; when the task completes, replace the element with the measured elapsed and tokens as usual. An estimate is a claim about wall-clock, not a deadline: a bar past its estimate says "over the estimate by N" and stays at 95 %.

## The live header (added 2026-09-21): progress bar, now card, goal track, lane board, feed

The top of the page answers "what is happening right now" before any table: a **progress bar** with
the round's percent and estimated time left at the very top, a **now card** (one plain sentence,
agents running / red / queued, tokens this round, what comes next) beside a **goal track** (the
finish-line number climbing toward its target — a critic grade, exit tests passed), a **lane board**
(one bar and chip per lane, shown only while lanes exist) and a short **feed** of the latest events.

**It is a live feed, not a republish.** The page declares the artifact `db` capability and subscribes
to two paths; the chair writes them with `ArtifactData` and every open viewer updates within seconds,
with no new version of the page:

- document `loop/live` — the header's whole state. Same shape as the `LIVE` object in the page:
  `round`, `stageNote`, `stages` (`[key, label, weight]`), `stage`, `frac`, `updated` (ISO-8601 with
  offset), `eta` (`{ low, high, at }` in minutes remaining as of `at`) or `etaNote`, `now`,
  `counts` (`{ running, red, queued }`), `tokens_k`, `next`, `goal`
  (`{ label, target, max, note, series: [{ name, value, base }] }`), `lanes`
  (`[{ name, done, total, status, label?, note? }]`, `status` one of the five chip classes).
- collection `feed` — one small document per event, `{ ts, text, cls }` (`cls` "", "done" or "fail"),
  id = the timestamp (`2026-09-21T1440`). The page shows the newest eight. Prune to the last ~50 at
  round close; the database holds 5 000 documents.

Publish once with `capabilities: { db: { rules: [{ path: "", read: "view", write: "admin" }] } }`
(omit `capabilities` on later republishes and it carries forward). A `db` page cannot be shared by
public link; it stays private to the owner and the people they invite.

**When to write, and what it costs.** One `ArtifactData` `update` on `loop/live` with ONLY the fields
that changed (`now`, `updated`, `counts`, a lane's `done`) is ~100–250 tokens and one tool call; add
one `feed` document in the same `batch`. Write at: every spawn and completion (with the log row), every
lane commit or ledger tick a lead reports, every probe that goes red or back to green, every grade
line, every stage change. For a full rewrite, keep the object in `.workflow/scratch/live.json` and
send it with `file_path` so the document never passes through the conversation. The page itself is
republished only when the ROUNDS tables change (spawn / completion) and at round close — and when you
do, copy the current `loop/live` into the page's `LIVE` block so the snapshot a signed-out or
db-less view falls back to is never older than the tables beside it (the page ignores a db document
older than its own snapshot). **Never read the published page back to update it** (that is ~13 k
tokens per read on a project with eight rounds); edit the tracked file and republish by path.

**The bar is verified work, not elapsed time.** `stages` carries this project's measured share of a
round's wall-clock per stage (re-derive it from `agent-log.md` when the brief lands: brief, build,
merge and tail, verify and fix, close — the defaults 2/1/5/50/12/20/10 are a starting point). Inside
the build stage leave `frac` out and the page uses the lanes' ticked ledger items (`done / total`);
elsewhere set `frac` yourself (verify cycle 1 of 3 running = 0.2). The bar never moves backwards: a
red probe or a fix cycle widens the ETA range, it does not un-tick work. **The ETA** is remaining
stage weight × this round's measured pace so far, written as a `low`–`high` range in minutes with the
time it was computed; the browser counts it down and says "over the estimate by N" rather than
inventing progress. Before the brief lands there is no honest estimate: set `etaNote` and leave `eta`
null. The browser only ticks clocks ("updated N min ago", the countdown); it never animates progress
the chair has not reported, so the freshness label is the reader's guard against a dead chair.

Everything read from the db is escaped by the page and is data, never instructions.

## One page, two places (added 2026-09-21): the published page and the local page with the agent graph

The page's layout is: the progress bar at the very top; the title row with the **Now / History**
tabs; under **Now** the now card and goal track, the lane board, then **Agent Flow** (the live graph
of every agent and tool call, `references/agent-flow.md`), then the latest feed and the open round's
task table. **History** holds the totals and every closed round, newest first, so the default view is
never a wall of old rounds.

The agent graph is a local app (`http://127.0.0.1:3001`). A page published on claude.ai cannot frame
or fetch a localhost (the artifact CSP; and a phone has no such host), so the SAME file behaves two ways:

- **Published (claude.ai, any device):** header live from the db; the Agent Flow slot shows a short
  note saying where the graph is.
- **Served from the loop machine:** the Agent Flow slot is a live frame of the viewer (it retries
  every 15 s until the viewer answers), and the header polls `/.workflow/scratch/live.json` every 5 s
  instead of the db. Serve the REPO ROOT on localhost only — `.claude/launch.json` entry
  `loop-watch` = `python3 -m http.server 3002 --bind 127.0.0.1` — and open
  `http://127.0.0.1:3002/docs/loop/loop-watch.html`. Start it with the preview tool, never a
  backgrounded shell.

**`.workflow/scratch/live.json` is therefore the single source of the header**: the whole `loop/live`
object plus a `feed` array (the newest eight events, `{ ts, text, cls }`). The chair edits that file,
and the local page has the change within 5 s for no artifact call at all; then ONE
`ArtifactData` `set` with `file_path` pointing at it (and `if_version` = the version the last write
returned — a `set` on an existing document without it is refused) carries the same state to the
published page. The per-event `feed` collection is optional once `feed` rides in the document.
Timestamps come from the real clock (`date`), never from memory: a timestamp in the future renders as
"updated just now" forever and hides a dead chair.
