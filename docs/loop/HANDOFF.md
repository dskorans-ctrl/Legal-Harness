# casefile: loop handoff (2026-10-26, end of round 1 session 2)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q24, `## Round 1`, the
critic-round lines), then `Librarian.md` (builder pre-flight first). Spec (canon): `docs/spec.md`.

## Where things stand
- Round 1 (spec §7 stage 1 plus the harness) was DISCARDED, not merged (Q23, Q5). Owner Q24: re-brief
  on the branch. `loop/round-01` keeps its tip; `main` is still the seed `5a55b54`. No `loop/round-02`.
- On the tip: `192 passed`, gate `0`, stage 1 exit test `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`.
  14 items ticked by a verifier, 4 deferred, R1-4 and R1-13 refused, V1 open.
- Round report: `docs/loop/round-01/round01-report.md` (verdict, numbers, carried items, design).

## Next session: round 1 re-brief (Q24), on `loop/round-01`
1. Ask the owner the tiers for the session (Q22 is the last answer).
2. Fable brief, limited scope: redesign the path-identity guards and the wrapper exit branches as ONE
   Python identity check shared by `src/casefile/config.py` and `scripts/run.sh`, with table-driven
   alias tests (case, root and subfolder symlinks, chains, loops, `..`, dangling, relative, unreadable)
   and one test per D12 exit branch. Items: V3-1 to V3-4 (`round01-verify3.md`), verify2 N2. Codex plan
   review, Fable revision, build (Codex per Q22 unless the owner changes it).
3. The full critic round (8a, 8b, 8c), with the cycle cap starting fresh for the re-brief.
4. Close: R1-12 (spec §11 as-built), tick R1-4 and R1-13, then V1. Fast-forward `main`, open
   `loop/round-02`, and prompt the owner to `git push origin main`.

## Held owner questions
- `docs/loop/questions-for-owner.md`: Q7 (Ollama login user or daemon) and items 8 to 14 from the output
  critic (DME as durable medical equipment, rule scope, bills, exam volume, cite forms, QME/AME, folder
  creation), all with interim rulings in force.
- Pending veto: spec §9 D12 to D21 and D23, including the 2026-10-26 amendments to D12 and D18.

## Machine rules
- Every run through `scripts/run.sh`, which now execs `scripts/run_capture.py` and needs a `python3` on
  PATH. The toolchain lives at `~/.casefile-dev/legal-harness` (D23).
- Codex: build with `codex exec -m gpt-6.1-sol -s workspace-write -C <tree> ... < /dev/null`; review with
  `-s read-only`. Run with the sandbox off, in the background. Codex cannot write `.git`, so the chair
  commits. Its sandbox denies socket binding, so the chair re-runs the full suite and gate before every
  commit.
- Socket tests run inside this session's sandbox now (Q18 takes effect at session start).
- Agents must not leave a stand-in server running: use pytest-driven runs.

## Cost rules (owner)
- One orchestrator alive at a time. Builders report once, no polling. Logs go to files, with short
  summaries and small tool outputs. A fresh session per round; this page is the entry point.
