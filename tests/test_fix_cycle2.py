"""Cycle 2 regressions use only invented sentences and temporary paths."""

from io import StringIO
import json
from urllib.error import URLError

import pytest

from casefile import doctor
from casefile.config import ConfigError, load
from casefile.rules import load as load_rules
from conftest import ROOT, write_config
from fakemodel.core import FakeModel
from test_doctor import invoke, passing_smoke, setup_config


def findings(text, unit="text"):
    return {f.rule_id for f in load_rules(ROOT / "playbook/rules.toml").check(text, unit=unit)}


def test_h1_ocr_unverified_with_two_successful_stubs(tmp_path):
    tools = {}
    for name in ("tesseract", "ocrmypdf"):
        stub = tmp_path / name
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
        tools[name] = str(stub)
    config = setup_config(tmp_path, ocr=tools)
    ok, reason = doctor.check_ocr(doctor.State(config, config=config))
    assert ok is False
    assert "smoke=ok" not in reason and "--version exit=0" in reason, reason


def test_h2_exam_label_variants():
    for label in ("D.M.E.", "I.M.E.", "DMEs", "IMEs", "d.m.e.s", "i.m.e.s."):
        assert findings(f"The {label} report records normal motion.") == {"no-dme-ime"}, label
    for side in ("independent", "defense"):
        for noun in ("exam", "exams", "examination", "examinations", "evaluation", "evaluations"):
            for space in (" ", "\t", "\n", "\r\n"):
                text = space.join((side, "medical", noun))
                assert findings(text) == {"no-dme-ime"}, repr(text)
    assert findings("The report records normal motion.") == set()


CLEAN = (
    "He was hired by Example Widgets on 2 June 2019.",
    "When were you hired?", "The retained hardware was removed.",
    "The claimant retained counsel.", "The attorney fees were approved.",
    "Under the fee schedule the visit was covered.",
)


def test_h3_hiring_and_fees_scoped_to_doctor_clause():
    for text in CLEAN:
        assert findings(text) == set(), text
    for event in ("hired", "retained", "fee", "fees"):
        for noun in ("doctor", "Dr.", "physician", "examiner", "exam", "examination", "evaluator"):
            for text in (f"Who {event} the {noun}?", f"The {noun} was {event} by the carrier."):
                assert findings(text) == {"no-hired-paid-retained"}, text
        for boundary in (".", ";", ":", "?", "!", "\n", "\r\n"):
            for text in (f"The claimant was {event}{boundary} The doctor agreed.",
                         f"The doctor agreed{boundary} The claimant was {event}."):
                assert findings(text) == set(), text
        for left, right in ((event, "doctor"), ("doctor", event)):
            assert findings(left + " " * 60 + right) == {"no-hired-paid-retained"}
            assert findings(left + " " * 61 + right) == set()
    for text in ("Who hired Dr. Example?", "Dr. Example was retained by the carrier.",
                 "What fees did you receive for the report?", "What is your fee for an examination?",
                 "Who referred you to Dr. Example for therapy?"):
        assert findings(text) == {"no-hired-paid-retained"}, text


def test_m1_doctor_billing_and_engagement():
    for event in ("charge", "charges", "charged", "rate", "billed", "bill", "engaged by"):
        for text in (f"What did you {event} for the exam?", f"Dr. Example was {event} by the carrier."):
            assert findings(text) == {"no-hired-paid-retained"}, text
        assert findings(f"{event}; the doctor agreed.") == set()
    assert findings("At whose request did you examine the claimant?") == {"no-hired-paid-retained"}
    assert findings("At whose request was the hardware removed?") == set()
    for text in CLEAN:
        assert findings(text) == set(), text


def test_m2_unit_is_required():
    with pytest.raises(TypeError, match="unit"):
        load_rules(ROOT / "playbook/rules.toml").check("What treatment and bills?")


def test_m3_treatment_cost_words():
    for noun in ("cost", "costs", "expense", "expenses", "lien", "liens", "balance"):
        text = f"What treatment did you receive and what were the {noun}?"
        assert findings(text, unit="question") == {"treatment-and-bills-apart"}, text
        assert findings(text, unit="text") == set()


def test_m5_bates_ranges_lists_and_no_pinpoints():
    for body in ("MED0001", "MED0001-MED0009", "MED0001 - MED0009", "MED0001, MED0004",
                 "MED0001, MED0004, MED0009"):
        assert findings(f"[cite {body}]") == set(), body
    for body in ("MED 0001 at 3", "p. 12", "MED0001 to MED0009", "MED0001,", "MED0001-junk"):
        assert findings(f"[cite {body}]") == {"bates-cites"}, body


def test_m6_every_failure_has_action(tmp_path, monkeypatch):
    runs = [invoke(tmp_path / "missing.toml")[1]]
    for mode in ("replay", "short_context", "truncated", "empty", "malformed"):
        runs.append(invoke(setup_config(tmp_path / mode), fake=FakeModel(mode=mode))[1])
    out = StringIO()
    class Offline:
        def open(self, *args, **kwargs):
            raise URLError("invented connection refused")
    doctor.run(setup_config(tmp_path / "offline"), out=out, opener=Offline(), ocr_smoke=passing_smoke)
    runs.append(out.getvalue())
    offline_output = runs[-1]
    for name in doctor.CHECKS:
        with monkeypatch.context() as patch:
            reason = f"invented {name} fault"
            patch.setattr(doctor, f"check_{name}", lambda state: (False, reason))
            output = invoke(setup_config(tmp_path / f"failed-{name}"))[1]
            assert f"doctor {name} FAIL {reason} | do: " in output
            runs.append(output)
    for output in runs:
        for line in output.splitlines():
            if " FAIL " in line:
                assert " | do: " in line, line
                assert line.split(" | do: ")[1].strip(), line
    assert "<urlopen error invented connection refused> | do: start the Ollama app" in offline_output
    assert "context_length=8192 want 65536 | do: set num_ctx in Ollama to 65536 or reload the model" in runs[2]
    for output in runs[3:5]:
        assert " | do: rerun doctor; if it repeats, reload the model" in output


def test_m7_missing_matters_is_not_created(tmp_path):
    missing = tmp_path / "typo" / "Casess"
    config = setup_config(tmp_path, matters=missing)
    ok, reason = doctor.check_folders(doctor.State(config, config=config))
    assert (ok, reason) == (False, f"matters folder not found: {missing}")
    assert not missing.exists()


def test_m8_matters_beside_config_and_exact_errors(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    path = home / "config.toml"
    matters = home / "Cases"
    path.write_text(f"[paths]\nmatters = {json.dumps(str(matters))}\n")
    assert load(path).paths.matters == matters
    for value, reason in (("Cases", "[paths].matters must be an absolute path"),
                          (str(ROOT / "invented-matters"), f"[paths].matters must be outside the checkout {ROOT}")):
        path.write_text(f"[paths]\nmatters = {json.dumps(value)}\n")
        with pytest.raises(ConfigError) as exc:
            load(path)
        assert str(exc.value) == reason


def test_l1_schema_reason_only_reports_this_run(tmp_path):
    _, output = invoke(setup_config(tmp_path))
    line = next(line for line in output.splitlines() if line.startswith("doctor runlog_schema "))
    assert line == "doctor runlog_schema PASS schema=1 triggers=15 (counted)"


def test_l2_runlog_job_blocked_by_context(tmp_path):
    _, output = invoke(setup_config(tmp_path), fake=FakeModel(mode="truncated"))
    assert "doctor context FAIL done_reason=length" in output
    assert "doctor runlog_job FAIL blocked by context" in output
