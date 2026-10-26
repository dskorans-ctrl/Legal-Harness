# casefile: loop ledger

Chair: the primary Claude Code session for each round. Loop: create (Fable brief, Codex review, Fable
revision) → build (Opus orchestrates, Sonnet codes) → critic (Codex code review, output critic, blind
verifier) → close, one round per branch and per session. Owner decisions are binding; see `## Clarified`.
Seeded 2026-10-25; round 1 opened 2026-10-25 on `loop/round-01`.

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
- Q10: tiers (owner, 2026-10-25)? -> gdd-loop's: Fable writes and revises the brief; Codex gpt-6.1-sol
  reviews plan and code; Opus 5.5 orchestrates, critiques outputs, verifies; Sonnet 5.5 writes all code.
  Builders may delegate to Sonnet children only.
- Q11: machine (owner, 2026-10-25)? -> this Mac is a dev Mac, not the Studio. Install Python 3.12
  project-local with uv only; no Ollama, no Tesseract, no brew. The stand-in model server replaces the
  model. `casefile doctor` reports OCR as FAIL (never skipped) until stage 3.
- Q12: first playbook (owner, 2026-10-25)? -> `rules.toml` holds the four firm rules in spec §4; every
  other playbook entry is an invented test fixture marked SAMPLE. Practice content is the owner's.
- Q13: additional instructions (owner, 2026-10-25)? -> none; proceed.
- Q14: builder tier (owner, 2026-10-25, supersedes Q10's coding tier for cost)? -> Codex gpt-6.1-sol
  writes all code, via the local `codex exec` CLI with `-s workspace-write` in the repo (or a worktree),
  never with network or outside-repo write. Opus still orchestrates and re-runs every CHECK and seed;
  Codex still does the plan and code reviews (independence reduced; the blind Opus verifier carries it).
- Q15: critic timing (owner, 2026-10-25)? -> no code review until the night of 2026-10-26. This session
  runs brief, plan review, revision and build, then stops before the critic round with round 1 unmerged
  on `loop/round-01`. The next session runs the critic round (8a to 8c) and close; the owner may
  change tiers then.
- Q16: firm rule 5 (owner, 2026-10-25, owner question 4)? -> checked on outputs only, never on the
  records being read. Outputs never name the exam as a DME or IME in any form: block "DME", "IME",
  "independent medical examination" and "defense medical examination" (whole words, any case); always
  "the report".
- Q17: matters folder (owner, question 3)? -> outside the repo checkout (e.g. ~/Cases), set in config.toml.
- Q18: local binding (owner, question 6)? -> yes: `sandbox.network.allowLocalBinding: true` in the
  project's `.claude/settings.json`.
- Q19: Ollama on the Studio (owner, question 7)? -> not decided; build for the login-user app case,
  question stays open.
- Q20: model tag (owner, question 2)? -> `qwen3.8:27b`, set in config.toml.
- Q21: Bates format (owner, question 5)? -> letters plus digits: `[A-Z]{1,8}[ -]?\d{4,}`, configurable.

## Round 1: stage 1 skeleton and harness (opened 2026-10-25)

- [ ] R1-1. Build brief reconciled to the code at main `5a55b54`, a CHECK and seed per item, Codex
  reviewed, revised with dispositions. `.workflow/scratch/round01-build-brief.md`.
- [ ] R1-2. `scripts/run.sh <cmd>`: caps combined stdout/stderr at 50 MB, exits 97 when the cap is hit,
  otherwise carries the child's exit code.
- [ ] R1-3. Skeleton: Python 3.12 (uv, project-local), package `casefile`, console entry `casefile`,
  `scripts/run.sh pytest -q` green.
- [ ] R1-4. Config: one config file with defaults and validation; an unknown key or bad value fails
  closed with a message, never a silent default.
- [ ] R1-5. `playbook/rules.toml` with the four spec §4 firm rules, loaded and validated; each rule has a
  test with a forbidden output that goes red.
- [ ] R1-6. Playbook loader: entries carry rule, why, good example, bad example, date added, where
  learned (spec §6); malformed entry fails closed; a playbook version is computed. Entries other than
  rules.toml are invented and marked SAMPLE (Q12).
- [ ] R1-7. Run log (SQLite): every run, card version, pages in, raw answer, failures, approvals
  (spec §5); records a test job.
- [ ] R1-8. Stand-in model server `tests/fakemodel/`: Ollama native `/api/chat` shape; replays recorded
  answers; returns truncated, malformed or forbidden answers on demand.
- [ ] R1-9. `casefile doctor`: Ollama on 127.0.0.1 only, full context loaded, OCR works, folders
  writable; each check PASS or FAIL with a reason, none skipped; exit code carries the verdict.
- [ ] R1-10. Gate `scripts/run.sh python -m casefile.gate` prints 0 when green; includes the privacy
  check (PDF, Word or image outside `tests/fixtures/`, or anything under `Cases/` or `Bench/`, fails).
- [ ] R1-11. Stage 1 exit test (spec §7): `casefile doctor` runs and the run log records a test job,
  driven end to end through `scripts/run.sh`.
- [ ] R1-12. Spec §9 rows for this round's rulings, §11 as-built updated; Librarian, agent log,
  round report under `docs/loop/round-01/`.
- [ ] V1. Fresh blind verification: every non-deferred R1 item `[x]` with the verifier's own evidence.
