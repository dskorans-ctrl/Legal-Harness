"""Eight explicit local readiness checks and one logged model warmup."""

from dataclasses import dataclass, field
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit

from . import config as configuration, intake, pdfsmoke, playbook, quotes, runlog
from . import stamps as stamp_finder
from .model import ModelClient


CHECKS = ("config", "folders", "playbook", "runlog_schema", "ollama_loopback",
          "context", "runlog_job", "ocr")
CARD_TEXT = "Reply with the single word READY."
SMOKE_LINE = "CASEFILE OCR SMOKE 7342"
SMOKE_STAMP = "SMOKE7342"
SMOKE_TIMEOUT_S = 120
MESSAGES = [{"role": "system", "content": CARD_TEXT},
            {"role": "user", "content": "casefile doctor warmup"}]


@dataclass
class State:
    source: object
    opener: object = None
    runner: object = subprocess.run
    ocr_smoke: object = None   # None runs the real tools (REAL); tests inject a callable
    config: object = None
    book: object = None
    log: object = None
    before: int = 0
    passed: dict = field(default_factory=dict)
    root: dict = field(default_factory=dict)   # check name -> the check whose own failure caused it


def check_config(state):
    state.config = (state.source if isinstance(state.source, configuration.Config)
                    else configuration.load(state.source))
    return True, f"source={state.config.source}"


def check_folders(state):
    for name in ("matters", "state", "playbook"):
        path = getattr(state.config.paths, name)
        try:
            if name == "state":
                path.mkdir(parents=True, exist_ok=True)
            elif name == "matters" and not path.is_dir():
                return False, f"matters folder not found: {path}"
            probe = path / f".doctor-write-{os.getpid()}"
            with probe.open("x"):
                pass
            probe.unlink()
        except OSError as exc:
            return False, f"{path}: {exc}"
    return True, "writable=3 of 3"


def check_playbook(state):
    state.book = playbook.load(state.config.paths.playbook)
    return True, f"version={state.book.version}"


def check_runlog_schema(state):
    state.log = runlog.open_db(state.config.paths.state / "runlog.sqlite")
    count = state.log.connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'"
    ).fetchone()[0]
    state.before = state.log.count_test_jobs()
    version = state.log.schema_version
    return version == 1 and count == 15, f"schema={version} triggers={count} (counted)"


def check_ollama_loopback(state):
    host = urlsplit(state.config.model.host)
    if host.hostname != "127.0.0.1":
        return False, f"hostname={host.hostname} want 127.0.0.1"
    ModelClient(state.config.model, state.opener).get("/api/version")
    port = host.port or 80
    result = state.runner(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
                          capture_output=True, text=True, timeout=30, check=False)
    lines = result.stdout.splitlines()
    # lsof returns 1 without stderr when there are no matching listeners.
    if result.returncode and (result.stderr.strip() or result.returncode != 1):
        return False, f"lsof failed: {result.stderr.strip() or result.returncode}"
    addresses = []
    for line in lines:
        columns = line.split()
        if not columns or columns[0] == "COMMAND":
            continue
        if len(columns) < 9 or columns[-1] != "(LISTEN)":
            return False, f"lsof failed: malformed listener row {line}"
        addresses.append(columns[-2])
    if not addresses:
        return False, f"no listener visible on {port}"
    for address in addresses:
        if address not in {f"127.0.0.1:{port}", f"[::1]:{port}"}:
            return False, f"listening on {address}"
    return True, f"addr=127.0.0.1:{port}"


def check_context(state):
    log = state.log
    run_id = log.start_run(job="doctor", card="doctor.warmup",
                           card_version=hashlib.sha256(CARD_TEXT.encode()).hexdigest()[:12],
                           playbook_version=state.book.version, model=state.config.model.name,
                           pages_in=0, prompt_sha256=hashlib.sha256(
                               json.dumps(MESSAGES, sort_keys=True).encode()).hexdigest())
    answer = None
    ok = False
    try:
        client = ModelClient(state.config.model, state.opener)
        answer = client.chat(MESSAGES, options={"num_ctx": state.config.model.num_ctx})
        models = client.get("/api/ps").get("models")
        if not isinstance(models, list):
            raise ValueError("context_length missing in /api/ps")
        loaded = next((m for m in models if isinstance(m, dict)
                       and m.get("name") == state.config.model.name), None)
        if loaded is None:
            reason = "model not loaded"
        elif "context_length" not in loaded:
            reason = "context_length missing in /api/ps"
        else:
            context_length = loaded["context_length"]
            context_ok = type(context_length) is int and context_length == state.config.model.num_ctx
            answer_ok = answer.content.strip() == "READY"
            counts_ok = all(type(count) is int and count > 0
                            for count in (answer.prompt_eval_count, answer.eval_count))
            ok = context_ok and answer.done_reason == "stop" and answer_ok and counts_ok
            if not context_ok:
                reason = f"context_length={context_length} want {state.config.model.num_ctx}"
            elif answer.done_reason != "stop":
                reason = f"done_reason={answer.done_reason}"
            elif not counts_ok:
                reason = "prompt_eval_count and eval_count must be positive integers"
            elif not answer_ok:
                reason = f"answer={answer.content[:40]} want READY"
            else:
                reason = f"context_length={context_length}"
    except Exception as exc:
        reason = str(exc)
    if answer is not None:
        log.record_answer(run_id, raw_answer=json.dumps(answer.raw), status="ok" if ok else "failed",
                          done_reason=answer.done_reason, prompt_eval_count=answer.prompt_eval_count,
                          eval_count=answer.eval_count)
    if not ok:
        log.record_failure(run_id, "doctor.context", reason)
    return ok, reason


def check_runlog_job(state):
    difference = state.log.count_test_jobs() - state.before
    return difference == 1, f"test_jobs={difference:+d}"


def real_smoke(config):
    """Render an image-only page, OCR it with intake's own flags, return (before, after, versions)."""
    with tempfile.TemporaryDirectory(prefix="casefile-doctor-ocr-") as folder:
        base = Path(folder).resolve()
        pdf, out, work = base / "smoke.pdf", base / "ocr.pdf", base / "work"
        work.mkdir()
        pdfsmoke.image_pdf([pdfsmoke.render_page([SMOKE_LINE], [])], pdf)
        before = "\n".join(intake.page_texts(pdf))
        versions = intake.run_ocr(config.ocr, pdf, out, base / "sidecar.txt", workdir=work,
                                  timeout_s=SMOKE_TIMEOUT_S)
        return before, "\n".join(intake.page_texts(out)), versions


REAL = None   # ocr_smoke=None means the real tools


def check_ocr(state):
    for name in ("tesseract", "ocrmypdf"):
        if shutil.which(getattr(state.config.ocr, name)) is None:
            return False, f"not found: {getattr(state.config.ocr, name)}"
    started = time.monotonic()
    try:
        before, after, versions = (state.ocr_smoke or real_smoke)(state.config)
    except intake.IntakeError as exc:
        return False, str(exc)
    if before.strip():
        return False, "smoke input had text"
    if quotes.normalize("casefile ocr smoke") not in quotes.normalize(after):
        return False, f"smoke text not read: {' '.join(after.split())[:40]}"
    found = [s.stamp for s in stamp_finder.find(after, state.config.ocr.stamp_pattern)]
    if found != [SMOKE_STAMP]:
        return False, "smoke stamp not found"
    ms = round((time.monotonic() - started) * 1000)
    return True, (f"smoke=ok stamps={SMOKE_STAMP} ocrmypdf={versions['ocrmypdf']} "
                  f"tesseract={versions['tesseract']} ms={ms}")


DEPENDENCIES = {"context": ("playbook", "runlog_schema", "ollama_loopback"),
                "runlog_job": ("runlog_schema", "context")}


def next_step(name, reason, state):
    if name == "context":
        if "context_length" in reason or "model not loaded" in reason:
            return f"set num_ctx in Ollama to {state.config.model.num_ctx} or reload the model"
        return "rerun doctor; if it repeats, reload the model"
    if name == "ollama_loopback":
        if "listening on" in reason or "hostname=" in reason:
            return "set Ollama to listen on 127.0.0.1 only"
        if "lsof failed" in reason:
            return "check lsof access and rerun doctor"
        return "start the Ollama app"
    if name == "ocr":
        if "not found:" in reason:
            return "install ocrmypdf (brew install ocrmypdf) and rerun doctor"
        return "check the ocrmypdf stderr in the reason and rerun doctor"
    return {"config": "correct the config file and rerun doctor",
            "folders": "check the configured folder paths and write access",
            "playbook": "correct the playbook files and rerun doctor",
            "runlog_schema": "check the state folder and run log schema",
            "runlog_job": "rerun doctor and check the run log"}[name]


def run(config=None, *, out=None, opener=None, lsof_runner=None, ocr_smoke=None) -> int:
    out = sys.stdout if out is None else out
    state = State(config, opener, subprocess.run if lsof_runner is None else lsof_runner,
                  ocr_smoke=ocr_smoke)
    failed = 0
    try:
        for name in CHECKS:
            dependencies = () if name == "config" else ("config",) + DEPENDENCIES.get(name, ())
            blocked = next((dep for dep in dependencies if not state.passed[dep]), None)
            if blocked:
                ok, reason = False, f"blocked by {blocked}"
                state.root[name] = state.root.get(blocked, blocked)
            else:
                try:
                    ok, reason = globals()[f"check_{name}"](state)
                except Exception as exc:
                    ok, reason = False, str(exc)
            state.passed[name] = ok
            failed += not ok
            reason = " ".join(str(reason).splitlines())
            if not ok:
                root = state.root.get(name)
                hint = (f"fix the {root} line above" if root and root != blocked
                        else next_step(blocked or name, reason, state))
                reason += " | do: " + hint
            print(f"doctor {name} {'PASS' if ok else 'FAIL'} {reason}", file=out)
        print(f"doctor failed={failed} of 8", file=out)
        return 0 if failed == 0 else 1
    finally:
        if state.log is not None:
            state.log.close()
