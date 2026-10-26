# Round 1 Codex code review (8a), gpt-6.1-sol, read-only, high effort, 2026-10-26

1. **CX-1 | high | CONFIRMED** | [src/casefile/config.py:125](/Users/davidskoranski/legal-harness/src/casefile/config.py:125)  
   The matters guard checks against the config file’s directory instead of the checkout root.  
   **Scenario:** Load `/tmp/settings/config.toml` with `matters="/Users/davidskoranski/legal-harness/Cases"` -> validation succeeds, permitting client storage inside the repository.

2. **CX-2 | high | CONFIRMED** | [src/casefile/privacy.py:7](/Users/davidskoranski/legal-harness/src/casefile/privacy.py:7)  
   The privacy extension list omits image formats covered by the blanket prohibition.  
   **Scenario:** An untracked `docs/client-scan.webp`, `.gif` or `.bmp` -> no privacy finding; these extensions also lack `.gitignore` protection, allowing accidental commits.

3. **CX-3 | med | CONFIRMED** | [src/casefile/runlog.py:32](/Users/davidskoranski/legal-harness/src/casefile/runlog.py:32)  
   The append-only triggers permit replacement of existing records when recursive triggers are disabled, which `open_db` never explicitly enables.  
   **Scenario:** With `recursive_triggers=OFF`, execute `INSERT OR REPLACE` for an existing approval ID with a changed decision -> the original approval disappears without an append-only error. SQLite documents that these replacement deletions only fire delete triggers when recursive triggers are enabled. [SQLite documentation](https://www.sqlite.org/lang_conflict.html)

4. **CX-4 | med | CONFIRMED** | [scripts/run.sh:11](/Users/davidskoranski/legal-harness/scripts/run.sh:11)  
   The cap closes the output pipeline but does not terminate the child, so reaching the cap need not produce exit 97.  
   **Scenario:** A child writes 52,428,801 bytes and then sleeps without further writes -> the readers finish, but Bash waits for the child before reaching the cap verdict, potentially indefinitely.

5. **CX-5 | med | CONFIRMED** | [src/casefile/doctor.py:124](/Users/davidskoranski/legal-harness/src/casefile/doctor.py:124)  
   Doctor marks an answer successful without checking completion’s `done` flag or validating prompt/output token counts.  
   **Scenario:** Return `READY`, `done_reason="stop"`, `done=false`, and zero or missing counts, with `/api/ps` reporting the configured context -> context passes and an `ok` answer is stored despite no verified prompt consumption or completion.

6. **CX-6 | med | CONFIRMED** | [src/casefile/privacy.py:19](/Users/davidskoranski/legal-harness/src/casefile/privacy.py:19)  
   The privacy scan checks lexical filenames without identifying symlinks or their targets.  
   **Scenario:** A tracked or untracked `Cases` symlink points to an external client folder -> Git inventories the link as `Cases`; neither the `Cases/` prefix nor an extension matches, so the prohibited tree passes.

7. **CX-7 | med | CONFIRMED** | [playbook/rules.toml:21](/Users/davidskoranski/legal-harness/playbook/rules.toml:21)  
   The payment patterns miss ordinary statements identifying who paid the doctor.  
   **Scenario:** Check `The insurer paid Dr. Example.` -> no finding, because the payment regex requires `for`, `by` or `to` immediately after `paid`, and the other patterns do not match.

8. **CX-8 | med | CONFIRMED** | [playbook/rules.toml:8](/Users/davidskoranski/legal-harness/playbook/rules.toml:8)  
   The spelled-out Q16 prohibitions require literal single spaces and miss the same whole-word phrases across whitespace variations.  
   **Scenario:** Check `The independent medical\nexamination found normal motion.` -> no finding, allowing the forbidden examination label through after a line wrap.

9. **CX-9 | med | CONFIRMED** | [src/casefile/doctor.py:156](/Users/davidskoranski/legal-harness/src/casefile/doctor.py:156)  
   OCR can report PASS before stage 3 based solely on executable presence and Tesseract’s version exit code.  
   **Scenario:** Tesseract’s `--version` succeeds while the discoverable `ocrmypdf` executable always fails -> OCR reports PASS; `ocr_expected_fail()` mirrors this incomplete check, so the tests accept that verdict.

10. **CX-10 | med | CONFIRMED** | [tests/test_doctor.py:64](/Users/davidskoranski/legal-harness/tests/test_doctor.py:64)  
    The truncation probes change both the answer content and stop reason, allowing the READY equality guard to mask a broken completion guard.  
    **Scenario:** Remove `and answer.done_reason == "stop"` from doctor’s success expression -> the fake truncated answer remains `RE`, so the existing probes still fail with the expected reason; they never exercise `READY` with `done_reason="length"`.

11. **CX-11 | low | CONFIRMED** | [tests/test_doctor.py:67](/Users/davidskoranski/legal-harness/tests/test_doctor.py:67)  
    Context failure tests discard doctor’s return code and therefore do not verify that their verdict affects process status.  
    **Scenario:** Exclude context failures from exit-status aggregation -> truncated/short-context output assertions still pass, while doctor can exit 0 when OCR and the other checks pass.

Count: **2 high, 8 med, 1 low.**
## Chair reproduction (every finding is a hypothesis until reproduced)

| ID | Status | Evidence (chair run, 2026-10-26) |
|---|---|---|
| CX-1 | REPRODUCED | config at scratchpad `cfg/config.toml` with `matters=<repo>/Cases` -> `accepted matters /Users/.../legal-harness/Cases` |
| CX-2 | REPRODUCED | `.webp`, `.gif` absent from `privacy.SUFFIXES` |
| CX-3 | REPRODUCED | `recursive_triggers = 0`; `INSERT OR REPLACE` on approval id 1 -> `decision now rejected`, no abort |
| CX-4 | REPRODUCED | `run.sh bash -c 'head -c 52428801 /dev/zero; sleep 6'` -> `exit=97 secs=6` (waits on the child; a hung child hangs run.sh) |
| CX-5 | REPRODUCED (trace) | `model.py:76-82` never reads `done`; doctor.py:124 checks no token counts |
| CX-6 | REPRODUCED | temp repo with untracked symlink `Cases -> ext/` -> `scan=[]`, `paths=['Cases','ext/x']` |
| CX-7 | REPRODUCED | `rules.check("The insurer paid Dr. Example.")` -> no finding |
| CX-8 | REPRODUCED | `"independent medical\nexamination"` and double-space form -> no finding |
| CX-9 | REPRODUCED (trace) | doctor.py:149-158: PASS on `which` plus `tesseract --version` exit 0; ocrmypdf never run |
| CX-10 | REPRODUCED | SEED drop `and answer.done_reason == "stop"` (doctor.py:124) -> `tests/test_doctor.py` `15 passed`; restored by cmp |
| CX-11 | REPRODUCED (trace) | test_doctor.py:62-80 discard the doctor exit code |

Routing: all eleven to fix cycle 1 (Codex gpt-6.1-sol builder per Q22). CX-9's real OCR smoke test on a
fixture PDF is stage 3 work (Q11): cycle 1 makes the check honest (both tools run, reason names what ran);
the smoke test is carried to the stage 3 brief as R1-19.
