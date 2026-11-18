"""Check that temporary free GitHub runners never bypass PLE constraints."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from scan_artifact_credentials import main, has_credential_pattern


def test_artifact_scanner_rejects_realistic_secret_shape_without_printing(capsys,tmp_path):
    (tmp_path/"out.txt").write_bytes(b"stuff AIza"+"A".encode()*32+b" more")
    assert has_credential_pattern(tmp_path)
    assert main([str(tmp_path)])==1
    assert "AIza" not in capsys.readouterr().out


def test_artifact_scanner_detects_cross_chunk_secret(tmp_path):
    token=b"hf_"+b"Z"*24
    (tmp_path/"out.bin").write_bytes(b"x"*(256*1024-7)+token+b"y")
    assert has_credential_pattern(tmp_path)


def test_artifact_scanner_accepts_innocent_original_export(tmp_path):
    (tmp_path/"manifest.json").write_text('{"format":1}')
    (tmp_path/".gitattributes").write_text("* -text")
    assert not has_credential_pattern(tmp_path)


def test_no_real_task_without_three_explicit_authorizations():
    wf=(ROOT/".github/workflows/ple-one-task-free-gated.yml").read_text()
    assert "workflow_dispatch:" in wf
    assert "\n  push:" not in wf and "\n  schedule:" not in wf
    assert "YES_UNBILLED" in wf
    assert "YES_WRITTEN_ORGANIZER_CLEARANCE" in wf
    assert "YES_FREE_RUNNER_ONLY" in wf
    assert "confirm_gated_data_permission" in wf
    assert "runs-on: ubuntu-latest" in wf
    assert "secrets.PLE_HF_TOKEN" in wf
    assert "secrets.PLE_GEMINI_API_KEY" in wf
    assert "eval/run.py" in wf
    assert "include-hidden-files: true" in wf
    assert "scan_artifact_credentials.py" in wf
    assert "git push" not in wf


def test_manual_workflow_cannot_spend_by_accidental_cost_gate():
    wf=(ROOT/".github/workflows/ple-one-task-free-gated.yml").read_text()
    assert "YES_I_AUTHORIZE_MODEL_COSTS" not in wf
    assert "self-hosted" not in wf
    assert "vertex_ai" not in wf
    assert "gcloud" not in wf
    assert "YES_WRITTEN_ORGANIZER_CLEARANCE" in wf
