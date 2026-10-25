---
name: app-loop
description: Run an app spec to completion as a create → build → critic loop, one round per fresh session, with a Requirements Ledger, a Fable-written brief per round that Codex attacks before Fable revises it, an Opus orchestrator that hands coding to Sonnet sub-agents, a critic round (Codex code review, an output critic, then a blind fresh verifier that seeds defects before trusting any green), a Librarian of every past bug, an agent log, and owner check-ins between rounds. The app version of gdd-loop. Use when the owner says "run the loop", "next round", "round 3", "start round N", "keep building", or hands over the spec and says "build this" for an app (first project casefile).
---

# App loop: one round per session, nothing green until it has been red

This is `gdd-loop` adapted for an app. The shape is unchanged: each round has **create** (a Fable
architect writes the brief, Codex attacks it, Fable revises it), **build** (an Opus 5.5 orchestrator
hands every coding task to Sonnet 5.5 sub-agents) and **critic** (a Codex review of the round's code,
an output critic that grades what the app produces, then a fresh blind verifier). The chair (you)
clarifies, rules, sequences, merges and reports. The chair's tokens are for judgment; bulk goes to
workers and stays on disk.

What changed from `gdd-loop`: the GDD is the **spec** (`docs/spec.md`); the engine is the app's own
test harness; rendered frames become **outputs** (Word documents, the web page) that are opened and
described; the art critic becomes the **output critic**; every round runs in its **own fresh
session**; and **no client data** ever enters a loop session.

## First use on a project: the project contract

Recorded once in the `## Project` block at the top of `.workflow/LEDGER.md`
(`references/project-contract.md` has casefile's, filled). It names: the spec path and its five
required parts (pillars, decisions table, open questions, roadmap with an exit test per stage,
as-built); the harness commands (tests, the benchmark, a full run on the invented test matter, the
page screenshot) and the output-capping wrapper they all run through; the finish line in the owner's
words; and the regression baselines. If the spec lacks a part, append it as an appendix and say so at
the first check-in. Never restructure the owner's document.

## Every session: Remote Control on, one round only

1. **Remote Control first.** Before anything else, turn on Remote Control so the owner can follow
   and steer from claude.ai/code or the phone. In the Claude desktop app call
   `mcp__ccd_session_mgmt__set_remote_control` with `session_id: "self"`, `enabled: true` (load it
   with ToolSearch if deferred) and say in one line that it is on. In a terminal session, it is on
   already if `~/.claude/settings.json` has `"remoteControlAtStartup": true`; otherwise tell the
   owner to type `/rc` and carry on without waiting. If it is unavailable, say so once and move on.
   Put anything the owner should see from another device in front of them with `SendUserFile`.
2. **One round per session.** A session reads `docs/loop/HANDOFF.md` (one page) first, runs exactly
   one round (or one named part of one), closes it, and ends. It never starts the next round. Long
   sessions re-read everything on every turn and cost the owner's usage; a fresh session starts from
   one page.
3. **At close, hand off.** Rewrite `docs/loop/HANDOFF.md` (where things stand, what is carried, held
   owner questions, machine rules) and write `docs/loop/next-round.md`: the exact opening prompt for
   the next session, starting "Use the app-loop skill. Read docs/loop/HANDOFF.md first." Then tell
   the owner the one command: `cd <repo> && claude "$(cat docs/loop/next-round.md)"`.

**Cost rules (owner, carried from Victory Realm):** one orchestrator alive at a time; builders
report once when done, with no polling or "still running" check-ins; logs go to files with a short
summary in the reply; small tool outputs (`wc`, `grep -n`, head and tail ranges), never a whole large file.

## Privacy: no client data, ever

Loop sessions run in the cloud model's context. **No real client record, name or fact enters a loop
session**, on any machine. Development uses invented test matters only (`tests/fixtures/matters/`),
written to look real but about invented people. The benchmark's real closed matters live only on
the Studio under `~/Bench/` and are run there by the owner, never opened by an agent. Every builder
and verifier prompt carries this rule. A gate check fails if the repo contains a PDF, Word file or
image outside `tests/fixtures/`, or anything under `Cases/` or `Bench/`.

## The round, in order

1. **Clarify** (round 1, and at every between-round check-in; `references/checkin.md`). Read the
   repo first; never ask what it answers. Ask with `AskUserQuestion` until you could write a
   worker's spec without guessing. Finish every check-in with: *"Any additional instructions for the
   next round or the loop in general?"* Record every answer under `## Clarified` in the ledger.
2. **Ledger.** Write `.workflow/LEDGER.md` before any spawn (`references/ledger-template.md`).
   Items numbered; `[x]` only after verification; `[~] deferred:` only with an approver; `V.` last,
   ticked only by the verifier. Discoveries appended, never folded in.
3. **Brief (Fable).** Spawn a Fable agent to write `.workflow/scratch/roundNN-build-brief.md`
   (`references/prompts.md` §1). It reconciles the spec, the plan and the code as it is today,
   decides everything a builder would otherwise guess, gives each work item a CHECK that prints the
   one number that fails it plus the seed that must turn it red, maps lanes on disjoint files, and
   lists the questions only the owner can answer.
4. **Adversarial plan review (Codex).** Run Codex read-only on the brief (§6, command below). Report
   to `.workflow/scratch/roundNN-brief-codex.md` and a tracked copy under `docs/loop/round-NN/`.
5. **Revision (Fable).** Fable updates the brief and appends a disposition table: every finding
   ACCEPTED, REJECTED (with evidence) or OWNER (§7). One pass. Then rule on each decision yourself
   and log the rulings in the spec's decisions table, pending owner veto, before any code is written.
6. **Build (Opus orchestrates, Sonnet codes).** The chair runs as the Opus 5.5 orchestrator (a chair
   on another model spawns one Opus 5.5 orchestrator with §2 and stays out of the build). Sonnet 5.5
   sub-agents (`model: "sonnet"`) do all coding, each on a disjoint file set; a second concurrent
   builder gets `isolation: "worktree"`. Every builder brief cites the Librarian and names every file
   in the defect's call graph. The orchestrator re-runs each builder's CHECKs and seeds before merging.
7. **Merge and tail.** Merge the lanes; run sequential items that touch both lanes' files with one
   Sonnet builder; close items (spec rows, Librarian, questions file, reports under `docs/loop/round-NN/`).
8. **Critic round.** Three passes, in this order, each kept separate:
   - **a. Codex code review** of the round's diff (`git diff main...loop/round-NN`; §8). Every
     finding is a hypothesis: the orchestrator reproduces each one (run it, compute it, or trace it to
     the line) before it becomes work. Reproduced findings go to Sonnet fix builders (§4) under the
     seed-red-first rule; ones needing design work go to the next brief with the owner's say-so. Log
     all of them in the ledger and the Librarian (`R<NN>-CX-*`).
   - **b. Output critic** (§9). A fresh Opus agent that built nothing runs the app end to end on the
     invented test matter, opens every output this round touched (Word documents, the web page via a
     Playwright screenshot), and grades them against the answer key and the firm's practice rules
     (`playbook/`, and the `deposition-prep`, `workers-comp-hearing-prep` and
     `motion-brief-memo-drafting` skills where they apply). It reports what an attorney would
     actually see: a missing visit, a wrong cite, a forbidden term, a question that breaks a firm
     rule. Its grade line goes in the round report. Its findings are hypotheses for the orchestrator
     to reproduce, like Codex's.
   - **c. Blind verifier** (§3). A fresh Opus 5.5 verifier gets the original request, the ledger
     path, the final tree and a bare list of source lines the builders already mutated, **not** the
     builders', Codex's or the critic's reports. It re-runs every CHECK from the ledger's own wording,
     seeds at least three defects on lines nobody mutated, opens the outputs and says what they show,
     and ticks items only with its own evidence. Only after every item is ticked or refused does it
     open the reports, to reconcile. It ticks `V.` only when every non-deferred item is `[x]`.
   Findings become a fix cycle (Opus orchestrates, Sonnet fixes). Cap three verify-fix cycles per
   round (8a's fixes count as the first), then discard the round and re-brief. Two stalled rounds in
   a row: stop and report to the owner.
9. **Close.** Finalise the round report (verdict first, measured numbers with the check that produced
   each, the output critic's grade, design calls pending veto, discoveries, process notes), update the
   Librarian (§5), the agent log and the live page, fast-forward merge to `main`, open the next
   branch, write the handoff (above), then check in with the owner. `main` is pushed to GitHub only on
   the owner's word: prompt them to run `git push origin main`.

### Running Codex

Codex runs as the local `codex` CLI, never as a sub-agent and never with write access:

```bash
codex exec -m gpt-6.1-sol -s read-only -c model_reasoning_effort=high -o <report.md> "<prompt>" < /dev/null > <report.log> 2>&1
```

Close stdin (`< /dev/null`) or it waits forever. Run it with the sandbox off, in the background, and
wait for its completion notice; check the log grows within about five minutes. Every prompt says:
static review only, do not modify files, do not run the model or the app. Log each run in the agent
log. If the CLI is missing or the model is refused, tell the owner and put an Opus 5.5 reviewer in
that seat, recorded as a deviation. Never skip the review silently.

Branch per round (`loop/round-NN`); merge only after `V.`; commit with targeted paths, never
`git add -A`; read `git diff --cached` at hunk level when another agent shares the tree.

## Verification discipline

A green check that has never been red is a decoration. For every new test, check or gate: baseline
green → mutate the one load-bearing line → RED → restore byte-identically (`cmp`) → green. Report
`Claim / Verified by / Control / Not verified` with every claim. The classes that recur
(`references/catalog.md`):
- a check that reads the constant it bounds cannot see it move: assert against the literal spec;
- presence-anywhere and substring checks are fail-open; a flag with a silent default is fail-open;
- two guards that both fire on every case mask each other: isolate each;
- a check that skips when its subject is absent is a pass it never earned: FAIL, never skip;
- an exit code that does not carry the verdict; a default branch that overrides a child's exit;
- a finding in a report is a hypothesis: reproduce it before acting;
- never a by-name exemption in a failing metric: fix the metric or record the limit;
- migrations enumerated by list get one behavioural test per member.

App-specific classes, from the harness design:
- **Fail closed.** A model answer that fails a gate is retried once, then its pages are marked failed
  in the coverage ledger. A test proves an empty or truncated answer is never saved as a result.
- **Truncation is a failure.** Every model-call test includes a cut-off answer and a prompt longer
  than the context, and both must go red.
- **Quotes are checked against the source in code**, never trusted from the model. The quote-check
  test includes a near-miss quote that must be rejected.
- **Firm rules are gates, not hopes.** Each rule in `rules.toml` has a test with a forbidden output
  that must go red.

A feature is not done until a driven run used it: the full pipeline on the invented test matter
and, where the feature is visible, the output opened and described. An output's file name is a
claim; its check must test content.

## The Librarian

`Librarian.md` at the repo root logs every bug, code issue and failure, in three sections: a
**builder pre-flight** (one question per failure class, pointing at an entry), **per-round entries**
(What broke (file:line) · Why (the class) · Caught by · Countermeasure · Status) and **open items**.
Every builder reads it first and reports which entries it checked. One Librarian per project, started
blank. Format: `references/librarian.md`. Cross-project classes go in `references/catalog.md` (a copy
of gdd-loop's catalog, taken 2026-10-25; app classes are appended here at round close). Never paste
the catalog into the Librarian.

## Visibility

- `docs/loop/agent-log.md`: per round, one row per worker and child: task, tier, started, elapsed,
  tokens, outcome; failed and restarted launches too; a total row (`references/agent-log.md`).
- The live page (`assets/loop-watch.html`): progress bar on verified work, a "now" card, the lane
  board and a feed. Publish it as a private artifact with the `db` capability on first request and
  feed it with small `ArtifactData` writes (`references/agent-log.md`, "The live header").
- Agent Flow, the second window (`references/agent-flow.md`): the owner starts it, never the chair.
- Round reports and work products live under `docs/loop/round-NN/` (tracked).

## Owner rules this skill carries

- **Tiers.** Fable writes and revises each round's brief; no other Fable agent without permission.
  Codex `gpt-6.1-sol` reviews the plan and the code. Opus 5.5 orchestrates, critiques outputs and
  verifies; Sonnet 5.5 writes all code. The owner may change tiers at any check-in (record it as a
  Clarified line).
- **Autonomy.** If the owner is offline, hold questions in `docs/loop/questions-for-owner.md`, rule
  by the spec's pillars, log each ruling as "pending veto", and keep going. Present the file at the
  next check-in.
- **Pushback.** Recommend changing any prior decision, including the owner's, when it hurts the
  loop; state the failure mode and a fix; let them veto.
- **Canon.** The spec wins over plans, comments and rules files; every design change lands in its
  decisions table; new questions in its open-questions section.
- **Tuning questions are not check-in questions.** A prompt wording, threshold or chunk size is
  settled by the benchmark, not by argument. Park such questions in `docs/loop/tuning-questions.md`
  with the as-built value, its file:line and what the benchmark says.
- **Legal content questions are the owner's.** What a deposition or hearing output should contain is
  practice, not engineering: it comes from the playbook and the owner, never from a builder's taste.
- **Prose** has no em or en dashes.

## Disciplines this loop is built from (bundled, read on demand)

- **Orchestrator:** `references/bundled/orchestrator/SKILL.md`: clarify axes, ledger rules, the
  40-line worker report, routing and effort by tier. Read at the start of a round and before spawning.
- **Andon:** `references/bundled/andon/SKILL.md`: defect → root cause → countermeasure → result,
  the Mistakes Log and Defect Ledger. Read when a mistake recurs, when an agent over-claims, and at close.
  (Its reference folder, the orchestrator plugin, the verification-discipline harness and the Agent
  Flow source are in the original `gdd-loop` skill under `references/bundled/`; they are not copied.)
- **Verification discipline:** this skill's section above.

Also use `app-development` for routing (design, UI, pipeline, engineering modules) and the firm
skills for legal content.

## Reference map

```
references/
├── project-contract.md   the `## Project` block for casefile: spec, harness, finish line, baselines
├── ledger-template.md    the Requirements Ledger (from gdd-loop; read "GDD" as "spec")
├── prompts.md            §1 brief · §2 builder · §3 verifier · §4 fix cycle · §5 close ·
│                         §6 Codex plan review · §7 Fable revision · §8 Codex code review · §9 output critic
├── checkin.md            the between-round check-in, adapted
├── librarian.md          Librarian.md format (from gdd-loop)
├── catalog.md            cross-project failure classes (copy of gdd-loop's; append app classes)
├── agent-log.md          agent log and live page data (from gdd-loop)
├── agent-flow.md         the second window (from gdd-loop)
└── bundled/              orchestrator and andon SKILL.md files, NOTICE.md
assets/
└── loop-watch.html       the live status page
```
