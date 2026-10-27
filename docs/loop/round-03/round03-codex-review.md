# Round 3 Codex code review (8a), gpt-6.1-sol, read-only, high

1. **high, CONFIRMED, [src/casefile/intake.py:172](/Users/davidskoranski/legal-harness/src/casefile/intake.py:172):** The destination guard never validates the identity of the `records` or `pages` parent directories. A valid external matter with `pages` symlinked into the checkout passes preflight when the binder is absent, then publishes client text JSON into the checkout; a link to another matter similarly mixes case data.

2. **high, CONFIRMED, [src/casefile/intake.py:264](/Users/davidskoranski/legal-harness/src/casefile/intake.py:264):** Failure cleanup deletes both predictable temporary directories without checking which ones this invocation created. If two intakes for the same binder pass preflight, invocation A creates its directories, then B’s `mkdir` fails and B deletes A’s active workspace.

3. **high, CONFIRMED, [src/casefile/intake.py:153](/Users/davidskoranski/legal-harness/src/casefile/intake.py:153):** Publication can permanently expose records without their page store because rollback handles only `OSError`. A `KeyboardInterrupt` after the first rename leaves `records/<binder>` published, while outer cleanup deletes `pages/<binder>.tmp`; subsequent intake is refused because the records binder exists.

4. **med, CONFIRMED, [src/casefile/model.py:21](/Users/davidskoranski/legal-harness/src/casefile/model.py:21):** A redirect body read failure loses the fact that a reply arrived because the redirect handler runs before `_request` sets `received=True`. A server returning 302 headers and then stalling causes a body timeout, no answer row, and bench exit 2; a truncated redirect body preserves its partial bytes but still incorrectly produces exit 2.

5. **med, CONFIRMED, [src/casefile/intake.py:109](/Users/davidskoranski/legal-harness/src/casefile/intake.py:109):** The OCR process group is never cleaned up when `communicate` returns normally. An OCR parent can spawn a child with redirected standard streams and then exit, including with an error; intake returns and removes its workspace while that child remains alive in the separate process group.

6. **med, CONFIRMED, [src/casefile/intake.py:111](/Users/davidskoranski/legal-harness/src/casefile/intake.py:111):** Signal cleanup covers only the OCR subprocess phase, leaving temporary client files behind during later processing. After OCR returns and restores the default handlers, SIGTERM during page extraction or JSON writing terminates intake without executing its `finally`, retaining both `.tmp` folders and blocking re-intake.

7. **med, CONFIRMED, [src/casefile/stamps.py:20](/Users/davidskoranski/legal-harness/src/casefile/stamps.py:20):** Stamp extraction lacks an ending token boundary and can record a truncated prefix as a Bates stamp. With the default pattern, `MED0001A` and `MED0001B` both yield raw `MED0001` and are deduplicated into one stamp, silently discarding their differing trailing letters.

8. **med, CONFIRMED, [tests/test_doctor.py:246](/Users/davidskoranski/legal-harness/tests/test_doctor.py:246):** The OCR failure exit assertion is unconditional success whenever `want_ok` is false. If doctor prints the expected OCR FAIL line but incorrectly returns 0, every injected OCR failure case still passes because the assertion ends with `or not want_ok`.

Static review only. No files changed or runtime checks executed.
## Orchestrator reproduction (2026-10-27)

- CX-1 REPRODUCED (run): matter 9002.001 with `pages` symlinked to matter 9002.002's `pages`; intake exit 1
  and 7 files written under 9002.002/pages/scan.
- CX-2 REPRODUCED (trace): intake.py:207 `folder.mkdir()` raises FileExistsError in a second intake; the
  `finally` at :263 removes both `.tmp` folders it did not create.
- CX-3 REPRODUCED (trace): `_publish` (intake.py:153) rolls back only on OSError; a KeyboardInterrupt after
  the first rename leaves `records/<binder>` published and `pages/<binder>.tmp` removed by the `finally`.
- CX-4 REPRODUCED (trace): model.py:21 `fp.read()` runs inside `opener.open`, before `_request` marks the
  reply received; a body timeout there is classed as no reply (exit 2).
- CX-5 REPRODUCED (trace): popen_runner kills the group only on timeout or exception, never after a normal
  return.
- CX-6 REPRODUCED (trace): signal handlers are restored when `communicate` returns (intake.py:110); a
  SIGTERM during page extraction or JSON writing skips the cleanup.
- CX-7 REPRODUCED (run): `stamps.find("MED0001A and MED0001B", Q21 pattern)` -> `[('MED0001', 'MED0001')]`.
  Chair ruling, pending veto: a match must end at a token boundary (not followed by a letter or digit), so a
  truncated token is never recorded; suffix forms are owner question 38.
- CX-8 REPRODUCED (read): tests/test_doctor.py:246 `assert code == (0 if want_ok else 1) or not want_ok` is
  vacuous whenever want_ok is false.
