# casefile: loop ledger

Chair: the primary Claude Code session for each round. Loop: create (Fable brief, Codex review, Fable
revision) → build (Opus orchestrates, Sonnet codes) → critic (Codex code review, output critic, blind
verifier) → close, one round per branch and per session. Owner decisions are binding; see `## Clarified`.
Seeded 2026-10-25; round 1 not yet opened.

## Project
- Spec: docs/spec.md (canon). Pillars §1 · decisions table §9 · open questions §10 · roadmap with an
  exit test per stage §7 · as-built §11.
- App: casefile, a fixed-workflow case system for one attorney, run locally on a Mac Studio. Python
  3.12, FastAPI and plain HTML, Ollama native API, SQLite run log, append-only JSON case file.
- Harness (round 1 builds and measures these): every run through `scripts/run.sh` (50 MB cap, exit 97);
  tests `scripts/run.sh pytest -q`; gate `scripts/run.sh python -m casefile.gate` prints 0;
  benchmark `scripts/run.sh casefile bench --matters tests/fixtures/matters`; full run
  `scripts/run.sh casefile demo tests/fixtures/matters/<matter>`; a stand-in model server in
  `tests/fakemodel/` (recorded answers, plus truncated, malformed and forbidden ones on demand);
  page screenshots with Playwright.
- Checks: a check prints the one number that fails it, exits non-zero on FAIL, and has been proven
  red on a seeded defect before its pass counts.
- Finish line (owner): spec §7 stages 1 to 8 done and verified in the loop; then stage 9 on the Studio.
- Standing freezes: none.
- Privacy: no real client record, name or fact in any loop session; fixtures are invented.
- Regression baselines: set in round 2.
- Records: Librarian.md · docs/loop/round-NN/ · docs/loop/agent-log.md · docs/loop/questions-for-owner.md ·
  docs/loop/tuning-questions.md · docs/loop/HANDOFF.md · docs/loop/next-round.md.

## Standing rules digest
- Spec is canon; every design change goes in spec §9.
- One round per session; Remote Control on; handoff and next-round prompt written at close.
- No client data in any session or commit.
- Every check proven red on a seed before its pass counts; never lower a threshold or exempt by name.
- `main` pushed only on the owner's word (`git push origin main`).
- Prose has no em or en dashes.

## Clarified
- Q1: scope? -> the case system in spec §2 and §7, built in stage order.
- Q2: done means? -> spec §7 stages 1 to 8 pass their exit tests and the verifier's V. in the loop;
  stage 9 (real benchmark on the Studio) is run by the owner.
- Q3: freezes? -> none.
- Q4: where does work land? -> branch per round `loop/round-NN`, merged to main only after V.
- Q5: stall rule? -> three verify-fix cycles per round, then discard and re-brief; two stalled rounds
  in a row stop the loop and report to the owner.
- Q6: check rule? -> every new check, test or gate goes red on a seeded defect before its pass counts.
- Q7: rulings while the owner is away? -> the chair, by the spec's pillars, logged as pending veto.
- Q8: sessions (owner, 2026-10-25)? -> a fresh session for each round, automatically on Remote
  Control, with a critic round before every close.
- Q9: client data (owner, 2026-10-25)? -> never in any build session; invented test matters only.
- Q10: tiers? -> OPEN: ask at round 1 (gdd-loop's tiers by default).
