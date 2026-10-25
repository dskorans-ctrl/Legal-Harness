# casefile: loop handoff (seeded 2026-10-25)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Standing rules digest`, `## Clarified`),
then `Librarian.md`. Spec (canon): `docs/spec.md`. The loop runs with the `app-loop` skill
(`.claude/skills/app-loop/SKILL.md`), with `app-development` for routing.

## Where things stand
- Repo seeded 2026-10-25: spec, ledger, blank Librarian, the app-loop skill, and the earlier cards,
  schemas and full reference skills (`cards/`, `schemas/`, `reference/`). No code yet.
- Next: round 1, spec §7 stage 1 (skeleton, config, rules file, playbook loader, run log,
  `casefile doctor`) plus the harness in the ledger's `## Project` block (`scripts/run.sh`, the
  stand-in model server, the gate).

## Held owner questions
- File: `docs/loop/questions-for-owner.md`. Ask Q10 (tiers) at round 1's clarify.

## Round close
- After the green merge to main, prompt the owner to push: `git push origin main`.
- Rewrite this page and `docs/loop/next-round.md`; give the owner the one command to start the next session.

## Machine rules
- Every run goes through `scripts/run.sh` (once it exists). One model or app run at a time.
- Codex: `codex exec -m gpt-6.1-sol -s read-only ... < /dev/null`, sandbox off, in the background.

## Cost rules (owner)
- One orchestrator alive at a time. Builders report once, no polling. Logs to files, short summaries,
  small tool outputs. A fresh session per round; this page is the entry point.
