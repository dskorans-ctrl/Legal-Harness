W5 is built and verified, including both jobs, CLI dispatch, stage 7 exit coverage, and the chair-authorized non-tty halt fix. No commits.

Mutation commands used `scripts/run.sh pytest -q -s --tb=short`. S = `tests/test_stage7_exit.py::test_stage7_exit`; H = `tests/test_anon_job.py::test_halt_four`.

| Claim | Verified by | Control and RED text |
|---|---|---|
| Check before publication | S | (a) Publish early: `AssertionError: package_written=1` |
| Require an anchor | S | (b) Blank typed anchor and remove votes: `packages=0 of 1; brief-out: cannot run: ANCHOR NEEDED: add date_of_accident to matter.toml [header]` |
| Restore quotes against pages | S | (c) Use prose restore: `checks=2 of 10 failed=8` |
| Failed drafts have no output event | S | (d) Append event: status gains `brief-in-draft-bad-quote:stale` |
| Independent identifier count | S | (e) Write surname into temporary package.md: `AssertionError: identifiers_in_package=1` |
| Require second pass | S | (f) Omit recording: `packages=0 of 1; brief-out: blocked at step 4 (model, offset 0); nothing was written` |
| Non-tty names stay private | H | Print hit name: `AssertionError: non-tty key_leak=1` |
| Blocked terminal stays private | S | Print surname: `AssertionError: key_leak=1` |
| Reject unsafe drafts | Draft-input cases | Disable guard: `assert (0 == 2)` |
| Unknown cites produce partials | Unknown-cite case | Remove citation exception: `AssertionError: assert 2 == 1` |
| Forward CLI options | CLI dispatch case | Drop flag: `AssertionError: --pages all was not forwarded` |
| Preserve configuration refusal | CLI config case | Return 0: `AssertionError: assert 0 == 2` |
| Preserve halt exit 2 | Prerequisite case | Return 0: `AssertionError: prerequisite exit=0` |
| Print review words | S | Omit words: `AssertionError: review words missing` |

Every listed seed followed GREEN → RED → byte-identical restoration verified by `cmp` → GREEN.

Repo files touched: [brief_out.py](/Users/davidskoranski/legal-harness/src/casefile/brief_out.py), [brief_in.py](/Users/davidskoranski/legal-harness/src/casefile/brief_in.py), [cli.py](/Users/davidskoranski/legal-harness/src/casefile/cli.py), [anon_job.py](/Users/davidskoranski/legal-harness/src/casefile/anon_job.py), [test_stage7_exit.py](/Users/davidskoranski/legal-harness/tests/test_stage7_exit.py), [test_cli.py](/Users/davidskoranski/legal-harness/tests/test_cli.py), [test_anon_job.py](/Users/davidskoranski/legal-harness/tests/test_anon_job.py).

Librarian entries checked against this work: R01-CX-11, R01-P-1, R01-V-B2; R02-CX-7; R03-PC-3, R03-CX-2, R03-CX-5, R03-OC-L1, R03-V-L1; R04-PC-4, R04-PC-6, R04-PC-7, R04-OC-1, R04-V-2, R04-CH-1; R05-PC-8, R05-PC-17, R05-CX-4; R06-PC-6, R06-PC-12, R06-CX-1, R06-CX-2, R06-CX-16.

Findings: seed (d) measures `:stale`, rather than the brief’s predicted `:current`. Initial integration reds corrected separate Markdown/JSON scanning, wrapper stream expectations, and the full-name quote oracle. Observed starting HEAD was `974b746`, rather than supplied `59df09e`.

Measured: `review=30`, `placeholders_restored=11`, `unused_imports=0`; `suite_time runs=3 max=86.03 verdict=PASS`.

Requested full pytest run and gate last lines, verbatim:
```text
846 passed in 89.00s (0:01:28)
0
```