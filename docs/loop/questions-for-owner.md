# Questions for the owner

Held questions, numbered, with any interim ruling made while the owner was away (pending veto).

1. Tiers for the loop: keep gdd-loop's (Fable writes the brief, Codex reviews, Opus orchestrates,
   Sonnet codes) or change for cost? Interim: gdd-loop's tiers.

2. The Ollama model tag for Qwen3.8-27B on the Studio (the default for `[model].name`). Interim:
   `qwen3.8:27b`.
3. Where matters live on the Studio: `Cases/` inside the repo checkout (as `.gitignore` implies) or a
   folder outside it. Interim: `[paths].matters = "Cases"` relative to the config file.
4. Firm rule 5 scope: the acronyms "DME" and "IME" only (spec §4), or also "independent medical
   examination" and "defense medical examination" (`cards/_core.md:10`)? And may "DME" ever appear in
   our outputs meaning durable medical equipment? Interim: acronyms only, whole words, any case.
5. The Bates stamp formats the firm's records carry (prefix letters, separator, digit count; the
   format only, no example from a file). Interim pattern `[A-Z]{1,8}[ -]?\d{4,}`.
6. May the loop set `sandbox.network.allowLocalBinding: true` in this project's Claude Code settings
   so the stand-in model server can listen on 127.0.0.1 during sandboxed test runs? Without it every
   socket test fails closed (exit 3) and the chair must run them outside the sandbox.
7. On the Studio, does Ollama run as your login user (the Ollama app) or as a system launchd daemon?
   The doctor's "127.0.0.1 only" check reads the listener with `lsof`, which sees only your own
   processes without root.

## Held 2026-10-26 (round 1 output critic; interim rulings by the chair, pending veto)
8. "DME" meaning durable medical equipment: Q16 blocks the bare word, so "The physician ordered DME,
   a lumbar brace." fails. Exempt that meaning, or always spell out "durable medical equipment"?
   Interim: blocked; outputs spell it out.
9. Does the hired, paid or retained rule reach only the report's author, or any doctor? Is "Who
   referred you to Dr. Example for your therapy?" (a treating doctor) allowed? Interim: any doctor,
   examiner or exam in the same clause; "who referred" stays blocked.
10. Is a wage or temporary disability payment a "bill" for the treatment and bills rule? Are liens,
    costs and expenses bills? Interim: "paid" stays a bill word; liens, costs, expenses and balance added.
11. Exam volume: does it include testimony counts and practice mix ("How many times have you testified
    for employers?")? Interim: as built (exam and report counts only).
12. Which cite forms are allowed: Bates ranges, lists of Bates numbers, Bates plus a pinpoint?
    Interim: single Bates, ranges (MED0001-MED0009) and comma lists; no pinpoints.
13. Should other exam labels (QME, AME, PQME) count as "any form" of DME or IME? Interim: no.
14. Should the doctor ever create a missing matters folder? Interim: never; FAIL and name the path.

15. Spec §8b (your commit 4614a1e) names its decisions D12 to D16; the §9 table already uses D12 to
    D16 for round 1's rulings (run.sh, config, data root, ...). Renumber §8b's as D24 to D28 in §9?
    Interim: cite them as "§8b D12" etc. to keep them apart; the chair does not edit your section.

19. (re-brief critic Q-A) `matters = "~"` or `"/"` loads although the checkout sits inside it. Refuse a
    matters folder that contains the checkout? Interim: allowed (D13 says only "outside the checkout").
20. (re-brief critic Q-B) Ctrl-Z stops only the wrapper; the job keeps running and resuming keeps its exit
    code. Should pause pause the job? Interim: as built.

## Answered 2026-10-25
- Q1 -> ledger Q10, Q14. Q2 -> Q20. Q3 -> Q17. Q4 -> Q16. Q5 -> Q21. Q6 -> Q18. Q7 -> Q19 (still open).

## Held (round 1 re-brief), 2026-10-26 (interim rulings by the chair, pending veto)
16. On the Studio, will a `python3` be on PATH before `uv sync` (Xcode Command Line Tools installed, or a
    python.org build)? `scripts/run.sh` needs one for the path guard and the capture stage before the
    venv exists; without one it exits 95 "cannot verify". Interim: assumed yes; the setup guide (stage 9)
    lists it as a prerequisite.
17. When a job's child exits but a background process it started still holds the output pipe, may the
    wrapper kill that process group after 2 seconds and return the child's code (so no run can hang on a
    stray server)? A process that detached itself is not reached. Interim: yes, 2 seconds, in D12.
18. `scripts/run.sh` puts its capture directory under `${TMPDIR:-/tmp}` (run.sh:33) and removes it when
    the run ends (run_capture.py:66). If TMPDIR were ever set to a folder inside the checkout, captured
    output would briefly live there. Should the wrapper refuse such a TMPDIR (a new limit, D12), or is
    "TMPDIR is never inside the checkout" a setup-guide rule? Interim: no new limit; the setup guide says
    it; the test suite's TMPDIR is outside (sandbox).

## Held 2026-10-26 (round 2 brief; interim rulings by the chair, pending veto)
21. What must the medical chronology, and so a benchmark answer key, contain at minimum per encounter:
    date of service, provider and facility, mechanism of injury as stated, pain scores, prior history,
    exam findings, imaging results, diagnosis, treatment and plan, restrictions and work status,
    causation and MMI statements, referrals and records referenced? The stage 2 key holds 26 facts and 5
    flags of these kinds for the invented matter 9001.001 (brief §2 W4). Which categories are missing or
    unnecessary for your practice? Interim: the 26 as listed.
22. On the Studio, where do the benchmark matters and their `key.json` live: beside the closed matters
    under `[paths].matters` (one `key.json` per matter folder), or in a separate folder outside the
    checkout passed with `casefile bench --matters`? Interim: a separate folder outside the checkout,
    same layout as `tests/fixtures/matters/`.
23. In the firm's scanned records, is the Bates stamp always one stamp per page at the bottom (the
    stage 2 fixture puts it alone on the last line), or do stamps appear top right, with a producing
    party prefix, or more than one per page? Interim: one stamp per page, last line; stage 3 reads the
    stamp from the page text with the configurable pattern (Q21).

## Round 2 overnight rulings (Q31: chair rulings while the owner is away, each pending veto or ratification)

- OR-1 (2026-10-26 23:05): "Gemma is free" is judged from `~/local-worker/ollama-serve.log`: the last
  POST /api/chat or /api/generate at least 15 minutes old and the server's last slot line "all slots are
  idle", checked every 30 minutes for up to 24 hours. Why: the other job keeps the model loaded for 24 h,
  so "unloaded" never fires. Risk: a job that pauses more than 15 minutes between requests would be
  shared with the build (Ollama queues; both still finish, just slower).
- OR-2 (2026-10-27): ratified the build orchestrator's b6a9624, which replaced 7 en and em dashes with
  hyphens in `docs/loop/round-02/round02-brief-codex.md` (a tracked copy of Codex's review) so the prose
  gate prints 0. The chair committed that copy at 600ad8f without running the gate (Mistakes Log). The
  untouched original stays in `.workflow/scratch/`.
- OR-3 (2026-10-27): the measured Sonnet cost control (offered at Q29, no veto before bed) runs now, in a
  throwaway worktree branch `control/r2-sonnet` from 2dfa4f5, rebuilding W3, the W5 code, W6 and W9
  (`--candidate` path) from the same brief; never merged. Its tokens scale to the round for the
  comparison in the round report.
- OR-4 (2026-10-27): Codex R2-CX-2 (the bench cannot tell when Ollama silently cut the prompt) is real
  against spec §4 gate 1, but the check needs the stage 4 model client design (Ollama does not count
  cached prompt tokens, so "tokens read = tokens sent" is not a one-line test). Deferred to the stage 4
  brief as a carried item; D25 gets a known-limit sentence. Stage 2's 14-page matter is about 5 k tokens
  against a 65 k context, so it cannot fire in the loop today.
