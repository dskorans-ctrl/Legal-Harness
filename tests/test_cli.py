"""Check the installed console entry point."""

import subprocess


def test_version():
    result = subprocess.run(
        ["casefile", "version"], capture_output=True, text=True, timeout=30
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, "casefile 0.1.0\n", "")


def test_no_args():
    result = subprocess.run(["casefile"], capture_output=True, text=True, timeout=30)
    assert (result.returncode, result.stdout) == (2, "")
    assert "usage: casefile" in result.stderr


def test_playbook_show(tmp_path):
    import os
    import shutil
    from conftest import ROOT, write_config

    config = write_config(tmp_path)
    shutil.copytree(ROOT / "playbook", tmp_path / "playbook", dirs_exist_ok=True)
    env = dict(os.environ, CASEFILE_CONFIG=str(tmp_path / "absent.toml"))
    result = subprocess.run(["casefile", "playbook", "show", "--config", str(config)],
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("version=pb-")
    assert "entries=20" in result.stdout.splitlines()[0]
    assert len(result.stdout.splitlines()) == 21


def test_doctor_config_override(tmp_path):
    import os
    from conftest import write_config

    config = write_config(tmp_path)
    # An explicitly missing config blocks every model path before any socket.
    result = subprocess.run(["casefile", "doctor", "--config", str(tmp_path / "absent.toml")],
                            env=dict(os.environ, CASEFILE_CONFIG=str(config)),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 1
    assert "doctor config FAIL no config file" in result.stdout
    assert result.stdout.count("FAIL blocked by config") == 7


def test_bad_playbook_show_exits_2(tmp_path):
    import shutil
    from conftest import ROOT, write_config

    config = write_config(tmp_path)
    shutil.copytree(ROOT / "playbook", tmp_path / "playbook", dirs_exist_ok=True)
    path = tmp_path / "playbook" / "rules.toml"
    lines = path.read_text().splitlines(keepends=True)
    index = next(i for i, line in enumerate(lines) if line.startswith("why = "))
    del lines[index]
    path.write_text("".join(lines))
    result = subprocess.run(["casefile", "playbook", "show", "--config", str(config)],
                            capture_output=True, text=True, timeout=30)
    assert (result.returncode, result.stdout) == (2, ""), result.stdout + result.stderr
    assert "PlaybookError:" in result.stderr and "why" in result.stderr


def test_hearing_flags(monkeypatch, tmp_path):
    from casefile import cli
    from conftest import write_config

    path = write_config(tmp_path)
    seen = []
    def run(config, number, **kwargs):
        seen.append((config, number, kwargs))
        return 7
    monkeypatch.setattr(cli.hearing, 'run', run)
    flags = ('outline', 'client', 'doctor', 'closing')
    count = 0
    for flag in flags:
        monkeypatch.setattr('sys.argv', ['casefile', 'hearing', '--matter', '9001.001',
                                        '--config', str(path), '--' + flag])
        code = cli.main()
        cfg, number, kwargs = seen[-1]
        count += int(code == 7 and number == '9001.001' and cfg.model.host == 'http://127.0.0.1:9'
                     and {key: kwargs[key] for key in flags} == {key: key == flag for key in flags})
    print(f'hearing_flags={count} of 4')
    assert len(seen) == 4 and count == 4, f'hearing_flags={count} of 4'
