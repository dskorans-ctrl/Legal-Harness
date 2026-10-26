"""Invented configs exercise refusal paths and visible defaults."""

from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
import subprocess

import pytest

from casefile.config import ConfigError, load
from conftest import write_config


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


def test_paths_defaults_and_frozen_config(tmp_path, monkeypatch):
    settings = tmp_path / "settings"
    settings.mkdir()
    path = settings / "config.toml"
    path.write_text(f"[paths]\nmatters = {json.dumps(str(tmp_path / 'matters'))}\n")
    config = load(path)
    assert config.paths.matters == tmp_path / "matters"
    assert config.paths.state == settings / "state"
    assert config.paths.playbook == settings / "playbook"
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
    assert len(lines) == 10
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
