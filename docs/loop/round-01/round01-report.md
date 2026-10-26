# Round 1 report: stage 1 skeleton and harness

**Verdict: DISCARDED (not merged).** Three verify passes failed V1. The owner granted one extra cycle
(Q23) and the focused re-verify then failed too, so the round was discarded per Q5. Owner Q24: re-brief
on the branch. `loop/round-01` keeps its tip; `main` stays at the seed `5a55b54`. 14 of 20 items are
ticked by a verifier, 4 are deferred with reasons and 2 are refused (R1-4, R1-13). All open defects sit in
one design: the path-identity guards (matters folder, toolchain) and the run wrapper's exit branches.

## Measured on the tip (chair re-runs, inside the session sandbox)

| Number | Check that produced it |
|---|---|
| `192 passed` | `scripts/run.sh pytest -q` (socket tests included, Q18 binding) |
| gate prints `0` | `scripts/run.sh python -m casefile.gate` |
| `exit=1 verdicts=8 fails={'ocr'} test_jobs=1` | `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` |
| `5 passed` socket tests in the sandbox | `scripts/run.sh pytest -q -m socket` (R1-15 confirmed) |
| doctor, no model server: `failed=4 of 8`, exit 1, every FAIL with `\| do:` | `scripts/run.sh casefile doctor --config <tmp>` |
| V3-2 still open: `exit=0`, want 95 | `CASEFILE_TOOLCHAIN=<scratch>/nope/../../../../../<checkout> scripts/run.sh true` |

## Critic round

- **8a Codex code review** (gpt-6.1-sol, read-only, high): 11 findings (2 high, 8 med, 1 low), all
  reproduced by the chair, all fixed in cycle 1 (28a5f96).
- **8b output critic** (fresh Opus 5.5): `OUTPUT CRITIC 5/10 · high 3 · med 8 · low 3`. The rules
  missed forms of DME/IME and blocked ordinary deposition prose ("When were you hired?", "attorney
  fees"). The doctor passed OCR on `--version` alone. Fixed in cycle 2 (8994fff), except M4 (carried as
  R1-20) and L3.
- **8c blind verifier**: FAIL on B1 (case-swapped matters path) and B2 (untested exit 98 branch); fixed
  in cycle 3 (f2023ae). Re-verifier: FAIL on B1b (symlink to a case-swapped subfolder) and B3; fixed in
  cycle 4 under Q23 (8aeba23). Focused re-verify: FAIL on V3-1 to V3-4 (below).

## Carried to the re-brief (Q24)

- **V3-2 (fail-open, D23):** a toolchain path with `..` segments escapes the run.sh guard; the guard
  walks the spelling, and `mkdir -p` can then create a venv inside the checkout.
- **V3-1:** a symlink loop as matters gives a `RuntimeError` traceback (exit 1, not 2).
- **V3-3:** the run.sh exit 96 branch has no test, and neither does the process-group kill (a
  background grandchild survives the cap).
- **V3-4:** the run.sh "cannot verify" exit 95 branch has no test.
- **Recommended design** (the chair's, for the brief): a single Python identity check used by both
  config.py and run.sh (run.sh calls it before uv), with table-driven alias tests (case, root and
  subfolder symlinks, chains, loops, `..`, dangling, relative, unreadable), and one test per D12 exit
  branch.
- R1-12: spec §11 as-built, written at the merge. R1-19 (OCR smoke, stage 3). R1-20 (unbracketed cites).

## Design calls pending owner veto

- D12 amended: exit 95 toolchain inside the checkout, 126 not executable, 127 not found, 98 capture only,
  and the cap kills the child process group.
- D18 amended: fake model mode `incomplete` (done=false).
- Interim rulings on owner questions 8 to 14 (`docs/loop/questions-for-owner.md`).
- Tuning question T-5: payment rule window of one clause, 60 characters.

## Discoveries

- The chair's own cycle 1 instruction added a config-folder limit that the spec does not have (M8). The
  Librarian now asks that every fix instruction be checked against its spec row.
- One guard took four passes. Fixing the alias a finding names invites the next alias, so test the
  whole alias table at once (Librarian #R01-V-B1b).

## Process notes

- Q22 tiers: Codex reviewed and wrote all fixes; Opus ran the critic and three verifiers.
- Codex's sandbox denies socket binding (5 failures in its runs). The chair re-ran every suite inside
  the session sandbox before each commit.
- Two agents left a stand-in model server running because `kill` is refused in the sandbox. The chair
  stopped one and the verifier stopped one with a single unsandboxed kill.
- The app-loop catalog (`.claude/skills/`) is not writable from this session, so app classes go to the
  Librarian only.
