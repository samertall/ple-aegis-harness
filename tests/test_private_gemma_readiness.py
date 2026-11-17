"""Readiness logic is purely advisory and makes no external requests."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_private_gemma_readiness import grade_local_host


def test_small_machine_flagged_unsuitable():
    r=grade_local_host(4,16,20,4)
    assert not r["plausible_local_gemma"]
    assert not r["host_ram_at_least_16_25_gib"]
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


def test_windows_dispatch_uses_host_memory_not_linux_proc(monkeypatch):
    import check_private_gemma_readiness as scanner
    monkeypatch.setattr(scanner.sys, "platform", "win32")
    monkeypatch.setattr(scanner, "read_windows_ram_gib", lambda: 63.75)
    assert scanner.read_ram_gib() == 63.75


def test_linux_proc_meminfo_is_still_supported(monkeypatch):
    import check_private_gemma_readiness as scanner
    monkeypatch.setattr(scanner.sys, "platform", "linux")
    original = Path.read_text
    def fake_read_text(self, *args, **kwargs):
        if str(self) == "/proc/meminfo":
            return "MemTotal:       33554432 kB\nMemFree: 1000 kB\n"
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", fake_read_text)
    assert scanner.read_ram_gib() == 32.0


def test_windows_ram_failure_reports_unknown_not_false_adequacy(monkeypatch):
    import check_private_gemma_readiness as scanner
    monkeypatch.setattr(scanner.sys, "platform", "win32")
    monkeypatch.setattr(scanner, "read_windows_ram_gib", lambda: 0.0)
    assert scanner.read_ram_gib() == 0.0
    assert not scanner.grade_local_host(8, scanner.read_ram_gib(), 100, 24)["plausible_local_gemma"]


def test_ram_threshold_is_host_only_not_docker_allocation():
    r=grade_local_host(20,23.71,14.51,6)
    assert r["host_ram_at_least_16_25_gib"] is True
    assert r["docker_memory_16_25_gib_verified"] is False
    assert r["disk_shortfall_to_60_gib"] == 45.49
    assert not r["plausible_local_gemma"]
    assert "Host RAM is not Docker" in r["note"]


def test_gemma_readiness_remains_advisory_even_with_good_host():
    r=grade_local_host(20,64.0,125.0,24)
    assert r["plausible_local_gemma"]
    assert not r["docker_memory_16_25_gib_verified"]
    assert r["disk_shortfall_to_60_gib"] == 0
    assert r["model_run_verified"] is False
