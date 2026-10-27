"""VF-2: unresolvable config, state and playbook paths are ConfigError, exit 2."""
import subprocess


from casefile.config import ConfigError, load
from conftest import write_config

def loop(tmp_path):
    (tmp_path / "loopA").symlink_to(tmp_path / "loopB")
    (tmp_path / "loopB").symlink_to(tmp_path / "loopA")
    return tmp_path / "loopA"

def test_refusals(tmp_path, capsys):
    looped = loop(tmp_path)
    cases = [
        (lambda: load(looped / "x.toml"), "cannot resolve config path"),
        (lambda: load("~nosuchuserxyz/c.toml"), "cannot resolve config path"),
        (lambda: load(write_config(tmp_path / "s", state=str(looped / "st"))), "cannot resolve [paths].state"),
        (lambda: load(write_config(tmp_path / "p", playbook="~nosuchuserxyz/pb")), "cannot resolve [paths].playbook"),
    ]
    results = []
    for fn, expected in cases:
        try:
            fn()
            results.append(False)
        except ConfigError as exc:
            results.append(expected in str(exc))

    result = subprocess.run(
        ["casefile", "config", "show", "--config", str(looped / "x.toml")],
        capture_output=True,
        text=True,
        timeout=30,
    )

    with capsys.disabled():
        print(f"resolve_refused={sum(results)} of 4 cli_exit={result.returncode}")

    assert results == [True] * 4
    assert result.returncode == 2
    assert result.stdout == ""
    assert "ConfigError: cannot resolve config path" in result.stderr
