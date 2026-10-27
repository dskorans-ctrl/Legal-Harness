OUTPUT CRITIC 6/10 · high 2 · med 5 · low 6

# Round 2 output critic

Critic: fresh session, no build context from this round. No code edited. Only invented fixtures were read.
Scratch files (probe candidates, scratch config and run log) live in
`/private/tmp/claude-501/-Users-davidskoranski-legal-harness/4ae9b508-6287-4877-ad1b-a9c6958d8c49/scratchpad/`.

## Runs (all through `scripts/run.sh`, sandbox on)

| Run | Output | Exit |
|---|---|---|
| bench, candidate `ideal.json` | `bench 9001.001 found=26 of 26 missed=0 invented=0 extra=2 flags=5 of 5 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14` / `bench matters=1 imperfect=0` | 0 |
| bench, candidate `flawed.json` | `bench 9001.001 found=23 of 26 missed=3 invented=2 extra=2 flags=4 of 5 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` / `bench matters=1 imperfect=1` | 1 |
| `pytest -q -s tests/test_stage2_exit.py` | `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`, the perfect line, `stage2-control exit=0 runs=+1 answers_ok=+1`, 2 passed | 0 |
| stand-in by hand, `--mode truncated`, port 18555, scratch config | `bench 9001.001 failure bench.truncation: done_reason=length`, then `found=0 of 26 ... pages_failed=14 of 14` | 1 |
| same config, server stopped | `bench 9001.001 failure bench.model: <urlopen error [Errno 61] Connection refused>`, then `found=0 of 26 ...` | 1 |
| stand-in, `--mode malformed` | `bench 9001.001 failure bench.answer: not JSON: Expecting property name enclosed in double quotes: line 1 column 23 (char 22)`, then `found=0 of 26 ...` | 1 |

Python listeners: 0 before, 0 after each server (`lsof -nP -iTCP -sTCP:LISTEN | grep -c Python`).
Run log (scratch `state/runlog.sqlite`): one `runs` row per model run (model `qwen3.8:27b`, card
`bench.extract`), an `answers` row with status `failed` and the raw reply, and a `failures` row
(`bench.truncation` / `done_reason=length`; `bench.model` / the urlopen text; `bench.answer` / the JSON
error). Candidate runs write nothing to the log (the repo's `state/runlog.sqlite` has 0 runs).

## Findings, most severe first

### H1 (high) A model that finds real conflicts on the pages fails the benchmark
- Output: probe candidate = `ideal.json` plus one flag `{"kind":"conflict","cites":["MED0007","DEF0002"]}`
  (Dr. Okonkwo-Lind's left L5 radiculopathy and positive left SLR, MED0007:23 and 25, against "No objective
  findings of radiculopathy", DEF0002:25) prints `flags=5 of 5 ... flags_extra=1`, `imperfect=1`, exit 1.
  A G1 flag that also cites DEF0001 (whose line 21 also says 60 pounds) prints `flags=4 of 5 flags_missed=1
  flags_extra=1`, exit 1.
- What is wrong: the key's five flags are not the full set of conflicts and gaps on the pages, and D25 makes
  `flags_extra` fail, so the more careful model loses.
- Unkeyed but real on the pages: radiculopathy (MED0007:23,25 vs DEF0002:24-25); the report calls L4-L5
  "degenerative" (DEF0002:32) where the MRI reads a 4 mm protrusion and puts the degeneration at L5-S1
  (MED0006:25-26, 31-32); treatment (MED0008:13 ESI vs DEF0003:23 "No further treatment is medically
  necessary"); gaps for PT notes for visits 2 to 5 and 7 to 12 (MED0005:7), the PT letter to Dr.
  Castellanos-Reyes (MED0005:34), the family medicine four week follow-up (MED0003:27), and any record of
  the ESI or the 06/20/2025 re-evaluation (MED0008:15,19).
- Breaks: key.json `flags` vs the pages; spec D25 "flags_extra ... fails".
- Reproduce: build the probe in `$TMPDIR` from ideal.json and run
  `scripts/run.sh casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate <probe>`.

### H2 (high) The key omits the treating doctor's current restrictions and two other case-deciding facts, so a model that misses them scores perfect
- Output: the ideal line `found=26 of 26 ... imperfect=0` although `ideal.json` has no MED0008 restriction
  fact; adding it only moves `extra=2` to `extra=3` (probe `cand_restriction.json`, exit 0).
- What is wrong: "Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on
  06/20/2025." (MED0008:15) is the matter bible's planted line (brief W4 table, row medical/008) but is
  neither in the 26 nor in the brief's "Not in the key" list (W5, G25), so it fell out silently; it is the
  basis of any wage loss claim and the direct opposite of F26. Also unkeyed: "No further treatment is
  medically necessary." (DEF0003:23, the ESI authorization dispute) and "Lumbar strain, likely work related."
  (MED0003:22, the first treating causation statement).
- Breaks: key.json facts vs MED0008:15, DEF0003:23, MED0003:22; brief W4 bible row medical/008.
- Reproduce: `grep -c "sedentary" tests/fixtures/matters/9001.001/key.json` prints 0; run the ideal bench.

### M1 (med) A failed bench run names no item, on the console or in the run log
- Output: flawed line `missed=3 invented=2 flags_missed=1 flags_extra=1 rules=1`; nothing says the misses
  are F04, F15, F24, the missed flag is G3, the invented facts are MED0099 and the "80 pounds" quote on
  MED0003, or that the rule hit is `no-dme-ime` on "The IME found no work restrictions." Candidate runs
  write no run log row.
- What is wrong: the owner sees counts only and must diff JSON by hand to learn what failed and where.
- Breaks: brief ask (3), "would the owner understand what failed and where".
- Reproduce: the flawed bench command above; then read `state/runlog.sqlite` (0 runs).

### M2 (med) Flag scoring proves the cites, not the conflict
- Output: probe `cand_vacuous_about.json` (every `about` = "Pages disagree.") prints `flags=5 of 5`,
  exit 0; probe `cand_mmi_second.json` adds an MMI conflict on MED0008 and DEF0003 and it is silently absorbed
  (`flags_extra=0`) while the radiculopathy flag in H1 counts as extra.
- What is wrong: a model that names the right two pages and says nothing useful scores as well as the ideal,
  and two real conflicts sharing a page pair (causation, MMI, restrictions, all MED0008/DEF0003) count once.
- Breaks: spec D25 "flags match by kind and cite set" (spec sanctioned; see owner question Q2).
- Reproduce: as H1 with those probes.

### M3 (med) Model server down reads as a model that scored zero
- Output: `bench 9001.001 failure bench.model: <urlopen error [Errno 61] Connection refused>` then
  `found=0 of 26 missed=26 ... pages_failed=14 of 14`, exit 1.
- What is wrong: the message gives raw urllib text without the host (`127.0.0.1:18555`) or "is Ollama
  running", and the score line that follows makes an unreachable server look like a failed model.
- Breaks: D25 exit 2 "when it cannot run" (the model is not in that list, so spec-conformant; Q3).
- Reproduce: scratch config with `host = "http://127.0.0.1:18555"`, no server, `casefile bench --config
  <it> --matters tests/fixtures/matters`.

### M4 (med) The bench line does not name the model it scored
- Output: every `bench 9001.001 ...` line above; the model appears only in `runs.model` in sqlite.
- What is wrong: this command exists to choose a model, and two runs of different models print
  indistinguishable lines.
- Breaks: spec §7 stage 2 purpose; D25 line format (spec defined; Q4).
- Reproduce: any bench run without `--candidate`.

### M5 (med) The truncation failure does not say what to do
- Output: `bench 9001.001 failure bench.truncation: done_reason=length`; `failures.message` is the same
  four words, though the answer row holds `eval_count=728`, `prompt_eval_count=4817`.
- What is wrong: the owner is not told the reply was cut off at the output limit, how long it got, or which
  setting to change.
- Breaks: brief ask (3).
- Reproduce: `scripts/run.sh python -m tests.fakemodel --port 18555 --bench-matter
  tests/fixtures/matters/9001.001 --mode truncated` with the scratch config; stop the server after.

### L1 (low) The ideal's own line shows `extra=2`
- Output: ideal line `extra=2`: "Date of hire: 08/02/2021" (EMP0001:17) and "Lift up to 50 pounds
  repeatedly during the shift." (EMP0002:26), both excluded from the key by brief W5.
- What is wrong: the reference answer reports facts the key calls extra; the job description's 50 pound
  limit against the 60 and 40 pound accounts is a fact the attorney would want keyed.
- Reproduce: the ideal bench command.

### L2 (low) Key texts drop qualifiers the attorney relies on
- F20 text omits "within a reasonable degree of medical probability" (MED0008:17); F25 text omits "as of
  today's examination" (DEF0003:21, the 06/20/2025 MMI date). Not scored at stage 2. Reproduce: read key.json F20, F25.

### L3 (low) Page realism nits
- MED0001:6 "Dr. Halvard Quist-Benning, MD" (double honorific); MED0002:12 "resting comfortably after
  medication" before medication is given at :18; EMP0001:17 hire date in the middle of the incident
  narrative; MED0005:14 home exercise program "provided last week" though it was given at the 03/24
  evaluation (MED0004:22); DEF0001:3 "Page 1 of 3" but DEF0003 carries no page number. Reproduce: read the pages.

### L4 (low) The file is thinner than a real comp file
- No carrier or adjuster, no state first report of injury, no medical bills, no record of who requested the
  report (correct not to key that, per `no-hired-paid-retained`). The hearing-prep skill's first item is the
  billing memo; no page lets a model be tested on bills. Reproduce: list `records/`.

### L5 (low) Generic facility names may match real businesses
- "Ridgeline Physical Therapy", "Lakeshore Imaging", "Lakeshore Orthopedic Associates" (MED0004:1,
  MED0006:1, MED0007:1) are common enough to exist; patient and doctor names read invented.

### L6 (low) `casefile bench --help` explains nothing
- Output: usage with `--matters MATTERS --candidate CANDIDATE --config CONFIG` and no description of a
  candidate, the line or the exit codes. Reproduce: `scripts/run.sh casefile bench --help`.

## Owner questions (practice the playbook does not settle)

- Q1: Should the key be widened to every real conflict and gap on the pages (H1 list), or should
  `flags_extra` stop failing a run while the key is a sample?
- Q2: Should a flag also need its `about` to name the subject (or should the key allow several flags on one
  page pair), so causation, MMI and restrictions on MED0008/DEF0003 count separately?
- Q3: Should an unreachable model be exit 2 ("cannot run") rather than a scored zero?
- Q4: Should the bench line carry the model name?
- Q5: Is a missing PT discharge summary (G5) the gap you want tested, or the missing visit notes 2 to 5 and
  7 to 12, the ESI record and the 06/20/2025 re-evaluation?
- Q6: Should a test matter carry bills (for the billing memo) and a carrier file?
- Q7: Is "Dr. Marchetti's report" the form you want in the key's texts, or the bare "the report" the
  `no-dme-ime` rule text suggests?

## Good enough to keep

- 14 pages, 3 binders, stamp alone on each last line; chronology holds (03/11 ER, 03/14 family medicine,
  03/24 PT, 04/14 PT 6 of 12, 04/18 MRI, 05/09 ortho, 06/20 report); ages, weekday (Tuesday 03/11/2025)
  and wage arithmetic ($11,861.20 / 13 = $912.40) check.
- No em or en dashes in the fixtures, key, ideal, flawed or playbook (byte grep).
- Every one of the 26 key quotes sits verbatim on its cited page, and each of the 5 flags is supported by its
  cited pages; the planted conflicts (tote weight, prior back history, causation) are good hearing issues.
- Key and ideal prose pass the firm rules (`rules=0`); the flawed "IME" text is caught (`rules=1`).
- Flawed candidate trips every counter it should (missed, invented, flags_missed, flags_extra, rules).
- Model path: every reply is stored, failures land under the right gate, the stand-in stops cleanly.
