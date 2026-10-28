Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Start round 6 of casefile (spec §7 stage 6: outputs, that is the deposition, hearing and report-analysis Word
documents built from the test matter, cards built from the playbook, and the `cards/` and `schemas/` rewrite) on
`loop/round-06`. Remote Control on. Begin with the owner check-in: present `docs/loop/questions-for-owner.md` 47 to 58
(lead with 56) and the design calls pending veto (spec §9 D31 to D43 and the chair's build rulings for rounds 4 and 5),
record every answer under `## Clarified`, and finish with "Any additional instructions for the next round or the loop
in general?". Tiers (owner Q46): Fable writes and revises the brief; fresh Fable agents do the plan review and the
code review (read-only); Opus 5.5 orchestrates and runs the output critic and the blind verifier; Codex `gpt-6.1-sol`
codes and fixes through `codex exec` (see HANDOFF machine rules). Then: brief, plan review, Fable revision, chair
rulings, build, critic round (code review, output critic, blind verifier, in that order, each separate), fix cycles
(cap three), and close: round report, Librarian, agent log, spec §11 as-built, ledger baselines, fast-forward `main`,
open `loop/round-07`, owner check-in. What a deposition or hearing output contains is practice: take it from the
playbook and the firm's `deposition-prep` and `workers-comp-hearing-prep` skills, and ask the owner where they do not
settle it. Every record is an invented fixture; no real client data at any point. Do not start round 7. At close,
write the handoff and the next-round prompt, prompt the owner to `git push origin main`, and stop.
