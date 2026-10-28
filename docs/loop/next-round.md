Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Resume round 5 of casefile (spec §7 stage 5: case file, merge, medical memo) on `loop/round-05`. Remote Control on.
Tiers (owner Q46): Fable writes the brief; a fresh Fable agent does the plan review and, later, the code review
(read-only); Opus 5.5 orchestrates and runs the output critic and the blind verifier; Codex `gpt-6.1-sol` codes and
fixes through `codex exec` (see HANDOFF machine rules). Start where the ledger's `## Round 5` section stops. First
present `docs/loop/questions-for-owner.md` (47 to 49 and any round 5 questions) and the design calls pending veto
(D31 onward) at a check-in. Then: brief, plan review, Fable revision, chair rulings, build, critic round (code
review, output critic, blind verifier, in that order, each separate), fix cycles (cap three), and close: round
report, Librarian, agent log, spec §11 as-built, ledger baselines, fast-forward `main`, open `loop/round-06`, owner
check-in. Every record is an invented fixture; no real client data at any point. Do not start round 6. At close,
write the handoff and the next-round prompt, prompt the owner to `git push origin main`, and stop.
