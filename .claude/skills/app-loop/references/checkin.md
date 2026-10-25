# The between-round check-in (app-loop)

Adapted from gdd-loop. Read "spec" (`docs/spec.md`) wherever the original said GDD.

Run this at round 1's start and again after every round closes (`V.` ticked, merged to main,
before the next branch opens). Its purpose is to remove every guess a builder would otherwise have
to make — ask front-loaded rounds of questions with `AskUserQuestion` until you could write a
worker's spec without guessing, then record the answers where the loop actually reads them.

## The seven clarify axes, plus the branch question

Ask about each axis that isn't already answered in the ledger's `## Clarified` section or the spec.
Never ask what the repo already answers — read the ledger and the spec first.

1. **Scope edge.** What is in this round/loop, and what is explicitly not — say the boundary
   plainly rather than let it be inferred from what got built.
2. **Done-means.** What is the observable that ends the loop, or ends this round? A number
   ("the benchmark passes on every closed matter"), a passing exit test, a specific behaviour — not a feeling.
3. **Constraints.** Any standing freeze, budget, or technical limit that bounds what a builder may
   touch this round.
4. **Who owns taste.** When a design call has no single right answer, who decides — the owner, the
   chair by pillar, a named reviewer?
5. **Priority conflicts.** If two goals this round trade off against each other, which wins?
6. **Contact with existing code.** Is a freeze on touching certain systems lifted or still in
   force? Say each one by name; a freeze nobody restates is a freeze nobody remembers to obey.
7. **Failure behaviour.** What happens when a round can't be made to pass — retry, discard and
   re-brief, or stop and ask? How many attempts before that decision fires?
8. **The branch question.** Where does this round's work land, and under what condition does it
   merge to main? Ask this every check-in even if the answer is "same as last round" — a silent
   assumption here is how work lands somewhere nobody is watching.

## Presenting held questions, with interim rulings

If any questions accumulated while the owner was away (offline protocol, below), present the full
list at the check-in, each with the ruling that was made in the owner's absence:

```
N. <the question, stated plainly>. Ruling: <what was decided and why, one sentence>. <Agree, or
   say what you'd have decided instead.>
```

Do not bury these inside other conversation — a ruling made without the owner is provisional by
definition, and a check-in that doesn't surface it as a question defeats the point of asking. Wait
for an explicit answer or an explicit "keep the ruling" before treating it as settled; silence is
not agreement.

## The mandatory open-ended question

End every check-in, without exception, with exactly this question:

> "Any additional instructions for the next round or the loop in general?"

This exists because the fixed axes above are a floor, not a ceiling — an owner may have a rule in
mind that doesn't map onto any of the seven, and the only way to surface it is to leave the door
open explicitly rather than assume the fixed list was exhaustive.

## Tuning questions are not check-in questions

A question about a tuning value (a chunk size, a retry count, a prompt wording, a threshold in a gate)
is settled by the benchmark, not by the owner's opinion from a report. Park it in
`docs/loop/tuning-questions.md` with the as-built value, its file:line and what the benchmark says,
and move it only when a measured defect forces it, logged as a decision. Questions about practice
content (what a deposition outline must include, how a question should be asked, what a hearing
needs) ARE owner questions: they go to the check-in, and the answer goes into `playbook/`.

## Recording answers

Every answer, fixed-axis or open-ended, becomes one new line under the ledger's `## Clarified`
section — numbered `Q<next>`, never edited into an existing line (a correction is a new Q-number
that supersedes the old one, so the record of what changed and when survives). A standing rule
that should bind every future round as well (not just the next one) also gets written to the
project's memory / standing-rules file, in the chair's own words, so it survives a fresh session
that has not re-read the whole ledger.

## The offline protocol

If the owner says they are going offline (for any length of time) and wants the loop to keep
running without them:

1. Hold every question that would otherwise go to the owner in `docs/loop/questions-for-owner.md`
   — append, one numbered entry per question, grouped by the round it arose in; never overwrite.
2. Rule on each one yourself, by the spec's stated design pillars (not by guessing what feels
   right) — log the ruling in the spec's own decisions table as "pending veto," so the spec stays
   the single place a builder looks to find the current, binding call.
3. Keep running rounds; a held question never blocks a round in progress. Log every ruling with
   enough reasoning (the measured numbers, the alternative rejected, why) that the owner can veto
   it on the numbers alone rather than having to re-derive them.
4. At the next check-in, present the full questions file in order, each with its interim ruling,
   before opening the next round's brief — the next round waits on the owner's answers precisely
   because a ruling made blind is the one class of decision that most needs a human check before
   it compounds into a second round's premises.

## Tell the owner where answers land

Close every check-in by saying, in one sentence, that each answer is recorded as a numbered entry
under `## Clarified` in `.workflow/LEDGER.md` (and, for standing rules, in memory), so the owner knows
their words become the binding record the workers read. Iteration-1 evaluation of this skill found the
check-in otherwise complete but silent on this, and the owner cannot know a rule stuck unless told.
