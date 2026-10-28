import errno
import http.client
import json
import os
import shutil
import socket
import subprocess
from urllib.error import URLError

import pytest

from conftest import ROOT, write_config

MATTERS = ROOT / "tests" / "fixtures" / "matters"
MATTER = MATTERS / "9001.001"
FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
           "flags_extra=0 rules=0 pages_failed=0 of 14")
FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
               "flags_extra=1 rules=1 pages_failed=0 of 14")

def bench(config, *args):
    """Run the installed `casefile bench` command as a child process with CASEFILE_CONFIG set."""
    env = dict(os.environ, CASEFILE_CONFIG=str(config))
    return subprocess.run(["casefile", "bench", *args], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=60)


def test_bench_exits(tmp_path, capsys):
    # Setup configuration
    config = write_config(tmp_path / "a", playbook=ROOT / "playbook", host="http://127.0.0.1:9")

    # Perfect run
    r1 = bench(config, "--matters", str(MATTERS), "--candidate", str(MATTER / "ideal.json"))
    lines1 = r1.stdout.splitlines()

    # Flawed run
    r2 = bench(config, "--matters", str(MATTERS), "--candidate", str(FLAWED))
    lines2 = r2.stdout.splitlines()

    # Bad key run
    bad_matter_dir = tmp_path / "bad" / "9001.001"
    shutil.copytree(MATTER, bad_matter_dir)

    key_path = bad_matter_dir / "key.json"

    # A key quote that is not on its page makes the key refuse to load.
    data = json.loads(key_path.read_text(encoding="utf-8"))
    data["facts"][0]["quote"] = "Pain 9/10 in the low back, no radiation."
    key_path.write_text(json.dumps(data), encoding="utf-8")

    r3 = bench(config, "--matters", str(tmp_path / "bad"), "--candidate", str(MATTER / "ideal.json"))

    # No config run
    r4 = bench(config, "--matters", str(MATTERS), "--candidate", str(MATTER / "ideal.json"), "--config", str(tmp_path / "missing.toml"))

    # No run log run
    blocker_file = tmp_path / "blocker"
    blocker_file.write_text("a file, not a folder", encoding="utf-8")

    # The state path sits under a plain file, so the run log cannot be opened (exit 2).
    config5 = write_config(tmp_path / "e", playbook=ROOT / "playbook", host="http://127.0.0.1:9", state=str(blocker_file / "state"))

    r5 = bench(config5, "--matters", str(MATTERS))

    # Print results
    summary = (f"bench_exit_perfect={r1.returncode} bench_exit_flawed={r2.returncode} "
               f"bench_exit_badkey={r3.returncode} bench_exit_noconfig={r4.returncode} "
               f"bench_exit_nolog={r5.returncode}")

    with capsys.disabled():
        print(summary)

    # Assertions

    # r1 assertions (Perfect)
    assert r1.returncode == 0
    assert lines1[0] == PERFECT
    assert lines1[-1] == "bench matters=1 imperfect=0"

    # r2 assertions (Flawed)
    assert r2.returncode == 1
    assert lines2[0] == FLAWED_LINE
    assert lines2[-1] == "bench matters=1 imperfect=1"

    # r3 assertions (Bad Key)
    assert r3.returncode == 2
    assert r3.stdout == ""
    assert r3.stderr.startswith("BenchKeyError:")

    # r4 assertions (No Config)
    assert r4.returncode == 2
    assert r4.stderr.startswith("ConfigError: no config file")

    # r5 assertions (No Run Log)
    assert r5.returncode == 2
    assert r5.stdout == ""
    assert r5.stderr.startswith("bench: cannot open run log")

    # Final check: no run log was created by the candidate runs
    # We check the state directory created in step 1 (tmp_path / "a")
    runlog_path = tmp_path / "a" / "state" / "runlog.sqlite"
    assert not runlog_path.exists()


def run_runner_mode(tmp_path, opener=None, host="http://127.0.0.1:9"):
    """casefile bench in runner mode, in process, with the stand-in's recordings or no server at all."""
    import io
    from casefile import bench
    config = write_config(tmp_path, playbook=ROOT / "playbook", host=host)
    out, err = io.StringIO(), io.StringIO()
    code = bench.main(MATTERS, config, out=out, err=err, opener=opener)
    return code, out.getvalue().splitlines(), err.getvalue()


def test_bench_no_reply_exit2(tmp_path, capsys):
    """No server at the host: nothing was received, so the run cannot be scored (Q26, D25): exit 2."""
    code, lines, err = run_runner_mode(tmp_path)
    with capsys.disabled():
        print(f"no_reply_exit={code}")
    assert code == 2
    reason = "no reply from the model server at http://127.0.0.1:9 (connection refused)"
    assert lines == [f"bench 9001.001 failure gate.model: {reason}"], "no-reply reason is not plain text"
    assert "bench matters=" not in "\n".join(lines)
    assert err == f"bench: cannot run: {reason}\n"


def test_bench_received_404_stays_exit1(tmp_path, capsys):
    """A 404 for an unknown model tag is a received reply: scored found=0, exit 1 (D25)."""
    from fakemodel.bench import recordings_for
    from fakemodel.core import FakeModel, FakeTransport
    opener = FakeTransport(FakeModel(recordings=recordings_for(MATTER), model="other:model"))
    code, lines, err = run_runner_mode(tmp_path, opener)
    with capsys.disabled():
        print(f"received_404_exit={code}")
    assert code == 1
    assert err == ""
    assert lines[0] == ("bench 9001.001 failure gate.model: status=404: fakemodel: unknown model; "
                        "not retried: the one retry was used")
    assert lines[1] == ("bench 9001.001 model=qwen3.8:27b found=0 of 36 missed=36 invented=0 extra=0 dates_wrong=0 "
                        "flags=0 of 9 flags_missed=9 flags_extra=0 rules=0 pages_failed=14 of 14")
    assert lines[-1] == "bench matters=1 imperfect=1"


def test_candidate_lines_name_the_model_candidate(tmp_path):
    r = bench(write_config(tmp_path, playbook=ROOT / "playbook", host="http://127.0.0.1:9"),
              "--matters", str(MATTERS), "--candidate", str(FLAWED))
    assert r.stdout.splitlines()[0].startswith("bench 9001.001 model=candidate found=")


def test_bench_received_bad_answer_stays_exit1(tmp_path, capsys):
    """A truncated answer reached us: scored with every page failed, exit 1, not exit 2 (D25)."""
    from fakemodel.bench import recordings_for
    from fakemodel.core import FakeModel, FakeTransport
    opener = FakeTransport(FakeModel(recordings=recordings_for(MATTER), mode="truncated"))
    code, lines, err = run_runner_mode(tmp_path, opener)
    with capsys.disabled():
        print(f"received_truncated_exit={code}")
    assert (code, err) == (1, "")
    assert lines[0] == ("bench 9001.001 failure gate.truncation: the answer stopped before it finished "
                        "(done_reason=length); not retried: the one retry was used")
    assert lines[1] == ("bench 9001.001 model=qwen3.8:27b found=0 of 36 missed=36 invented=0 extra=0 dates_wrong=0 "
                        "flags=0 of 9 flags_missed=9 flags_extra=0 rules=0 pages_failed=14 of 14")


def test_bench_prompt_too_long_stays_exit1(tmp_path, capsys):
    """The stand-in's context refusal is truncation, with every page failed and the reply stored."""
    from fakemodel.bench import recordings_for
    from fakemodel.core import FakeModel, FakeTransport
    opener = FakeTransport(FakeModel(recordings=recordings_for(MATTER), mode="prompt_too_long"))
    code, lines, err = run_runner_mode(tmp_path, opener)
    with capsys.disabled():
        print("\n".join(lines))
    assert (code, err) == (1, "")
    assert lines == [
        'bench 9001.001 failure gate.truncation: status=400: '
        'the prompt is longer than the context length currently available to the model; '
        'shorten the prompt, adjust the context length in settings, or use a model ...; '
        'not retried: the prompt was too long; the chunk must be made smaller',
        "bench 9001.001 model=qwen3.8:27b found=0 of 36 missed=36 invented=0 extra=0 dates_wrong=0 "
        "flags=0 of 9 flags_missed=9 flags_extra=0 rules=0 pages_failed=14 of 14",
        "  missed: " + " ".join(f"F{i:02}" for i in range(1, 37)),
        "  flags_missed: G1 G2 G3 G4 G5 G6 G7 G8 G9",
        "bench matters=1 imperfect=1",
    ]


@pytest.mark.parametrize("failure, detail", [
    (URLError(ConnectionRefusedError(errno.ECONNREFUSED, "invented private detail")), "connection refused"),
    (ConnectionRefusedError("invented refusal"), "connection refused"),
    (URLError(TimeoutError("invented private detail")), "connection timed out"),
    (TimeoutError("invented timeout"), "connection timed out"),
    (URLError(socket.gaierror("invented private detail")), "server address could not be found"),
    (OSError(errno.ENETUNREACH, "invented private detail"), "network unreachable"),
    (OSError(errno.EHOSTUNREACH, "invented private detail"), "network unreachable"),
    (ConnectionResetError("invented reset"), "connection closed before a reply"),
    (http.client.RemoteDisconnected("invented disconnect"), "connection closed before a reply"),
    (http.client.IncompleteRead(b"", 1), "no complete reply"),
    (URLError("invented private detail"), "server could not be reached"),
    (OSError(), "server could not be reached"),
])
def test_bench_no_reply_plain_words(tmp_path, failure, detail):
    class NoReply:
        def open(self, request, timeout=None):
            raise failure

    code, lines, err = run_runner_mode(tmp_path, NoReply())
    reason = f"gate.model: no reply from the model server at http://127.0.0.1:9 ({detail})"
    assert code == 2
    assert lines == [f"bench 9001.001 failure {reason}"], "no-reply reason is not plain text"
    assert err == f"bench: cannot run: {reason.removeprefix('gate.model: ')}\n"
