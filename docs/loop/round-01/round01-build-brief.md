# Round 1 build brief: stage 1 skeleton and harness

Branch `loop/round-01`, reconciled to main `5a55b54` on 2026-10-25. Scope: ledger items R1-2 to
R1-11 (R1-12 is the chair's close, deferred to the next session by Q15). Spec canon: `docs/spec.md`
§1, §4, §5, §6, §7 stage 1, §9, §10, §11. Owner rulings Q1 to Q21 in `.workflow/LEDGER.md` are
binding and are not re-asked here; Q14 to Q21 arrived after the first draft and are applied in §6.
Revised once after the Codex review (`round01-brief-codex.md`); dispositions in §8.

Every number in this brief was measured on this Mac today, in the Claude Code sandbox, unless a line
says otherwise. Builder (Q14): Codex gpt-6.1-sol through `codex exec -s workspace-write -C <tree>`,
no network, no write outside its tree. Each §2 item is written as a self-contained prompt: the
orchestrator pastes the item's text, the D-sections it names, and the §6b privacy paragraph into one
`codex exec` run, then re-runs the item's CHECK and SEED itself (catalog #101) before the next item.
Codex cannot reach the network, so every `uv sync`, `uv python install` and `git worktree add` is the
orchestrator's step, named where it falls in §3. The Librarian is blank; each item's pre-flight line
cites the catalog IDs the builder is told to read.

Privacy rule carried by every builder prompt: no real client record, name or fact in any file,
prompt, fixture, recording or test. Every fixture is invented (ledger Q9, §6b below).

## §0 Drift since the seed commit

Verified with `git diff 5a55b54` and a full tree listing:

- Files changed since `5a55b54` (re-checked at revision time with `git status`): `.workflow/LEDGER.md`
  (line 6 "round 1 opened 2026-10-25 on `loop/round-01`"; Q10 to Q21 in `## Clarified`; the
  `## Round 1` block R1-1 to R1-12, V1), `docs/loop/agent-log.md`, `docs/loop/questions-for-owner.md`
  (questions 1 to 7 and an "Answered 2026-10-25" block), `docs/loop/tuning-questions.md` (T-1 to T-4);
  untracked: `.claude/settings.json` (`sandbox.network.allowLocalBinding: true`, Q18) and
  `docs/loop/round-01/round01-brief-codex.md`. No code exists. Q14 moved the coding tier from Sonnet
  5.5 to Codex gpt-6.1-sol (`codex-cli 0.159.2` is at `~/.local/bin/codex`; `codex exec --help` lists
  `-s, --sandbox <MODE>` and `-C, --cd <DIR>`).
- No code exists. The tree holds `docs/`, `cards/` (45 cards plus `cards/manifest.json`), `schemas/`
  (19 JSON schemas), `reference/`, `.claude/skills/app-loop/`, `README.md`, `CLAUDE.md`,
  `Librarian.md` (blank: header, "Builder pre-flight", "Open items" only), `.gitignore`.
- `.gitignore` (checked line by line): ignores `Cases/`, `Bench/`, `*.pdf`, `*.doc`, `*.docx`, `*.png`,
  `*.jpg`, `*.jpeg`, `*.tif`, `*.tiff`, `*.heic`, with `!tests/fixtures/**` and `!.claude/skills/**`;
  ignores `.workflow/scratch/`, `.venv/`, `config.toml`, `*.sqlite`, `*.db`. Two entries this round
  adds: `.uv/` and `state/` (see D-5).
- Machine (verified, matches the chair's facts): bash `3.2.57(1)-release`; `/usr/bin/head`,
  `/usr/bin/tee`, `/bin/dd` are BSD (no `--version`, no GNU `timeout`, no `stdbuf`); `python3` is
  3.14.6 at `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`; `python3.12` not on PATH;
  `uv 0.11.30` at `~/.local/bin/uv`; `ollama` and `tesseract` not found; macOS 26.4 (Darwin 25.4.0).
- Sandbox facts the ledger does not record (measured in the Bash tool's sandbox, auto mode):
  - Sockets: `bind(("127.0.0.1", 0))` fails `PermissionError: [Errno 1]`; `connect` to 127.0.0.1 fails
    `EPERM`; a UDP connect for LAN address discovery fails `EPERM`. Re-measured at revision time with
    `.claude/settings.json` already holding `allowLocalBinding: true` (Q18): the bind in this agent's
    sandbox still fails `[Errno 1]`, and the Codex `workspace-write` sandbox is a second, separate
    policy. Socket tests are therefore a separate marker the orchestrator runs (D-13); nothing in the
    build depends on a socket working inside a builder's sandbox.
  - `urllib.request.build_opener().handlers` here is `ProxyHandler, UnknownHandler, HTTPHandler,
    HTTPDefaultErrorHandler, HTTPRedirectHandler, FTPHandler, FileHandler, DataHandler, HTTPSHandler,
    HTTPErrorProcessor`; `getproxies()` returns the sandbox's proxy for `http` and `https` with a `no`
    list containing `127.0.0.1`, and `proxy_bypass("127.0.0.1")` is `True` here. The bypass is an
    environment fact, not a property of the client, so D-10 builds its opener with `ProxyHandler({})`.
  - `git ls-files --cached --others --exclude-standard` in a throwaway repo with `Cases/c.txt` and
    `docs/d.pdf` present and ignored lists neither; `git ls-files --others` (no exclude) lists both.
    A throwaway uv project with `pytest` has 516 files in `.venv` and 0 with a forbidden suffix
    (`.pdf .doc .docx .png .jpg .jpeg .tif .tiff .heic`, case-insensitive); `git ls-files --others`
    there lists 1037 paths. D-12 scans ignored files too, with no exemption list.
  - The D-3 pipeline's four `PIPESTATUS` values: `0 0 0 0` for a child at CAP and at CAP+1 (CAP 1000),
    `141 0 0 0` for a 60 MiB child (SIGPIPE on the child, the three capture stages exit 0), `3 0 0 0`
    for `exit 3`. `mktemp -d` under an unwritable `TMPDIR` returns 1 with an empty `tmp`, after which
    `tee "$tmp/out"` fails `tee: /out: Operation not permitted` and `wc -c < "$tmp/out"` fails: the
    first draft would have returned the child's `0` here (D-3 now exits 98).
  - Writable paths are the repo, `$TMPDIR` and a few system paths; `~/.local/share/uv` and
    `~/.cache/uv` are not writable. With `UV_PYTHON_INSTALL_DIR` and `UV_CACHE_DIR` pointed at a
    writable directory, `uv python install 3.12` installed `cpython-3.12.13-macos-aarch64-none`
    (23.8 MiB) in 1.53 s from `github.com` plus `objects.githubusercontent.com` /
    `release-assets.githubusercontent.com`; `releases.astral.sh` was denied and the install still
    succeeded (it is a version check).
  - `uv sync` of the exact pyproject in D-1 resolved from `pypi.org` and `files.pythonhosted.org`:
    `pytest==8.4.2`, `pluggy==1.7.0`, `iniconfig==2.3.1`, `packaging==26.3`, `pygments==2.21.0`;
    `.venv/bin/casefile` ran; `pytest -q` passed one test in 0.00 s.
  - `lsof -nP -iTCP -sTCP:LISTEN` works in the sandbox and prints this user's listeners with numeric
    addresses (`*:8581` for all interfaces). `netstat -an -p tcp` printed no LISTEN rows here, so
    netstat is not usable as a probe.
- The output-cap pipeline in D-3 was run on this bash and these BSD tools: a 60 MiB child capped to
  exactly 52428800 bytes on stdout in 1.79 s with exit 97; child exits 3, 0 and 137 (SIGKILL) carried
  through under the cap; stdout 600 + stderr 600 bytes against a 1000 cap gave 97; a Python child that
  keeps writing after the cap ended in 1.09 s (no hang). The seed (drop the `+ 1`) made the cap+1 case
  exit 0, so the CHECK in R1-2 has teeth.
- Prose dashes: `grep -c` with the literal U+2014 and U+2013 characters as two `-e` patterns (a shell
  unicode escape of the same code points did not work and returned 0 on the catalog; the gate uses
  Python, not grep) finds 293 in the skill's catalog
  (control) and 0 in `docs/`, `README.md`, `CLAUDE.md`, `Librarian.md`, `.workflow/LEDGER.md`, and 0
  in `cards/`, `reference/`, `schemas/`. The prose gate row (D-13) starts green.
- Wording drift inside the owner's own material: `cards/_core.md:10` forbids "DME", "IME",
  "independent medical examination" and "defense medical examination";
  spec §4 rule 5 forbids only "DME" and "IME". `cards/02-depo/c-defense-doctor.md:31` lists "hired,
  paid, retained, or referred ... Fees. How many of these exams". Ruled by Q16: all four phrases,
  whole words, any case, on outputs only (D-7).

## §1 Decisions, with trade-offs

### D-1 Toolchain, layout, pyproject
Decision: `uv` project, `src/` layout, build backend `uv_build`, Python pinned by `.python-version`
containing `3.12` and `requires-python = ">=3.12,<3.13"`. `uv.lock` is committed. `scripts/run.sh`
exports `UV_PYTHON_INSTALL_DIR="$ROOT/.uv/python"` and `UV_CACHE_DIR="$ROOT/.uv/cache"` so the
interpreter and cache are project-local (Q11) and inside the sandbox's writable set; `.uv/` is
gitignored. Console entry `casefile = "casefile.cli:main"`. Verified pyproject (drift bullet above):

```toml
[project]
name = "casefile"
version = "0.1.0"
description = "Local case system for one attorney (stage 1 skeleton)"
requires-python = ">=3.12,<3.13"
dependencies = []

[project.scripts]
casefile = "casefile.cli:main"

[dependency-groups]
dev = ["pytest>=8,<9"]

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-p no:cacheprovider"
```

Layout:
```
pyproject.toml  uv.lock  .python-version  config.example.toml  scripts/run.sh
src/casefile/__init__.py cli.py config.py runlog.py model.py rules.py playbook.py doctor.py
            gate.py privacy.py prose.py
playbook/rules.toml  playbook/samples/depo-goals.toml
tests/conftest.py  tests/fakemodel/__init__.py __main__.py core.py server.py recordings.json
tests/fixtures/playbook/{malformed-missing-why.toml,unmarked.toml,bad-date.toml}
tests/test_run_sh.py test_config.py test_runlog.py test_rules.py test_playbook.py
      test_fakemodel.py test_model.py test_doctor.py test_privacy.py test_prose.py test_gate.py
      test_stage1_exit.py
```
Rejected: flat `casefile/` package (import-from-cwd shadows the installed package and hides a broken
install); hatchling (one more download, no gain); `uv_build` was chosen because uv is already the
toolchain and `uv init --package` emits it. Why `src/`: `python -m casefile.gate` must import the
installed package, never the checkout by accident.

### D-2 Dependencies: none at runtime, pytest only for dev
Decision: runtime `dependencies = []`. TOML via `tomllib` (3.11+), SQLite via `sqlite3`, HTTP client
via `urllib.request`, the fake server via `http.server.ThreadingHTTPServer`, CLI via `argparse`,
hashing via `hashlib`. Dev group: `pytest>=8,<9` (locks to 8.4.2 today). Rejected: FastAPI for the
fake server (spec §5 names FastAPI for the web page, stage 8, not for a test stand-in; it would pull
pydantic, starlette, uvicorn into a round that ships zero endpoints of its own); typer or click
(argparse is enough for `doctor`, `config show`, `playbook show`, `version`); Playwright (ledger
`## Project` names it for page screenshots; there are no pages until stage 8, deferred, §6 C3).
Why: the smaller the lock, the smaller the surface the privacy and supply chain story must cover,
and `uv sync` stays under a second.

### D-3 `scripts/run.sh` cap mechanics (bash 3.2, BSD tools)
Decision: the wrapper is `#!/bin/bash` (bash 3.2 is on every Mac; zsh's `pipestatus` differs), and
runs:

```bash
CAP=52428800                      # 50 MiB of combined stdout and stderr
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export UV_PYTHON_INSTALL_DIR="$ROOT/.uv/python" UV_CACHE_DIR="$ROOT/.uv/cache"
[ -d "$ROOT/.venv/bin" ] && PATH="$ROOT/.venv/bin:$PATH"
[ "$#" -ge 1 ] || { echo "run.sh: usage: scripts/run.sh <cmd> [args]" >&2; exit 96; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/casefile-run.XXXXXX")" \
  || { echo "run.sh: cannot create capture dir under ${TMPDIR:-/tmp}; exit 98" >&2; exit 98; }
set -o pipefail
"$@" 2>&1 | head -c "$((CAP + 1))" | tee "$tmp/out" | head -c "$CAP"
st=("${PIPESTATUS[@]}")
bytes="$(wc -c < "$tmp/out" 2>/dev/null | tr -d ' ')"
rm -rf "$tmp"
case "$bytes" in ''|*[!0-9]*)
  echo "run.sh: capture file unreadable (stages ${st[*]}); exit 98" >&2; exit 98;; esac
if [ "$bytes" -gt "$CAP" ]; then
  echo "run.sh: output cap $CAP bytes hit (child status ${st[0]}); exit 97" >&2
  exit 97
fi
if [ "${st[1]}" != 0 ] || [ "${st[2]}" != 0 ] || [ "${st[3]}" != 0 ]; then
  echo "run.sh: capture stage failed (stages ${st[*]}); exit 98" >&2
  exit 98
fi
exit "${st[0]}"
```

How the child's exit code survives the pipe: `PIPESTATUS[0]` is the first stage (the child), read
on the line right after the pipeline (bash 3.2 verified: `false | true | true | true` gives
`1 0 0 0`). How the cap is detected exactly: the first `head -c CAP+1` bounds everything (disk and
memory: `tee`'s file can never exceed CAP+1 bytes, catalog #34), `tee` writes that bounded stream
to a file whose byte count tells whether the child produced more than CAP, and the last
`head -c CAP` bounds what is relayed to the caller to exactly CAP. Measured: 60 MiB child relays
52428800 bytes, exit 97; CAP bytes exactly relays CAP, exit 0; CAP+1 relays CAP, exit 97.
Rejected: `head -c CAP` alone (cannot tell "exactly CAP" from "more than CAP"); reading the child's
exit status for SIGPIPE (Python exits 120 or 1 on EPIPE, bash 141, not a cap signal); a second
`head -c 1` after the first on the shared pipe (BSD head over-reads into a buffer, so CAP+1 was
eaten in a trial design); a Python wrapper (the wrapper must work before any venv exists and
`/usr/bin/python3` is 3.9 from Xcode, writing an xcrun cache the sandbox denies). Known gap: a child
that ignores EPIPE and never exits after the cap would block the wrapper; no wall-clock ceiling in
round 1 (risk R-5; catalog #34 asks for one later).
Capture failure (Codex finding 18): `mktemp` failing, the capture file unreadable, or any of the three
capture stages (`head`, `tee`, `head`) exiting non-zero when the cap was not hit, is exit 98 with a
notice on stderr; the child's code is never returned when the wrapper cannot vouch for its own
accounting. Measured (§0): the three capture stages exit `0 0 0` at CAP, at CAP+1 and at 60 MiB (the
child's own `141` is what SIGPIPE produces), so 98 never fires on a healthy pipe; with
`TMPDIR=/nonexistent/dir`, `mktemp -d` returns 1 and `tmp` is empty, which the first draft would have
carried through to the child's `0`.
Exit codes shipped: 97 cap hit; 96 wrapper misuse (no command); 98 capture failure; otherwise the
child's code (127 command not found, 128+signal for a signal death, both measured).

### D-4 Config file: location, format, fail-closed loading
Decision: one TOML file. Path: `$CASEFILE_CONFIG` if set, else `./config.toml` relative to the
current working directory (the repo root in practice; `.gitignore` already ignores `config.toml`).
`config.example.toml` is committed and documents every key. A missing file is an error, not
defaults: `ConfigError: no config file at <path>; copy config.example.toml to config.toml`
(pillar 2; a Studio with a missing config must not quietly read `Cases/` from wherever it was
started; §6 C6). Defaults apply only to keys omitted inside an existing file. Schema, stage 1:

```toml
[paths]
matters  = "~/Cases"      # REQUIRED, no default: the matters folder, outside the repo checkout (Q17)
state    = "state"        # run log and later caches, relative to this file
playbook = "playbook"
[model]
host        = "http://127.0.0.1:11434"
name        = "qwen3.8:27b"       # Q20
num_ctx     = 65536               # spec §5 value; 65536 or more, never less
temperature = 0.1
timeout_s   = 600
[ocr]
tesseract = "tesseract"
ocrmypdf  = "ocrmypdf"
```

Validation in `config.py: load(path) -> Config` (frozen dataclasses): unknown table or key anywhere
raises `ConfigError("unknown key [model].hots; known: host, name, num_ctx, temperature, timeout_s")`;
a wrong type raises `ConfigError("[model].num_ctx: expected int, got str")`; `num_ctx < 65536` raises
(spec §5 says `num_ctx` 65536 "in the Modelfile and on every call": 65536 is the shipped value, the
loader accepts a larger one only so that a stage 9 benchmark can raise it under pillar 6, and every
consumer, the doctor included, reads `config.model.num_ctx` rather than a literal; Codex finding 12);
`name` must be non-empty (catalog #102); `model.host` must parse with `hostname == "127.0.0.1"` and
scheme `http` (`localhost` and `::1` are rejected: DNS and IPv6 are two more ways to leak off-box; §6
C7). `[paths].matters` is required (Q17: the owner sets it; a default here would be a silent guess at
where client records live), `~` is expanded, the result must be absolute and must not lie under the
config file's directory (the repo checkout): `ConfigError("[paths].matters must be outside the
checkout <dir>")`. `state` and `playbook` are relative to the config file's directory. No per-key
environment overrides (an env override is a silent default by another name; catalog "Fail-open CLI
default"). `casefile config show` prints the effective config with the source of each value (`file`
or `default`), so a default is never silent.
Rejected: YAML (a dependency); JSON (no comments for the owner); defaults when the file is missing
(the Studio case above); a default for `matters` (Q17); `~/.config/casefile` (two places to look; the
repo root is where `install.sh` and `casefile doctor` already run per spec §8).

### D-5 Data root and test isolation
Decision: data root is `[paths].matters`, a folder outside the checkout the owner names in
`config.toml` (Q17; `config.example.toml` shows `~/Cases`). `Cases/` and `Bench/` stay in `.gitignore`
and in the privacy row as forbidden prefixes (ledger R1-10). The run log lives at
`[paths].state/runlog.sqlite`, default `state/runlog.sqlite` (new gitignore entry `state/`; `*.sqlite`
is already ignored). Tests never touch a production path: `tests/conftest.py` has an autouse session
fixture `isolated_config(tmp_path_factory)` that writes a complete `config.toml` under a tmp directory
with `matters`, `state` and `playbook` pointing inside that directory (`playbook` is a `copytree` of
the repo's `playbook/` when that directory exists, else an empty directory, so R1-3 is green before
lane B lands and loader tests can mutate their copy; Codex finding 6) and sets `CASEFILE_CONFIG` to
it in `os.environ` for the session. Isolation is a precondition, checked before any test runs
(catalog #111; Codex finding 7): the fixture calls `config.load` on the file it wrote and asserts
that `matters`, `state` and `playbook` are each under the tmp root (`Path.is_relative_to`), and that
`os.environ["CASEFILE_CONFIG"]` is that file; any miss is `pytest.exit("test isolation failed: <path>",
returncode=3)` before the first test. A second autouse session fixture `production_dirs_untouched`
takes a snapshot (every file's relative path, size and `st_mtime_ns`, recursively) of repo-root
`state/`, `Cases/` and `Bench/` (those that exist) before the session and asserts the identical
snapshot after (a changed file inside an unchanged directory is caught, which a directory mtime would
miss). Tests that need a different config build one with `tests/conftest.py: write_config(tmp_path,
**overrides)`.
Rejected: `monkeypatch.chdir` into tmp (subprocess tests such as the exit test run `scripts/run.sh`
from the repo root and would lose the cwd trick); an in-memory SQLite (the exit test must read the
run log from a second process); a post-session check alone (it reports damage after the fact).

### D-6 Run log: SQLite schema v1, append-only, "a test job"
Decision: `runlog.py: open_db(path) -> RunLog`, creating schema version 1 on first open:

```sql
CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);           -- ('schema_version','1')
CREATE TABLE runs(id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL,
  job TEXT NOT NULL, matter TEXT, card TEXT NOT NULL, card_version TEXT NOT NULL,
  playbook_version TEXT NOT NULL, model TEXT NOT NULL, pages_in INTEGER NOT NULL,
  prompt_sha256 TEXT NOT NULL);
CREATE TABLE answers(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  finished_at TEXT NOT NULL, raw_answer TEXT NOT NULL, done_reason TEXT,
  prompt_eval_count INTEGER, eval_count INTEGER,
  status TEXT NOT NULL CHECK(status IN ('ok','failed')));
CREATE TABLE failures(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  at TEXT NOT NULL, gate TEXT NOT NULL, message TEXT NOT NULL);
CREATE TABLE approvals(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES runs(id),
  at TEXT NOT NULL, item TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('approved','rejected','edited')), by_whom TEXT NOT NULL);
```
plus eight triggers, `<table>_no_update BEFORE UPDATE` and `<table>_no_delete BEFORE DELETE` on each
of the four tables, each `SELECT RAISE(ABORT, 'runlog is append-only')`. `PRAGMA foreign_keys=ON`
and `journal_mode=WAL` on every connection. Timestamps are ISO 8601 UTC with a `Z`. `pages_in` is a
count; the page IDs themselves arrive with stage 3. API: `start_run(...) -> run_id`,
`record_answer(run_id, ...)`, `record_failure(run_id, gate, message)`, `record_approval(...)`,
`count_test_jobs()`.
"A test job" (spec §7 stage 1 exit test, R1-7) is defined as: a `runs` row with `job='doctor'` and
`card='doctor.warmup'` joined to an `answers` row with `status='ok'`. `casefile doctor` writes exactly
one per invocation (D-11). `count_test_jobs()` is that join's count.
The eight triggers are each exercised, not counted: `tests/test_runlog.py::test_append_only` attempts
one `UPDATE` and one `DELETE` on every table (eight raw-SQL statements) and asserts all eight raise
(Codex finding 17); the doctor's `runlog_schema` check counts them because it cannot write to the
production log, and says so in its reason text (`triggers=8 (counted, exercised by the test suite)`).
Rejected: one `runs` row updated at finish (an UPDATE on an append-only log; a crash mid-run would
leave no record of the start); JSON lines (spec §5 says SQLite; approvals need a join); triggers
omitted "because the code never updates" (the property must be enforced where the data is, catalog
"Probe certifies its own mechanism").

### D-7 `rules.toml`: schema and how a forbidden output is detected
Decision: `playbook/rules.toml` is a TOML document with `version = 1` and an array `[[rule]]`.
Each rule carries the six spec §6 fields (`rule`, `why`, `good`, `bad`, `added`, `learned`) plus
`id`, `kind`, `severity`, `unit` and the kind's pattern fields. Dates are TOML native dates.

```toml
version = 1

[[rule]]
id = "no-dme-ime"
kind = "forbid"              # any pattern matching anywhere in the unit is a finding
severity = "error"
unit = "text"
patterns = ['\bDME\b', '\bIME\b', '\bindependent medical examinations?\b',
            '\bdefense medical examinations?\b']       # Q16: the four phrases, whole words, any case
rule = "Never name the exam as a DME or IME in any form; write \"the report\"."
why = "The labels frame the examiner as independent or as the defense's; the report speaks for itself."
good = "The report of 14 March 2025 records a normal gait."
bad = "The IME found a normal gait."
added = 2026-10-25
learned = "spec §4 rule 5; ledger Q16"

[[rule]]
id = "no-hired-paid-retained"
kind = "forbid"
severity = "error"
unit = "text"
patterns = ['\b(hired|hires|hiring|retained|retains|retaining)\b',
            '\b(paid|pays|paying|payment|compensat(ed|ion)) (for|by|to) (the )?(doctor|dr\.?|examiner|exam|examination|report)\b',
            '\bwho (pays|paid|hired|retained|referred)\b', '\breferred (by|to) (the )?(defense|employer|insurer|carrier)\b',
            '\bfees?\b', '\bhow many (of these )?(exams|examinations|reports)\b',
            '\b(exams?|examinations?|reports?) (per|a|each) (year|month|week)\b']
rule = "Never ask or write who hired, paid or retained the doctor, the fees, or the exam volume."
...

[[rule]]
id = "treatment-and-bills-apart"
kind = "conjunction"        # a finding when every group in all_of matches the same unit
severity = "error"
unit = "question"
all_of = [['\btreat(ment|ed|ing|s)?\b', '\btherapy\b', '\bsurgery\b'],
          ['\bbill(s|ing|ed)?\b', '\bcharges?\b', '\binvoices?\b', '\bpaid\b']]
rule = "Treatment and bills are never in one question."
...

[[rule]]
id = "bates-cites"
kind = "cite"               # every cite in the unit must BE a Bates number; else error if stamped, warning if not
severity = "error"
unit = "text"
cite_pattern = '\[(?:cite|p\.|page)\s*([^\]]*)\]'    # group 1 is the cite body
bates_pattern = '[A-Z]{1,8}[ -]?\d{4,}'              # Q21; the owner edits this value here
rule = "Cite by Bates number; when the records are not stamped, cite page IDs and expect a warning."
...
```

Detection in `rules.py: load(path) -> Rules` and `Rules.check(text, *, unit="text", stamped=True) ->
list[Finding]` with `Finding(rule_id, severity, start, end, excerpt)`. Matching is `re.search` with
`re.IGNORECASE` for `forbid` and `conjunction`; every entry of `patterns` and `all_of` must contain
`\b` or an anchor, enforced at load time (a pattern without a boundary fails to load: "rule
no-dme-ime pattern 1 has no word boundary"), because a bare substring check is fail-open (skill rule:
presence-anywhere and substring checks are fail-open). The boundary rule does not apply to
`cite_pattern` (its literal brackets are its boundary) or to `bates_pattern`, which is never searched:
it is applied with `re.fullmatch` (case-sensitive; Bates prefixes are upper case) to the stripped body
of each cite, so `[cite ABC0001]` passes and `[cite garbage ABC0001tail]`, `[cite p. 12]` and
`[cite ABC0001 and more]` are findings (Codex findings 8 and 10). `kind="cite"`: every cite whose body
is not exactly one Bates number is a finding with `severity="error"` when `stamped=True` and
`"warning"` when `stamped=False` (spec §4 rule 5's "warning when records are not stamped"). A unit with
no cite is not a finding in round 1: "every fact carries a cite" (pillar 1) is spec §4 gate 6, the
coverage ledger, whose unit is a fact, not a text, and it arrives at stage 4; the round 1 checker
judges the cites it is given (Codex finding 9; this keeps `good` examples and the boundary cases
clean). The caller decides what a warning does; in round 1 a warning never fails a check but is
printed. Loader validation: exactly these four `id`s are present in `playbook/rules.toml`, `version ==
1`, every field present and typed, `kind in {forbid, conjunction, cite}`, `severity in {error,
warning}`, `unit in {text, question}`, and every pattern compiles. Any miss is `RulesError` naming the
rule id and the field (fail closed). Q16: the checker runs on outputs only; nothing in stage 1 or
later applies `rules.toml` to the text of a record being read.
Rejected: hard-coding the four rules in Python (spec §5: "`rules.toml`, read by cards and checker";
spec §6: a hard rule "also goes into the checker", so the file is the source); case-sensitive
matching for the forbid kinds (a lower-case "ime" is not an English word, so insensitivity costs no
false hits and catches "Ime"); a conjunction expressed as one regex (unreadable to the owner, who will
edit it); `re.search` for the Bates body (presence-anywhere certifies a malformed cite).
Known weakness, deliberately not hidden: `\bDME\b` also matches "DME" as durable medical equipment;
Q16 blocks the word in outputs regardless; tuning question T-1 watches the false hits. The hiring rule
is a word list, and a word list misses paraphrase ("the carrier's doctor"); T-2 watches the misses.

### D-8 Playbook entries, the SAMPLE marker, the version hash
Decision: `playbook/**/*.toml`; every file other than `rules.toml` holds `[[entry]]` tables with the
six spec §6 fields plus `id`, `kind` (`depo-goal`, `topic-order`, `question`, `hearing`, `checklist`,
`rule`), `deponent` (optional), and `sample` (bool, required). An entry is SAMPLE when
`sample = true` and its `rule` text starts with `SAMPLE:`; the loader requires both or neither,
and in round 1 requires both for every entry outside `rules.toml` (Q12: every other entry is an
invented fixture marked SAMPLE; §6 C5 makes "no unmarked entries" a gate row until the owner adds
practice content). `rules.toml` entries are never SAMPLE (they are the owner's four rules).
`playbook.py: load(dir) -> Playbook` fails closed with `PlaybookError("<file>: entry <n> (<id>):
missing field why")` on any missing field, wrong type (dates must be TOML dates, not strings), unknown
field, duplicate id across the whole playbook, or a non-SAMPLE entry outside rules.toml.
Version: `Playbook.version` is `"pb-" + sha256(concat over sorted relative paths of
path + b"\0" + file bytes + b"\0"))[:12]`. It changes on any byte change in any playbook file and
on a rename; it is stored on every run (`runs.playbook_version`). Round 1 ships one sample file,
`playbook/samples/depo-goals.toml`, with three invented entries (a deposition goal for an invented
defense doctor, a topic order, a question with good and bad wording), each `SAMPLE:` and
`sample = true`, and three malformed fixtures under `tests/fixtures/playbook/` for the fail-closed
tests.
Rejected: Markdown entries (six typed fields and a date want a typed format; the owner edits through
the Lessons screen in stage 8, not by hand); a version counter (two edits in one commit would share a
number; a hash cannot); hashing parsed content (whitespace edits should bump the version, because
the cards are built from the text).

### D-9 Stand-in model server `tests/fakemodel/`
Decision: stdlib `http.server.ThreadingHTTPServer`, logic in a pure module
`tests/fakemodel/core.py: FakeModel.handle(method, path, body: bytes) -> (status, dict)` so unit
tests can call it in-process without a socket (sandbox fact above; catalog #52), and
`tests/fakemodel/server.py: serve(bind, port, model) -> server` for real HTTP. Defaults:
bind `127.0.0.1`, port `18434` (not 11434: on the Studio Ollama holds 11434 and a test must never
collide with the real model; 18434 is free on this Mac), `--port 0` picks an ephemeral port and the
server prints `fakemodel: listening on 127.0.0.1:<port>` as its first stdout line. `--bind 0.0.0.0`
exists only to make the doctor's loopback check FAIL in a test.
Ollama native shape (spec §5: `/api/chat`, never the OpenAI route):
- `POST /api/chat` with `stream: false` returns `{"model", "created_at", "message": {"role":
  "assistant", "content"}, "done": true, "done_reason": "stop", "total_duration",
  "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"}`.
  `prompt_eval_count = sum(len(m["content"]) for m in messages) // 4 + 8`;
  `eval_count = len(content) // 4 + 1`; durations are fixed small integers in nanoseconds.
  `stream: true` or a missing `stream` gets HTTP 400 `{"error": "fakemodel: stream must be false"}`
  (the client always sends `stream: false`; fail closed on anything else).
- `GET /api/ps` returns `{"models": [{"name", "model", "size": 0, "digest": "fake", "details": {},
  "expires_at", "size_vram": 0, "context_length": <ctx>}]}` with `ctx` 65536 by default; the model
  appears only after the first `/api/chat` (Ollama loads on first use).
- `POST /api/show` returns `{"modelfile": "FROM qwen\nPARAMETER num_ctx <ctx>", "parameters":
  "num_ctx <ctx>", "details": {}}`; `GET /api/tags` lists the configured model; `GET /api/version`
  returns `{"version": "0.0.0-fake"}`. Unknown paths 404.
Answers: `tests/fakemodel/recordings.json` is a list of `{"name", "messages", "answer"}`; a chat whose
`messages` (role and content, canonical JSON) equal a recording's returns that answer; otherwise HTTP
404 `{"error": "fakemodel: no recording for these messages"}` and the client raises (no invented
answer, pillar 2). Round 1 ships one recording, `doctor-warmup`, answer `READY`.
How a test asks for a bad answer: a mode, sticky until changed, set by `POST /_fake/mode` with
`{"mode": "<m>"}` (and read by `GET /_fake/mode`), or by `--mode <m>` on the command line, or by
`FakeModel(mode=...)` in-process. Modes: `replay` (default); `truncated` (content is the recorded
answer cut to half its length, `done_reason: "length"`); `malformed` (content `{"facts": [{"page":
1,` with no closer); `forbidden` (content `The IME found no injury; the doctor was retained by the
employer.`); `short_context` (`/api/ps` reports `context_length: 8192` and `prompt_eval_count` is
capped at 8192); `empty` (content `""`, `done_reason: "stop"`, every other field as in replay: the
answer that looks finished and says nothing, Codex finding 5). Six modes. An unknown mode is HTTP
400 and the CLI exits 2 (fail closed).
Rejected: FastAPI (D-2); a marker inside the prompt text to select the mode (the page text slot is
the model's input, and a marker there would survive into a recorded prompt hash); random answers
(nothing to compare against; spec §5 wants recorded answers).

### D-10 Model client, minimal
Decision: `model.py: ModelClient(config, opener=None).chat(messages, *, options) -> Answer(content,
done_reason, prompt_eval_count, eval_count, raw: dict)` using `urllib.request` with `stream: false`,
`options = {"num_ctx": config.num_ctx, "temperature": config.temperature}` on every call (spec §5),
`timeout_s` from config. `opener` is injectable so unit tests pass `tests/fakemodel/core.py`'s
in-process transport (`FakeTransport(model)` implementing `.open(request, timeout)`); only the exit
test and the HTTP smoke test use a socket. The production opener is
`model.py: build_opener() -> urllib.request.OpenerDirector`, built as
`urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())` where `NoRedirect` is an
`HTTPRedirectHandler` whose `redirect_request` raises `ModelError("redirect refused: <code> to <url>")`:
with `ProxyHandler({})` the environment's `http_proxy`, `https_proxy` and `all_proxy` are never read,
so a POST carrying page text cannot be routed through a proxy by an environment variable, and a 3xx
from the model host cannot send it elsewhere (pillar 3; Codex finding 4; §0 records that the default
opener here carries a `ProxyHandler` fed by the sandbox's own proxy settings). Any non-200, a
non-JSON body, a missing `message.content`, or a `message.content` that is empty or whitespace raises
`ModelError` with the status and the first 200 bytes (an empty answer is never an answer, pillar 2;
Codex finding 5). Gates are stage 4; round 1 records `done_reason`, `prompt_eval_count` and
`eval_count` in the run log so the truncation gate has its data when it arrives.
`tests/test_model.py` (in-process): fields parsed from `FakeTransport`; 404 raises; non-JSON raises;
`empty` mode raises `ModelError` containing `empty`; `build_opener().handlers` contains no
`ProxyHandler` whose `proxies` is non-empty; an injected transport answering `302 Location:
http://127.0.0.1:1/` raises `ModelError` containing `redirect refused`. Two socket tests (marker
`socket`): a plain chat over HTTP against the fake on `127.0.0.1:<port>` returns `READY`; and with
`HTTP_PROXY=http://127.0.0.1:1` and `NO_PROXY` unset in the environment, the same chat still returns
`READY` (the proxy at port 1 is never contacted).

### D-11 `casefile doctor`
Decision: eight checks, always all printed, each one line
`doctor <check> PASS|FAIL <reason or number>`, then `doctor failed=<n> of 8`; exit 0 only when
`n == 0`, else 1 (argparse usage errors exit 2 before any check runs). A check whose precondition
failed prints `FAIL blocked by <check>`, never skip (Q6, Q11, skill rule "FAIL, never skip").
Order and rule for each:
1. `config`: `config.load` succeeds; reason on FAIL is the `ConfigError` text.
2. `folders`: for each of `matters`, `state`, `playbook`: exists or is created (matters and state
   only), then a probe file `.doctor-write-<pid>` is created and removed; FAIL names the first path
   and the OSError.
3. `playbook`: `playbook.load` succeeds; prints `version=pb-...`; FAIL is the `PlaybookError` text.
4. `runlog_schema`: `open_db` succeeds, `schema_version == 1`, trigger count == 8; prints
   `schema=1 triggers=8 (counted, exercised by the test suite)`.
5. `ollama_loopback`: `config.model.host` hostname is `127.0.0.1` (already enforced at load; checked
   again here against the live value); `GET /api/version` answers 200; then
   `lsof -nP -iTCP:<port> -sTCP:LISTEN` is run and its NAME column parsed: PASS iff at least one row
   and every row's local address is `127.0.0.1:<port>` or `[::1]:<port>`; FAIL `listening on
   *:<port>` when any row is `*:` or a non-loopback address; FAIL `no listener visible on <port>`
   when lsof prints no rows; FAIL `lsof failed: <stderr>` when lsof itself fails. The sandbox allows
   lsof over this user's processes (drift bullet). Prints `addr=127.0.0.1:18434`.
   Rejected: connecting to the LAN address and expecting ECONNREFUSED (EPERM in the sandbox, which is
   a denial, not a refusal, catalog #52 and #73; also meaningless on a Mac with no LAN); trusting the
   fake server's own report of its bind address (catalog #32, green against the stand-in).
6. `context`: one warmup chat (`messages = [{"role": "system", "content": "Reply with the single word
   READY."}, {"role": "user", "content": "casefile doctor warmup"}]`, `options.num_ctx =
   config.model.num_ctx`, never a literal) recorded as a run (`job='doctor'`, `card='doctor.warmup'`,
   `card_version = sha256(card text)[:12]`, `pages_in = 0`, the raw answer and the three count fields,
   `status='ok'` only when the whole predicate below holds, else `status='failed'` with a `failures`
   row naming the gate `doctor.context`), then `GET /api/ps`: PASS iff the configured model is listed
   with `context_length == config.model.num_ctx`, the warmup's `done_reason == "stop"`, and
   `content.strip() == "READY"` (the answer is checked, not only its shape; Codex finding 5); FAIL
   reasons `model not loaded`, `context_length=8192 want 65536`, `done_reason=length`,
   `answer=<first 40 chars> want READY`, or the `ModelError` text (the `empty` mode arrives as a
   `ModelError`, recorded as a failed run with no answer row). Prints `context_length=65536`.
7. `runlog_job`: `count_test_jobs()` increased by exactly one during this invocation; prints
   `test_jobs=+1` (a failed warmup leaves the count unchanged and this check FAILs `test_jobs=+0`).
8. `ocr`: `shutil.which(config.ocr.tesseract)` and `shutil.which(config.ocr.ocrmypdf)` both found
   and `tesseract --version` exits 0; FAIL `tesseract not found on PATH` on this Mac (Q11; stage 3
   replaces this with a real OCR of an invented image and keeps the FAIL path). The oracle the tests
   use for this check is `tests/conftest.py: ocr_expected_fail() -> bool`, which repeats the same
   three observations with its own `shutil.which` and `subprocess.run` calls (both binaries on PATH and
   `tesseract --version` exit 0), never one of them alone (Codex finding 13); on this Mac both binaries
   are absent, so the expected FAIL set is `{"ocr"}` either way.
Rejected: a `--expect-fail ocr` flag (an exemption by name, forbidden by the standing rules); running
the warmup without recording it (then the exit test's "records a test job" would need a second
code path, and the doctor's own `runlog_job` check would have nothing to count).

### D-12 Gate and the privacy rule
Decision: `gate.py: main(rows: Sequence[Row] | None = None, root: Path | None = None) -> int` runs
the five rows (all of them when `rows` is `None`; `root` defaults to the repo root found from
`__file__`), prints `gate <row> PASS|FAIL <number>` per row, then a final line that is only the
integer count of failed rows, and returns that integer; `__main__` is `raise SystemExit(main())`, so
the process exit code is the same integer, and `tests/test_gate.py` asserts the return value and a
subprocess's `returncode`, not only the printed line (Codex finding 15). `rows` and `root` exist for
the tests; the shipped command takes no arguments.
Rows:
1. `pytest`: `subprocess.run([sys.executable, "-m", "pytest", "-q"])` (both markers, so the socket
   tests run and FAIL where sockets are denied, D-13) with stdout and stderr inherited (not captured,
   so the run.sh cap is the only cap, catalog #91); number `exit=<code>`; PASS iff 0.
2. `privacy` (`privacy.py: scan(repo_root) -> list[str]`): the file list is `git ls-files -z
   --cached --others` run at the repo root: tracked files plus every untracked file, ignored ones
   included (`--exclude-standard` is deliberately absent: §0 measured that with it an ignored
   `Cases/c.txt` and `docs/d.pdf` are invisible, Codex finding 3). There is no exemption list: `.venv/`
   and `.uv/` are scanned too (§0: 0 forbidden suffixes among a pytest venv's 516 files, 1037 untracked
   paths in all, so the cost is a second). A path is an offender when (a) its suffix, lower-cased, is
   one of `.pdf`, `.doc`, `.docx`, `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.heic` and the path does
   not start with `tests/fixtures/`; or (b) the path starts with `Cases/` or `Bench/`. Prints
   `offenders=<n> scanned=<m>` and one `privacy offender <path>` line per offender. This is the ledger
   R1-10 rule applied to the checkout as it sits on disk, not to what git would commit: a client PDF
   dropped in `docs/` is an offender whether or not `.gitignore` would have stopped the commit.
   Content is not scanned in round 1 (no mechanical test for a real name exists; the rule in §6b is
   the control).
3. `rules_selftest`: for every rule in `playbook/rules.toml`, `check(rule.bad)` yields at least one
   finding with that rule's id and `check(rule.good)` yields none for it (`stamped=True`,
   `unit=rule.unit`); prints `misses=<a> false_hits=<b>`; PASS iff both 0 (catalog #101: the
   fixtures are proven to trip their own rule).
4. `playbook`: `playbook.load("playbook")` succeeds and the count of non-SAMPLE entries outside
   `rules.toml` is 0; prints `invalid=<0|1> unmarked=<n> version=pb-...`.
5. `prose` (`prose.py`): count of U+2013 and U+2014 characters in `*.md` at the root, `docs/**/*.md`,
   `.workflow/LEDGER.md`, `playbook/**/*.toml`, `src/**/*.py`, `tests/**/*.py`, `scripts/*`,
   `config.example.toml`, `pyproject.toml`; excludes `.claude/`, `cards/`, `reference/`, `schemas/`
   (pre-loop material the owner wrote; 0 dashes there today anyway); prints `dashes=<n> files=<m>`
   and `prose <file>:<line>` per hit. Baseline today 0 (drift bullet).
Rejected: the gate running `casefile doctor` directly (on this Mac the doctor exits 1 by design,
Q11; the exit test covers the doctor with an exact-set assertion tied to an independent fact, §6 C4);
a "known reds" list (catalog #81); parsing pytest's summary line for a count (the exit code is the
contract; a parse is one more thing to seed).

### D-13 Sandbox posture for socket tests (Q18)
Decision: a pytest marker `socket`, registered in `pyproject.toml` (`markers = ["socket: binds or
connects to 127.0.0.1"]`, with `--strict-markers` in `addopts`). Every test that binds or connects
carries it; there are five: fake HTTP smoke (R1-8), model client over HTTP and the proxy-environment
test (D-10), doctor `ollama_loopback` against `--bind 0.0.0.0` (R1-9), the stage 1 exit test (R1-11).
Everything else is in-process against `FakeTransport` or pure functions (rules, playbook, config, run
log, fake model logic, privacy, prose, the gate rows other than pytest). Codex builders, whose
`workspace-write` sandbox may deny sockets, run `scripts/run.sh pytest -q -m "not socket"` and quote
that command in their report; the orchestrator runs `scripts/run.sh pytest -q -m socket` itself in
the Claude Code sandbox (Q18 allows binding there; §0 notes this agent's sandbox still returned
`[Errno 1]`, so the orchestrator re-measures and, if denied, runs the five outside the sandbox and
labels those numbers in the round report). A socket test that meets `PermissionError` FAILS with the
errno in its message; there is no `pytest.skip`, no `skipif`, and no session exit (Q6; the session
exit of the first draft would have taken the in-process suite down with it, Codex finding 6). The
gate's `pytest` row runs the whole suite with both markers, so a denied sandbox shows as exactly five
failures and `exit=1` there.
Rejected: `pytest.skip` on EPERM (a skip is a pass never earned); mocking sockets (then the exit test
would not be end to end); an autouse bind-probe that exits the session (one denied socket must cost
five tests, not the suite).

### D-14 CLI surface this round
`casefile version`, `casefile config show [--config PATH]`, `casefile playbook show`, `casefile
doctor`. `--config PATH` on every subcommand overrides `CASEFILE_CONFIG`. argparse; unknown
subcommand exits 2. `casefile` with no arguments prints usage and exits 2.

### D-15 Exit code table (shipped numbers)
| Program | 0 | 1 | 2 | 3 | 96 | 97 | 98 |
|---|---|---|---|---|---|---|---|
| `scripts/run.sh` | child's | child's | child's | child's | no command given | output cap 52428800 hit | capture failure (mktemp, tee, head, wc) |
| `casefile doctor` | all 8 PASS | any FAIL | usage error | | | | |
| `casefile config show` etc. | ok | | usage or ConfigError | | | | |
| `python -m casefile.gate` | all rows PASS | 1 row FAIL | 2 rows | 3 rows (and so on, up to 5) | | | |
| `pytest` | green | failures (a denied socket is a failure, D-13) | usage | isolation precondition failed (D-5) | | | |
| `python -m tests.fakemodel` | clean stop | bind error | bad args or mode | | | | |

## §2 Work items, in build order

Format per item: files; numbers; CHECK (headless, prints the one number, and exits non-zero on FAIL:
a shell CHECK ends in a comparison, never in a bare `echo`, ledger line 19, Codex finding 14); SEED
(one-line mutation that must turn the CHECK red); pre-flight (catalog IDs; Librarian is blank).

How an item becomes a Codex run (Q14). The orchestrator writes one prompt file per item,
`.workflow/scratch/round01-prompts/R1-N.md`, holding in this order: the §6b privacy paragraph's first
sentence and the ledger's privacy line; the item's text below; the D-sections the item names, pasted
in full; the lane's file list from §3 with "edit nothing outside this list"; "no network; do not run
`uv sync`, `uv python install`, `git worktree` or `git push`; run `scripts/run.sh pytest -q -m 'not
socket'` and quote its last line; run the CHECK and the SEED and quote both outputs; prose has no em
or en dashes; commit on your lane's branch with the item id first in the message". Then:
`codex exec -s workspace-write -C <tree> "$(cat .workflow/scratch/round01-prompts/R1-N.md)"`. The
orchestrator re-runs the CHECK and the SEED afterwards and only then moves to the next item. Items
R1-9 to R1-11 name every file in their call graph because the Librarian is blank.

### R1-2 `scripts/run.sh` (lane A)
Files: `scripts/run.sh` (the D-3 text, executable bit set); `tests/test_run_sh.py`.
Numbers: CAP 52428800; exit 97 on cap; 96 on no command; 98 on capture failure; child's code otherwise.
CHECK (under bash):
`o=$(scripts/run.sh bash -c 'head -c 52428801 /dev/zero | tr "\0" a' 2>/dev/null | wc -c | tr -d ' ');
r=${PIPESTATUS[0]}; [ "$r:$o" = "97:52428800" ] && echo "PASS exit=$r bytes=$o" || { echo "FAIL
exit=$r bytes=$o"; exit 1; }` prints `PASS exit=97 bytes=52428800` and exits 0. Also
`scripts/run.sh bash -c 'exit 3'; [ $? -eq 3 ] && echo PASS || { echo FAIL; exit 1; }`, and the exact
cap: `o=$(scripts/run.sh bash -c 'head -c 52428800 /dev/zero | tr "\0" a' | wc -c | tr -d ' ');
r=${PIPESTATUS[0]}; [ "$r:$o" = "0:52428800" ] && echo PASS || { echo "FAIL $r:$o"; exit 1; }`, and
the capture failure: `TMPDIR=/nonexistent/dir scripts/run.sh true; [ $? -eq 98 ] && echo PASS || {
echo FAIL; exit 1; }`. `tests/test_run_sh.py` runs these four plus a stderr-only overflow and a
SIGKILL child (`exit=137`) through `subprocess.run` and asserts each pair (6 cases).
SEED: in `scripts/run.sh`, change `head -c "$((CAP + 1))"` to `head -c "$CAP"`; the first CHECK
prints `FAIL exit=0 bytes=52428800` and exits 1 (measured today on the prototype: seed exit 0).
Second seed: drop the `|| { ...; exit 98; }` after `mktemp`; the capture-failure CHECK prints `FAIL`.
Pre-flight: catalog #34 (one wrapper, caps output, real exit code), #41 (a wrapper reporting the
engine's code is still fail-open if the engine never ran: here `127` is relayed, not swallowed),
#26 (temp dir created and removed inside one invocation), #91 (children of children escape the cap;
the gate inherits stdout for this reason).

### R1-3 Skeleton (lane A; two steps, Codex then orchestrator)
Files: `pyproject.toml` (D-1 text plus the `socket` marker and `--strict-markers`, D-13),
`.python-version` (`3.12`), `.gitignore` (+ `.uv/`, `state/`), `src/casefile/__init__.py`
(`__version__ = "0.1.0"`), `src/casefile/cli.py` (`main() -> int`; `version` subcommand),
`tests/conftest.py` (D-5 fixtures: `isolated_config` with the conditional `playbook/` copy,
`production_dirs_untouched`, `write_config`, `ocr_expected_fail`; no socket probe), `tests/test_cli.py`
(version prints `casefile 0.1.0`; no args exits 2). Then, the orchestrator's step (network, outside
Codex): `scripts/run.sh uv python install 3.12` if needed, `scripts/run.sh uv sync`, commit `uv.lock`.
Numbers: Python 3.12.13; pytest 8.4.2; `uv sync` under 2 s warm (1.13 s measured at revision time).
CHECK (after the orchestrator's sync): `v=$(scripts/run.sh python -c 'import sys, casefile;
print(sys.version.split()[0], casefile.__version__)'); [ "$v" = "3.12.13 0.1.0" ] && echo "PASS $v"
|| { echo "FAIL $v"; exit 1; }`; `scripts/run.sh pytest -q -m "not socket"; [ $? -eq 0 ] && echo PASS
|| { echo FAIL; exit 1; }`; `[ "$(scripts/run.sh casefile version)" = "casefile 0.1.0" ] && echo PASS
|| { echo FAIL; exit 1; }`. R1-3 is green on its own: `playbook/` does not exist yet and
`isolated_config` points at an empty tmp directory (D-5; Codex finding 6).
SEED: change `requires-python` to `">=3.14"` and `.python-version` to `3.14`; after `uv sync` the first
CHECK prints `FAIL 3.14.6 0.1.0` and exits 1 (the wrong interpreter). Restore and re-sync. Second
seed: in `isolated_config`, write `matters` as the repo-root `Cases` path; the suite ends
`test isolation failed` with exit 3 before any test runs.
Pre-flight: catalog #64 (a fresh worktree lacks `.venv` and `.uv`: the orchestrator runs
`scripts/run.sh uv sync` in every worktree before any number is quoted), #52 (network denials for
`github.com`, `objects.githubusercontent.com`, `release-assets.githubusercontent.com`, `pypi.org`,
`files.pythonhosted.org` are sandbox facts to re-run with the host listed, not test failures), #111
(isolation is a precondition).

### R1-4 Config (lane A)
Files: `src/casefile/config.py` (`load`, `Config`, `ConfigError`, `KNOWN_KEYS`), `config.example.toml`,
`src/casefile/cli.py` (`config show`), `tests/test_config.py`.
Numbers: 3 tables, 10 keys; `num_ctx` minimum 65536; hostname must equal `127.0.0.1`; `matters`
required, absolute after `~`, outside the config file's directory.
CHECK: `tests/test_config.py::test_rejections` writes a config with `[model] hots = "x"` and asserts
`ConfigError` whose text contains `unknown key [model].hots`; then `num_ctx = 8192`; then a missing
file (`no config file`); then `host = "http://localhost:11434"`; then `name = ""`; then `matters`
omitted (`[paths].matters is required`); then `matters = "Cases"` (relative, resolves under the config
directory: `must be outside the checkout`). The test prints `rejected=7 of 7`. Headless:
`CASEFILE_CONFIG=/nonexistent scripts/run.sh casefile config show; [ $? -eq 2 ] && echo PASS || {
echo FAIL; exit 1; }`.
SEED: in `config.load`, replace the unknown-key raise with `continue`; `rejected=6 of 7`.
Pre-flight: catalog "Fail-open CLI default" (an unrecognised value falling back silently), #102
(an error sentinel that is also a legal value: the empty string for `name` must be rejected, test it),
#48 (the test holds its own literal `65536`, not `config.num_ctx`).

### R1-7 Run log (lane A)
Files: `src/casefile/runlog.py` (D-6), `tests/test_runlog.py`.
Numbers: schema version 1; 4 tables; 8 triggers; `test_jobs` count.
CHECK: `tests/test_runlog.py::test_append_only` inserts one row in each of the four tables through
the API, then attempts, in raw SQL, an `UPDATE` and a `DELETE` on each table (eight statements) and
asserts `sqlite3.DatabaseError` with message containing `append-only` on every one; prints
`blocked_writes=8 of 8` (Codex finding 17). `::test_test_job_count` records one doctor run with an
`ok` answer and one with `failed` and asserts `count_test_jobs() == 1`.
SEED: replace the body of `approvals_no_delete` with `SELECT 1`; the trigger count stays 8 and
`blocked_writes=7 of 8`.
Pre-flight: catalog "Probe certifies its own mechanism" (the test uses raw SQL, not the API, to
attempt the update), #96 (a completeness check on "non-empty" passes with one row: assert the
exact count 1, not `> 0`), #69 (invariant, not direction).

### R1-8 Stand-in model server (lane B, first)
Files: `tests/fakemodel/__init__.py`, `core.py` (`FakeModel`, `FakeTransport`), `server.py`,
`__main__.py` (argparse: `--bind`, `--port`, `--mode`, `--model`), `recordings.json`,
`tests/test_fakemodel.py`.
Numbers: port 18434; `context_length` 65536 (8192 in `short_context`); 6 modes; HTTP 400 for
`stream != false`; 404 for an unknown prompt.
CHECK (in-process, no socket): `tests/test_fakemodel.py::test_modes` sends the doctor warmup
through `FakeModel.handle` in each mode and asserts: replay `content == "READY"`, `done_reason ==
"stop"`, `prompt_eval_count == (len(system)+len(user))//4 + 8`; truncated `done_reason == "length"`
and `len(content) == len("READY")//2`; malformed `json.loads(content)` raises; forbidden content
contains `IME`; short_context `/api/ps` reports `8192`; empty `content == ""` with `done_reason ==
"stop"`; unknown messages 404; `stream: true` 400. Prints `modes_ok=6 of 6 refusals=2 of 2`. Socket
smoke (`::test_http_roundtrip`, marker `socket`): start on port 0, `urllib` POST, same assertions
for replay; prints `http_ok=1`; a `PermissionError` on bind is an assertion failure quoting the errno.
SEED: in `core.py`, make the truncated mode return `done_reason: "stop"`; `modes_ok=5 of 6`.
Pre-flight: catalog #32 (a stand-in's green is provisional: the recording format and the field names
are copied from Ollama's documented native response and will be re-checked on the Studio at stage
9; the brief records this in risk R-4), #62 (unknown fields in a request are refused, not dropped:
an unknown top-level key in `/api/chat` is 400), #72 (the accepted mode grammar is printed in the
400 body).

### R1-5 `rules.toml` and checker (lane B)
Files: `playbook/rules.toml` (D-7, four rules, invented examples), `src/casefile/rules.py`,
`tests/test_rules.py`.
Numbers: 4 rules; every `patterns` and `all_of` entry carries `\b`; the Bates body is a `fullmatch`;
`stamped=False` demotes cite findings to `warning`.
CHECK: `tests/test_rules.py::test_each_rule_goes_red` runs, per rule, forbidden outputs that are not
the rule's own `bad` example and asserts exactly that rule id appears on each: `no-dme-ime` on
`"the ime report"`, `"an Independent Medical Examination"` and `"two defense medical examinations"`
(Q16's four phrases, mixed case, plural); `no-hired-paid-retained` on `"Who retained you?"` and on
`"The employer hired Dr. Example. [cite ABC0001]"` (Codex finding 11: a direct statement, not a "by"
phrase, with a valid cite so no other rule fires); `treatment-and-bills-apart` on `"Describe your
treatment and the bills you received"` as `unit="question"`; `bates-cites` on `"[cite p. 12] gait
normal"`, `"[cite garbage ABC0001tail]"` and `"[cite ABC0001 and ABC0002]"` with `stamped=True`
(Codex finding 10). Prints `rules_red=9 of 9`. `::test_bates_accepts_fullmatch` asserts `"[cite
ABC0001] gait normal"`, `"[cite AB-00012]"` and `"[cite ABCDEFGH 123456]"` yield no finding.
`::test_bates_warning_when_unstamped` asserts `"[cite p. 12]"` with `stamped=False` yields severity
`warning`; `::test_good_examples_clean` asserts `check(good)` is empty for all four; `::test_boundary`
asserts `"time"`, `"Dimension"`, `"the report of 14 March"` and `"an examination"` produce no
finding; `::test_pattern_without_boundary_refused` asserts a rules file with `patterns = ['IME']`
fails to load, and that the shipped `playbook/rules.toml` loads (its `cite_pattern` and
`bates_pattern` are exempt from the boundary rule by kind, Codex finding 8).
SEED: in `rules.py`, drop `re.IGNORECASE`; `rules_red=8 of 9` (the lower-case "ime" case). Second
seed: change the Bates `fullmatch` to `search`; `rules_red=7 of 9` (`garbage ABC0001tail` and
`ABC0001 and ABC0002` pass).
Pre-flight: skill rule on substring checks (fail-open), catalog #69 (assert the exact rule id, not
"some finding"; a cite body is matched whole, not searched), #29 (two guards masking: the `bad`
example and the extra forbidden outputs are separate inputs so a rule whose pattern only matches its
own `bad` text is caught), #155 (a boundary case on either side: `time` clean, `IME` red).

### R1-6 Playbook loader (lane B)
Files: `src/casefile/playbook.py` (D-8), `playbook/samples/depo-goals.toml`,
`tests/fixtures/playbook/malformed-missing-why.toml`, `unmarked.toml`, `bad-date.toml`,
`tests/test_playbook.py`, `src/casefile/cli.py` (`playbook show`: lane A adds the two-line
subcommand after merge).
Numbers: 6 required fields; version `pb-` + 12 hex; 3 sample entries; 0 unmarked.
CHECK: `tests/test_playbook.py::test_malformed_fail_closed` copies `playbook/` to tmp, adds each
fixture in turn and asserts `PlaybookError` naming the file and field; prints `refused=3 of 3`.
`::test_version_moves` loads, appends one byte to the sample file, reloads, asserts the version
differs and has the form `pb-[0-9a-f]{12}`; prints `version_changed=1`. `::test_rules_file_entries_not_sample`
asserts the four rules load through the same loader with `sample` absent.
SEED: in `playbook.py`, make the missing-field check `if field not in entry and field != "why"`;
`refused=2 of 3`.
Pre-flight: catalog #108 (a version keyed on a description, not the bytes: hash the bytes), #35
(a loader that fails must leave no previous playbook in place: `load` returns a new object or
raises; it never mutates a shared one), #62 (unknown fields refused, not dropped).

### R1-9 `casefile doctor` (lane A, after the lane B merge)
Files: `src/casefile/doctor.py` (D-11: `run(config, *, out) -> int`, one function per check, `CHECKS`
tuple in order), `src/casefile/model.py` (D-10), `src/casefile/cli.py` (`doctor`), `tests/test_model.py`,
`tests/test_doctor.py`.
Numbers: 8 checks; exit 0/1; `context_length` equals `config.model.num_ctx` (65536 shipped); one
warmup run per invocation; the warmup answer must be `READY`.
Call graph the builder must read (Librarian blank): `config.py`, `runlog.py`, `model.py`,
`playbook.py`, `tests/fakemodel/core.py`, `tests/conftest.py`.
CHECK: `tests/test_doctor.py::test_fake_green_except_ocr` runs `doctor.run` against an in-process
`FakeTransport` (the loopback check is given an injected `lsof` runner returning one `127.0.0.1:18434`
row) and asserts that the eight check names each appear exactly once, in D-11 order, each with `PASS`
or `FAIL`, and that the FAIL set is exactly `{"ocr"}` when `ocr_expected_fail()` is true, else empty;
prints `verdicts=8 fails={'ocr'} expected={'ocr'}`. `::test_short_context_fails` sets mode
`short_context` and asserts `context` FAILs with `context_length=8192 want 65536`;
`::test_truncated_fails` asserts `done_reason=length`; `::test_empty_answer_fails` sets mode `empty`
and asserts `context` FAILs with a reason containing `empty` and that `count_test_jobs()` did not
rise (Codex finding 5); `::test_wrong_word_fails` uses a recording whose answer is `READY.` with a
trailing period and asserts `answer=READY. want READY`; `::test_loopback_star_fails` injects an lsof
row `*:18434` and asserts `ollama_loopback` FAIL `listening on *:18434`; `::test_nothing_skipped`
breaks the config and asserts all 8 lines print, 7 of them `FAIL blocked by config`;
`::test_records_one_job` asserts `count_test_jobs()` rose by exactly 1; `::test_uses_config_num_ctx`
writes a config with `num_ctx = 131072` against a fake whose `/api/ps` reports 131072 and asserts
`context PASS context_length=131072` and that the recorded warmup request carried
`options.num_ctx == 131072` (Codex finding 12). Socket test `::test_loopback_real_bind_all` (marker
`socket`) starts the fake with `--bind 0.0.0.0 --port 0` and runs the real lsof path, asserting FAIL.
SEED: in `doctor.py`, make check 6 compare `context_length >= 8192`; `test_short_context_fails`
goes red (prints `context PASS` where `FAIL` was expected). Second seed: drop the `content.strip() ==
"READY"` clause; `test_wrong_word_fails` goes red.
Pre-flight: catalog #52 and #73 (a denied probe is a FAIL with the errno, never a pass), #117 (a
missing measurement is a FAIL on its own line), #90 (a check that is off for a class prints like a
pass: no check is ever off), #80 (the exit test's expectation comes from `shutil.which`, not from
the doctor's own code), #25 (the loopback check's control: `--bind 0.0.0.0` must FAIL).

### R1-10 Gate and privacy (lane A)
Files: `src/casefile/gate.py` (D-12; `main() -> int`; `if __name__ == "__main__": raise
SystemExit(main())`), `src/casefile/privacy.py`, `src/casefile/prose.py`, `tests/test_privacy.py`,
`tests/test_prose.py`, `tests/test_gate.py`.
Numbers: 5 rows; final line is the failed-row integer and `main` returns it; privacy suffix set of 9;
prefix `tests/fixtures/` allowed; `Cases/`, `Bench/` forbidden; ignored files scanned.
Call graph the builder must read: `rules.py`, `playbook.py`, `tests/conftest.py`, `.gitignore`.
CHECK: `scripts/run.sh python -m casefile.gate; r=$?; [ $r -eq 0 ] && echo "PASS exit=$r" || { echo
"FAIL exit=$r"; exit 1; }` (the final printed line is `0` and the exit code is `0`).
`tests/test_privacy.py::test_offenders` builds a tmp git repo whose `.gitignore` is a copy of the
repo's, with `tests/fixtures/a.pdf` (allowed, committed), `docs/b.PNG` (offender, ignored and
untracked), `Cases/c.txt` (offender, ignored and untracked, not force-added: the scan must find it
anyway, Codex finding 3), `Bench/k.md` (offender), `docs/tests/fixtures/x.pdf` (offender: a substring
match would pass it), `notes.md` (clean, committed), `.venv/lib/site.py` (clean, ignored) and asserts
`scan()` returns exactly the sorted four offenders; prints `offenders=4 expected=4 scanned=7`. The
fixture files are zero-byte invented placeholders created by the test, never committed.
`tests/test_prose.py` writes a tmp file with one U+2014 and asserts `dashes=1`.
`tests/test_gate.py::test_return_value` calls `gate.main(rows=<the four non-pytest rows>,
root=<tmp repo>)` with a clean tmp repo and asserts the return value is `0` and the last printed line
is `0`; then adds `docs/b.PNG` to the tmp repo and asserts the return value is `1` and the last line
`1`. `::test_process_exit_code` runs `subprocess.run([sys.executable, "-c", "from casefile import
gate; raise SystemExit(gate.main(rows=gate.ROWS_WITHOUT_PYTEST, root=<tmp repo with one offender>))"])`
and asserts `returncode == 1` (Codex finding 15: the printed count and the process code are two
different things and each is asserted).
SEED: in `privacy.py`, add `--exclude-standard` to the `git ls-files` call; `offenders=2 expected=4`
(`Cases/c.txt` and `docs/b.PNG` vanish). Second seed: change `path.startswith("tests/fixtures/")` to
`"tests/fixtures" in path`; `offenders=3 expected=4`. Third seed: make `main` `return 0` after the
print; `test_return_value` and `test_process_exit_code` go red while the printed line still reads `1`.
Pre-flight: catalog "Dispatcher default overriding exit code" (the exit code is computed once from
the row list), #74 (the chair reads every row line, not only the final integer), #81 (no known-reds
list), #91 (pytest output inherited, not captured), "presence-anywhere" (prefix, not substring).

### R1-11 Stage 1 exit test (lane A, last)
Files: `tests/test_stage1_exit.py`.
Numbers: doctor exit 1 on this Mac (0 where tesseract and ocrmypdf both work); FAIL set `{"ocr"}` (or
empty); 8 verdicts; `test_jobs=1`. Marker `socket`.
Call graph the builder must read: `doctor.py`, `cli.py`, `runlog.py`, `tests/fakemodel/server.py`,
`tests/conftest.py`, `scripts/run.sh`.
CHECK: the test starts the fake server in-process on `127.0.0.1:0`, writes a config in tmp with that
host and port (`matters` under tmp), runs `subprocess.run(["scripts/run.sh", "casefile", "doctor"],
cwd=repo_root, env={..., "CASEFILE_CONFIG": tmp_config}, capture_output=True, text=True)`, computes
`expected = {"ocr"} if ocr_expected_fail() else set()` (D-11 check 8: both binaries and a working
`tesseract --version`, Codex finding 13), parses the `doctor ...` lines and asserts the eight check
names each appear exactly once, in order, each with `PASS` or `FAIL` (Codex finding 16), asserts the
FAIL set equals `expected` and `returncode == (1 if expected else 0)`, opens the tmp run log and
asserts `count_test_jobs() == 1`; prints `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`. Headless
equivalent for the verifier: `scripts/run.sh pytest -q -m socket tests/test_stage1_exit.py -s; [ $?
-eq 0 ] && echo PASS || { echo FAIL; exit 1; }`.
SEED: in `doctor.py` check 6, remove the `runlog.record_answer(...)` call; `test_jobs=0` red. Second
seed: make check 8 return PASS unconditionally; `fails=set() expected={'ocr'}` red on this Mac. Third
seed: skip printing the `folders` line when it passes; `verdicts=7` red while the FAIL set and the
exit code are unchanged.
Pre-flight: catalog #86 (the test quotes its exact command line in its failure message), #79 (the
shipped input, `playbook/` as committed, is what the doctor loads here, not a synthetic copy: the
tmp config's `playbook` path points at the repo's `playbook/` for this one test), #84 (the guarded
path, recording the answer, runs on this fixture by construction).

## §3 Parallelisation map

Two lanes at most, both Codex (Q14). Lane A works on `loop/round-01` in the main checkout
(`codex exec -s workspace-write -C /Users/davidskoranski/legal-harness`); lane B in a worktree the
orchestrator creates with `git worktree add ../legal-harness-laneB loop/round-01-laneB` from lane A's
R1-3 commit, then `scripts/run.sh uv sync` inside it (network, orchestrator only), then
`codex exec -s workspace-write -C ../legal-harness-laneB` (B needs `pyproject.toml`, `uv.lock` and
`src/casefile/__init__.py` to exist; it never edits them). Both lanes report with `pytest -q -m "not
socket"`; the orchestrator runs the `socket` marker (D-13).

Lane A owns: `scripts/run.sh`, `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`,
`config.example.toml`, `src/casefile/__init__.py`, `cli.py`, `config.py`, `runlog.py`, `model.py`,
`doctor.py`, `gate.py`, `privacy.py`, `prose.py`, `tests/conftest.py`, `tests/test_run_sh.py`,
`test_cli.py`, `test_config.py`, `test_runlog.py`, `test_model.py`, `test_doctor.py`, `test_privacy.py`,
`test_prose.py`, `test_gate.py`, `test_stage1_exit.py`.
Lane B owns: `src/casefile/rules.py`, `src/casefile/playbook.py`, `playbook/**`, `tests/fakemodel/**`,
`tests/fixtures/playbook/**`, `tests/test_rules.py`, `tests/test_playbook.py`, `tests/test_fakemodel.py`.
Shared files: `pyproject.toml` and `src/casefile/cli.py` belong to lane A only; lane B adds no
dependency and no subcommand (the `playbook show` subcommand is lane A's two lines after the merge).
`tests/conftest.py` belongs to lane A; lane B keeps its fixtures inside its own test modules.
Merge rule: `git diff --name-only <A-base>...loop/round-01-laneB` must list only lane B's paths;
anything else rejects the merge (risk R-7).

Sequence: orchestrator logs the §6 rulings as spec §9 rows D12 to D21 (before any code, SKILL.md step
5; Codex finding 2). A: R1-2, R1-3 (Codex writes, orchestrator syncs and commits `uv.lock`; B branches
here), R1-4, R1-7 in parallel with B: R1-8, R1-5, R1-6. Then merge B into A. Then A alone: R1-9
(imports `model.py`, `playbook.py`, uses `tests/fakemodel`), R1-10 (rows call `rules.py`,
`playbook.py`, `privacy.py`, `prose.py`), R1-11. R1-9 to R1-11 are sequential because each consumes
the previous item's module and the exit test is the integration of all of them. The orchestrator runs
`scripts/run.sh uv sync` in lane B's worktree before B's first run (catalog #64); each lane commits at
each item (catalog #83). The chair touches neither tree while a lane is live (catalog #53).
Stopping point (Q15): after R1-11's CHECK and seeds pass and the gate prints `0`, the session writes
`docs/loop/HANDOFF.md` and `docs/loop/next-round.md` and stops with round 1 unmerged on
`loop/round-01`; no code review, no critic, no merge, no §11 as-built update this session. The next
session runs the critic round and R1-12.

## §4 Test design

Regression set after round 1 (all under `scripts/run.sh pytest -q`, which the gate's `pytest` row runs):
`test_run_sh.py` (6 cases: cap+1, exact cap, exit 3, capture failure, stderr overflow, SIGKILL),
`test_cli.py` (2), `test_config.py` (7 rejections plus `config show` sources), `test_runlog.py`
(append-only 8 of 8, test-job count, schema version), `test_fakemodel.py` (6 modes, 2 refusals, 1 HTTP
smoke [socket]), `test_rules.py` (9 red, Bates fullmatch accepts, 4 clean, boundary, unstamped
warning, boundary-less pattern refused and shipped file loads), `test_playbook.py` (3 refused, version
moves, rules file loads), `test_model.py` (client over `FakeTransport`: fields parsed, 404 raises,
non-JSON raises, empty raises, no proxy handler, redirect refused; 2 [socket]: plain HTTP and the
proxy environment), `test_doctor.py` (9 in-process, 1 [socket]), `test_privacy.py`, `test_prose.py`,
`test_gate.py` (return value, process exit code), `test_stage1_exit.py` (1 [socket], end to end).
Five `socket` tests in all; `pytest -q -m "not socket"` is the builders' command and
`pytest -q -m socket` the orchestrator's; the gate runs both.

The stage 1 exit test is driven through `scripts/run.sh` twice: the suite is `scripts/run.sh pytest
-q`, and inside it `test_stage1_exit.py` spawns `scripts/run.sh casefile doctor`, so the doctor's
output passes the cap and its exit code comes back through `PIPESTATUS[0]`. Its expected FAIL set is
derived from `ocr_expected_fail()` (both OCR binaries on PATH and `tesseract --version` exit 0,
observed by the test itself), an observation independent of the doctor's code, so on this Mac it is
`{"ocr"}` and on a Studio with working OCR it is empty with no code change (catalog #80).

Baselines to record at close (ledger "Regression baselines: set in round 2" stays; round 1 only
records the numbers): gate final line `0`; doctor on this Mac `failed=1 of 8`; pytest count.

Every CHECK above was designed so a verifier can run it from the ledger wording alone; each item's
SEED is a one-line edit the verifier can apply and revert byte-identically (`git stash` or
`git checkout -- <file>`).

## §5 Risks, each with a tripwire

- R-1 A sandbox denies sockets (Claude Code's: measured `[Errno 1]` today even with Q18's setting
  present in `.claude/settings.json`; Codex `workspace-write`: unmeasured, assumed denied). Tripwire:
  `scripts/run.sh pytest -q -m socket` shows five failures each quoting `[Errno 1]`; the gate's
  `pytest` row reads `exit=1`. Resolution: the orchestrator re-measures the bind in its own sandbox;
  if denied, it runs the five socket tests outside the sandbox and labels those numbers in the round
  report. Builders never run the `socket` marker. No skip.
- R-11 Codex `workspace-write` denies something a builder needs (a write under `$TMPDIR`, `lsof`, a
  `git commit`). Tripwire: a Codex run reports `Operation not permitted` or ends without the commit it
  was told to make; the orchestrator reads the transcript, and if the denial is on a path or tool
  outside the tree, performs that one step itself and records it in the agent log. No
  `--dangerously-bypass-approvals-and-sandbox`.
- R-12 A proxy environment variable on the Studio (`http_proxy`, `all_proxy`) is set for some other
  tool. Tripwire: none needed in code (D-10's opener ignores them, and `test_model.py`'s
  proxy-environment test proves it); the doctor's `ollama_loopback` check would still FAIL if the
  listener were not loopback.
- R-2 Network hosts for uv. Tripwire: a `<sandbox_violations>` block naming `github.com`,
  `objects.githubusercontent.com`, `release-assets.githubusercontent.com`, `pypi.org` or
  `files.pythonhosted.org`; re-run with the host listed. `releases.astral.sh` denied is harmless
  (measured: install succeeded).
- R-3 lsof cannot see the Studio's Ollama (if it runs as another user). Tripwire: `doctor
  ollama_loopback FAIL no listener visible on 11434` on the Studio while `/api/version` answers.
  Q19 left how Ollama runs undecided (question 7 stays open); the check stays honest either way.
- R-4 Ollama's real `/api/ps` or `/api/chat` differs from the fake (field absent or renamed).
  Tripwire: `doctor context FAIL context_length missing in /api/ps` or `ModelError` on the Studio at
  stage 9; the fake is corrected then, and the recording format re-checked (catalog #32).
- R-5 A child that ignores EPIPE after the cap blocks `run.sh`. Tripwire: `test_run_sh.py` has a
  Python child that catches `BrokenPipeError`, sleeps 1 s, exits; the wrapper must return 97 within
  5 s. A child that never exits is not covered; a wall-clock ceiling is round 2's item.
- R-6 `\bDME\b` hits "durable medical equipment" in legitimate output. Tripwire: a `no-dme-ime`
  finding whose excerpt is followed by `supplier`, `equipment` or `provider` in any stage 4+ run;
  tuning question T-1.
- R-7 Lane B touches a lane A file. Tripwire: the merge-rule diff lists a path outside B's set;
  the orchestrator rejects and asks B to revert that file.
- R-8 Two nested `run.sh` invocations in the exit test. Tripwire: the inner wrapper's cap notice
  appears in the outer output; none expected (`doctor` prints under 2 KB).
- R-9 The playbook version changes on every commit that touches `playbook/`, so a run log from
  another day cannot be reproduced without the commit. Tripwire: none this round; stage 6 stores
  the playbook snapshot by version.
- R-10 `tee` and `head` behaviour differs on the Studio's macOS version. Tripwire:
  `test_run_sh.py` is in the gate; a different BSD build shows as a failed cap case there.

## §6 Contradictions and rulings (pending veto, Q7)

Each becomes a spec §9 row before any code is written (SKILL.md step 5; the first draft deferred
them to R1-12, Codex finding 2, and Q15 moves R1-12 to the next session, so the rows would have
trailed the code by a day). The orchestrator writes rows D12 to D21 as its first act of the build; the
proposed row text is the "new" column. R1-12 then only updates §11 as-built and the records.

Owner rulings received after the first draft, each applied above:
- Q14: builder is Codex gpt-6.1-sol via `codex exec -s workspace-write`, no network; items are
  self-contained prompts (§2 preamble); lanes disjoint; lane B in a worktree; the orchestrator does
  every network step and re-runs every CHECK and seed (§3). Old: Sonnet 5.5 sub-agents.
- Q15: no code review this session; build, then stop unmerged on `loop/round-01` (§3 stopping
  point). Old: critic round and close in this session.
- Q16: rule 5 blocks "DME", "IME", "independent medical examination", "defense medical examination",
  whole words, any case, on outputs only (D-7). Old: acronyms only, pending question 4. C2 closed.
- Q17: `[paths].matters` is required, outside the checkout, set in `config.toml`; tests use tmp
  (D-4, D-5). Old: default `Cases/` inside the checkout.
- Q18: `allowLocalBinding: true` is set; socket tests are a separate `socket` marker the orchestrator
  runs, failing (never skipping) when denied; everything else is in-process (D-13). Old: a session
  exit on EPERM.
- Q19: Ollama's user on the Studio undecided; the `lsof` loopback check is built for the login-user
  app case (D-11 check 5, risk R-3 stays). Question 7 stays open.
- Q20: `[model].name = "qwen3.8:27b"` (D-4). Q21: `bates_pattern = '[A-Z]{1,8}[ -]?\d{4,}'` in
  `playbook/rules.toml`, where the owner edits it (D-7).

- C1 Spec §5 "Ollama on 127.0.0.1 only". Old: unspecified method. New: `casefile doctor` checks
  the configured hostname is `127.0.0.1`, that `/api/version` answers there, and that `lsof` shows
  every listener on the port bound to a loopback address. Why: the LAN connect probe is EPERM in the
  sandbox (a denial that reads as a refusal) and meaningless off-network. Row D19.
- C2 Spec §4 rule 5 versus `cards/_core.md:10`. Resolved by Q16: all four phrases, on outputs only.
  The spec §4 rule 5 text gains the two spelled-out phrases in row D16.
- C3 Ledger `## Project`: "page screenshots with Playwright". New: no Playwright dependency until
  stage 8; `casefile.shots` is not built. Why: zero pages this round (D-2). Not a §9 row; a note in
  the round report and HANDOFF.
- C4 Q11 ("doctor reports OCR as FAIL until stage 3") against R1-10 ("gate prints 0 when green").
  New: the gate does not run `casefile doctor`; the stage 1 exit test asserts the doctor's FAIL set
  equals exactly the set implied by `ocr_expected_fail()` (both OCR binaries present and `tesseract
  --version` exit 0), and that test is in the gate's `pytest` row. Why: a by-name exemption is
  forbidden; an exact-set invariant tied to an independent fact is not an exemption (catalog #69,
  #80). Row D20.
- C5 Q12 extension. New: a gate row fails on any non-SAMPLE entry outside `rules.toml`, until the
  owner adds practice content (then the row is retired by a §9 row, not loosened). Row D17.
- C6 R1-4 "one config file with defaults". New: defaults apply to omitted keys inside an existing
  file; a missing file is a `ConfigError`. Why: pillar 2 on the Studio (D-4). Row D13.
- C7 Spec §5 host. New: `model.host` must be `http://127.0.0.1:<port>`; `localhost` is rejected at
  load. Why: DNS resolution of `localhost` is a second path off the box. Row D13.
- C8 `project-contract.md` harness block names `casefile bench ... --runs 1`, `casefile demo`,
  `python -m casefile.shots`. New: not this round (stages 2, 5, 8). Note only.
- C9 R1-7 "records a test job". New: a test job is the doctor's warmup run as defined in D-6.
  Row D15.
- C10 R1-8 port. New: the stand-in listens on 18434, not Ollama's 11434. Why: the Studio must never
  have a test server on the model's port. Row D18.
- C11 Spec §4 rule 5 "Bates cites". Old: a cite "contains" a Bates number. New: a cite's body is
  exactly one Bates number (`re.fullmatch`); "every fact carries a cite" is gate 6's job at stage 4,
  not the round 1 text checker's. Why: presence-anywhere certifies malformed cites (Codex 10); a
  text-level no-cite finding contradicts every clean example (Codex 9). Row D16.
- C12 Pillar 3 against `urllib`'s defaults. New: the model client's opener has `ProxyHandler({})` and
  refuses redirects; an empty `message.content` is a `ModelError`. Why: the default opener reads
  `http_proxy` and follows 3xx (§0 measured both handlers present). Row D21.
- Proposed rows: D12 run.sh cap mechanics and codes 96/97/98; D13 config location, format,
  fail-closed rules, `matters` required and outside the checkout (Q17), model tag (Q20); D14 data
  root outside the checkout, `state/` in the checkout, `Cases/` and `Bench/` forbidden prefixes; D15
  run log schema v1, append-only triggers, test job; D16 rules.toml schema and detection semantics
  (Q16 phrases, outputs only, Bates fullmatch, Q21 pattern configurable); D17 playbook entry format,
  SAMPLE marker, version hash, no-unmarked gate row; D18 stand-in server shape, port, six modes; D19
  doctor checks (warmup answer `READY`, `num_ctx` from config, OCR oracle) and exit codes; D20 gate
  rows, privacy rule over ignored files too, exit code equals the failed-row count, doctor coverage
  via the exit test; D21 model client transport: no proxy, no redirect, empty answer is an error.

## §6b Privacy

Every fixture this round adds is invented and content-free of real matters: the four rule examples
in `playbook/rules.toml` (generic sentences, no names, an invented date), the three SAMPLE entries in
`playbook/samples/depo-goals.toml` (an invented defense doctor named "Dr. Example"; no case, no
employer, no claimant), the forbidden-output sentences in `tests/test_rules.py` (the same "Dr.
Example", an unnamed employer, invented Bates numbers such as `ABC0001`), the recordings in
`tests/fakemodel/recordings.json` (the warmup prompt, the word `READY`, and one `READY.` variant for
the wrong-word test), the three malformed playbook fixtures, and the zero-byte placeholder files the
privacy test creates in a temporary git repository and never commits. No PDF, Word file or image is
added anywhere, including under `tests/fixtures/`. No real client record, name or fact appears in any
prompt, test, recording or document. Every builder prompt carries this paragraph's first sentence and
the ledger's privacy line verbatim.

## §7 Questions only the owner can answer

Questions 2 to 7 were appended to `docs/loop/questions-for-owner.md` with the first draft and are
ANSWERED (its "Answered 2026-10-25" block): 2 -> Q20, 3 -> Q17, 4 -> Q16, 5 -> Q21, 6 -> Q18, 7 -> Q19
(the owner has not decided; the brief builds for the login-user case and the question stays open in
that file). The Codex review raised no question only the owner can answer (§8 has no OWNER row), so
nothing new is appended this revision. Tuning questions T-1 to T-4 stand in `docs/loop/tuning-questions.md`;
T-1's premise changed (Q16 blocks "DME" in outputs regardless of meaning), so T-1 now watches false
hits on durable medical equipment rather than asking the owner's preference, and T-2's pattern list is
the broader D-7 list.

2. (answered, Q20) The Ollama model tag: `qwen3.8:27b`.
3. (answered, Q17) Matters live outside the checkout, set in `config.toml`.
4. (answered, Q16) Rule 5: all four phrases, whole words, any case, outputs only.
5. (answered, Q21) Bates: `[A-Z]{1,8}[ -]?\d{4,}`, configurable in `rules.toml`.
6. (answered, Q18) `allowLocalBinding: true` is set; socket tests are a separate marker.
7. (answered as "undecided", Q19) Ollama's user on the Studio; built for the login-user app case.

## §8 Codex dispositions

Review: `.workflow/scratch/round01-brief-codex.md` (tracked copy `docs/loop/round-01/`). Each finding
was checked against the files or measured before acceptance; "measured" numbers are in §0.

| # | Disposition | Evidence or change |
|---|---|---|
| 1 | ACCEPTED | Ledger `## Clarified` now reaches Q21 (LEDGER.md:58 to 76). Header rewritten for Q14 and Q15; §2 preamble gives the Codex prompt contract; §3 gives the worktree commands and the stopping point; §6 lists every ruling applied. |
| 2 | ACCEPTED | `app-loop/SKILL.md:77` to 79: rulings logged in spec §9 "before any code is written". §6 opening and §3 sequence: the orchestrator writes rows D12 to D21 first; R1-12 keeps only §11 and the records. |
| 3 | ACCEPTED | Measured in a throwaway repo: `git ls-files --cached --others --exclude-standard` omits ignored `Cases/c.txt` and `docs/d.pdf`; without `--exclude-standard` both are listed. A pytest venv has 0 forbidden suffixes in 516 files, so no exemption list is needed. D-12 row 2 and R1-10 rewritten (ignored files scanned; test adds ignored, not force-added, offenders; new seed restores `--exclude-standard`). |
| 4 | ACCEPTED | Measured: `build_opener().handlers` includes `ProxyHandler` and `HTTPRedirectHandler`; `getproxies()` here returns the sandbox proxy for `http`. The bypass of 127.0.0.1 is an environment fact (`no_proxy`), not a client property. D-10: `ProxyHandler({})` plus a redirect handler that raises; two in-process tests and one socket proxy-environment test; §6 C12, row D21; risk R-12. |
| 5 | ACCEPTED | D-10 brief text raised only on a missing `message.content`; D-11 check 6 compared shape only. D-10: empty or whitespace content is `ModelError`; D-11 check 6 requires `content.strip() == "READY"` and records `status='failed'` plus a `failures` row otherwise; D-9 adds mode `empty` (six modes); R1-9 adds `test_empty_answer_fails` and `test_wrong_word_fails` with a seed. |
| 6 | ACCEPTED | Brief had `isolated_config` copy `playbook/` (created by lane B at R1-5) and an autouse session exit on EPERM, so R1-3 could not be green and one denied socket took the suite down. D-5: `copytree` only when `playbook/` exists, else an empty dir; D-13: no session exit, a `socket` marker with five tests that FAIL on EPERM (also Q18). R1-3 text says it is green on its own. |
| 7 | ACCEPTED | Catalog #111 (catalog.md:540): "a failed isolation precondition stops the probe before any write". D-5: `isolated_config` asserts the written config's three paths are under tmp before yielding (`pytest.exit` code 3 otherwise), and the post-check snapshots every file's path, size and `st_mtime_ns` recursively, not a directory mtime. R1-3 gains a second seed (`matters` pointed at the repo). |
| 8 | ACCEPTED | D-7 said "every pattern must contain `\b` or an anchor" while `cite_pattern` and `bates_pattern` had neither. D-7: the boundary rule applies to `patterns` and `all_of`; `cite_pattern` is bounded by its literal brackets; `bates_pattern` is applied with `fullmatch`. R1-5's refusal test also asserts the shipped file loads. |
| 9 | ACCEPTED | D-7's `no-cite` finding contradicted `test_good_examples_clean` and `test_boundary`. D-7: no finding for a unit without a cite in round 1; "every fact carries a cite" is spec §4 gate 6 at stage 4 (fact units). §6 C11. |
| 10 | ACCEPTED | D-7: the cite body (group 1 of `cite_pattern`, stripped) must `fullmatch` `bates_pattern`; R1-5 adds `[cite garbage ABC0001tail]` and `[cite ABC0001 and ABC0002]` as red cases, `test_bates_accepts_fullmatch` as the control, and a `search` seed. |
| 11 | ACCEPTED | `\b(hired|paid|retained|referred) by\b` does not match "The employer hired Dr. Example." D-7 patterns broadened (bare `hired`, `hires`, `hiring`, `retained`, `retains`, `retaining`; `paid for the doctor`; `who pays`; `referred by the defense`); R1-5 adds that sentence with a valid cite as a red case; T-2 watches false hits. |
| 12 | ACCEPTED | spec.md:80 says `num_ctx` 65536 "in the Modelfile and on every call", not a floor. D-4 wording corrected (65536 is the shipped value; larger accepted only for a pillar 6 benchmark); D-11 check 6 reads `config.model.num_ctx` instead of a literal; R1-9 adds `test_uses_config_num_ctx` at 131072. |
| 13 | ACCEPTED | D-11 check 8 needs both binaries and `tesseract --version` exit 0; R1-9 and R1-11 oracles used `shutil.which("tesseract")` alone. New `tests/conftest.py: ocr_expected_fail()` repeats all three observations; D-11, R1-9, R1-11, §4 and §6 C4 use it. On this Mac both binaries are absent (§0), so the expected set is unchanged here. |
| 14 | ACCEPTED | LEDGER.md:19: a check "exits non-zero on FAIL". R1-2, R1-3, R1-4, R1-10 and R1-11 shell CHECKs now end in a comparison and `exit 1`; the §2 preamble states the rule. |
| 15 | ACCEPTED | D-12: `main(rows=None, root=None) -> int` returns the count; `__main__` is `raise SystemExit(main())`; R1-10's `test_return_value` asserts the return value and `test_process_exit_code` asserts a subprocess `returncode == 1` against a tmp repo with one offender; third seed `return 0` after the print. |
| 16 | ACCEPTED | R1-11 and R1-9 `test_fake_green_except_ocr` assert the eight check names each appear exactly once, in order, with `PASS` or `FAIL`; R1-11 gains a third seed (suppress the `folders` PASS line). |
| 17 | ACCEPTED | R1-7 `test_append_only` attempts `UPDATE` and `DELETE` on all four tables (`blocked_writes=8 of 8`); the seed is a trigger body replaced by `SELECT 1` (count stays 8, writes 7 of 8); D-6 and D-11 check 4 say the doctor's count is a count. |
| 18 | ACCEPTED | Measured: `mktemp -d` under an unwritable `TMPDIR` returns 1 with an empty `tmp`, then `tee "$tmp/out"` fails and `wc` fails; the draft returned the child's `0`. D-3: `mktemp` guarded, non-numeric byte count and non-zero capture stages exit 98 when the cap was not hit; measured capture stages are `0 0 0` at CAP, CAP+1 and 60 MiB, so 98 never fires on a healthy pipe. R1-2 CHECK and `test_run_sh.py` gain the capture-failure case; D-15 gains column 98. |

Counts: 18 ACCEPTED, 0 REJECTED, 0 OWNER. Codex's three insisted-on changes map to findings 1 and 2
(contract), 3, 4, 5 and 7 (privacy and success paths), 6, 8 to 11, 14 to 16 (acceptance), all taken.
