"""No-cost regression tests for PLE check error classification and safety."""
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from diagnose_ple_check import classify_check, main


def report(status, detail=""):
    return {"stages":[
        {"name":"submission.yaml","status":"pass"},
        {"name":"files","status":"pass"},
        {"name":"build","status":"pass"},
        {"name":"model","status":status,"detail":detail},
    ]}


@pytest.mark.parametrize(("detail","expected"),[
    ("HTTP 503 UNAVAILABLE high demand","UPSTREAM_503"),
    ("TimeoutError: timed out","MODEL_TIMEOUT"),
    ("HTTP 429 quota exhausted","FREE_QUOTA_LIMIT"),
    ("HTTP 401 unauthorized","MODEL_AUTH"),
    ("HTTP 404 model not found","MODEL_NOT_FOUND"),
    ("other provider error","MODEL_FAILURE"),
])
def test_classifies_model_failures_without_logging_raw_detail(detail,expected):
    result=classify_check(report("fail",detail))
    assert result["blocker"]==expected
    assert detail not in json.dumps(result)
    assert result["stages"]["listen"]=="not_run"
    assert not result["official_29_task_score_verified"]


def test_protocol_pass_not_same_as_evaluation_artifacts():
    data=report("pass")
    data["stages"].extend({"name":n,"status":"pass"} for n in ("listen","smoke","mcp"))
    res=classify_check(data)
    assert res["public_protocol_pass"]
    assert res["blocker"]=="ARTIFACTS_MISSING"
    assert not res["artifacts_check_pass"]


def test_kit_check_cannot_prove_full_dev_score():
    data=report("pass")
    data["stages"].extend({"name":n,"status":"pass"} for n in ("listen","smoke","mcp","artifacts"))
    res=classify_check(data)
    assert res["blocker"]=="KIT_CHECK_PASSED"
    assert res["artifacts_check_pass"]
    assert res["official_29_task_score_verified"] is False


def test_secret_from_provider_error_never_in_diagnostics():
    secret="PLACEHOLDER_FAKE_API_KEY_ABC123"
    data=report("fail","HTTP 503 x-api-key="+secret)
    result=classify_check(data)
    assert secret not in json.dumps(result)


def test_handles_missing_and_invalid_files(tmp_path,capsys):
    path=tmp_path/"check.json"
    assert main([str(path)])==2
    path.write_text("{bad json",encoding="utf-8")
    assert main([str(path)])==2
    assert "raw content suppressed" in capsys.readouterr().out
