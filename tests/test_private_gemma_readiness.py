"""Readiness logic is purely advisory and makes no external requests."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_private_gemma_readiness import grade_local_host


def test_small_machine_flagged_unsuitable():
    r=grade_local_host(4,16,20,4)
    assert not r["plausible_local_gemma"]
    assert not r["ple_docker_16_25_gib"]
    assert not r["suggested_disk_60_gib"]
    assert not r["model_run_verified"]


def test_suitable_gpu_machine_is_still_unverified():
    r=grade_local_host(12,64,200,32)
    assert r["plausible_local_gemma"]
    assert not r["model_run_verified"]


def test_suitable_ram_only_host_is_only_plausible():
    r=grade_local_host(8,64,150,0)
    assert r["plausible_local_gemma"]
    assert "Estimate only" in r["note"]


def test_gpu_does_not_override_missing_docker_ram():
    r=grade_local_host(8,12,120,48)
    assert not r["plausible_local_gemma"]


def test_does_not_use_credentials_or_download_models():
    code=(ROOT/"scripts/check_private_gemma_readiness.py").read_text()
    assert "GEMINI_API_KEY" not in code
    assert "HF_TOKEN" not in code
    assert "urlopen" not in code
    assert "requests." not in code
    assert "ollama pull" not in code
    assert "model_run_verified" in code
