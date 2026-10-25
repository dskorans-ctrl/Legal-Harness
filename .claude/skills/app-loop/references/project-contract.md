# Project contract: the block every round reads

Put this at the top of `.workflow/LEDGER.md` on first use. Fill it from the repo and the round-1
clarify, never from memory of another project. This one is casefile's, as seeded on 2026-10-25;
the round-1 session confirms the harness commands and records baselines.

```markdown
## Project
- Spec: docs/spec.md (canon). Pillars §1 · decisions table §9 · open questions §10 · roadmap with an
  exit test per stage §7 · as-built §11.
- App: casefile, a fixed-workflow case system for one attorney, run locally on a Mac Studio. Python
  3.12, FastAPI and plain HTML, Ollama native API, SQLite run log, append-only JSON case file.
- Harness (round 1 builds and measures these):
  - every run goes through `scripts/run.sh <cmd>`, which caps stdout/stderr at 50 MB and exits 97 when
    the cap is hit;
  - tests: `scripts/run.sh pytest -q`;
  - gate: `scripts/run.sh python -m casefile.gate` prints 0 when every regression row is green;
  - benchmark: `scripts/run.sh casefile bench --matters tests/fixtures/matters --runs 1` (invented
    matters only in the loop; the real closed matters run on the Studio, by the owner);
  - full run: `scripts/run.sh casefile demo tests/fixtures/matters/<matter>` (intake to outputs);
  - model in development: a stand-in model server (`tests/fakemodel/`) that replays recorded answers
    and can be told to return truncated, malformed or forbidden answers; optionally a small Qwen via a
    local Ollama for plumbing only;
  - page screenshot: Playwright, `scripts/run.sh python -m casefile.shots <screen>`.
- Checks: a check prints the one number that fails it, exits non-zero on FAIL, and has been proven
  red on a seeded defect before its pass counts.
- Finish line (owner): build stages 1 to 8 of spec §7 done and verified in the loop; then stage 9 on
  the Studio: the benchmark on real closed matters passes at 8-bit and full precision over three days.
  Scope order: spec §7 stage order. The playbook (§6) and Obsidian (possible later) only as the spec says.
- Standing freezes: none.
- Privacy: no real client record, name or fact in any loop session. Fixtures are invented.
- Regression baselines: set in round 2 (gate 0; every gate in spec §4 red on its seed; the invented
  test matter's benchmark score recorded).
- Records: Librarian.md (root) · docs/loop/round-NN/ reports · docs/loop/agent-log.md ·
  docs/loop/questions-for-owner.md · docs/loop/tuning-questions.md · docs/loop/HANDOFF.md ·
  docs/loop/next-round.md · live page URL (in memory).
```

## What the spec must provide, and what to do if it does not

| Needed | Used for | If absent |
|---|---|---|
| Pillars | tie-breaking every ruling made without the owner | append "Appendix A: pillars (proposed)"; mark proposed |
| Decisions table | every change to a prior decision, with who decided and why | append "Appendix B: decisions" |
| Open questions | new questions found mid-round | append "Appendix C: open questions" |
| Roadmap with exit tests | round scope and the observable "done" per stage | append "Appendix D: roadmap"; each stage gets one exit test the owner confirms |
| As-built table | what exists vs. the design, per part | append "Appendix E: as-built"; a round-1 worker fills it |

## Runs are capped

Every check, test, benchmark and app run goes through `scripts/run.sh`, which caps stdout/stderr and
exits with a distinct code when the cap is hit. Builders, critics, verifiers and children all use it;
the raw command is never run with an unbounded capture.
