"""Eight explicit local readiness checks and one logged model warmup."""

from dataclasses import dataclass, field
import hashlib
import json
import os
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

from . import config as configuration, playbook, runlog
from .model import ModelClient


CHECKS = ("config", "folders", "playbook", "runlog_schema", "ollama_loopback",
          "context", "runlog_job", "ocr")
CARD_TEXT = "Reply with the single word READY."
MESSAGES = [{"role": "system", "content": CARD_TEXT},
            {"role": "user", "content": "casefile doctor warmup"}]


@dataclass
class State:
    source: object
    opener: object = None
    runner: object = subprocess.run
    config: object = None
    book: object = None
    log: object = None
    before: int = 0
    passed: dict = field(default_factory=dict)


def check_config(state):
    state.config = (state.source if isinstance(state.source, configuration.Config)
                    else configuration.load(state.source))
    return True, f"source={state.config.source}"


def check_folders(state):
    for name in ("matters", "state", "playbook"):
        path = getattr(state.config.paths, name)
        try:
            if name != "playbook":
                path.mkdir(parents=True, exist_ok=True)
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
    return version == 1 and count == 8, f"schema={version} triggers={count} (counted, exercised by the test suite)"


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
            ok = context_ok and answer.done_reason == "stop" and answer_ok
            if not context_ok:
                reason = f"context_length={context_length} want {state.config.model.num_ctx}"
            elif answer.done_reason != "stop":
                reason = f"done_reason={answer.done_reason}"
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


def check_ocr(state):
    tesseract = shutil.which(state.config.ocr.tesseract)
    ocrmypdf = shutil.which(state.config.ocr.ocrmypdf)
    if tesseract is None:
        return False, "tesseract not found on PATH"
    if ocrmypdf is None:
        return False, "ocrmypdf not found on PATH"
    result = subprocess.run([tesseract, "--version"], capture_output=True, timeout=30, check=False)
    return result.returncode == 0, f"tesseract --version exit={result.returncode}"


DEPENDENCIES = {"context": ("playbook", "runlog_schema", "ollama_loopback"),
                "runlog_job": ("runlog_schema",)}


def run(config=None, *, out=None, opener=None, lsof_runner=None) -> int:
    out = sys.stdout if out is None else out
    state = State(config, opener, subprocess.run if lsof_runner is None else lsof_runner)
    failed = 0
    try:
        for name in CHECKS:
            dependencies = () if name == "config" else ("config",) + DEPENDENCIES.get(name, ())
            blocked = next((dep for dep in dependencies if not state.passed[dep]), None)
            if blocked:
                ok, reason = False, f"blocked by {blocked}"
            else:
                try:
                    ok, reason = globals()[f"check_{name}"](state)
                except Exception as exc:
                    ok, reason = False, str(exc)
            state.passed[name] = ok
            failed += not ok
            reason = " ".join(str(reason).splitlines())
            print(f"doctor {name} {'PASS' if ok else 'FAIL'} {reason}", file=out)
        print(f"doctor failed={failed} of 8", file=out)
        return 0 if failed == 0 else 1
    finally:
        if state.log is not None:
            state.log.close()
