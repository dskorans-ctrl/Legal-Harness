**Do not build this brief unchanged.** Static review only: I did not modify files or run the model, app, tests, or `scripts/run.sh`. CONFIRMED findings are traced in current source; PLAUSIBLE findings concern proposed code that does not yet exist.

1. **High · CONFIRMED · W1/G1: the required baseline is wrong.**  
   [run.sh:18](/Users/davidskoranski/legal-harness/scripts/run.sh:18) prints `$TOOLCHAIN` directly. The specified path contains one literal newline, so the refusal produces **two stderr lines**, not the required `lines=1`. [pathguard.py:55](/Users/davidskoranski/legal-harness/src/casefile/pathguard.py:55) sanitizes its own verdict only. G1 therefore fails on correct current behavior, and W1’s “no app code changes” file list cannot deliver its promised result.

2. **High · CONFIRMED · D0.14/§1.17: the builder driver does not fully fail closed.**  
   [gemma_task.py:165](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:165) rejects only `done_reason == "length"`; it never requires `done is True` or `done_reason == "stop"`. [Lines 188-194](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:188) write FILE answers without parsing them, while [lines 94-99](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:94) accept unfenced content. An incomplete response carrying a partial FILE block can overwrite working code and return “applied.” The advertised splice protection applies only to FUNCTION answers.

3. **High · CONFIRMED · W8/G25: token-count failures can become successful answers.**  
   [model.py:78](/Users/davidskoranski/legal-harness/src/casefile/model.py:78) accepts missing counts (`None`), zero, and negative integers; it checks only the type of non-null values. The proposed runner checks `done_reason`, then parses JSON and records `status="ok"` without validating either count. Contrast [doctor.py:127](/Users/davidskoranski/legal-harness/src/casefile/doctor.py:127), which requires positive integers. Valid JSON with absent counts would produce `pages_failed=0`, repeating Librarian CX-5.

4. **High · PLAUSIBLE · W6/G19, D25: invented summaries can receive a perfect score.**  
   The proposed matching algorithm at brief lines 566-575 compares only cite and quote; `text` is inspected only for firm-rule violations. The current [Rules.check implementation](/Users/davidskoranski/legal-harness/src/casefile/rules.py:65) performs regex checks, not factual comparison. Keep every ideal cite and quote, but reverse the MMI summary to “The patient has reached maximum medical improvement”: the prescribed scorer still reports perfect. This benchmark would miss the medical inventions it is meant to measure.

5. **High · PLAUSIBLE · §1.7/W6: false flags cannot make an otherwise complete answer fail.**  
   Brief lines 556-558 omit `flags_extra` from `perfect`, and lines 570-573 match flags solely by kind and cite set. A candidate can emit both kinds for every page combination, cover all five expected signatures, and pass despite numerous unsupported conflicts and gaps. The proposed parser also accepts arbitrary `about` strings. This undermines the benchmark required by [spec.md:91](/Users/davidskoranski/legal-harness/docs/spec.md:91).

6. **High · CONFIRMED · W7/G24 and §5 R3: the recording CHECK supplies its own expected request.**  
   G24 sends `rows[0]["messages"]` to a fake constructed from those same rows. [core.py:32](/Users/davidskoranski/legal-harness/tests/fakemodel/core.py:32) builds its lookup from those messages, and [core.py:102](/Users/davidskoranski/legal-harness/tests/fakemodel/core.py:102) checks that lookup. Reversing recording pages therefore **does not produce the promised 404 in W7’s CHECK**. More broadly, rebuilding recordings with production `benchrun.messages()` lets an omission in that function affect both request and oracle while replay still returns the complete ideal answer.

7. **Med · CONFIRMED · W6 seed (c): changing `unit` does not remove the IME finding.**  
   [rules.py:61](/Users/davidskoranski/legal-harness/src/casefile/rules.py:61) skips question-only rules when checking text; it does not skip text rules when checking questions. The IME rule is explicitly `unit="text"` at [rules.toml:7](/Users/davidskoranski/legal-harness/playbook/rules.toml:7). Changing the scorer to `unit="question"` still finds “The IME.” The claimed change from `rules=1` to `rules=0` is false, so this seed does not establish the claimed sensitivity.

8. **Med · CONFIRMED · W8 seed (c): deleting the caller’s context option changes nothing.**  
   [model.py:67](/Users/davidskoranski/legal-harness/src/casefile/model.py:67) unconditionally installs the configured `num_ctx` and temperature. Without the runner’s `options` argument, the request still contains **`num_ctx=65536`**. [test_model.py:29](/Users/davidskoranski/legal-harness/tests/test_model.py:29) already verifies that caller values are overridden. The prescribed request-shape assertion stays green under this seed.

9. **High · PLAUSIBLE · §3 build order: recording tests run before their required asset exists.**  
   The specified order runs G24 and G26 before G21 creates `ideal.json`. G22’s prescribed code reads that file immediately, and both tests call G22’s helper. The driver itself neither synthesizes dependencies nor executes prerequisite tasks; its application path starts at [gemma_task.py:172](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:172). As written, the builder reaches missing-file failures and retries a dependency error as a coding failure.

10. **High · CONFIRMED · G9-G12 versus D0.14: fixture tasks cannot fit the allowed output contract.**  
    G9 and G10 each request four files; G11 and G12 each request three. D0.14 assigns every task one allowed path, and [gemma_task.py:176](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:176) rejects any other path. G9/G10 also permit 100-160 answer lines before headers, exceeding the protocol’s approximately 120-line ceiling. These must be individual page tasks; the stated 31-task plan is not executable as specified.

11. **Med · CONFIRMED · G2/G3: the chair-written code exception conflicts with Q28.**  
    [LEDGER.md:94](/Users/davidskoranski/legal-harness/.workflow/LEDGER.md:94) assigns **all code and fixes** to Gemma, with the recorded fallback procedure. The brief instead directs the chair to write both config changes. Its size justification also fails: [config.load](/Users/davidskoranski/legal-harness/src/casefile/config.py:65) occupies 83 lines, below the protocol’s approximately 120-line answer allowance, and the [driver supports function replacement](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:103). This bypasses the owner’s builder experiment without using its authorized fallback.

12. **Med · CONFIRMED · §2 CHECK convention/W11: command status does not carry the verdict.**  
    `pytest; echo "pytest_exit=$?"; grep ...` returns grep’s status, so a failed test that printed its evidence line can leave the CHECK command successful. W11’s `gate; tail -1` likewise returns tail’s status. This discards the failure status carried by [run_capture.py:109](/Users/davidskoranski/legal-harness/scripts/run_capture.py:109) and [gate.py:75](/Users/davidskoranski/legal-harness/src/casefile/gate.py:75), repeating Librarian CX-11/V-B2 at the orchestration layer. Printing the status is not asserting it.

13. **Med · CONFIRMED · W10 seed (b)/R6: the listener probe cannot prove shutdown happened.**  
    Removing `server.shutdown()` leaves `server.server_close()` in place, following [test_stage1_exit.py:57](/Users/davidskoranski/legal-harness/tests/test_stage1_exit.py:57). The installed [socketserver.py:495](/Users/davidskoranski/.casefile-dev/legal-harness/python/cpython-3.12.13-macos-aarch64-none/lib/python3.12/socketserver.py:495) closes the listening socket there. A listener count need not increase even if the serving thread remains alive, and the proposed `thread.join(timeout=5)` has no subsequent liveness assertion. The promised seed detection is unsupported.

14. **Med · PLAUSIBLE · W3/G7 and W9/G27: the “cannot run → exit 2” boundary misses filesystem failures.**  
    G7 specifies wrapping metadata read errors but not missing/unreadable `records`, binder enumeration, page reads, or decoding errors. G27 catches `MatterError`, not those underlying exceptions; it also leaves run-log failures unhandled. [runlog.py:107](/Users/davidskoranski/legal-harness/src/casefile/runlog.py:107) can raise during directory creation, connection, or schema validation. Ordinary malformed input or an unwritable state directory can therefore produce a traceback and exit 1 instead of the promised exit 2. The work list needs the complete error-conversion path and isolated tests.

15. **Med · CONFIRMED · W8/G25: failed model replies can disappear from answer history.**  
    [model.py:76](/Users/davidskoranski/legal-harness/src/casefile/model.py:76) raises on `done=false` without retaining the raw response in the exception. G25’s `ModelError` branch writes only a failure row, so an actual received, incomplete answer gets no answer row. [runlog.py:67](/Users/davidskoranski/legal-harness/src/casefile/runlog.py:67) supports failed raw-answer storage, but W8’s file list omits the client change needed to supply it. None of G26’s five probes enters this branch.

16. **Med · PLAUSIBLE · §1.18: R1-20 is still reachable through candidate prose.**  
    G17 permits arbitrary strings in `text` and `about`; nothing forbids inline citations. The current [rules.toml:56](/Users/davidskoranski/legal-harness/playbook/rules.toml:56) recognizes bracketed forms only, so a candidate summary ending “See page 12” can retain a valid structured cite and avoid a citation finding. “Cites are structured” does not establish that free-form output cannot contain additional, unverified citations.

The three changes I would insist on before build:

1. **Repair the CHECKs and seeds:** correct W1’s baseline, preserve failing exit statuses, replace the ineffective seeds, and use independent request and cleanup assertions.
2. **Make the Gemma plan executable under Q28:** split fixture pages into individual tasks, fix asset dependencies, route code through the authorized builder procedure, and harden the driver’s completion/write boundary.
3. **Close the benchmark’s verification gaps before freezing baselines:** address invented summaries and false flags, validate completion counts, preserve failed raw replies, and specify complete error-to-verdict handling.