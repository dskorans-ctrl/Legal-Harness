Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Continue round 7 of casefile on `loop/round-07` (opened in the round 6 session; the owner check-in is DONE, ledger Q60 and Q61: skip it and go straight to the brief). If round 7 is already closed, start round 8 instead with its check-in. For a fresh round 8, begin with the owner check-in: present the design calls
pending veto (spec §9 D44 to D51 and D52 to D62, and the chair's round 6 build rulings in the ledger), the round 6 output
critic's remaining findings (`docs/loop/round-06/round06-critic2.md` M1 to M6, leading with M1, fact identity), the 15
practice questions at the end of `docs/loop/design/output-format-from-examples.md`, and the round 7 scope choice in the
HANDOFF (recommended: spec §7 stage 7, the brief package and the anonymizer under casefile-anon/1, with critic 2 M1
folded in; the owner's Q59 items 82 to 86 and the format specification either here or in a stage 6 follow-up round, as
the owner decides). Record every answer under `## Clarified`, and finish with "Any additional instructions for the next
round or the loop in general?". Tiers (owner Q46): Fable writes and revises the brief; fresh Fable agents do the plan
review and the code review (read-only); Opus 5.5 orchestrates and runs the output critic and the blind verifier; Codex
`gpt-6.1-sol` codes and fixes through `codex exec` (see HANDOFF machine rules). Then: brief, plan review, Fable revision,
chair rulings, build, critic round (code review, output critic, blind verifier, in that order, each separate), fix cycles
(cap three), and close: round report, Librarian, agent log, spec §11 as-built, ledger baselines, fast-forward `main`,
open `loop/round-08`, owner check-in. Practice content comes from the playbook, the firm skills and the owner. Every
record is an invented fixture; no real client data at any point. Do not start round 8. At close, write the handoff and
the next-round prompt, prompt the owner to `git push origin main`, and stop.
