"""Verify free temporary-runner resource audit cannot fabricate PLE readiness."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from audit_free_runner import compare


def snap(cpu=4, ram=15.6, disk=20.0, docker=True):
    return {
        "cpu_count": cpu,
        "physical_ram_gib": ram,
        "disk_free_gib": disk,
        "disk_total_gib": 80,
        "docker_executable_found": docker,
        "is_github_hosted": True,
    }


def test_more_temp_disk_does_not_hide_runner_cpu_shortage():
    finding=compare(snap(), snap(disk=70))
    assert finding["disk_reclaimed_gib"]==50
    assert finding["disk_meets_advisory_scratch_budget"]
    assert not finding["cpu_meets_full_ple_guideline"]
    assert not finding["full_ple_runner_ready"]
    assert not finding["evaluator_trial_verified"]


def test_partial_single_task_estimate_is_not_claimed_as_proof():
    finding=compare(snap(),snap(disk=51))
    assert finding["could_attempt_one_small_task"]
    assert not finding["full_ple_runner_ready"]
    assert not finding["evaluator_trial_verified"]


def test_full_resource_thresholds_still_not_benchmark_evidence():
    finding=compare(snap(cpu=6,ram=20,disk=70),snap(cpu=6,ram=20,disk=72))
    assert finding["full_ple_runner_ready"]
    assert not finding["evaluator_trial_verified"]


def test_missing_docker_prevents_runner_ready():
    finding=compare(snap(cpu=6,ram=20,disk=70,docker=False),snap(cpu=6,ram=20,disk=70,docker=False))
    assert not finding["full_ple_runner_ready"]


def test_audit_has_no_credential_or_cloud_model_calls():
    code=(ROOT/"scripts/audit_free_runner.py").read_text()
    flow=(ROOT/".github/workflows/ple-free-runner-capacity.yml").read_text()
    assert "HF_TOKEN" not in code and "GEMINI_API_KEY" not in code
    assert "eval/run.py" not in flow
    assert "PLE_HF_TOKEN" not in flow
    assert "secrets." not in flow
    assert "runs-on: ubuntu-latest" in flow
    assert "RUNNER_ENVIRONMENT" in flow
    assert "sudo rm -rf" in flow
    assert "github-hosted" in flow


def test_bad_resource_snapshot_rejected():
    try:
        compare({},snap())
    except ValueError:
        return
    assert False, "Expected invalid snapshot to be rejected"
