# Round 1 blind verification (V1)

FAIL: 14 ticked, 4 deferred, 2 refused (R1-4, R1-13); two blocking findings, both small, both fit the one cycle Q5 leaves.

Verifier: fresh Opus 5.5, 2026-10-26, branch `loop/round-01`, tip `9c25e8f`. I built nothing this round
and had no build context. Blind order kept: nothing under `docs/loop/round-01/` or `.workflow/scratch/`
was opened until every item was ticked or refused in the ledger. All probe text is invented. Every
command ran through `scripts/run.sh`. No server outlived its probe (each stand-in ran in-process and
was shut down in a `finally`).

## Blocking findings

B1. `src/casefile/config.py:128`, R1-4 (D13, Q17, pillar 3). The guard
`matters.resolve().is_relative_to(checkout)` compares path strings case-sensitively, but this Mac's
volume is case-insensitive. Probe: config with
`[paths].matters = "/Users/davidskoranski/LEGAL-HARNESS/invented-matters"`, then
`scripts/run.sh casefile config show --config <it>`. Observed: exit `0`,
`paths.matters = "/Users/davidskoranski/LEGAL-HARNESS/invented-matters" (source=file)`
(`ls -d /Users/davidskoranski/LEGAL-HARNESS` exists: it is the checkout). Expected: exit 2,
`ConfigError: [paths].matters must be outside the checkout /Users/davidskoranski/legal-harness`.
The doctor shares `config.load`, so it would PASS `config` too. Fix direction: compare by
filesystem identity, not by string. Walk `matters` and each existing ancestor and refuse if any
`os.path.samefile(ancestor, checkout)`. That also covers Unicode-normalisation variants. Test: a
case-swapped checkout path must raise. It has to FAIL rather than skip on a case-sensitive volume, so
pair it with a symlink-alias case that exercises the same identity check.

B2. `scripts/run_capture.py:33-35`, R1-13 part (b) (D12 exit 98). The brief's discovery asked that
the two 98 guards be isolated. The mktemp guard now is (seed S17 red), but the capture-stage guard
is not. SEED `return 98` -> `return 0` at run_capture.py:35 gives `162 passed`. On the tip,
`scripts/run.sh invented-no-such-cmd` prints
`run.sh: capture stage failed: [Errno 2] No such file or directory: 'invented-no-such-cmd'; exit 98`
and exits 98, but no test covers it. Under the seed the same call would exit 0, a fail-open
wrapper. Expected: a case in `tests/test_run_sh.py` that runs `scripts/run.sh invented-no-such-cmd`
and asserts `(98, b"capture stage failed" in stderr)`. Design note to log: the brief (R1-2 pre-flight,
catalog #41) said a missing command relays `127`. The tip returns 98. Spec §9 D12 should say which.

## Measured numbers (probe for each)

| Number | Probe |
|---|---|
| `162 passed in 9.82s`, exit 0 | `scripts/run.sh pytest -q` |
| gate rows all PASS, privacy `offenders=0 scanned=213`, prose `dashes=0 files=57`, playbook `pb-8c41a5ae7727`, prints `0`, exit 0 | `scripts/run.sh python -m casefile.gate` |
| overflow `52428800` bytes, exit `97` (with pipefail), `0` without | `scripts/run.sh bash -c 'head -c 52428801 /dev/zero \| tr "\0" a' \| wc -c` |
| stderr `run.sh: output cap 52428800 bytes hit (child status -9); exit 97` | same |
| stderr overflow `52428865` bytes on stderr (cap plus the 65-byte message) | `... >&2` variant |
| child `3`, exact cap `0`, no args `96`, `TMPDIR=/nonexistent/dir` `98`, missing command `98` | `scripts/run.sh ...` |
| `Python 3.12.13`, `casefile 0.1.0`, venv `~/.casefile-dev/legal-harness/venv` | `scripts/run.sh python --version`, `casefile version`, `which casefile` |
| config refusals exit 2 (unknown key, str num_ctx, num_ctx 32768, host 0.0.0.0, host with path, missing file, matters in checkout); defaults listed with `(source=default)` | `scripts/run.sh casefile config show --config <invented>` |
| `version=pb-8c41a5ae7727 entries=7`; after one appended byte `pb-959a6c383d9a`; malformed fixtures exit 2 | `scripts/run.sh casefile playbook show --config <invented>` |
| `rules_red=9 of 9`, `good_clean=4 of 4`; probe table in the ledger | `scripts/run.sh python` with `rules.load(...).check(...)` |
| stand-in over HTTP: replay `READY/stop/65536`, truncated `RE/length`, malformed JSON fragment, forbidden IME sentence, short_context ps `8192`, empty `''`, unrecorded `404`, OpenAI route `404` | in-process `fakemodel.server.serve(port=0)`, urllib with no proxy |
| `5 passed, 157 deselected` inside the sandbox | `scripts/run.sh pytest -q -m socket` |
| `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`; companion the same; `2 passed` | `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` |

## Driven run (stage 1 exit, R1-9 and R1-11)

A stand-in server ran on 127.0.0.1 with an ephemeral port, and an invented config pointed at it.
`scripts/run.sh casefile doctor --config <it>` ran twice, then I read the SQLite run log directly.
Both runs printed the same eight lines:

```text
doctor config PASS source=/private/tmp/claude-501/vdrive/config.toml
doctor folders PASS writable=3 of 3
doctor playbook PASS version=pb-8c41a5ae7727
doctor runlog_schema PASS schema=1 triggers=15 (counted)
doctor ollama_loopback PASS addr=127.0.0.1:53510
doctor context PASS context_length=65536
doctor runlog_job PASS test_jobs=+1
doctor ocr FAIL OCR not verified: tools unavailable (tesseract exit=not-found, ocrmypdf exit=not-found); smoke test arrives in stage 3 | do: install tesseract and ocrmypdf; expected until stage 3
doctor failed=1 of 8
```

Exit was 1 both times. Against R1-9:
- Loopback: proved by lsof on the live listener.
- Full context: `/api/ps` reports 65536, equal to config, plus an exact `READY` answer with `done_reason=stop` and positive counts.
- OCR: FAIL with a reason, as Q11 requires.
- Folders: three writable.
- No line was skipped, and the exit code carries the verdict.

Against R1-11, the run log held two `runs` rows `(doctor, doctor.warmup, a48ba54e9a3e, pb-8c41a5ae7727, qwen3.8:27b, pages_in 0)` and two `answers` rows `(ok, stop, 21, 2, raw JSON)`, with no failures. `DELETE FROM runs` returned `runlog is append-only`.

## Seeds

Each seed changed one line on a line not on the brief's already-mutated list (except the R1-16 re-seed). Each ran the full `scripts/run.sh pytest -q`, was restored from a copy, and was checked with `cmp` (all `cmp_exit=0`). The suite was GREEN `162 passed` after.

| # | Line, mutation | Result |
|---|---|---|
| S1 | cli.py:32 `return doctor.run(...)` -> call without return | RED 3 failed (cli override, both stage exits) |
| S2 | cli.py:38 playbook error `return 2` -> `return 0` | GREEN 162 passed: no teeth (N4) |
| S3 | model.py:18 `ProxyHandler({})` -> `ProxyHandler()` | RED 2 failed (`test_no_proxy`, `test_http[proxy_environment]`) |
| S4 | model.py:66-67 caller options applied last | RED 1 failed (`test_fields`) |
| S5 | runlog.py:111 `foreign_keys=ON` -> `OFF` | RED 2 failed |
| S6 | gate.py:37 drop `and false_hits == 0` | GREEN 162 passed: no teeth (N1) |
| S7 | fakemodel core.py:88 stream check off | RED 2 failed |
| S8 | privacy.py:11 drop `--others` | RED 4 failed |
| S9 | doctor.py:152 `difference == 1` -> `>= 0` | GREEN 162 passed: no teeth (N2) |
| S9b | S9 plus doctor.py:142 status always `failed` | RED, but the doctor printed `runlog_job PASS test_jobs=+0`; only the exit test's own count caught it |
| S10 | config.py:116 drop host path clause | GREEN 162 passed: no teeth (N3); the tip refuses `/evil` path, exit 2 |
| S11 | doctor.py:83 lsof error ignored | RED 1 failed |
| S12 | run_capture.py:32 `128 - status` -> `1` | RED 1 failed (sigkill `(1, 0) == (137, 0)`) |
| S13 | doctor.py:47 missing matters check off | RED 1 failed (m7) |
| S14 | playbook.py:86 rules.toml guard off | RED 1 failed |
| S15 | fakemodel core.py:46 short_context ctx | RED 4 failed |
| S16 | doctor.py:142 answer status always `failed` | RED 4 failed |
| S17 | run.sh:8 drop mktemp `\|\| {...}` | RED (capture-failure `(1, 0)`); it also wrote a stray `out` into the cwd, removed (N6) |
| S18 | rules.py:76 `fullmatch` -> `match` | RED 2 failed |
| S19 | rules.py:61 unit skip off | RED 2 failed |
| S20 | playbook.py:72 SAMPLE check off | RED 3 failed |
| S21 | playbook.py:109 duplicate id off | RED 2 failed |
| S22 | rules.toml:43 drop the `bill` pattern | RED 4 failed (gate tests and rules) |
| S23 | run_capture.py:35 `return 98` -> `return 0` | GREEN 162 passed: no teeth (B2) |
| S24 | config.py:69 missing-file branch removed | RED 3 failed |
| S25 | runlog.py:92 drop card filter | RED 1 failed (`assert 2 == 1`) |
| R16 | run.sh:5 `UV_CACHE_DIR="$ROOT/.uv/cache"` (re-run of the builder seed, as R1-16 asks) | RED `toolchain_inside_repo=1` |
| G | transient `state/probe-seed.HEIC`, `Bench/invented-notes.txt`, `docs/probe-seed.md` with U+2013 | gate prints `2`, exit 2 (`offenders=2`, `dashes=1`); removed, `state/` and `Bench/` deleted |

Count: 27 code seeds (S1 to S25, S9b, R16) and 1 file seed. 22 code seeds went RED. Five stayed GREEN: S23 is B2 (blocking); S6, S9, S10 and S2 are N1 to N4 (non-blocking).

## Non-blocking findings (recommend for the same fix cycle)

- N1. gate.py:37: the `false_hits` leg of `rules_selftest_row` has no test. The gate still goes red overall through `test_good_examples_clean` in the pytest row. This overlaps critic L3 (carried).
- N2. doctor.py:152: the `runlog_job` comparator is untested and redundant with the context dependency. With S9b the doctor prints a false `PASS test_jobs=+0`. Add a test where context passes and the stored answer is not `ok`.
- N3. config.py:116: no test for the host path clause. Add `http://127.0.0.1:11434/x` to `test_bad_values`.
- N4. cli.py:38: no test that `casefile playbook show` exits 2 on a malformed playbook.
- N5. rules.toml:8: hyphenated spelled-out labels pass: "independent-medical-examination" and "defense medical-examination" give `[]`. Q16's four listed forms are all caught; "any form" suggests `[\s-]+`.
- N6. run_capture.py:16: an empty directory argument makes the capture file `./out` in the cwd. Only the run.sh guard prevents it. Refuse an empty or non-directory argument.
- N7. `CASEFILE_TOOLCHAIN` may point inside the checkout without refusal (D23 permits the override). The privacy row would still catch images there.

## Unlogged design calls

- Fake mode `incomplete` exists (core.py:11) but is not in spec §9 D18's mode list.
- A missing command now returns 98 (`capture stage failed`). The brief said 127 is relayed. D12 does not say which (B2).
- `scripts/run_capture.py` (needs `python3` on PATH before `uv sync`) is recorded in the ledger critic section but not in D12.

## Process notes

- R1-14, R1-17 and R1-18 were ticked on reading the record (agent-log rows 4 to 8, `git show --stat 3e12678`, commit authorship). Their Librarian entries belong to R1-12 (Librarian is still empty).
- R1-15: in a fresh session the sandbox allowed local binding (`5 passed`), so Q18 holds from session start.
- The seed harness lived in the session scratchpad. Each backup was compared with `cmp` after restore. `git status -s` at the end shows only the ledger and this report.

## Reconciliation (after all items were ticked or refused)

Numbers that match: `162 passed` and gate `0` (ledger, cycle 2); `exit=1 verdicts=8 fails={'ocr'} test_jobs=1` (A3, ledger); `triggers=15` (fix1 CX-3); `pb-8c41a5ae7727` (fix2 report gate); `toolchain_inside_repo=1` (F1); `rules_red=9 of 9`, `refused=3 of 3`, `version_changed=1`, `blocked_writes=8 of 8`, `test_jobs=1` (lane B, A2); socket `5 passed` (ledger R1-15 note); `52428800`/`97`/`3`/`98` (A1). Privacy `scanned=213` against fix2's `212` is one file added after that run, not a discrepancy.

Claims I could not reproduce or that are now stale:
- The R1-10 build note (`scanned=188`, `pb-e46d368e8caf`) predates cycles 1 and 2.
- A1's "second SEED survived" is resolved for the mktemp guard (S17 red) but not for the capture-stage guard (B2).
- The critic's "Good enough" quotes an OCR reason starting `versions only:`. The tip says `OCR not verified:` (cycle 2 H1).
- CX-1 was fixed for an exact-case path only. B1 is its residue.

Seeds they used that I would have chosen too:
- the `approvals_no_delete` trigger body and the answer-status filter (A2);
- `fullmatch` -> `search` and dropping `IGNORECASE` (B);
- removing the process-group kill (CX-4);
- dropping the done_reason guard (CX-10, chair);
- dropping the `--others` style exclusion (A3);
- the toolchain path seed (F1).

I avoided all of those lines except R1-16's re-seed.
