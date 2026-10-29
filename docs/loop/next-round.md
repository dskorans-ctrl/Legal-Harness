Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Start round 8 of casefile on `loop/round-08` (opened at the round 7 close with no work). Begin with the owner check-in:
present the design calls pending veto (spec §9 D63 to D68 and the chair's round 7 rulings in the ledger `## Round 7`),
the round 7 recorded limits (HANDOFF "Carried into round 8"), and the round 8 scope choice in the HANDOFF: (a) stage 7b,
the cloud round trip (D52 to D62, `docs/loop/design/cloud-roundtrip-proposal.md`), or (b) the stage 6 output follow-up
(owner Q59 items 82 to 86, the 15 practice questions at the end of `docs/loop/design/output-format-from-examples.md`,
`docs/loop/round-06/round06-critic2.md` M2 to M6). Record every answer under `## Clarified`, and finish with "Any
additional instructions for the next round or the loop in general?". Tiers (owner Q46): Fable writes and revises the
brief; fresh Fable agents do the plan review and the code review (read-only); Opus 5.5 orchestrates and runs the output
critic and the blind verifier; Codex `gpt-6.1-sol` codes and fixes through `codex exec` (see HANDOFF machine rules).
Then: brief, plan review, Fable revision, chair rulings, build, critic round (code review, output critic, blind
verifier, in that order, each separate), fix cycles (cap three), and close: round report, Librarian, agent log, spec §11
as-built, ledger baselines, fast-forward `main`, open `loop/round-09`, owner check-in. Practice content comes from the
playbook, the firm skills and the owner. Every record is an invented fixture; no real client data at any point. Do not
start round 9. At close, write the handoff and the next-round prompt, prompt the owner to `git push origin main`, and
stop.
