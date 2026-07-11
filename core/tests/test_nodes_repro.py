from unittest.mock import patch

from redink_core.nodes_repro import repro_check
from redink_core.repro import ReproResult

STATE = {"code_repo": "https://github.com/foo/bar"}


def _run(result=None, docker=True):
    with patch("redink_core.nodes_repro.docker_available", return_value=docker), \
         patch("redink_core.nodes_repro.run_repro_check", return_value=result):
        return repro_check(STATE)


def test_ok_emits_no_finding_but_records_result():
    out = _run(ReproResult("ok", STATE["code_repo"], package="bar", log="IMPORT_OK:bar"))
    assert out["findings"] == []
    assert out["repro_result"]["status"] == "ok"


def test_no_docker_emits_no_finding():
    out = _run(docker=False)
    assert out["findings"] == []
    assert out["repro_result"]["status"] == "no_docker"


def test_install_fail_is_major_grounded_finding():
    out = _run(ReproResult("install_fail", STATE["code_repo"], log="No matching distribution torch"))
    assert len(out["findings"]) == 1
    f = out["findings"][0]
    assert f.dimension == "reproducibility"
    assert f.severity == "major"
    assert f.grounded is True
    assert f.evidence_verified is True
    assert "torch" in f.evidence


def test_import_fail_is_major():
    out = _run(ReproResult("import_fail", STATE["code_repo"], log="ImportError"))
    assert out["findings"][0].severity == "major"


def test_timeout_is_major():
    out = _run(ReproResult("timeout", STATE["code_repo"], log="passou de 180s"))
    assert out["findings"][0].severity == "major"


def test_repo_missing_is_critical():
    out = _run(ReproResult("repo_missing", STATE["code_repo"], log="not found"))
    assert out["findings"][0].severity == "critical"
    assert out["findings"][0].grounded is True


def test_no_code_repo_skips():
    out = repro_check({})
    assert out["findings"] == []
    assert out["repro_result"]["status"] == "no_docker" or out["repro_result"].get("skipped")
