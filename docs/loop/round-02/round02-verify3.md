PASS: V2b-F1 is fixed. Every received 3xx reply is stored as one failed answer row holding its body on all three refusal paths, the redirect is still refused, the new test bites, and the regression set holds.

# Round 2 verify 3 (blind, extra fix cycle, 2026-10-27, tip 695b97b)

Scope: ledger items R2-3e, R2-8, R2-9 and V2 (extra cycle). Read from each item's own wording and the spec D25 row. Reports, ledger notes and commit messages were opened only after every item was ticked.

## Regression set

- `scripts/run.sh pytest -q`: `270 passed in 36.71s`.
- `scripts/run.sh python -m casefile.gate`: `gate playbook PASS invalid=0 unmarked=0 version=pb-00be6eb62752`, `gate prose PASS dashes=0 files=138`, then `0`.
- `pytest -q -s tests/test_stage1_exit.py tests/test_stage2_exit.py`: `4 passed in 1.48s`; prints `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`.
- `casefile bench ... --candidate tests/fixtures/bench/flawed.json`: exit 1, `bench 9001.001 found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`, detail lines `missed: F04 F15 F24`, two `invented:`, `flags_missed: G3`, `flags_extra: conflict MED0001,MED0004`, `rules: no-dme-ime DEF0003`, then `bench matters=1 imperfect=1`.
- Ideal candidate: the brief's path `tests/fixtures/bench/ideal.json` does not exist (exit 2, CandidateError). The ideal file lives at `tests/fixtures/matters/9001.001/ideal.json`, as the tests use it; with that path: exit 0, `found=29 of 29 ... flags=6 of 6 ... pages_failed=0 of 14`, `bench matters=1 imperfect=0`. Not a code finding.

## Probe (own, scratchpad, not the repo test)

`benchrun.run` on invented matter 9001.001, a loopback server, and a second loopback server as the redirect target that counts hits.

| Path | Status | Answer rows | Failure | Target hit |
|---|---|---|---|---|
| real opener | 302, 307, 301, 303, 308 | one `failed`, body exact | one `bench.model` `redirect refused: N to ...` | 0 |
| real opener | 302, empty body | one `failed`, `''` | one `bench.model` | 0 |
| real opener | 404, 503 | one `failed`, body exact | one `bench.model` `status=N` | 0 |
| real opener | 200 good reply | one `ok` | none | 0 |
| transport returns 3xx | 302, 307 | one `failed`, body exact | one `bench.model` | 0 |
| transport raises HTTPError 3xx | 302, 307 | one `failed`, body exact | one `bench.model` | 0 |

Summary line: `probe_v3 bad=0 runs=13 answers=13 target_hits=0`. The probe goes red under seeds (below), so it can fail.

## Seeds

Each applied (`cmp -s` against a saved copy differed), run, restored (`cmp` ok). Lines 18 to 19, 51 to 53 and 55 to 59 of model.py were left to others for teeth; the three raw-drop seeds there were rerun only to reproduce the R2-9 CHECK.

| Seed | Mutation | test_benchrun.py | Probe |
|---|---|---|---|
| S1 | benchrun.py:71 stores status `ok` not `failed` | `4 failed, 1 passed` (redirect test red) | bad=12 |
| S2 | benchrun.py:70 always `json.dumps(exc.raw)` | `3 failed, 2 passed` (redirect test red) | bad=12 |
| S3 | model.py:50 `300 <= status` to `303 <= status` | `1 failed, 4 passed` (redirect test red) | bad=1 |
| S4 | model.py:23 `NoRedirect()` dropped from the opener | `1 failed, 4 passed` (redirect test red) | bad=4, target hit 4 times |
| S5 | benchrun.py:69 `is not None` to truthiness | `5 passed` (green) | bad=1 (empty 302 lost its row) |
| S6 | test's own assertion `("failed", body)` to `("failed", row[1])` | `5 passed` (green, expected: the body equality is the only body check, and S2 shows it bites) | bad=0 |
| S7 | model.py:60 raw dropped (HTTPError non-3xx) | full suite `1 failed, 269 passed` | bad=2 |
| S8 | model.py:64 raw dropped (status != 200) | full suite `1 failed, 269 passed` | bad=0 (no probe case for a returned non-3xx non-200) |
| C19, C52, C58 | raw dropped at each redirect raise alone | `1 failed, 4 passed` each | not run |

## Findings

- None blocking.
- Non-blocking gap: the redirect test has no empty-body 3xx case, so S5 (truthiness at benchrun.py:69) stays green. The code is right by probe (empty 302 gives one `failed` row with `''`).
- Note: R2-9 names the pre-fix lines model.py:18, :50, :54; at the tip the raises sit at :19, :52 to 53 and :58 to 59.
- Note: the brief's ideal path was wrong (see Regression set).

## Ledger

R2-3e, R2-8, R2-9 ticked `[x]`; V2 (extra cycle) ticked `[x]`. R2-4 and R2-5 left alone. The earlier V2 line under the round 2 section was left as it was.

## Reconciliation

After ticking I read commit 695b97b and the R2-9 note. They agree with my evidence: the fix passes the decoded body as raw at all three redirect refusals, the refusal is unchanged, `270 passed`, gate 0, and each of the three raises seeded alone goes red. Nothing I found contradicts them; my S5 gap is not mentioned there.
