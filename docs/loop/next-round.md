Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Run round 3 of casefile (spec §7 stage 3: intake and OCR with page IDs) on `loop/round-03`. Remote Control
on. Start with the check-in: owner questions 21 to 29 (and the round 1 holds) in
docs/loop/questions-for-owner.md, then "Any additional instructions for the next round or the loop in
general?". Default tiers (Q30): Fable brief (carry the items listed in the handoff), Codex plan review,
Fable revision, build (Opus orchestrates, Sonnet 5.5 codes), critic round (Codex code review, output
critic, blind verifier, in that order, each separate), fix cycles (cap three), and close: round report,
Librarian, agent log, spec §11 as-built, ledger baselines, fast-forward `main`, open `loop/round-04`,
owner check-in. The scanned PDF and every other record are invented fixtures; no real client data at any
point. Do not start round 4. At close, write the handoff and the next-round prompt, prompt the owner to
`git push origin main`, and stop.
