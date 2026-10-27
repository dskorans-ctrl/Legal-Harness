"""Send one coding task to the local Gemma model and apply its answer (round 2, owner Q28).

Loop tooling, not part of the app. The orchestrator writes a task file; this script inlines the
named context files, asks Ollama, and writes only the files (or functions) the task allows.

  python3 scripts/gemma_task.py --task T.md [--context F ...] --allow PATH [--allow PATH ...]
                                [--function PATH::NAME] [--feedback F] [--no-think]

Answer formats the model is told to use:
  === FILE: <path> ===      then one fenced block holding the COMPLETE file
  === FUNCTION: <path>::<name> ===  then one fenced block holding one def (or Class.method)

Exit: 0 applied · 2 no usable block · 3 truncated or incomplete (nothing written) · 4 path not allowed ·
5 model server error · 6 splice failed or an answer does not parse (nothing written).
"""

import argparse
import ast
import datetime
import json
import os
import re
import sys
import time
import urllib.request

MODEL = "gemma4:e4b-it-qat"
URL = "http://127.0.0.1:11434/api/chat"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGDIR = os.path.join(ROOT, ".workflow", "scratch", "gemma")

SYSTEM = """You are a careful Python 3.12 programmer working on one small task in an existing project.
Rules:
- Follow the task exactly: the signatures, names, error messages and behaviour it gives are fixed.
- Use only the standard library and the project modules the task names. Do not invent APIs; if the
  task quotes a function signature, call it exactly as quoted.
- Answer with the code only, in the format the task asks for:
  === FILE: <path> ===
  ```python
  <the COMPLETE file, nothing omitted, no "..." placeholders>
  ```
  or, when asked for one function:
  === FUNCTION: <path>::<name> ===
  ```python
  <one complete def, with its decorators>
  ```
- Write only the paths the task allows. No prose before the first header. At most five short
  lines of notes after the last block.
- Never use real people's names or records; any example data is invented.
- Do not use em dashes or en dashes in comments or strings."""

HEADER = re.compile(r"^===\s*(FILE|FUNCTION):\s*(\S+?)\s*===\s*$", re.M)
FENCE = re.compile(r"```[a-zA-Z0-9]*\n(.*?)\n```", re.S)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_prompt(args):
    parts = [read(args.task).rstrip()]
    for c in args.context or []:
        rel = os.path.relpath(os.path.abspath(c), ROOT)
        parts.append(f"--- context: {rel} ---\n{read(c).rstrip()}\n--- end {rel} ---")
    if args.feedback:
        parts.append("--- your previous answer failed; fix it. Feedback: ---\n" + read(args.feedback).rstrip())
    allowed = ", ".join(args.allow) + (f"; function {args.function}" if args.function else "")
    parts.append(f"Allowed output: {allowed}")
    return "\n\n".join(parts)


def ask(prompt, think, num_ctx, num_predict):
    body = {
        "model": MODEL,
        "stream": False,
        "think": think,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        "options": {"temperature": 0.2, "num_ctx": num_ctx, "num_predict": num_predict},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # loopback only, never a proxy
    with opener.open(req, timeout=1800) as r:
        return json.loads(r.read())


def blocks(text):
    """Pair each header with the first fenced block after it."""
    out = []
    heads = list(HEADER.finditer(text))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        seg = text[h.end():end].strip("\n")
        m = FENCE.search(seg)
        if m and seg.startswith("```"):
            code = m.group(1)
        else:  # the small model sometimes drops the opening fence: take up to a closing one
            code = seg.split("\n```", 1)[0].rstrip()
        if code.strip():
            out.append((h.group(1), h.group(2), code + "\n"))
    return out


def splice(path, name, code):
    """Replace top-level def NAME (or Class.method) in PATH with CODE; append if absent."""
    src = read(path) if os.path.exists(path) else ""
    new = ast.parse(code)
    if len(new.body) != 1 or not isinstance(new.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError("answer is not exactly one def")
    tree = ast.parse(src)
    cls, _, fn = name.rpartition(".")
    scope = tree.body
    indent = ""
    if cls:
        found = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls]
        if not found:
            raise ValueError(f"class {cls} not found")
        scope = found[0].body
        indent = " " * found[0].body[0].col_offset
    target = [n for n in scope if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == fn]
    body = "".join(indent + ln if ln.strip() else ln for ln in code.splitlines(True))
    lines = src.splitlines(True)
    if target:
        t = target[0]
        start = (t.decorator_list[0].lineno if t.decorator_list else t.lineno) - 1
        lines[start:t.end_lineno] = [body]
    else:
        if cls:
            raise ValueError(f"method {name} not found")
        lines.append(("\n\n" if src.strip() else "") + body)
    result = "".join(lines)
    ast.parse(result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--context", action="append")
    p.add_argument("--allow", action="append", required=True)
    p.add_argument("--function")
    p.add_argument("--feedback")
    p.add_argument("--no-think", action="store_true")
    p.add_argument("--num-ctx", type=int, default=32768)
    p.add_argument("--num-predict", type=int, default=16384)
    args = p.parse_args()

    prompt = build_prompt(args)
    os.makedirs(LOGDIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = os.path.splitext(os.path.basename(args.task))[0]
    log = os.path.join(LOGDIR, f"{stamp}-{tag}.json")
    t0 = time.time()
    try:
        resp = ask(prompt, not args.no_think, args.num_ctx, args.num_predict)
    except Exception as e:  # noqa: BLE001 - any server failure is exit 5
        print(f"gemma: server error: {e}")
        return 5
    secs = time.time() - t0
    msg = resp.get("message", {})
    text = msg.get("content", "")
    with open(log, "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt, "response": resp}, f, indent=1)
    stats = (f"secs={secs:.0f} prompt_tokens={resp.get('prompt_eval_count')} "
             f"out_tokens={resp.get('eval_count')} done={resp.get('done_reason')} log={os.path.relpath(log, ROOT)}")
    if resp.get("done") is not True or resp.get("done_reason") != "stop":
        print(f"gemma: TRUNCATED or incomplete, nothing written; {stats}")
        return 3
    got = blocks(text)
    if not got:
        print(f"gemma: no usable FILE/FUNCTION block; {stats}")
        return 2
    allow = {os.path.normpath(a) for a in args.allow}
    writes = {}
    for kind, target, code in got:
        if args.function and kind == "FILE":
            print(f"gemma: FILE answer on a function task: {target}; {stats}")
            return 4
        path = target.split("::")[0] if kind == "FUNCTION" else target
        if os.path.normpath(path) not in allow:
            print(f"gemma: path not allowed: {path}; {stats}")
            return 4
        if kind == "FUNCTION":
            if not args.function or target != args.function or path in writes:
                print(f"gemma: function not allowed: {target}; {stats}")
                return 4
            try:
                writes[path] = splice(os.path.join(ROOT, path), target.split("::")[1], code)
            except (ValueError, SyntaxError) as e:
                print(f"gemma: splice failed: {e}; {stats}")
                return 6
        else:
            writes[path] = code
    for path, content in writes.items():  # every answer must parse before anything is written
        real = os.path.realpath(os.path.join(ROOT, path))
        if os.path.islink(os.path.join(ROOT, path)) or os.path.commonpath([real, os.path.realpath(ROOT)]) != os.path.realpath(ROOT):
            print(f"gemma: {path} is a link or outside the checkout, nothing written; {stats}")
            return 4
        try:
            if path.endswith(".py"):
                ast.parse(content)
            elif path.endswith(".json"):
                json.loads(content)
        except (SyntaxError, ValueError) as e:
            print(f"gemma: {path} does not parse, nothing written: {e}; {stats}")
            return 6
    for path, content in writes.items():
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"gemma: wrote {path} lines={content.count(chr(10))}")
    print(f"gemma: ok; {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
