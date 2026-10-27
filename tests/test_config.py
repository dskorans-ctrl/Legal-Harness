"""Invented configs exercise refusal paths and visible defaults."""

from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
import subprocess

import pytest

from casefile.config import ConfigError, load
from conftest import ROOT, alias_table, write_config


def test_rejections(tmp_path, capsys):
    cases = [
        (write_config(tmp_path / "typo", model={"hots": "x"}), "unknown key [model].hots"),
        (write_config(tmp_path / "context", num_ctx=8192), "at least 65536"),
        (tmp_path / "absent.toml", "no config file"),
        (write_config(tmp_path / "host", host="http://localhost:11434"), "hostname 127.0.0.1"),
        (write_config(tmp_path / "name", name=""), "must be non-empty"),
        (tmp_path / "omitted.toml", "[paths].matters is required"),
        (write_config(tmp_path / "relative", matters="Cases"), "must be an absolute path"),
    ]
    cases[5][0].write_text("[paths]\nstate = 'state'\n", encoding="utf-8")
    results = []
    for path, expected in cases:
        try:
            load(path)
        except ConfigError as exc:
            results.append(expected in str(exc))
        else:
            results.append(False)
    with capsys.disabled():
        print(f"rejected={sum(results)} of 7")
    assert results == [True] * 7


@pytest.mark.parametrize("overrides, message", [
    ({"model": {"num_ctx": "65536"}}, "[model].num_ctx: expected int, got str"),
    ({"num_ctx": True}, "expected int, got bool"),
    ({"model": "wrong"}, "[model]: expected table, got str"),
    ({"extra": {"value": 1}}, "unknown key [extra]"),
    ({"paths": {"typo": "x"}}, "unknown key [paths].typo"),
    ({"ocr": {"typo": "x"}}, "unknown key [ocr].typo"),
    ({"name": "  "}, "must be non-empty"),
    ({"host": "http://[::1]:11434"}, "hostname 127.0.0.1"),
    ({"host": "https://127.0.0.1:11434"}, "hostname 127.0.0.1"),
    ({"temperature": -0.1}, "between 0 and 2"),
    ({"timeout_s": 0}, "must be positive"),
])
def test_bad_values(tmp_path, overrides, message):
    with pytest.raises(ConfigError, match=None) as caught:
        load(write_config(tmp_path, **overrides))
    assert message in str(caught.value)


@pytest.mark.parametrize("ocr, message", [
    ({"x": "y"}, "unknown key [ocr].x"),
    ({"timeout_s": 0}, "[ocr].timeout_s must be positive"),
    ({"timeout_s": "5"}, "[ocr].timeout_s: expected int, got str"),
    ({"stamp_pattern": "("}, "[ocr].stamp_pattern is not a valid pattern"),
    ({"stamp_pattern": " "}, "[ocr].stamp_pattern must be non-empty"),
])
def test_ocr_key_refusals(tmp_path, capsys, ocr, message):
    with pytest.raises(ConfigError) as caught:
        load(write_config(tmp_path, ocr=ocr))
    assert message in str(caught.value)
    with capsys.disabled():
        print(f"config_refusals=+1 ({message})")


def test_ocr_defaults(tmp_path):
    config = load(write_config(tmp_path))
    assert config.ocr.timeout_s == 3600
    assert config.ocr.stamp_pattern == r"[A-Z]{1,8}[ -]?\d{4,}"


def test_paths_defaults_and_frozen_config(tmp_path, monkeypatch):
    settings = tmp_path / "settings"
    settings.mkdir()
    path = settings / "config.toml"
    path.write_text(f"[paths]\nmatters = {json.dumps(str(tmp_path / 'matters'))}\n")
    config = load(path)
    assert config.paths.matters == tmp_path / "matters"
    assert config.paths.state == ROOT / "state"
    assert config.paths.playbook == ROOT / "playbook"
    assert config.model.num_ctx == 65536
    assert config.model.name == "qwen3.8:27b"
    assert config.sources["paths.matters"] == "file"
    assert config.sources["model.num_ctx"] == "default"
    with pytest.raises(FrozenInstanceError):
        config.model.name = "changed"
    with pytest.raises(TypeError):
        config.sources["model.name"] = "changed"
    monkeypatch.setenv("CASEFILE_CONFIG", str(path))
    monkeypatch.setenv("CASEFILE_MODEL_NAME", "ignored")
    assert load() == config
    monkeypatch.delenv("CASEFILE_CONFIG")
    monkeypatch.chdir(settings)
    assert load() == config
    path.write_text("[paths]\nmatters = '~/invented-casefile-test'\n[model]\nnum_ctx = 131072\n")
    assert load(path).paths.matters == Path.home() / "invented-casefile-test"
    assert load(path).model.num_ctx == 131072
    path.write_text(f"[paths]\nmatters = {json.dumps(str(settings / 'nested'))}\n")
    assert load(path).paths.matters == settings / "nested"
    path.write_text("[broken")
    with pytest.raises(ConfigError, match="cannot load config"):
        load(path)


def test_config_show(tmp_path, capsys):
    path = tmp_path / "config.toml"
    path.write_text(f"[paths]\nmatters = {json.dumps(str(tmp_path.parent / 'invented-matters'))}\n")
    env = dict(os.environ, CASEFILE_CONFIG=str(tmp_path / "absent.toml"))
    result = subprocess.run(["casefile", "config", "show", "--config", str(path)],
                            env=env, capture_output=True, text=True, timeout=30)
    assert (result.returncode, result.stderr) == (0, "")
    lines = dict(line.split(" = ", 1) for line in result.stdout.splitlines())
    assert len(lines) == 12
    assert lines["paths.matters"] == f'{json.dumps(str(tmp_path.parent / "invented-matters"))} (source=file)'
    assert lines["model.num_ctx"] == "65536 (source=default)"
    assert all("(source=default)" in value for key, value in lines.items() if key != "paths.matters")
    failed = subprocess.run(["casefile", "config", "show"], env=env,
                            capture_output=True, text=True, timeout=30)
    assert (failed.returncode, failed.stdout) == (2, "")
    assert "ConfigError: no config file" in failed.stderr
    path.write_text(path.read_text() + '\n[model]\nhots = "x"\n')
    unknown = subprocess.run(["casefile", "config", "show", "--config", str(path)],
                             env=env, capture_output=True, text=True, timeout=30)
    with capsys.disabled():
        print(f"unknown_key_cli_exit={unknown.returncode}")
    assert (unknown.returncode, unknown.stdout) == (2, "")
    assert "unknown key [model].hots" in unknown.stderr


def test_external_config_cannot_put_matters_in_checkout(tmp_path):
    from conftest import ROOT

    path = write_config(tmp_path, matters=ROOT / "invented-matters")
    assert not path.is_relative_to(ROOT)
    with pytest.raises(ConfigError, match="must be outside the checkout"):
        load(path)


@pytest.mark.parametrize("suffix", ["", "invented-matters/nested"])
def test_case_swapped_checkout_matters_refused(tmp_path, suffix):
    from conftest import ROOT

    alias = ROOT.with_name(ROOT.name.swapcase())
    # This disk must exercise the actual case alias, never a skipped probe.
    assert alias != ROOT and os.path.samefile(alias, ROOT)
    path = write_config(tmp_path, matters=alias / suffix)
    result = subprocess.run(["casefile", "config", "show", "--config", str(path)],
                            capture_output=True, text=True, timeout=30)
    assert (result.returncode, result.stdout) == (2, ""), result.stdout + result.stderr
    assert "must be outside the checkout" in result.stderr
    with pytest.raises(ConfigError, match="must be outside the checkout"):
        load(path)


@pytest.mark.parametrize("suffix", ["", "invented-matters/nested"])
def test_symlink_checkout_identity_refused(tmp_path, monkeypatch, suffix):
    from conftest import ROOT

    alias = tmp_path / "invented-checkout-alias"
    alias.symlink_to(ROOT, target_is_directory=True)
    assert os.path.samefile(alias, ROOT)
    path = write_config(tmp_path, matters=alias / suffix)
    # Force a lexical miss so this exercises identity even on a case-sensitive disk.
    with pytest.raises(ConfigError, match="must be outside the checkout"):
        with monkeypatch.context() as lexical:
            lexical.setattr(Path, "is_relative_to", lambda self, *other: False)
            load(path)


def test_host_path_refused(tmp_path):
    with pytest.raises(ConfigError, match="hostname 127.0.0.1"):
        load(write_config(tmp_path, host="http://127.0.0.1:11434/x"))


@pytest.mark.parametrize("suffix", ["", "invented-matter"])
def test_symlink_case_swapped_checkout_subdirectory_refused(tmp_path, suffix):
    from conftest import ROOT

    target = ROOT.with_name(ROOT.name.swapcase()) / "tests" / "fixtures"
    assert os.path.samefile(target, ROOT / "tests" / "fixtures")
    alias = tmp_path / "invented-fixture-alias"
    alias.symlink_to(target, target_is_directory=True)
    path = write_config(tmp_path, matters=alias / suffix)
    result = subprocess.run([str(ROOT / "scripts/run.sh"), "casefile", "config", "show",
                             "--config", str(path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "paths.matters =" not in result.stdout
    assert "ConfigError:" in result.stdout + result.stderr
    assert "must be outside the checkout" in result.stdout + result.stderr
    with pytest.raises(ConfigError, match="must be outside the checkout"):
        load(path)


def test_matters_identity_cannot_be_verified_refused(tmp_path):
    from conftest import ROOT

    blocked = tmp_path / "invented-inaccessible"
    blocked.mkdir()
    matters = blocked / "invented-matter"
    path = write_config(tmp_path, matters=matters)
    blocked.chmod(0o000)
    try:
        result = subprocess.run([str(ROOT / "scripts/run.sh"), "casefile", "config", "show",
                                 "--config", str(path)], capture_output=True, text=True, timeout=30)
        assert result.returncode == 2, result.stdout + result.stderr
        assert "paths.matters =" not in result.stdout
        assert "ConfigError: cannot verify [paths].matters" in result.stdout + result.stderr
        with pytest.raises(ConfigError, match="cannot verify"):
            load(path)
    finally:
        blocked.chmod(0o700)


def test_matters_alias_table(tmp_path):
    base = tmp_path / "aliases"
    base.mkdir()
    messages = {"inside": "must be outside the checkout", "relative": "must be an absolute path",
                "cannot-verify": "cannot verify [paths].matters is outside the checkout"}
    wrong = set()
    with alias_table(base, ROOT) as rows:
        for row_id, matters, expected in rows:
            path = write_config(tmp_path / "cfg", matters=matters)
            result = subprocess.run([str(ROOT / "scripts/run.sh"), "casefile", "config", "show",
                                     "--config", str(path)], capture_output=True, text=True,
                                    timeout=30)
            shown = "paths.matters = " + json.dumps(os.path.realpath(matters))
            if expected == "outside":
                if result.returncode != 0 or shown not in result.stdout:
                    wrong.add(f"{row_id}@cli")
                if load(path).paths.matters != Path(os.path.realpath(matters)):
                    wrong.add(f"{row_id}@load")
                continue
            if (result.returncode != 2 or "paths.matters =" in result.stdout
                    or messages[expected] not in result.stdout + result.stderr):
                wrong.add(f"{row_id}@cli")
            try:
                load(path)
                wrong.add(f"{row_id}@load")
            except ConfigError as exc:
                if messages[expected] not in str(exc):
                    wrong.add(f"{row_id}@load")
        total = len(rows)
    print(f"\nmatters_alias_wrong={len({name.split('@')[0] for name in wrong})} of {total}")
    assert not wrong, sorted(wrong)


def test_matters_unexpandable_home(tmp_path, monkeypatch):
    path = write_config(tmp_path, matters="~/invented-casefile-test")
    monkeypatch.setattr(os.path, "expanduser", lambda value: value)
    with pytest.raises(ConfigError, match="cannot expand ~ in \\[paths\\].matters"):
        load(path)
