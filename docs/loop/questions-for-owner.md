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
