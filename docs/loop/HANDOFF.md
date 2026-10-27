# casefile: loop handoff (2026-10-27, round 2 closed and merged)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q33), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stage 1 (round 1) and stage 2 (round 2: `casefile bench`, invented matter 9001.001, answer key) are built,
  verified and merged to `main`. Round 2 passed after one extra fix cycle on V2b-F1 (owner Q32).
- Baselines (ledger `## Project`): `270 passed`, gate `0`, flawed bench exit 1 `found=26 of 29 ...`, ideal
  bench exit 0 `found=29 of 29 ...`, stage 2 exit test `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`.
- Owner ratified OR-1 to OR-9, D25 and D26 (2026-10-27).
- Round 2 report with the Gemma against Sonnet cost comparison: `docs/loop/round-02/round02-report.md`.

## Next session: round 3 on `loop/round-03` (spec §7 stage 3)
- Stage 3: intake and OCR with page IDs. Exit test: a scanned PDF becomes page text with correct IDs. The
  scanned PDF is an invented fixture under `tests/fixtures/` (no real records). Doctor's OCR check turns
  PASS here (Q11); R1-19 (OCR smoke test on an invented fixture PDF) lands here.
- Tiers return to the defaults (Q30): Fable brief and revision, Codex plan and code review, Opus
  orchestrator, output critic and verifier, Sonnet 5.5 code. Gemma is not a builder in round 3.
- Carried into the round 3 brief: the empty-body 3xx test case (verifier 3, S5); OR-5 lows (Gemma
  whitespace, unused imports, prompt comments, `.DS_Store` refusing a matter, F4 to F6); a non-200
  HTTPError with no body stream; duplicate matter numbers not refused; verifier test gaps N2 to N5;
  R1-20 still open; R2-CX-2 waits for stage 4.

## Held owner questions
- `docs/loop/questions-for-owner.md`: 21 to 29 (round 2: key contents, Studio bench folder, Bates
  placement, key completeness, flag wording, unreachable model exit, model name on the line, bills, "the
  report" wording), Q7 and items 8 to 20 from round 1. Ask them at the round 3 check-in.

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile` on this Mac.
- Codex reviews only (`codex exec -m gpt-6.1-sol -s read-only ... < /dev/null`), sandbox off, background.
- Run the gate before every chair commit (Mistakes Log). Verify a seed applied (`cmp -s`) before counting it.
- Leftovers needing the owner's say-so to delete: worktree `.claude/worktrees/agent-a582821e2b2e41b16` and
  branch `control/r2-sonnet` (the Sonnet cost control, never merged); old `casefile-run.*` folders in the
  shared TMPDIR.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short
summaries. A fresh session per round; this page is the entry point.
