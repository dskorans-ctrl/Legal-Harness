1. **High | CONFIRMED | [scripts/gemma_task.py:82](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:82)** - The supposedly local model request uses urllib’s default opener, which honors external proxies.  
   **Scenario:** `http_proxy` points to an off-machine proxy and `no_proxy` excludes neither loopback nor everything → the entire task and context POST reaches that proxy despite the hard-coded `127.0.0.1` URL. I traced this through the installed Python 3.12 urllib implementation; the application client correctly disables proxies, but this new script does not.

2. **High | CONFIRMED | [src/casefile/benchrun.py:83](/Users/davidskoranski/legal-harness/src/casefile/benchrun.py:83)** - Positive token counts are treated as proof of complete input consumption, so prompt truncation can pass undetected.  
   **Scenario:** A large matter produces a response with `done=true`, `done_reason="stop"`, positive counts reflecting only the retained input, and valid candidate JSON → the runner records `status="ok"` and `pages_failed=0`. If the retained material supplies the key matches, bench exits 0 despite unread input. There is no prompt-size bound or comparison against tokens sent, contrary to spec §4.1.

3. **Med | CONFIRMED | [scripts/gemma_task.py:200](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:200)** - The output allowlist compares path spellings but follows symlinks when writing, permitting changes outside the allowed filesystem target.  
   **Scenario:** Allowed `tests/generated.py` is a symlink to `/outside/stored.py` → a valid FILE answer passes the allowlist and AST check, then overwrites `/outside/stored.py`. Joining with `ROOT` does not enforce the brief’s checkout boundary.

4. **Med | CONFIRMED | [scripts/gemma_task.py:188](/Users/davidskoranski/legal-harness/scripts/gemma_task.py:188)** - A function-scoped task can bypass its restriction by returning a FILE block.  
   **Scenario:** Invoke with `--allow src/casefile/config.py --function src/casefile/config.py::load`; the model returns a FILE block containing only a syntactically valid `load` definition → the driver replaces the entire module, removes its other definitions, and exits 0. The function restriction is checked only for FUNCTION blocks.

5. **Med | CONFIRMED | [src/casefile/benchscore.py:60](/Users/davidskoranski/legal-harness/src/casefile/benchscore.py:60), [benchscore.py:69](/Users/davidskoranski/legal-harness/src/casefile/benchscore.py:69)** - Keys accepted by the loader can contain matching-identity collisions that make a perfect score impossible.  
   **Scenario:** Two facts have distinct IDs but identical cite and normalized quote → every candidate occurrence matches only the first ID, yielding at most `found=1 of 2`. Likewise, two distinct flag IDs with identical kind and cite set collapse into one dictionary entry while `flags_total` remains 2, yielding `flags_missed=1` even when both were supplied. The loader checks duplicate IDs, not these collisions.

6. **Med | CONFIRMED | [src/casefile/benchrun.py:68](/Users/davidskoranski/legal-harness/src/casefile/benchrun.py:68)** - Received replies rejected inside `_request` disappear from the answer history, violating D25’s requirement to store every received reply.  
   **Scenario:** HTTP 200 returns malformed JSON or a JSON array → `model.py:63-65` raises `ModelError` without `raw`; this handler skips `record_answer`. The run retains only a failure message containing at most the first 200 response bytes, with no answer row.

7. **Med | CONFIRMED | [src/casefile/matter.py:57](/Users/davidskoranski/legal-harness/src/casefile/matter.py:57)** - Invalid UTF-8 in `matter.toml` escapes the matter-error boundary and returns the wrong verdict code.  
   **Scenario:** A discovered matter’s manifest contains byte `0xff` → `tomllib.load` raises `UnicodeDecodeError`, which this handler does not catch; `bench.main` also does not catch it → traceback and exit 1 instead of D25’s “cannot run” exit 2.

All findings were confirmed by static tracing. No files were modified and no app, model, tests, or scripts were run.