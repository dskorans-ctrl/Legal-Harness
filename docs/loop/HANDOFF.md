# casefile: loop handoff (2026-10-25, end of round 1 session 1)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q21, `## Round 1`,
`## Discoveries during round 1`), then `Librarian.md`. Spec (canon): `docs/spec.md`.

## Where things stand
- Round 1 (spec §7 stage 1 plus the harness) is BUILT but NOT verified, NOT merged. Branch
  `loop/round-01` at 9d05301 plus the close commit. `main` is still at the seed 5a55b54.
- Built by Codex gpt-6.1-sol (owner Q14): run.sh, skeleton, config, run log, stand-in model server,
  rules.toml, playbook loader, doctor, gate, stage 1 exit test. Chair re-ran CHECKs and seeds (ledger
  "Build note" lines; notes, not ticks). Full suite `98 passed`; gate prints `0`.
- Stage 1 exit test: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1` (OCR FAIL by Q11).
- Brief (tracked copy): `docs/loop/round-01/round01-build-brief.md`. Codex lane reports in the same
  folder: the blind verifier must NOT open them until it has ticked or refused every item.

## Next session: round 1 session 2 (critic round and close only; owner Q15)
1. Ask the owner the tiers for this session first (Q14/Q15 said they would "switch it all up").
2. Critic round (SKILL.md step 8): a. Codex code review of `git diff main...loop/round-01`;
   b. output critic: stage 1 has no Word or page output, so it grades `casefile doctor` and gate
   output and `playbook/rules.toml` against the firm rules (owner Q16); c. blind verifier, mutated
   lines list: run.sh:4-5 and the cap `head -c`; conftest.py:34; config.py:82; runlog.py:32;
   rules.py:59; fakemodel truncated reason; playbook `why` check and digest bytes; doctor context and
   READY equality; privacy exclusion and prefix; gate return; prose U+2014; stage companion seeds.
3. Fix cycles (cap three), close (R1-12: spec §11 as-built, Librarian round-1 entries incl. R1-14 and
   R1-17, round report), fast-forward `main`, open `loop/round-02`, owner check-in.

## Held owner questions
- `docs/loop/questions-for-owner.md`: Q7 (Ollama as login user or launchd daemon) still open.
- Pending veto: spec §9 D12 to D21 and D23 (chair rulings).

## Machine rules
- Every run through `scripts/run.sh`. Toolchain lives at `~/.casefile-dev/legal-harness` (D23); a
  fresh checkout or worktree needs `scripts/run.sh uv sync` (network, sandbox off).
- Codex: build with `codex exec -m gpt-6.1-sol -s workspace-write -C <tree> ... < /dev/null`; review
  with `-s read-only`. Sandbox off, in the background. Codex cannot write `.git`: the chair commits.
- Socket tests (`-m socket`, 5 tests) need `allowLocalBinding` (project `.claude/settings.json`) or
  run outside the sandbox; they FAIL, never skip, when denied.

## Cost rules (owner)
- One orchestrator alive at a time. Builders report once, no polling. Logs to files, short summaries,
  small tool outputs. A fresh session per round; this page is the entry point.
