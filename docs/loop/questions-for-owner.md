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
   ANSWERED 2026-10-27 (round 4 check-in, ledger Q43): the login-user app.

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

## Answered 2026-10-27 (round 3 check-in)
- 8 to 20: interim rulings ratified (ledger Q34). 7 still open (Q19).
- 21, 22, 25, 26, 27, 29 -> ledger Q34. 23 -> Q35. 24 -> Q36 (chair ruling, owner had no preference;
  pending veto). 28 -> Q37.

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

## Round 2 questions from the output critic (round02-critic.md)

24. Benchmark key completeness (critic H1, Q1, Q5): should the answer key list every real conflict and
    gap a careful reader would flag (for example the missing PT visit notes 2 to 5 and 7 to 12, the PT
    letter, the ESI record and the 06/20/2025 re-evaluation), or should an extra flag stop failing the
    run? Interim: the chair added the one clear cross-page conflict (radiculopathy, MED0007 vs DEF0002) and
    three verbatim facts (OR-7); gaps beyond G4 and G5 wait for this answer and question 21.
25. Should a flag's `about` text count toward a match, so that two different conflicts on the same pair
    of pages (causation and MMI, MED0008 vs DEF0003) are scored separately (critic M2)? Interim: D25,
    kind plus cite set.
26. When the model server cannot be reached, should `casefile bench` exit 2 (cannot run) instead of
    scoring the matter `found=0` with exit 1 (critic M3, Q3)? Interim: D25, exit 1 with the failure line.
27. Should the bench line name the model it scored (critic M4, Q4)? Interim: D25's line; the model is in
    the run log.
28. Should a test matter include bills (for the billing memo) and a carrier file (critic Q6)?
29. Outputs say "Dr. Marchetti's report" in the fixture prose; is that right, or always just "the
    report" (critic Q7, Q16)?
30. Round 2 is held at the fix-cycle cap (Q5) on V2b-F1: a 302 or 307 reply from the model server stores
    no answer row (model.py:18, :50, :54). Choose: (a) one extra fix cycle limited to V2b-F1 (pass the body
    as `raw` at the three raises, add a 302 test) and one focused re-verify, then close and merge
    (recommended; the fix is three arguments and one test; Q23 precedent); (b) rule that a refused
    redirect is not a received reply (amend D25 and OR-8), then close and merge; (c) discard and re-brief
    per Q5.
    ANSWERED 2026-10-27: (a).

## Round 2 overnight rulings (Q31: chair rulings while the owner is away, each pending veto or ratification)

Owner, 2026-10-27: OR-1 to OR-9 RATIFIED, D25 and D26 RATIFIED; question 30 answered (a) (ledger Q32).

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
- OR-5 (2026-10-27): fix cycle 1 (Gemma) takes the correctness findings R2-CH-1, R2-CX-5 (= Fable F1),
  R2-CX-6, R2-CX-7 (= Fable F1b) and Fable F2 (`from exc` dropped at 5 sites, a brief-fidelity miss).
  Deferred to round 3 (Sonnet, Q30): Fable's cosmetic findings (33 trailing-whitespace lines, unused imports
  in 8 test files, prompt-framing comments, F7, F8) and the design lows F3 (`.DS_Store` in `records/`
  refuses the matter; likely on a Mac, needs a ruling on which files to ignore), F4 (binder listed twice
  reports a false duplicate stamp), F5 (validate names before reading), F6 (whitespace-only page text).
  Why: correctness first inside the three-cycle cap; lint rewrites of eight files by the small model cost
  more than they return this round.
- OR-6 (2026-10-27): fix cycle 1 choices ratified by the chair: `ModelError.raw` is a dict or the reply text
  as received (text stored as is, dict via json.dumps); collision messages name the later ID first. Carried
  to round 3: a non-200 reply still stores no answer row (model.py:59), outside the finding.
- OR-7 (2026-10-27): output critic 8b (`OUTPUT CRITIC 6/10 · high 2 · med 5 · low 6`). Chair verified H1 and
  H2 on the pages (MED0007 "left L5 radiculopathy" vs DEF0002 "No objective findings of radiculopathy";
  MED0008 15 pound restriction vs DEF0003 "No work restrictions"). Fix cycle 2 (Gemma): add flag G6
  (conflict MED0007, DEF0002, radiculopathy) and facts F27 (MED0008 restriction line), F28 (DEF0003 "No
  further treatment is medically necessary."), F29 (MED0003 "Lumbar strain, likely work related."); update
  ideal.json and flawed.json and every exact number; M1: the bench prints which fact IDs were missed, which
  flags missed and extra, which candidate facts were invented and which rules fired. Owner questions 24 to
  29 for the rest; M5 (truncation message detail) and the lows go to stage 4 and round 3.
- OR-8 (2026-10-27): blind verifier 8c FAIL, R2-3e refused on V2-F1 (a non-200 reply stores no answer row;
  model.py:55 and :59 raise without `raw`). Chair rules D25 means what it says: every received reply,
  any status, is stored. Fix cycle 3 (the last allowed, Q5): V2-F1 plus tests for the verifier's five green
  seeds S1 (only folders with matter.toml are matters), S2 (cite must match for found), S4 (missing
  done_reason is not a stop), S5 (a duplicated extra flag counts once), S6 (imperfect counts accumulate
  across matters). Unlogged design calls, ratified pending veto: a duplicate candidate fact counts once
  (neither found twice nor extra); candidate mode writes no run log (no model call is made). Carried to
  round 3: two matters with the same number are not refused.
- OR-9 (2026-10-27): round 2 held at the cap: not merged, `loop/round-03` not opened, no re-brief.
  Owner question 30. Round report written; Librarian and spec §11 wait for the close.

## Held 2026-10-27 (round 3 brief)

31. Stamp separators: are `MED0001`, `MED 0001` and `MED-0001` the same stamp to you (one page, three
    spellings by three scanners), or different stamps? Intake records each stamp exactly as OCR reads it;
    cite matching later needs to know whether to treat them as one. Interim: recorded raw, no normalisation.
32. Blank pages: when a page has no text after OCR (a separator sheet, an unstamped blank back), should
    intake list it as an open item every time (the command exits 1 and names the page), or record it as
    blank quietly and exit 0? Interim: listed, exit 1; the page is never counted as read.
33. Binder naming: when you drop a PDF, should the binder be named by you (`--binder medical`, and later a
    box on the web page) or taken from the file name? File names carry dates, spaces and sometimes a client
    name. Interim: a typed name, letters, digits and hyphens only.
34. Re-intake: when a binder is scanned again (a better scan, missing pages added), should the new file
    replace the old pages or should intake refuse until the old binder is removed by hand? Interim: refuse.
35. Stamp shapes on your records: do stamps ever carry a suffix after the digits (such as `MED0001-A` or
    `MED0001.2`), and do your pages carry other tokens that look like a stamp, such as claim numbers of the
    form `ABC-2025-0418`? With the Q21 pattern such a token is recorded as a stamp `ABC-2025`. Interim: the
    Q21 pattern with word boundaries; everything that matches is recorded and shown.
36. Languages: are any records in a language other than English (Spanish medical records, for example)?
    OCR runs with English only until told otherwise. Interim: English only.

Answered 2026-10-27 (ledger Q40): 31 same stamp, raw plus normalised form kept; 32 to 36 as the interim
rulings.

## Held 2026-10-27 (round 3 brief revision)

37. In the invented matter 9001.001, the report says "The L4-L5 disc changes are described as degenerative"
    (DEF0002:32) while the MRI reads "L4-L5: 4 mm posterior central disc protrusion contacting the thecal
    sac" (MED0006:25) and also notes "mild degenerative change noted at the lower vertebral levels"
    (MED0006:23). Is that a conflict you would flag between the two records, or is it an inference the
    benchmark should not require? A keyed flag fails a model that does not report it; an unkeyed one fails a
    model that does. Interim: not keyed (only unambiguous disagreements are in the key).
ANSWERED 2026-10-27 (ledger Q40): 31 same stamp (raw kept plus a normalised form); 32 to 36 as the interim
rulings.

## Held 2026-10-27 (round 3 critic, Codex CX-7; interim ruling by the chair, pending veto)
38. Do your Bates stamps ever carry a suffix after the digits (`MED0001-A`, `MED0001A`, `MED0001.2`)? Today a
    stamp must end at a token boundary, so `MED0001A` is not recorded at all (before the fix it was recorded
    as `MED0001` and merged with `MED0001B`). After fix cycle 2 (critic H1) a stamp also may not run on into
    `-`, `.` or `/` plus a letter or digit, so `MED0001-A`, `MED0001.2` and claim numbers like `QRL-2025-0418`
    record nothing. Interim: boundary rule; suffix forms wait for your answer.

## Held 2026-10-27 (round 3 output critic, round03-critic.md; interim rulings by the chair, pending veto)
39. The stamp pattern (Q21) also records whole tokens that are not Bates stamps, such as `ABC 123456` or a
    billing code like `CPT 99213`. Since every match is recorded (Q35) and you pick the stamp at hearing prep,
    should each page record also say where each stamp sits (bottom centre, top right), so hearing prep can
    offer your firm's bottom-centre stamp first? Interim: no position recorded (OCR text carries none).
40. When one page shows the same stamp in two spellings (`MED 0001` and `MED-0001`), keep both raw forms, or
    is the first enough since they are one stamp (Q40 item 31)? Interim: first raw kept (critic L5).
41. Binder names are lowercase only, because macOS folders ignore case and `Medical` and `medical` would be
    one folder. Is that acceptable? Interim: lowercase, with a plain-words message (critic L2).

ANSWERED 2026-10-27 at the round 3 close (ledger Q42): 38 no suffixes, rule stands; 39 no position; 40 first
spelling enough; 41 lowercase accepted. D27 to D30, the whole-token rule and G9 ratified.

## Held 2026-10-27 (round 4 brief)

42. When a chunk of pages fails both attempts, should you be able to mark those pages as read by hand (an approval
    row in the run log, with your name) so the memo can proceed with them, or must a failed page stay open until the
    model reads it on a later run? Interim: open until the model reads it; no manual read.
43. A quote copied from a defense report may itself say "IME" or "retained by the employer". The firm rule check
    skips quoted spans (they are the record's words, not ours) and checks everything we write around them. Is that
    right, or should a quote holding those labels never appear in an output either? Interim: quotes are exempt.
44. Do your scanned binders carry a repeated line on every page besides the Bates stamp (firm name, "CONFIDENTIAL",
    a fax header, a date), which the quote check should ignore when a quoted passage runs across it? If so, what
    does it look like (shape only, no example from a file)? Interim: only a stamp alone on a line and "Page N of M"
    lines are ignored.
45. When a quote matches the page only through the OCR-fault rung (a ligature, a hyphen at a line end, a header
    inside the passage), should the memo mark it (for example "[OCR]") so you check the page by eye, or treat it as
    verified like an exact match? Interim: counted as verified; the rung is recorded in the run log only.
46. Repairs to an answer's punctuation (a trailing comma, a missing final brace) are logged and the answer is used.
    Should any output tell you that its source answer was repaired, or is the log enough? Interim: the log only.

ANSWERED 2026-10-27 (round 4 check-in, ledger Q44): 42 to 46, every interim ruling kept (42 stays open, 43 quotes
exempt, 44 stamp and "Page N of M" lines only, 45 verified with the rung logged, 46 log only).

## Held 2026-10-27 (round 4 brief, revised after the Codex plan review)

47. When a chunk of pages passes every check but the model cites nothing on one of its pages (a cover sheet, a
    blank page, or a page it skipped: the code cannot tell which), that page is listed as an open item marked
    "uncited" and never counted as read. Should that stay so, or should the model's own per-page statement
    "nothing relevant on this page" close it, or should you close it by hand with your name in the log (as question
    42 asked for failed pages)? Interim: it stays open; nothing closes it.
48. The checks verify a fact's quote against the page and that every number in the fact's summary sentence appears
    in its quote; the rest of the summary's wording is the model's and is not verified. Should the memo show the
    quote as the verified text and label the summary as the model's reading, or should a second model call judge
    each summary against its quote before the memo uses it? Interim: no output of this round or the next uses a
    summary as verified; the quote is the verified thing.
