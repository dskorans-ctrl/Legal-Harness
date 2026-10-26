Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Run round 1 session 2 of casefile: Remote Control on; first ask the owner which tiers to use this
session (owner said they would change them once they have more usage). Then run the critic round
on `loop/round-01` (Codex code review, output critic, blind verifier, in that order, each separate),
fix cycles if needed (cap three), and close: R1-12, round report, Librarian, agent log, fast-forward
`main`, open `loop/round-02`, owner check-in. No real client data at any point. Do not start round 2.
At close, write the handoff and the next-round prompt, prompt the owner to `git push origin main`,
and stop.
