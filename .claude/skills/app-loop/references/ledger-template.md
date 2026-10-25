# Requirements Ledger — template

Write this file at `.workflow/LEDGER.md` before spawning anyone, first round and every round after.
It is the single source of truth for what is in scope, what "done" means, and what has been
verified — a builder or verifier who has read only this file (plus the GDD and the Librarian)
should be able to work without guessing. Update it in place; never keep a second copy.

```markdown
# <Project name> — loop ledger

Chair: <who/what is running the loop>. Loop: create → build → critic/QA → verify, one round per
branch. Owner decisions are binding; see `## Clarified`. Round 1 opened <date>.

## Clarified
- Q1: which tracks are in scope? -> <e.g. gameplay first, then art to a numeric grade>
- Q2: what does finalized mean? -> <the observable that ends the loop, e.g. "critic grade >= 8.5
  day and night AND every phase's exit test passes under a driven playtest">
- Q3: are any standing freezes lifted? -> <name each one and its new state explicitly; a freeze
  nobody restates is a freeze nobody remembers to obey>
- Q4: where does work land? -> branch per round `loop/round-NN`, merged to main only after the
  fresh verifier ticks `V.`; a round that fails verification is discarded, not patched in place
- Q5: stall rule? -> a round failing verification <N> times is discarded and re-briefed; two
  consecutive stalled rounds stop the loop and report to the owner — a loop that can fail forever
  without saying so is not autonomous, it is lost
- Q6: probe rule? -> every new probe, test or gate must go red on a seeded defect before its pass
  counts (a green that was never red is a decoration, not evidence)
- Q7: who rules on gaps while the owner is offline? -> the chair, by the GDD's design pillars,
  logged in the GDD's decisions table and the round report, owner vetoes at the next check-in
- Q8: engine-use rule? -> <when workers may launch/drive the engine, headless or windowed, and
  what a rendered capture needs (e.g. the sandbox disabled)> — say this once so nobody re-asks it
- Q9: check-in cadence? -> the owner is asked between rounds; if the owner is offline, hold
  questions and keep working rather than stall the loop on a reply that may not come
- Q10+: <scope-specific rulings as they arise — each gets its own numbered line, never edited
  after the fact; a correction is a new Q-number that supersedes, so the record of what changed
  and when survives>
- Q<N>: tier rule? -> <which tiers write briefs vs. build vs. verify, and any standing permission
  needed to use a higher tier — stated once so the chair doesn't re-ask every round>
- Q<N>: delegation rule? -> <may a lane lead split its own work to sub-agents, and what those
  children may never be (e.g. never the tier that writes the brief) — this is what makes "lane
  lead" different from "sole worker" and needs to be explicit before anyone delegates>
- Q<N>: open-question rule? -> every between-round check-in also asks one open-ended question
  ("any additional instructions?") so the owner can hand over anything the fixed axes didn't
  cover; each answer is recorded here as a new Clarified line, not folded into an old one
- Branch: round 1 on `loop/round-01` (merged to main at `<sha>`); round 2 cut from main at `<sha>`
```

Why a `## Clarified` section at all: every one of these is a question a builder would otherwise
have to guess, and a guess made under deadline pressure defaults to whatever is easiest to build,
not whatever the owner meant. Answering it once, in writing, removes the guess.

## Item notation

Every work item is numbered and carries exactly one status mark:

- `- [ ] N. <description>` — not yet done.
- `- [x] N. <description> — **VERIFIED (cycle K):** <the evidence, verbatim numbers, not a
  restatement of the claim>` — done. `[x]` is set only by (or after) the verifier, never by the
  builder who did the work; the builder who claims their own work is the failure mode this whole
  loop exists to prevent.
- `- [~] N. deferred: <what, and to where> — <who approved the deferral>` — explicitly out of
  scope for this round. A deferral needs a named approver (the owner, or a chair ruling under the
  offline-ruling rule) so "deferred" cannot quietly mean "forgotten."
- `V.` — always the last item of the round, ticked only by the fresh verifier, only when every
  non-deferred item above it is `[x]`. `V.` is the round's one bit of truth; nothing before it
  means anything until this is set.

Numbering is per-round and never reused: round 2's items are `R2-1, R2-2, …`; a discovery gets the
next free number in whatever section it was found in, appended, never inserted to keep a sequence
tidy — renumbering erases the order things were actually found in.

## A round section (example, filled)

```markdown
## Round 2 — <round title> (opened <date>)

- [x] R2-1. Build brief reconciled to the code at `<sha>` for every item below, with file/function/
  line refs and a headless CHECK per item. `.workflow/scratch/round02-build-brief.md` — **VERIFIED
  (cycle 1):** brief present at both paths, N lines, N CHECK blocks with file/function refs.
- [x] R2-2. <e.g. "W5 Thief: kind row, FLEEING state, steals 5 units from the fattest reachable
  pile, loot drops on death"> — **VERIFIED (cycle 1):** `PHASE1_THIEF PASS` reproduced verbatim;
  an unseeded seed (`enemy.gd:371`, the post-steal state transition removed) went RED — `the Thief
  is in state 0 after stealing, not FLEEING(2)`; tree restored byte-identical.
- [~] R2-17. deferred: <item> → round 3 (owner, Q11).
- [x] V2. fresh-eyes verification passed — **PASSED <date> (cycle 2, @ `<sha>`):** every
  non-deferred round-2 item is `[x]`; both cycle-1 survived seeds now go RED; full regression
  re-run here: <the actual gate lines>.
```

Every `[x]` line's evidence is a verbatim number or quoted line from a real run, never a
paraphrase — "PASS" with nothing after it is not evidence, it is the claim restated.

## A discoveries section

Anything found mid-round that isn't the work item being built goes here, not folded into the item
whose work surfaced it — folding it in erases the fact that it was unplanned, which is exactly the
information the next round's brief needs to scope correctly.

```markdown
## Discoveries during round N (appended, not yet scheduled)

- [ ] N. <what was found, measured, with the file:line and the number>. <what GDD/plan clause it
  violates, if any>. → <owner question at check-in, or candidate round-(N+1) item>
```

A discovery is closed the same way any item is: `[x]` with verifier evidence, `[~]` deferred with
an approver, or carried forward untouched into the next round's own section under its own new
number — never silently dropped.

`V.` is always the very last line of the ledger's active round. Nothing after it; nothing before
it is trusted until it is set.
