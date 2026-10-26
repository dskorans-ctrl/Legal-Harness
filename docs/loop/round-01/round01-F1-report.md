Changed only:

- `scripts/run.sh`: external toolchain paths and PATH; cap mechanics and exit handling remain byte-identical.
- `tests/test_run_sh.py`: child-environment check for all three toolchain paths.
- `docs/loop/round-01/round01-brief-codex.md`: replaced the sole en dash with “to”; no em or en dashes remain.

Baseline: 92 passed, 5 deselected. Restoration verified with `cmp`. Diff check passed.

```text
RED (caught): UV_PROJECT_ENVIRONMENT=$ROOT/.venv; toolchain_inside_repo=1; 1 failed, 6 passed
GREEN: restored wrapper; 7 passed
```

The full privacy gate awaits the orchestrator’s toolchain move.