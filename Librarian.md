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

## Open items a future pass must not re-discover

- **R1-19**: OCR smoke test on an invented fixture PDF: stage 3 (#R01-CX-9).
- **R1-20**: `bates-cites` sees only bracketed cites; "See page 12" passes: the stage that writes cited prose.
- **Owner questions 7 to 14** (`docs/loop/questions-for-owner.md`): interim rulings in force.
- **run.sh needs python3 on PATH** before `uv sync` on a fresh checkout (#R01-CX-4).
