"""Offline hardware capability check for a PRIVATE Gemma 4 26B PLE option.

Reads only local CPU, RAM, disk, NVIDIA VRAM and Docker readiness.
Never downloads a model or reads/discloses API keys, hostnames or files.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GIB = 1024 ** 3


def grade_local_host(cpu_count, ram_gib, free_disk_gib, gpu_vram_gib):
    """Advisory only: true capacity depends on model quantization/context/runtime."""
    cpu_ok = cpu_count >= 6
    # Physical host RAM does NOT establish the memory allocated to Docker/WSL.
    host_ram_ok = ram_gib >= 16.25
    disk_ok = free_disk_gib >= 60
    # Gemma 4 26B A4B Q4 weighs roughly 16-19GB before KV/context.
    plausible_gpu = gpu_vram_gib >= 24
    plausible_ram_only = ram_gib >= 48
    return {
        "cpu_6_cores": cpu_ok,
        "host_ram_at_least_16_25_gib": host_ram_ok,
        "docker_memory_16_25_gib_verified": False,
        "disk_shortfall_to_60_gib": round(max(0.0, 60.0 - free_disk_gib), 2),
        "suggested_disk_60_gib": disk_ok,
        "plausible_local_gemma": bool(
            cpu_ok and host_ram_ok and disk_ok
            and (plausible_gpu or plausible_ram_only)
        ),
        "model_run_verified": False,
        "note": "Host RAM is not Docker/WSL allocated memory. Private Gemma+PLE capacity and speed require separate validation.",
    }


def read_windows_ram_gib():
    """Physical host memory from Windows kernel; not WSL/Docker allocation."""
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        state = MEMORYSTATUSEX()
        state.dwLength = ctypes.sizeof(state)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
            return 0.0
        return state.ullTotalPhys / GIB
    except (AttributeError, OSError, ValueError):
        return 0.0


def read_ram_gib():
    if sys.platform == "win32":
        return read_windows_ram_gib()
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024 / GIB
    except (OSError, ValueError, IndexError):
        pass
    return 0.0


def read_gpu_vram_gib():
    if not shutil.which("nvidia-smi"):
        return 0.0
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=4, check=True,
        )
        sizes = [int(row.strip()) for row in result.stdout.splitlines() if row.strip().isdigit()]
        return max(sizes, default=0) * 1024**2 / GIB
    except (OSError, subprocess.SubprocessError, ValueError):
        return 0.0


def docker_ready():
    if not shutil.which("docker"):
        return False
    try:
        r = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False, timeout=7,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def main():
    cpu = os.cpu_count() or 0
    ram = round(read_ram_gib(), 2)
    disk = round(shutil.disk_usage(Path.home()).free / GIB, 2)
    gpu = round(read_gpu_vram_gib(), 2)
    out = {
        "platform": sys.platform,
        "cpu_cores": cpu, "ram_gib": ram, "home_disk_free_gib": disk,
        "max_nvidia_gpu_vram_gib": gpu, "docker_available": docker_ready(),
    }
    if sys.platform == "win32":
        out["windows_note"] = (
            "RAM is Windows host physical memory, NOT WSL2 or Docker allocated RAM. "
            "Verify WSL2 and Docker resources separately before running PLE."
        )
    out["readiness"] = grade_local_host(cpu,ram,disk,gpu)
    out["readiness"]["ple_docker_daemon_verified"] = out["docker_available"]
    out["readiness"]["ple_local_evaluation_ready"] = False  # hardware grade alone cannot verify a real evaluator
    print(json.dumps(out, indent=2))
    print("This check is OFFLINE; no cloud, model inference, download or PLE task used.")


if __name__ == "__main__":
    main()
