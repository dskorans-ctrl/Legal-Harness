# Librarian

This file is the project's running record of bugs, code issues and failures found in any pass, so
the next pass does not repeat them. It indexes the round reports under `docs/loop/round-NN/` and the
ledger at `.workflow/LEDGER.md` without replacing them. Updated by: the chair at every round close
(new entries for that round, survivors moved to "Open items"); any builder who finds a new one
mid-round appends it under the current round heading. Every builder brief must cite this file; every
builder report must state which entries it checked its work against.

Cross-project failure classes live in the app-loop skill's catalog
(`.claude/skills/app-loop/references/catalog.md`); consult it, never copy it here.

## Builder pre-flight

- Does a path guard compare by filesystem identity (samefile, every existing ancestor), not by
  spelling? This Mac's disk is case-insensitive and symlinks alias folders. (#R01-CX-1, #R01-V-B1)
- Does a "forbidden file" scan cover every format of the class (all image and Word formats), the
  folder name in any case, and symlinks that point into Cases or Bench? (#R01-CX-2, #R01-CX-6)
- Does an append-only table refuse INSERT OR REPLACE with recursive_triggers OFF? (#R01-CX-3)
- When an output cap trips, is the child process group killed so the verdict comes promptly? (#R01-CX-4)
- Does every model answer path read `done`, `done_reason` and both token counts, and does each guard
  have a probe where only that guard is wrong (READY with done_reason=length)? (#R01-CX-5, #R01-CX-10)
- Does a firm rule regex hold across whitespace, line breaks, hyphens, dots and plurals, AND pass a
  list of ordinary memo and deposition sentences (hired by an employer, retained hardware, attorney
  fees, benefits paid)? Test both directions. (#R01-CX-7, #R01-CX-8, #R01-OC-H2, #R01-OC-H3)
- Does a health check claim only what it ran (versions are not "OCR works")? (#R01-CX-9, #R01-OC-H1)
- Do failure tests assert the exit code, not only the printed line? (#R01-CX-11)
- Does a parameter whose default silently skips a rule have a default at all? (#R01-OC-M2)
- Does a check ever create the thing it checks for (mkdir of a mistyped folder)? (#R01-OC-M7)
- Does every exit-code branch have its own test, so seeding `return 98` to `return 0` goes red? (#R01-V-B2, #R01-V-B3)
- When a guard is fixed, is every alias of the protected thing tested (case, symlink to root, symlink
  to a subfolder, chains, `..`), not only the one the finding named? (#R01-V-B1b)
- Is the chair's fix instruction itself checked against the spec row before sending? (#R01-OC-M8)
- Does a process watcher treat a stop or continue as an exit? Use kqueue NOTE_EXIT, not SIGCHLD. (#R01R-RX-1)
- Does every interrupt (HUP, TERM, INT) kill the job and remove its capture, so client text never
  lingers in a temp folder? (#R01R-OC-F1)
- Is a relative path resolved against the root the spec names (D14: the checkout), not the config's folder? (#R01R-OC-F2)
- Is the interpreter that runs a step the same one the guard ran under? (#R01R-RX-2)
- Does every path that receives a reply (200, non-200, 3xx refused, non-JSON, wrong shape) store it,
  and does a test drive each path, including the real opener's redirect handler? (#R02-V-F1)
- Does a loader refuse two entries that would collide (same id, or same cite and quote), so a key can
  never be unreachable? (#R02-CX-5)
- Does every input read as text name its encoding and turn a decode error into the documented exit? (#R02-CX-7)
- Does a positive-number gate have a test at zero, not only at None? (#R02-CH-1)
- Is an answer key checked against the pages by a reader, not only by the loader (a key missing a fact
  on the page fails a correct model)? (#R02-OC-H1)
- When the orchestrator copies a review record into the tree, did the gate run before the commit? (#R02-P-1)
- Does a step that shells out to a tool prove the work per unit (per page: placeholder text such as
  `[skipped page]`, masked text, a no-op copy), and does its smoke input force the tool to do the work
  (image-only, not a file that already holds the answer)? (#R03-PC-1)
- Does a text-similarity or `--check` oracle fail on one changed digit, a dropped "no", and a changed
  text layer, not only on a structural or percentage drop? (#R03-PC-2)
- Was every premise of a brief (an example, a "defect", a call graph, the existing tests it breaks) run
  against the real code and the project interpreter, and against the owner rulings added since it was
  written, before the lanes split? (#R03-PC-3)
- Does cleanup remove only what this run created, does publication roll back on BaseException, and do the
  no-overwrite and rollback checks cover the same folders? (#R03-CX-2)
- Does a token matcher refuse a match that is a prefix, suffix or fragment of a longer token (letters,
  digits, `-./` joins) at both ends, in any letter case? (#R03-CX-5)
- Does a refusal or open-item message name every folder or page involved, say what to do, use words and
  not a pattern, and keep library noise off the line? (#R03-OC-L1)
- Is every refusal decided before the first side effect (a model call, a log row, a printed result)? (#R03-V-L1)
- Does prompt survival have evidence independent of counts and server claims, with a byte ceiling and fresh two-message retry?, #R04-PC-1
- Do recordings and live requests canonicalise dynamic fields symmetrically, including the retry path?, #R04-PC-4
- Does coverage reject empty arrays and blank placeholder records, and leave every uncited page open?, #R04-PC-6
- Does validation check every reference and summary number, and label the remaining summary wording as unverified?, #R04-PC-7
- Does a required missing-data warning run even when no text matches the warning rule?, #R04-PC-9
- Does each earlier gate admit every punctuation form that a later gate is allowed to repair?, #R04-PC-11
- Does coverage use stable page IDs and refuse a stamp that resolves to more than one page?, #R04-CX-1
- Does OCR dehyphenation join only letters and preserve numeric ranges and minus signs in matching and equality?, #R04-CX-3
- Does every JSON loader reject duplicate object keys at every depth before a dictionary can discard content?, #R04-CX-7
- Does enum equality preserve JSON types recursively, including booleans nested in arrays and objects?, #R04-CX-9
- Does a mutation control execute the changed source with isolated or cleared bytecode caches?, #R04-OC-1
- Does a numeric evidence check distinguish citation identifiers from the numbers asserted in prose?, #R04-V-2
- Does a quote test reject text present elsewhere in the chunk but absent from the cited page?, #R04-CH-1
- Does an incremental or chunked reader measure relationships across chunks and runs, and state which pairs it never compares?, #R05-PC-1
- Does an append-only file recover an incomplete final write without accepting corruption in a completed or interior record?, #R05-PC-7
- Do tests default to a closed endpoint so losing an injected transport cannot reach the owner's live service?, #R05-PC-8
- Does a renderer emit every accumulated version or reading of a merged record, with a multiple-version control?, #R05-PC-12
- Does a test copy a shared fixture before a job writes into it, leaving the session fixture unchanged?, #R05-PC-17
- Does a read verdict require both coverage and durable case-file facts, and does a failed append cause those pages to be re-sent?, #R05-CX-2
- Does a view retain every stored fact when its original page disappears, with an explicit place for facts whose pages are all absent?, #R05-CX-3
- Does a matter lock cover load, identity allocation, merge and append, with duplicate stored IDs refused on load?, #R05-CX-4
- Does each merged reading retain its source page, including identical wording on two pages, and name that page when displayed elsewhere?, #R05-CX-5
- Does a hash-chain integrity claim test an edited final payload and a deleted complete tail against an independently anchored head?, #R05-CX-6
- Does a relationship require the right number of distinct resolved pages, with cites deduplicated in the same order as page IDs?, #R05-CX-7
- Do intake and output validation share one stamp definition, or refuse incompatible configured definitions before processing?, #R05-CX-9
- Does a newly rebuilt output describe its own published state while still reporting other outputs that remain stale?, #R05-OC-1
- Do change counts measure the semantic content added inside every event kind, including a new fact's initial reading?, #R05-OC-3
- Does a shared error describe only its own layer, with caller-specific consequences and prefixes added once by each command?, #R05-V-1
- Are all accepted build and fix rulings reconciled with the canonical decisions table before the round closes?, #R05-V-2

## Round 1 (2026-10-25 to 2026-10-26)

### R01-CX-1: matters guard compared against the config folder, not the checkout
**What broke:** `src/casefile/config.py:125`: a config outside the repo with `matters=<repo>/Cases` loaded.
**Why:** a guard anchored to the wrong root; the intended boundary (the checkout) was never tested.
**Caught by:** 8a Codex review; chair repro `accepted matters .../legal-harness/Cases`.
**Countermeasure:** checkout-root check, tests/test_config.py. Superseded in part by #R01-V-B1.
**Status:** fixed (28a5f96, f2023ae).

### R01-CX-2: privacy scan missed image and Word formats
**What broke:** `src/casefile/privacy.py:7` lacked .gif, .webp, .bmp and others.
**Why:** a forbidden class enumerated by a short list instead of the whole class.
**Caught by:** 8a Codex review.
**Countermeasure:** wider SUFFIXES and .gitignore; tests/test_privacy.py.
**Status:** fixed (28a5f96).

### R01-CX-3: append-only run log allowed INSERT OR REPLACE
**What broke:** `src/casefile/runlog.py:32`: with recursive_triggers OFF an approval decision was replaced.
**Why:** DELETE triggers do not fire on REPLACE conflict resolution unless recursive triggers are on.
**Caught by:** 8a Codex review; chair repro `decision now rejected`.
**Countermeasure:** BEFORE INSERT duplicate-id triggers in every table; tests/test_runlog.py.
**Status:** fixed (28a5f96).

### R01-CX-4: output cap waited on a sleeping child
**What broke:** `scripts/run.sh:11`: cap hit, then run.sh waited for the child (6 s measured).
**Why:** closing a pipe is not stopping a process.
**Caught by:** 8a Codex review.
**Countermeasure:** `scripts/run_capture.py` kills the child process group on overflow; tests/test_run_sh.py.
**Status:** fixed (28a5f96). Risk: run.sh now needs a `python3` on PATH before `uv sync`.

### R01-CX-5: an answer with done=false or no token counts passed
**What broke:** `src/casefile/model.py:76-82` never read `done`; doctor checked no counts.
**Why:** fail-open on incomplete model answers (truncation is a failure).
**Caught by:** 8a Codex review.
**Countermeasure:** ModelError on done != true; doctor counts_ok; fake model `incomplete` mode (D18).
**Status:** fixed (28a5f96).

### R01-CX-6: privacy scan passed a `Cases` symlink
**What broke:** `src/casefile/privacy.py:19`: untracked symlink `Cases` gave `scan=[]`.
**Why:** a lexical prefix check (`Cases/`) on an inventory that lists a link without a slash.
**Caught by:** 8a Codex review; chair repro in a temp repo.
**Countermeasure:** first-component casefold check and resolved symlink targets.
**Status:** fixed (28a5f96).

### R01-CX-7: payment rule missed "The insurer paid Dr. Example", then over-blocked benefits prose
**What broke:** `playbook/rules.toml:21`; the first fix used a 120-char cross-sentence window and
blocked "The carrier paid temporary total disability ...; Dr. Lane released him".
**Why:** a regex rule widened without a must-pass list of ordinary prose.
**Caught by:** 8a Codex review; the over-block by the chair's own probe.
**Countermeasure:** one clause, 60 chars; must-pass and must-fail tests; tuning question T-5.
**Status:** fixed (28a5f96).

### R01-CX-8: spelled-out DME/IME labels missed across whitespace
**What broke:** `playbook/rules.toml:8`: "independent medical\nexamination" passed.
**Why:** literal spaces in a pattern meant to match words.
**Caught by:** 8a Codex review.
**Countermeasure:** `\s+`, later `[\s-]+`; tests/test_rules.py.
**Status:** fixed (28a5f96, f2023ae).

### R01-CX-9 and R01-OC-H1: doctor OCR passed on `--version` alone
**What broke:** `src/casefile/doctor.py:149-158`: two stub tools exiting 0 gave `ocr PASS`, `failed=0 of 8`.
**Why:** a health check that claims more than it ran.
**Caught by:** 8a Codex review (CX-9), then 8b output critic (H1) after cycle 1's partial fix.
**Countermeasure:** OCR FAIL until the stage 3 smoke test (D19), reason says "OCR not verified".
**Status:** fixed (8994fff); real smoke test carried as R1-19.

### R01-CX-10: doctor truncation probes masked the done_reason guard
**What broke:** `tests/test_doctor.py:64`: seed dropping `done_reason == "stop"` left `15 passed`.
**Why:** two guards that both fire on every probe mask each other (catalog class).
**Caught by:** 8a Codex review; chair seed.
**Countermeasure:** READY with done_reason=length and READY with done=false probes.
**Status:** fixed (28a5f96); chair seed `1 failed, 32 passed`.

### R01-CX-11: context failure tests ignored the exit code
**What broke:** `tests/test_doctor.py:62-80`.
**Why:** an exit code that does not carry the verdict is untested if only the text is asserted.
**Caught by:** 8a Codex review.
**Countermeasure:** exit code asserted in every context failure test.
**Status:** fixed (28a5f96).

### R01-OC-H2: DME/IME rule missed dotted, plural and "exam/evaluation" forms
**What broke:** `playbook/rules.toml:8`: 7 of 7 forms passed (D.M.E., IMEs, "independent medical evaluation").
**Why:** "in any form" (Q16) tested with only the canonical spellings.
**Caught by:** 8b output critic; chair repro.
**Countermeasure:** dotted, plural, exam/evaluation, hyphen forms; tests.
**Status:** fixed (8994fff, f2023ae).

### R01-OC-H3: hired/retained/fees rule blocked ordinary deposition prose
**What broke:** `playbook/rules.toml:21`: "When were you hired?", "retained hardware", "attorney fees" failed.
**Why:** bare words matched outside the doctor context the spec rule is about.
**Caught by:** 8b output critic; chair repro 6 of 6.
**Countermeasure:** hired/retained/fees only in a doctor clause; must-pass list.
**Status:** fixed (8994fff); scope held as owner question 9.

### R01-OC-M2: Rules.check defaulted to unit="text", silently skipping the question rule
**What broke:** `src/casefile/rules.py:53`.
**Why:** a flag with a silent default is fail-open (catalog class).
**Caught by:** 8b output critic.
**Countermeasure:** `unit` is required.
**Status:** fixed (8994fff).

### R01-OC-M7: doctor created a mistyped matters folder and passed
**What broke:** `src/casefile/doctor.py` check_folders mkdir.
**Why:** a check that creates its own subject.
**Caught by:** 8b output critic.
**Countermeasure:** matters never created; FAIL names the path (owner question 14 interim).
**Status:** fixed (8994fff).

### R01-OC-M8: cycle 1 added a config-folder limit the spec does not have
**What broke:** `src/casefile/config.py:126` refused `~/Cases` beside `~/config.toml`.
**Why:** the chair's fix instruction for CX-1 went beyond D13 and Q17; not checked against the spec row.
**Caught by:** 8b output critic.
**Countermeasure:** limit removed; separate messages for relative and inside-checkout.
**Status:** fixed (8994fff).

### R01-V-B1: matters guard was case-sensitive on a case-insensitive disk
**What broke:** `src/casefile/config.py:128`: `/Users/.../LEGAL-HARNESS/invented-matters` loaded, exit 0.
**Why:** paths compared by spelling, not identity (follow-on of #R01-CX-1).
**Caught by:** 8c blind verifier; chair repro `B1 exit=0`.
**Countermeasure:** samefile on matters and each existing ancestor; case and symlink alias tests.
**Status:** fixed (f2023ae).

### R01-V-B2: run_capture.py exit-98 guard had no test; missing command returned 98
**What broke:** `scripts/run_capture.py:33-35`: seed `return 98` -> `return 0` left `162 passed`.
**Why:** an exit branch with no test of its own (two guards masking each other, R1-13).
**Caught by:** 8c blind verifier.
**Countermeasure:** 127 not found, 126 not executable, 98 capture only (D12 amended); tests per branch.
**Status:** fixed (f2023ae); chair seed `5 failed, 13 passed`.

### R01-V-B1b: matters and toolchain guards walked the typed path, not the resolved one
**What broke:** `src/casefile/config.py:129-134` and `scripts/run.sh:12-15`: a symlink to a
case-swapped subfolder of the checkout loaded (exit 0); the "cannot verify" branch had no test.
**Why:** the B1 fix covered aliases of the checkout root only; identity must be checked on the
resolved path and every ancestor of both spellings (third pass on one guard: #R01-CX-1, #R01-V-B1).
**Caught by:** 8c re-verifier; chair repro `B1b exit=0`.
**Countermeasure:** resolved-path identity walk in config.py and run.sh (toolchain exits 95, D12).
**Status:** fixed (8aeba23).

### R01-V-B3: capture write failure branch untested; short writes not looped
**What broke:** `scripts/run_capture.py:38-41`: seed `return capture_failed(exc)` -> `pass` stayed green.
**Why:** an exit branch without its own test (#R01-V-B2 class, second guard in the same file).
**Caught by:** 8c re-verifier.
**Countermeasure:** write loop to completion; write-failure test; chair seed `2 failed, 21 passed`.
**Status:** fixed (8aeba23).

### R01-P-1: process notes
- Codex workspace-write cannot write `.git`; the chair commits every Codex item (R1-14).
- The chair committed loop records while a Codex lane was live in the main tree (R1-17, catalog #53).
- Codex's sandbox denies socket binding, so its full-suite runs show 5 socket failures; the chair
  re-runs the suite and gate inside the session sandbox (allowLocalBinding, Q18) before every commit.
- The output critic left a stand-in server running; kill was refused in its sandbox. Critic and
  verifier prompts must prefer pytest-driven runs that clean up.

## Round 1 re-brief (2026-10-26, Q24, Q26, Q27)

### R01R-1: one identity guard replaces four spelling-based patches
**What broke:** the guards of #R01-CX-1, #R01-V-B1, #R01-V-B1b each closed one alias; `..` after a missing
part still escaped run.sh (V3-2), a symlink loop gave a traceback (V3-1).
**Why:** a guard rebuilt per finding instead of designed for the class.
**Caught by:** three verifier passes; the re-brief (Fable) redesigned it, Codex attacked the plan (19 findings).
**Countermeasure:** `src/casefile/pathguard.py` (D24): identity of every ancestor of the typed and real
spellings; one alias table drives the module, config and run.sh tests; final verifier ran 26 + 26 probes.
**Status:** fixed (330ff81..a69814d, 22d0125).

### R01R-RX-1: a stopped and resumed child was killed as if it had exited
**What broke:** `scripts/run_capture.py:29` SIGCHLD handler started the 2 s grace on SIGSTOP; chair probe
`exit=137 secs=2`, want 3.
**Why:** SIGCHLD fires on stop and continue too (no SA_NOCLDSTOP in CPython).
**Caught by:** re-brief 8a Codex review; chair reproduced.
**Countermeasure:** kqueue NOTE_EXIT watch (also removes select's 1024-descriptor limit, RX-5).
**Status:** fixed (22d0125).

### R01R-RX-2: the wrapper exec'd a different python3 than the one that ran the guard
**What broke:** `scripts/run.sh:17`: venv/bin prepended to PATH before `exec python3`.
**Why:** a check and its consumer resolved the same name twice.
**Caught by:** re-brief 8a Codex review.
**Countermeasure:** `PY` resolved once and used for both.
**Status:** fixed (22d0125).

### R01R-OC-F1: hangup or TERM left the job running and its output in a temp folder
**What broke:** `scripts/run_capture.py`: SIGHUP -> exit 129, child alive, capture folder kept.
**Why:** start_new_session isolates the child from terminal signals; default handlers skip `finally`.
**Caught by:** re-brief 8b output critic; chair reproduced.
**Countermeasure:** HUP/TERM/INT handlers kill the group, remove the capture, exit 128+n.
**Status:** fixed (9f86d07).

### R01R-OC-F2: state and playbook defaults followed the config file, not the checkout
**What broke:** `src/casefile/config.py`: config in the home folder made doctor create ~/state and FAIL playbook.
**Why:** relative paths anchored to the wrong root (D14 says the checkout).
**Caught by:** re-brief 8b output critic.
**Countermeasure:** relative state and playbook resolve against the checkout.
**Status:** fixed (9f86d07).

## Round 2 (2026-10-26 to 2026-10-27; Gemma trial, Q28)

### R02-CX-5: duplicate facts in the answer key made a perfect score impossible
**What broke:** `src/casefile/benchkey.py`: two facts with the same cite and quote; one candidate fact
matched only one of them (`found=26 of 27`, never perfect).
**Why:** a loader that accepted entries the scorer cannot tell apart.
**Caught by:** 8a Codex review; chair repro with fact F99.
**Countermeasure:** key refuses id collisions and same cite and quote (exit 2).
**Status:** fixed (0f2022d).

### R02-CX-6 and R02-V-F1: received replies stored no answer row (non-JSON 200, then non-200)
**What broke:** `src/casefile/model.py:62-65` (non-JSON 200), then `:52-60` (404, 503) raised `ModelError`
without `raw`, so `benchrun.py:69` stored nothing; D25 says every received reply is a row.
**Why:** the store rule was enforced per raise, not per path; each review found the next raise.
**Caught by:** 8a Codex (CX-6), verifier 1 (V2-F1, probe404 answers=0).
**Countermeasure:** whole decoded body as `raw` at each raise; tests per path.
**Status:** fixed (ba24d90, 81c78ce). Third member: #R02-V-F1b.

### R02-V-F1b: a 302 or 307 reply stored no answer row
**What broke:** `src/casefile/model.py:18` (`NoRedirect.redirect_request`), `:50`, `:54` refused redirects
without `raw`.
**Why:** same class as #R02-V-F1; the redirect paths were written (G33) before OR-8 made "any status" explicit.
**Caught by:** verifier 2 through the real opener on a loopback socket (`real_opener status=302 answers=[]`).
**Countermeasure:** body as `raw` on all three paths; one test per path, each seeded red alone.
**Status:** fixed (695b97b), extra fix cycle (Q32).

### R02-CX-7: a bad byte in matter.toml gave a traceback, exit 1
**What broke:** `src/casefile/matter.py`: `UnicodeDecodeError` escaped; D25 wants exit 2.
**Why:** the except listed OSError and TOMLDecodeError; `tomllib.load` raises UnicodeDecodeError on bad bytes.
**Caught by:** 8a Codex review; chair repro (0xff).
**Countermeasure:** UnicodeDecodeError added to the refusal; test_refusals case 12.
**Status:** fixed (408991c).

### R02-CH-1: zero token counts passed the counts gate untested
**What broke:** `src/casefile/benchrun.py:43`: seed `c > 0` -> `c >= 0` stayed green.
**Why:** a gate tested at None but not at its boundary.
**Caught by:** chair seed after the build.
**Countermeasure:** test_benchrun_zero_counts.
**Status:** fixed (9c82349).

### R02-OC-H1: the answer key missed a conflict and three facts that are on the pages
**What broke:** `tests/fixtures/matters/9001.001/key.json`: radiculopathy conflict MED0007/DEF0002 and facts
at MED0008, DEF0003, MED0003 absent; a correct model would score flags_extra and fail.
**Why:** a key validated by the loader (every quote on its page) but never read for completeness.
**Caught by:** 8b output critic (H1, H2); chair verified on the pages.
**Countermeasure:** G6, F27 to F29; ideal and flawed updated; bench prints detail lines (M1).
**Status:** fixed (6c1968c, d007821). Key completeness rule: owner question 26.

### R02-P-1: process notes
- The chair committed a copied review record with em dashes without running the gate (Mistakes Log).
- One chair seed did not apply (`raw` positional); caught by `cmp -s` before it counted.
- Gemma hygiene (dropped `from exc`, whitespace, unused imports, prompt text in comments): Fable review;
  `from exc` fixed (365f1e0), the rest carried (OR-5).
- R2-CX-2 (prompt truncation not detectable): deferred to stage 4 (OR-4).

## Round 3 (2026-10-27; stage 3 intake and OCR)

### R03-PC-1: a tool that exits 0 did not do the work (plan review items 3, 4, 16)
**What broke:** in the plan (no code yet): ocrmypdf 17.13.0 catches a per-page Tesseract timeout, writes
`[skipped page]` and exits 0 (`tesseract.py:402`); in redo mode it masks the digital text before OCR
(`_pipeline.py:788`), so a mixed page's stamp is missing from the sidecar and skipped pages can collapse
into one placeholder (`:1553`); the doctor smoke input already held the answer, so a tool that copies input
to output passed.
**Why:** the tool's success was read as proof of the work, one level above the unit (page) that matters
(same class as #R01-CX-9, a check claiming more than it ran).
**Caught by:** 8a Codex plan review of the round brief, before any code.
**Countermeasure:** per-page outcomes (ok, empty, failed with `ocr timeout`), page text from the PDF with
the sidecar only a fallback checked against the page count, image-only doctor smoke that must produce a
text layer (`doctor ocr PASS smoke=ok`); no-op tool seed.
**Status:** fixed in the revised brief (09518c4), built in c8bff68. Closes R1-19 (verifier ticked R3-2).

### R03-PC-2: weak oracles for text and fixtures (plan review items 14, 15)
**What broke:** in the plan: a `difflib` ratio over 0.95 passes a page with one digit changed (0.99 on 100
characters) or a dropped negation; the fixture `--check` compared page count, layer presence and image
size, and Pillow stamps the current date into the PDF.
**Why:** an oracle measured by closeness cannot see the one-character errors that matter in medical text.
**Caught by:** 8a Codex plan review.
**Countermeasure:** exact stamp and must-contain phrases beside the ratio (`must_ok=5 of 5`), critical-text
corruption seeds, `--check` compares regenerated content.
**Status:** fixed in the revised brief (09518c4). A text-layer change on page 5 is still untested: #R03-V-S1.

### R03-PC-3: brief premises not checked against the code, the interpreter or the owner (items 1, 2, 8 to 13, 17, 18)
**What broke:** in the plan: raw-only stamps against owner Q40 (raw plus normalised); the required example
`XKMR2344` is a valid match under `[A-Z]{1,8}[ -]?\d{4,}`; the "HTTPError with no stream" defect does not
exist on Python 3.12 (`error.py:45` supplies a BytesIO); duplicate-number refusal broke
`test_bench_multi.py`; three more tests (`test_benchscore_cite`, `test_config` field count,
`test_fix_cycle2` reason text) and two `RunResult` construction paths were missing; no exit-status contract;
G7 was an inferred contradiction.
**Why:** the brief was written from memory of the code and ran no premise before it was handed to lanes
(cousin of #R01-OC-M8, a fix instruction not checked against its source of truth).
**Caught by:** 8a Codex plan review (14 findings, 9 high or confirmed).
**Countermeasure:** Fable revision with each premise re-read in code; regression inventory by grep; Q40
folded in; exit statuses specified; G7 limited to what the pages say.
**Status:** fixed in the revised brief (09518c4).

### R03-CX-1: `records` or `pages` symlinked below a valid external matter (also plan item 7)
**What broke:** `src/casefile/intake.py:172`: matter 9002.001 with `pages` linked to 9002.002's `pages`
passed preflight; 7 files of client text were written into the other matter (exit 1).
**Why:** a descendant alias of the protected thing, the #R01-V-B1b class: the root was checked, its children
were not.
**Caught by:** 8a Codex review; chair run; the plan review had predicted it (item 7).
**Countermeasure:** `records` and `pages` must not be links (dangling too), exit 2, nothing written; six tests.
**Status:** fixed (4d615be).

### R03-CX-2: cleanup and rollback did not own what they touched (CX-2, CX-3, plan item 6)
**What broke:** `intake.py:264`: a second intake's `mkdir` failed and its `finally` removed the first
intake's two `.tmp` folders; `intake.py:153`: `_publish` rolled back only on `OSError`, so a
`KeyboardInterrupt` after the first rename left `records/<binder>` with no `pages/<binder>` and re-intake
refused. The plan also guarded `pages/<binder>` but wrote and deleted `records/<binder>`.
**Why:** cleanup keyed to a predictable name instead of to what this run created; the guard and the
rollback covered different folders.
**Caught by:** 8a Codex review; chair traces.
**Countermeasure:** only folders this run created are removed; rollback on BaseException; refusal names
every existing folder; seeds `except OSError` and "remove both" red.
**Status:** fixed (4d615be). Open: a signal between `mkdir` and `created.append` leaks one folder (carried).

### R03-CX-3: OCR process group and signal cleanup covered one phase only (CX-5, CX-6, plan item 5)
**What broke:** `intake.py:109`: a detached OCR child survived a normal return (exit 0 or 7) in its own
process group; `intake.py:111`: handlers were restored after `communicate`, so SIGTERM during page
extraction or JSON writing skipped `finally` and left both `.tmp` folders.
**Why:** the interrupt rule of #R01R-OC-F1 was applied to the subprocess phase, not to the whole run, and
group cleanup ran only on the timeout path.
**Caught by:** 8a Codex review; chair traces.
**Countermeasure:** the group is killed after every return; whole-intake handlers, exit 143, no `.tmp`.
**Status:** fixed (4d615be).

### R03-CX-4: a received reply was classed as no reply (CX-4, plan item 9)
**What broke:** `src/casefile/model.py:21`: the redirect handler read the body before `_request` set
`received=True`; a stalled or truncated 302 body gave no answer row and bench exit 2. `IncompleteRead`
escaped both handlers.
**Why:** the state flag was set after the step that can fail; the same "every received reply is a row"
class as #R02-V-F1 and #R02-V-F1b, a fourth path.
**Caught by:** 8a Codex review and plan review; chair trace.
**Countermeasure:** `ModelError.received`, `HTTPException` handled, loopback tests for stall and truncation.
**Status:** fixed (4d615be).

### R03-CX-5: a stamp match was recorded from inside a longer token (CX-7, H1, plan item 2)
**What broke:** `src/casefile/stamps.py:20`: `MED0001A` and `MED0001B` both gave `MED0001`; after the first
fix `Claim Number: QRL-2025-0418` still gave the stamp `QRL-2025` (critic H1), three pages of the bench
matter would share a false stamp, and the exit test could not see it.
**Why:** a boundary applied at one end and for one join character; the fix went one case at a time
(letters, then `-./`, upper case, then any case).
**Caught by:** 8a Codex review (CX-7), then 8b output critic (H1) after fix cycle 1; the chair's CX-7
ruling is pending owner veto.
**Countermeasure:** no letter or digit and no `-./` plus letter or digit on either side; cases
`QRL-2025-0418`, `MED0001-A`, `MED0001.2`, `xMED0001`, `AB-MED0001`, `MED0001A` give nothing, and
`MED 0001 Page 3`, `(MED0001)`, `Ends MED0001.` still match; three seeds red.
**Status:** fixed (4d615be, ab507e1). Suffix forms are owner question 38.

### R03-CX-6: the OCR failure test asserted nothing when it should (CX-8)
**What broke:** `tests/test_doctor.py:246`: `assert code == (0 if want_ok else 1) or not want_ok` is true
whenever `want_ok` is false; the doctor could return 0 on OCR FAIL.
**Why:** an exit-code assertion with a vacuous escape clause (#R01-CX-11 with a tautology added).
**Caught by:** 8a Codex review; chair read.
**Countermeasure:** exit 1 asserted in every OCR failure case; seed "doctor returns 0 on OCR FAIL" red.
**Status:** fixed (4d615be).

### R03-OC-M1: key flag G9 did not say what the conflict is
**What broke:** `tests/fixtures/matters/9001.001/key.json` (and `ideal.json`, `flawed.json`) flag G9 `about`
set "degenerative" against a protrusion and omitted the real disagreement (DEF0002 says the L4-L5 changes
are degenerative; MED0006 places degenerative disease at L5-S1). Plan item 18 had already warned that G7
could be an inferred contradiction.
**Why:** a key entry never read against both pages by a person (#R02-OC-H1 again).
**Caught by:** 8b output critic; the verifier read G7 to G9 against the pages and found them true.
**Countermeasure:** about names the L5-S1 finding; test reads the about against the pages; seed key at HEAD red.
**Status:** fixed (ab507e1).

### R03-OC-L1: refusal and open-item messages were incomplete (L1 to L4)
**What broke:** re-intake refusal named one folder, so removing it gave a second refusal; the binder rule
was shown as `[a-z][a-z0-9-]{0,39}`; a non-PDF leaked pypdf warnings and a missing file was called an
unreadable PDF; an empty page record held `"reason": ""`.
**Why:** messages written for the author, not for the attorney who must act on them.
**Caught by:** 8b output critic.
**Countermeasure:** every existing folder named with "remove the old binder by hand"; binder rule in
words; `file not found: <path>`, pypdf logger silenced; reason `no text after OCR`; seeds red.
**Status:** fixed (ab507e1).

### R03-OC-L5: a second spelling of one stamp is dropped; the sidecar is not the binder text (L5, L6)
**What broke:** `MED 0001` and `MED-0001` on one page keep only the first raw form; `records/scan/sidecar.txt`
has nothing for page 5 and omits page 6's digital stamp.
**Why:** dedup by normalised form discards the raw text Q40 says to keep; the sidecar is a working file
read as the binder text.
**Caught by:** 8b output critic.
**Countermeasure:** none yet; owner questions 38 to 41 (suffixes, where the stamp sits, two spellings,
lowercase binder names).
**Status:** open, owner questions 38 to 41; the sidecar is a working file and the page records are complete.

### R03-V-S1: three seeds stayed green (S1, S2, S5)
**What broke:** `intake.py:306` page record `matter` set to the file stem: `358 passed`; `intake.py:85`
`!= pages` to `< pages` (extra sidecar segments): `358 passed`; `make_scanned.py:171` `--check` comparing
pixels only: `358 passed`.
**Why:** a field, a direction and a layer nobody asserted (the #R01-V-B2 class, branches without their own
test). None of the builders' seeds touched them.
**Caught by:** 8c blind verifier (seeded copies, restored by `cmp`); seeds S3, S4, S6 and N2 to N5 went red.
**Countermeasure:** carried: add `matter` and `page` to the `id` verdict of `tests/test_stage3_exit.py:42`,
a `7 of 6` sidecar case, a page 5 text-layer change expecting `check page 5 differs`.
**Status:** open, carried to a fix worker (non-blocking).

### R03-V-L1: a duplicate matter number is refused late; `normalize` is narrow; step comments remain
**What broke:** `bench.py:64` to `79`: the duplicate is found at the second root, after the first matter
ran (model call, run log rows, bench line printed), then exit 2; `stamps.py:14` `normalize` strips only
space and hyphen, and `config.py:124` compiles the pattern with a different wrapper than `stamps.py:23`;
`# Main Loop` and `# Process facts` style comments remain in `bench.py` and `benchcandidate.py`.
**Why:** a check placed after the work it should prevent; a normaliser narrower than the patterns
configuration allows.
**Caught by:** 8c blind verifier.
**Countermeasure:** none yet.
**Status:** open, listed in Open items.

### R03-P-1: process notes
- The Codex plan review (8a, before code) found 14 items; 9 shaped the design, which is cheaper than the
  same findings after the code.
- Owner question 38 still says `MED0001-A` records `MED0001`; after H1 it records nothing. Stale text.
- Suite wall time 63 s (fix cycle 1), 66.93 s (merge), 72.67 s (tip) against the 90 s budget (T-11);
  one run was 87 s.

## Round 4 (2026-10-27 to 2026-10-28; stage 4 model client and gates)

### R04-PC-1: counts and a returned nonce did not prove the page-bearing prompt survived
**What broke:** `src/casefile/model.py:99` (pre-build), brief decision 1.1: acceptable counts and an echoed
nonce could survive loss of the pages, especially when retry history held the previous answer; `ceil(chars/2)`
was an estimate, not a token ceiling.
**Why:** evidence of one retained marker was treated as evidence of the entire input.
**Caught by:** Astra plan review item 1; accepted in brief §8 item 1.
**Countermeasure:** D31: UTF-8 byte ceiling plus template allowance before each call, `truncate: false`,
one nonce at the prompt front, boundary IDs, and a fresh two-message retry without the previous answer;
counts stored but never trusted as proof of reading; isolated cut-prompt and retry-budget probes.
**Status:** built by W1/W4/W7; R4-2 verified on aa11799, closing R2-CX-2 / OR-4; D31 pending veto.

### R04-PC-4: recording lookup and live nonce-bearing requests had different canonical forms
**What broke:** `tests/fakemodel/core.py:32,102` (pre-build): removing the request's first nonce line did
not match the recording's literal `__PROMPT_ID__`, repeated nonce values or four-message retries; good calls
would get 404 before reaching the intended gate.
**Why:** the producer and consumer of a lookup key applied different canonicalisation contracts.
**Caught by:** Astra plan review item 4; accepted in brief §8 item 4.
**Countermeasure:** D36: one nonce occurrence, symmetric placeholder substitution, two-message retries,
and removal of the retry line while retaining its flag; W4 tests live nonces and retry lookup.
**Status:** fixed in the revised brief and built by W4; stage 4 and retry_ok reproduced by the verifier.

### R04-PC-6: empty extraction and placeholder records could clear coverage
**What broke:** `src/casefile/benchcandidate.py:40` (plan premise) accepted empty lists; the proposed gates
could mark the whole chunk read. Later `src/casefile/gates.py:223` accepted a nonempty flags list whose
only entry had blank `about`, marking its cite read without an extracted statement (code review CX-5).
**Why:** structural presence was mistaken for substantive extraction and evidence of per-page reading.
**Caught by:** Astra plan review item 6; chair reproduced Astra code review CX-5.
**Countermeasure:** D38: reject no facts and no flags; fix cycle 1 also rejects blank fact text or quote,
blank flag about and empty flag cites; passing answers mark only cited pages read and keep uncited pages open.
**Status:** built by W3/W4/W7 and fixed in cycle 1; eight blank-record tests seeded red; owner question 47 held.

### R04-PC-7: verified quotations were presented as verification of unsupported summaries and references
**What broke:** `src/casefile/benchscore.py:76,108` (pre-build): a real quote of pain 7/10 could accompany
summary text saying 0/10; proposed flag cites had no quote pair and escaped reference checking altogether.
**Why:** validation of one evidence field was allowed to confer trust on related fields it never checked.
**Caught by:** Astra plan review item 7; accepted in brief §8 item 7.
**Countermeasure:** D38 checks every fact cite and flag cite against the chunk and every summary digit run
against its quote; W4 isolates each fault; the quote alone is verified and summary wording remains the model's reading.
**Status:** built and verified; owner question 48 held; citation digits require the separate ruling in #R04-V-2.

### R04-PC-9: unstamped records produced no warning when prose had no bracketed cite
**What broke:** `src/casefile/rules.py:75` and `playbook/rules.toml:56`: setting `stamped=False` only changed
the severity of matched bracketed cites; the planned unstamped probe had no match and yielded zero warnings.
**Why:** a warning required by missing metadata depended on a text match that need not exist.
**Caught by:** Astra plan review item 9; accepted in brief §8 item 9.
**Countermeasure:** gate 5 emits its own warning naming every unstamped page; rule findings retain their
warning severity; W7 seed dropping the pipeline warning fails `warning=1`.
**Status:** built and verified; the missing mixed-chunk severity test is carried under #R01-V-B2 below.

### R04-PC-11: truncation checks blocked punctuation repairs before the repair gate
**What broke:** `docs/loop/round-04/round04-build-brief.md:880` records the original strict opening-ID
check rejecting a fenced answer before fence repair. Later `src/casefile/gates.py:127` rejected
`"end_id":"<nonce>",}` although trailing-comma repair was explicitly permitted (CX-6).
**Why:** independently specified gates disagreed on the intermediate forms their composition must accept.
**Caught by:** Astra plan review item 11; chair reproduced Astra code review CX-6.
**Countermeasure:** gate 1 inspects IDs after pure `unfence`; gate 2 logs fence repair; the end-ID check
admits one trailing comma before closers; an integration test proves that form reaches repair and passes.
**Status:** plan corrected and cycle 1 fixed; the tail-comma test failed on the original guard, then passed.

### R04-CX-1: a nonunique stamp was used as page identity
**What broke:** `src/casefile/gates.py:74` (reviewed revision): two pages whose first stamp was MED0001
collapsed into one coverage key, and citing only the first marked both read.
**Why:** a potentially shared citation label was used as the unique identity of a record.
**Caught by:** Astra code review CX-1; chair reproduced `ids=['MED0001', 'MED0001'] read_both=True`.
**Countermeasure:** coverage uses `page.page_id`; lookup refuses a normalised stamp matching multiple
pages; fix cycle 1 tests both ambiguity and distinct coverage keys, with the original lookup seeded red.
**Status:** fixed in cycle 1; verifier reproduced page-ID coverage on aa11799.

### R04-CX-3: OCR folding manufactured a number by joining a numeric hyphen
**What broke:** `src/casefile/quotes.py:31` (reviewed revision): `Dose 1-\n2 mg.` matched `Dose 12 mg.`
at the OCR rung, and the manufactured number also passed the summary digit check.
**Why:** a word-repair transformation erased punctuation that carries numeric meaning.
**Caught by:** Astra code review CX-3; chair reproduced the OCR hit.
**Countermeasure:** join a line-break hyphen only between letters, in both matching and `same`; six
numeric punctuation tests fail under the original join, alongside the existing changed-digit rejects.
**Status:** fixed in cycle 1; numeric ranges and minus signs preserved.

### R04-CX-7: duplicate JSON keys silently discarded earlier extracted facts
**What broke:** `src/casefile/jsonrepair.py:76` (reviewed revision): two `facts` keys parsed with no repair
or error, retaining only the second list; downstream gates passed and coverage cleared.
**Why:** ordinary dictionary decoding discarded duplicate input before validation could see the loss.
**Caught by:** Astra code review CX-7; chair reproduced `repairs=() parsed_facts=[{'x': 2}]`.
**Countermeasure:** shared `object_pairs_hook` rejects duplicate keys at every depth; both pipeline parses
and schema, candidate, key and model-envelope loaders use it; adjacent loader probes first failed to refuse.
**Status:** fixed in cycle 1; original-parser controls went red before the corrected tests passed.

### R04-CX-9: Python equality conflated nested JSON booleans and numbers
**What broke:** `src/casefile/schema.py:80` (reviewed revision): enum `[[true]]` accepted `[1]` under an
integer-array schema because Python considers `[True] == [1]`.
**Why:** host-language equality was substituted for the data format's recursive type-aware equality.
**Caught by:** Astra code review CX-9; chair reproduced `errors_for_[1]=[]`.
**Countermeasure:** deep JSON equality distinguishes booleans from numbers inside arrays and objects;
four enum tests fail when the original comparison is restored.
**Status:** fixed in cycle 1; verifier also seeded the adjacent boolean-as-number type check red.

### R04-OC-1: a same-size mutation executed stale bytecode
**What broke:** `.workflow/scratch/round04-fix2.md:22`: a same-size mutation exposed stale Python bytecode
during cycle 2 controls, so changing the source alone did not establish which code a probe executed.
**Why:** cached executable artifacts could outlive a source mutation and invalidate its verdict.
**Caught by:** the fix worker while addressing the output critic; the verifier explicitly excluded the
same risk with a fresh `PYTHONPYCACHEPREFIX` for its green seed 7.
**Countermeasure:** clear generated caches or use an isolated bytecode prefix for mutation reruns,
alongside `cmp` checks that the seed applied and restoration is byte-identical.
**Status:** cycle 2 controls clear caches; the verifier's mixed-chunk green result survived cache isolation.

### R04-V-2: citation identifiers were treated as unsupported medical numbers
**What broke:** `src/casefile/gates.py:128` to `131`: summary text holding `[cite MED0001]` fails when
its quote has no `0001`; the verifier reproduced the same fault with `[cite mixed/002]` and the playbook's
good `[cite ABC0001]` example.
**Why:** a numeric evidence check scanned reference syntax and factual prose as one semantic domain.
**Caught by:** blind verifier, design call 1; non-blocking at stage 4 because extraction text has no bracketed cites.
**Countermeasure:** rule with R1-20 before any stage writes cited prose: either exclude cite spans from
the digit check or keep cites outside summary text, then test the chosen contract with a real bracketed cite.
**Status:** open, deferred; separate from T-19's date-formatting issue, although the close ledger groups them.

### R04-CH-1: quote tests could not detect searching the wrong page
**What broke:** `src/casefile/gates.py:105` (chair seed): checking a quote against the whole chunk instead
of its cited page left both gate suites green (`28 passed`).
**Why:** tests proved that evidence existed somewhere but did not prove its association with the named source.
**Caught by:** chair seed after the build, recorded in the code review reproduction table and ledger.
**Countermeasure:** `test_ch1_quote_must_be_on_cited_page` supplies a quote present only on another page;
the whole-chunk seed must fail `CH-1: quote from another page accepted`.
**Status:** fixed in cycle 1; original scoped lookup retained and the missing relational test added.

Round 4 repeats and dispositions (no duplicate entries or pre-flight bullets):

- Plan items 2, 8, 12 and 14, and W0/W3 seed-count discrepancies and W4/W7's four-versus-five faults:
  #R03-PC-3 (premises and regression callers), with #R01-OC-M8 for the Q44 boundary; corrected before acceptance.
- Plan item 3: #R02-CX-5, key equivalence must follow scorer equivalence; W5 built folded collision refusal.
- Plan item 5 and item 10: #R01-CX-10 and #R02-CH-1, probes must reach and isolate the intended guard;
  `unrepairable`, `length_only` and isolated count edits built. Item 13's weak controls share #R01-CX-10
  (a second change can mask the intended seed) and #R03-PC-3 (timestamps and complete deployed v1 schema).
- Plan item 15: #R03-V-L1, assert no run-log creation before refusal; W5's file assertion catches moving
  only `open_db`. Item 16: #R01-CX-11, timing verdict must affect the exit code; W6 built `suite_time.sh`.
- CX-2: #R03-CX-5, token boundaries at both ends, now applied to every quote rung and `found_in`.
  CX-5 and CX-6 are the later instances documented in #R04-PC-6 and #R04-PC-11 above.
- CX-8 and the cycle 2 doctor losing received error replies: #R02-V-F1, every received reply must be stored;
  decoder `ValueError` and `RecursionError` now become logged, retried gate-2 failures; doctor retains raw replies.
- CX-4 is not a real reproduced finding: the chair saw triggers restored from 19 to 21 on reopen through
  `open_db`; no fix and no new failure entry.
- Critic H1, H2, M2, M3, M4, L1, L2 and L3: #R03-OC-L1, readable and actionable output. Cycle 2 fixed
  H1/H2/M3/M4/L1/L2; M2 and L3 remain below. M1 also repeats #R01-CX-9 (claim only the search actually run);
  cycle 2 names the cited page and lists chunk pages only for cite faults. L4 is owner question 49, interim rule id kept.
- Verifier seed 7 / low L1: #R01-V-B2 (a branch without its own test), also #R03-V-S1. `gates.py:241`
  `stamped=all(...)` seeded to `any(...)` left `537 passed`, including with isolated bytecode; the mixed-chunk
  severity test remains open. The brief rules mixed chunks but the spec/as-built wording needs reconciliation.

## Round 5 (2026-10-28; stage 5 case file, merge and medical memo)

Plan and code IDs use the findings' order in each report (High, Medium, Low); gaps are repeats or dispositions
listed below. Records checked: every round 5 report, brief §8, W0 to W8 including W3b and W5b, both fix reports,
and the ledger's Round 5 section. Fixed statuses below report that evidence, not new code work at this close.

### R05-PC-1: incremental chunks cannot see relationships outside their input
**What broke:** `src/casefile/gates.py:96-99` and brief §1.4: lookup sees only the current chunk and only unread
pages are sent; a later defense report cannot conflict with an earlier medical page, and three chunks find only
5 of 9 fixture flags even within one run.
**Why:** independent extraction batches were treated as sufficient context for relationships spanning batches.
**Caught by:** plan review H1; chair's W3 measurement; output critic's later DEF0001 weight disagreement.
**Countermeasure:** memo states that conflicts and gaps are checked only between pages sent together and counts
runs that read pages; Q56 holds re-sending context, T-22 measures losses before a reconciliation pass is designed.
**Status:** open limit, disclosed and verified; no cross-chunk or cross-run reconciliation built.

### R05-PC-7: a torn append could make a matter permanently unreadable
**What broke:** `docs/loop/round-05/round05-build-brief.md:252-258` specifies the revised recovery contract;
the original append-mode-only design had no recovery from a crash midway through the last JSON object.
**Why:** append-only storage was specified without distinguishing a completed record from an interrupted write.
**Caught by:** plan review M5, accepted in brief §8.
**Countermeasure:** load reports and ignores an incomplete final object, append truncates only that torn tail
before writing and fsyncs; complete records without a final newline survive; interior corruption refuses.
**Status:** built by W4; torn-tail load, recovery and cut-middle controls all red under their separate seeds.

### R05-PC-8: an injected test transport hid an unsafe live-service default
**What broke:** `tests/conftest.py:41` defaulted to the owner's Ollama on port 11434; dropping one forwarded
`opener` parameter could send fixture pages to that service before the test failed.
**Why:** test isolation depended on perfect dependency injection while the fallback addressed a live service.
**Caught by:** plan review M6; brief §8 confirms the default and its callers, with no observed suite request.
**Countermeasure:** default test host is port 9; live tests name a stand-in port they opened; grep checks remaining
11434 references and W7's omitted-opener seed fails without reaching the owner's server.
**Status:** preventive fix built by W0/W7; verifier checked references; round report records request delta 0.

### R05-PC-12: a singular renderer would discard accumulated flag readings
**What broke:** `docs/loop/round-05/round05-brief-review.md:119-121` identifies W5's single reading paragraph
for a flag whose identity allows multiple `about` versions, including two gaps on the same page.
**Why:** a display contract assumed one value where the merge contract accumulates several versions.
**Caught by:** plan review L2, accepted in brief §8.
**Countermeasure:** one labelled paragraph per `about`, in case-file order; W5 includes a two-about gap and a seed
that renders only the first reading.
**Status:** built by W5b; check 7 red under the first-about-only seed, rechecked in fix cycle 2.

### R05-PC-17: a job test would mutate the shared session fixture
**What broke:** `tests/conftest.py:131-144` provides session-scoped `scanned_intake`; W7 originally planned to write
`casefile.jsonl` and `outputs/` into that same matter, which other intake tests read.
**Why:** mutable test output shared the lifetime and location of an input fixture used by other tests.
**Caught by:** plan review L7, accepted in brief §8.
**Countermeasure:** copy the invented matter under the test's own configured matters root before running the job;
assert that the shared fixture still contains only `records` and `pages`.
**Status:** built and checked by W7; no cross-test writes to the session fixture.

### R05-CX-2: coverage committed before facts could suppress every recovery read
**What broke:** `src/casefile/gates.py:312-317` committed `read` before `memo_job.py:49-51` appended facts;
an append failure left pages permanently skipped while a later empty memo could exit 0.
**Why:** success in one persistent store was treated as proof that the dependent write to another had committed.
**Caught by:** code review H2; chair reproduced by tracing the write order.
**Countermeasure:** count a page read only when its latest memo coverage row joins a case-file `run` event;
probe append access before the model call, inject a post-coverage append failure, and assert the next run re-sends.
**Status:** fixed in cycle 1, including status; both missing-join and late-probe seeds red. Deleting complete
tail events also reopens affected pages through this join; an edited last payload remains #R05-CX-6.

### R05-CX-3: facts vanished when their original page left the current page set
**What broke:** `src/casefile/memo.py:98-102` placed a fact only under `page_ids[0]`; after a binder rename or
removal, the case file and status counted the fact while the memo silently omitted it.
**Why:** rendering was driven only by current source headings with no total placement rule for retained records.
**Caught by:** code review M1; chair reproduced a fact with an absent first page and a present later cite.
**Countermeasure:** use the first present cited page, place facts with no present page under `Facts on pages not
in this matter`, and assert that rendered fact counts agree with the case file.
**Status:** fixed in cycle 1; original-first-page placement seed red; D41 amended at close.

### R05-CX-4: concurrent writers allocated the same fact identity from a stale base
**What broke:** `src/casefile/facts.py:237-239,202` allocated IDs before append re-read the chain; two writers
kept valid sequence links but both appended F1, and `CaseFile.facts` retained only the second fact.
**Why:** serialization of individual appends did not serialize the read, identity allocation and merge transaction.
**Caught by:** code review M2; chair reproduced duplicate IDs and loss from the view, with the concurrent trigger plausible.
**Countermeasure:** exclusive matter `flock` around load, merge and append; load refuses repeated fact and flag IDs
(also #R02-CX-5's collision guard); tests remove or share the lock and separately disable each duplicate-ID guard.
**Status:** fixed in cycle 1; lock and duplicate-ID seeds red; low-level append documents caller serialization.

### R05-CX-5: merged readings lost the page that supplied their meaning
**What broke:** `src/casefile/facts.py:56,258-259` stored readings as fact, text and run only;
`memo.py:109-110` showed a MED0007 reflex reading under MED0001's gait heading because both quoted `Normal.`.
**Why:** deduplication of shared evidence erased the source association of distinct interpretations.
**Caught by:** code review M3; chair reproduced; verifier independently attacked render and merge provenance.
**Countermeasure:** every reading carries `page_id`, dedupe by text plus page, and name another page in its label;
test identical reading wording on two pages as well as different readings (source-association tests: #R04-CH-1).
**Status:** fixed in cycle 1; old readings without a page refuse; verifier seeds 1 and 2 both red.

### R05-CX-6: a predecessor hash cannot authenticate the chain's final payload
**What broke:** `src/casefile/facts.py:171` in the reviewed revision checked only each line's predecessor;
editing the last payload or deleting complete trailing lines still loaded clean despite the original refusal claim.
**Why:** a chain with no independently anchored head cannot prove the integrity or completeness of its own tail.
**Caught by:** code review M4; chair reproduced both an edited last payload and a shortened complete chain.
**Countermeasure:** narrow the integrity claim; #R05-CX-2's committed-run join recovers missing tail runs;
an independent stored head hash and sequence plus explicit final-payload tests are needed to detect tail edits.
**Status:** open recorded limit: an edited last line still loads clean; no head anchor added this round.

### R05-CX-7: citation aliases satisfied a relationship that required distinct pages
**What broke:** `src/casefile/facts.py:263,267` deduped page IDs separately from cites, while gate 4 accepted
`MED0001` and `MED 0001` as the two sides of a one-page conflict.
**Why:** relationship cardinality was counted before resolving aliases to distinct entities.
**Caught by:** code review L1; chair reproduced a single-page conflict with duplicate stamp labels.
**Countermeasure:** gate 4 requires two distinct resolved pages for a conflict; dedupe flag cites and page IDs
together, preserving their pairing and order.
**Status:** fixed in cycle 1; missing distinct-page guard and unpaired cite-dedup seeds each red.

### R05-CX-9: intake and output validation define stamps independently
**What broke:** `playbook/rules.toml:57` requires at least four digits while `src/casefile/config.py:28` allows
an owner-configured `stamp_pattern`; a three-digit stamp can be intaken but its memo cite would fail the playbook.
**Why:** two configurable authorities describe the same identifier without a compatibility contract.
**Caught by:** code review L3; chair classified it plausible only because the current defaults agree.
**Countermeasure:** share a canonical stamp definition or refuse incompatible intake and playbook definitions
before processing; test a configured three-digit stamp through intake and memo validation.
**Status:** open for stage 6; no code change and no end-to-end reproduction with divergent config this round.

### R05-OC-1: a replacement memo reported the previous memo's staleness as its own
**What broke:** `src/casefile/memo.py:95` read stale outputs before `memo_job.py:70` appended the replacement's
output event; run 3's fresh memo said `memo` was stale while status immediately said `memo:current`.
**Why:** an output's self-description was computed from its predecessor's state before publication.
**Caught by:** output critic M1; chair traced the order; the original exit test had pinned the wrong answer.
**Countermeasure:** omit the memo being rebuilt from its own stale list, preserve other stale outputs, and reopen
the produced memo to compare its stale section with status after publication.
**Status:** fixed in cycle 2; include-self seed red; stage 5 pin changed to `none`; verifier read the corrected memo.

### R05-OC-3: event-kind counts understated the semantic content added
**What broke:** `src/casefile/memo.py:89` in the critic's revision counted only `reading` events, so a new
fact brought a visible model-reading paragraph while What changed said `0 readings added`.
**Why:** a semantic change count was equated with one event kind even though another event embeds the same content.
**Caught by:** output critic L1; chair reproduced the change line.
**Countermeasure:** count initial readings in new fact events plus later reading events, count new flag readings,
and test the exact reopened change paragraph; plural handling shares #R03-OC-L1.
**Status:** fixed in cycle 2; omit-initial-reading seed red; verifier confirmed the revised output.

### R05-V-1: a transport error carried memo-specific consequences into every caller
**What broke:** `src/casefile/model.py:57-58` says the page stays open even in `doctor`, where no page is
involved; `memo_job.py:99` adds a second no-reply prefix around that same reason.
**Why:** shared transport errors included workflow context that only the calling command could truthfully supply.
**Caught by:** blind verifier L1; W3b's doctor assertion had been re-pinned to the misleading page clause.
**Countermeasure:** keep the shared no-reply reason transport-only, add the page consequence in gates, and add
each command's context once; re-pin doctor and memo assertions against their own command semantics.
**Status:** open, carried to round 6; plain wording alone (#R03-OC-L1) did not prevent this caller-context leak.

### R05-V-2: accepted output rulings were missing from the canonical decision row
**What broke:** `docs/spec.md:258` (D41 before the close amendment) omitted page placeholders, the unstamped
warning and the absent-page facts section introduced by the code-review rulings and fixes.
**Why:** implementation decisions accumulated during fixes without reconciliation into the canonical specification.
**Caught by:** blind verifier L2; round 5 report records the close amendment.
**Countermeasure:** reconcile every accepted review and fix ruling against spec §9 at close, including visible
wording and sections, with each omission either recorded as a decision or explicitly deferred.
**Status:** closed by the chair's D41 amendment, present in the current spec; pending owner veto.

Round 5 repeats and dispositions (no duplicate entries or pre-flight bullets):

- Plan H2: #R02-V-F1 and #R02-V-F1b; W3 migrated all nine runner-level reply-storage probes before deleting
  the old runner tests. Plan M2: #R03-PC-3, every consumer of the changed capture contract must migrate;
  `cite_body` now handles alternation in both rules and gates. M3 repeats #R01-CX-7/#R01-OC-H3's two-way prose tests.
- Plan M1, L4, L5, L8 and L10, plus W0/W1/W2/W3/W8 count and pin discrepancies: #R03-PC-3 (measured premises,
  callers and contracts), with #R02-CH-1 for the chunk boundary. W0's changed-card recording seed repeats
  #R01-CX-10: symmetric request and recording changes masked that oracle; the independent version pin did fail.
- Plan M4: #R04-CH-1, evidence must sit under its own source heading. L1 is the stated folded-quote identity
  consequence, not a new defect; L2 is #R05-PC-12. L3 repeats #R01-OC-M2 (job is now required).
- Plan M7 / Q55 / T-21 is a documented consequence of #R04-PC-6: a re-sent cover sheet with an empty answer
  costs two calls and turns failed; it stays open. M8 repeats #R03-V-L1: binder-rule refusal before any side effect,
  with the practice boundary held as Q57. L9 is Q54's ordering choice. L6 was rejected: ModelClient already sends num_ctx.
- Build W3's missing lane B dependency and W5's contradictory run count and missing inputs repeat #R03-PC-3;
  the chair merged the dependency first and ruled the run-count and interface contracts before rebuilding.
- W2's status and identity seeds initially survived masked probes; W5b's reason seed initially also checked quotes:
  #R01-CX-10, isolated and rerun red. W7's late binder check needed a database-file assertion, not just run rows:
  #R03-V-L1. Its overlapping development controls were rerun serially; no new class.
- Code H1: #R04-PC-11, extraction accepted a page-id cite that the stamped memo refused; cycle 1 canonicalises
  it to the page's first stamp at merge and tests rendering. Code L2: #R04-PC-6, an empty pages folder cannot
  justify success; cycle 1 refuses it. L5 repeats #R03-OC-L1; cycle 1 fixes the newline, duplicate excerpt and section.
- Code L4 is T-20 tuning: 8192 retry bytes are a guessed margin, not a bound; around 67 quote faults can exhaust
  it. #R04-PC-1 still requires checking the actual retry budget; measure the maximum reason before changing the margin.
- Critic M2, L2, L3 and L4 repeat #R03-OC-L1: explain unquoted pages and empty sections, use a reader-facing
  warning naming text pages, and capitalize headings; cycle 2 fixed them. L1's grammar shares that entry, while
  its missing initial-reading count is #R05-OC-3. L5 repeats the label-scope issue of #R01-OC-H2, held as Q58;
  `defense report` still appears under the interim, with no new rule. Owner questions 50 to 58 remain held.
- Chair seed R05-CH-1 repeats #R01-V-B2/#R03-V-S1: the last line's wrong seq had no isolated test, so dropping
  the guard stayed green. Cycle 1 added a final-line sequence case; the exact seed now fails
  `CH-1: wrong seq on last line accepted`. No new failure class or pre-flight bullet.
- Verifier seeds 1 to 5 all went red; no new test gap. L3's copied `.claude/.cc-writes` marker is harmless harness
  debris, recorded for the owner; no behavior failure or new class was demonstrated.

## Open items a future pass must not re-discover

- **Closed in round 5**: verifier L1 mixed-chunk test (#R01-V-B2, #R03-V-S1); verifier L2 citation digits
  (#R04-V-2) and R1-20 cite forms; critic M2 open items by stamp and L3 bench invented kinds and rule excerpts
  (#R03-OC-L1). R5-2/R5-3 independently verified with `gate_cases=31 of 31`, `cite_forms=11 of 11`,
  `invented_kinds=2 of 2 rule_excerpt_ok=1` and status's stamped open line.
- **Edited last case-file line loads clean** (#R05-CX-6, code M4): recorded integrity limit; no independent head
  anchor. Missing complete tail runs recover through #R05-CX-2; editing the last payload remains undetected.
- **Two stamp definitions** (#R05-CX-9, code L3): `rules.toml` bates_pattern versus config stamp_pattern;
  defaults agree, divergent owner configuration is not checked for compatibility. Stage 6, plausible risk.
- **No-reply wording in doctor and memo** (#R05-V-1, verifier L1): every reason says the page stays open even
  when no page is involved; memo repeats the no-reply words. Carry to round 6 and re-pin both command assertions.
- **Cross-chunk and cross-run conflicts not seen** (#R05-PC-1, Q56, T-22): only pages sent together can yield
  conflicts or gaps; three-chunk fixture finds 5 of 9 flags. Limit disclosed, reconciliation still unbuilt.
- **Owner questions 7 to 14** (`docs/loop/questions-for-owner.md`): interim rulings in force.
- **run.sh needs python3 on PATH** before `uv sync` on a fresh checkout (#R01-CX-4; owner question 16).
- **Closed in round 4**: R2-CX-2 / OR-4 (D31, R4-2; #R04-PC-1); verifier gaps S1, S2, S5
  (#R03-V-S1, R4-3); verifier lows (duplicate refusal before work, stamp normalisation and step comments,
  #R03-V-L1, R4-4); suite time T-11, now three-run PASS `max=57.46` against 90 s.
- **Owner questions 47, 48, 49**: uncited-page closure (#R04-PC-6), summary wording (#R04-PC-7), and rule
  IDs in output (#R03-OC-L1); interims stand, D31 to D38 pending veto.
- **Leftover capture folders** from killed test runs before 9f86d07 sit in the shared TMPDIR (invented text).
- **Closed in round 3**: R1-19 (the doctor's OCR smoke runs for real, D29; R3-2), the OR-5 lows, non-200
  HTTPError with no body stream, duplicate matter numbers, test gaps N2 to N5 (R3-5, R3-6, R3-7 ticked).
- **Owner questions 38 to 41**: stamp suffixes, stamp position, two spellings of one stamp, lowercase
  binder names (#R03-OC-L5). Answered at the round 3 close (ledger Q42).
- **Pending owner veto**: the stamp lookbehind case and the joined-token rule (CX-7, H1; #R03-CX-5).
- **Conflict excerpts for Claude review**: owner Q41, a later stage.
- **Intake leak**: a signal between `mkdir` and `created.append` leaks one `.tmp` folder (#R03-CX-2).
